"""
Cognitive Pipeline Orchestrator
Chains all cognitive processing steps: analyze -> baseline -> alert -> digest
"""

import logging
import uuid
from datetime import datetime, date, UTC
from typing import Optional

from .utils import calculate_cognitive_score

logger = logging.getLogger(__name__)


class CognitivePipeline:
    """
    Orchestrates the full cognitive analysis pipeline
    Entry point: process_conversation() is called after each voice conversation
    """
    
    def __init__(
        self,
        analyzer,
        baseline_tracker,
        alert_engine,
        data_store,
        notification_service=None
    ):
        """
        Args:
            analyzer: CognitiveAnalyzer instance
            baseline_tracker: BaselineTracker instance
            alert_engine: AlertEngine instance
            data_store: DataStore implementation
            notification_service: Optional EmailNotifier for sending digests
        """
        self.analyzer = analyzer
        self.baseline_tracker = baseline_tracker
        self.alert_engine = alert_engine
        self.data_store = data_store
        self.notification_service = notification_service
    
    async def process_conversation(
        self,
        patient_id: str,
        transcript: str,
        duration: int,
        summary: str,
        detected_mood: str,
        response_times: Optional[list[float]] = None,
        conversation_id: Optional[str] = None,
        analysis: Optional[dict] = None
    ) -> dict:
        """
        Run full cognitive pipeline on a conversation
        
        Args:
            patient_id: Patient identifier
            transcript: Full conversation transcript
            duration: Duration in seconds
            summary: Conversation summary
            detected_mood: Detected mood (happy, sad, etc.)
            response_times: Optional list of response latencies
            conversation_id: Optional conversation ID
            
        Returns:
            Pipeline result dict with conversation_id, metrics, alerts, digest
        """
        logger.info(f"Processing conversation for patient: {patient_id}")
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = f"conversation-{uuid.uuid4().hex[:8]}"
        
        # Get patient info
        patient = await self.data_store.get_patient(patient_id)
        if not patient:
            logger.error(f"Patient not found: {patient_id}")
            return {"success": False, "error": "Patient not found"}
        
        patient_name = patient.get("preferred_name") or patient.get("name") or "Patient"
        
        # Get recent conversation history for cross-conversation repetition detection
        recent_convos = await self.data_store.get_conversations(patient_id=patient_id, limit=5)
        history_transcripts = [c.get("transcript", "") for c in recent_convos if c.get("transcript")]
        
        # Step 1: Analyze conversation with NLP metrics (including cross-conversation repetition)
        logger.info("Step 1: Analyzing conversation metrics...")
        metrics = await self.analyzer.analyze_conversation(
            transcript=transcript,
            patient_name=patient_name,
            response_times=response_times,
            conversation_id=conversation_id,
            patient_id=patient_id,
            history_transcripts=history_transcripts  # For cross-conversation repetition
        )
        
        # Step 2: Save conversation with metrics
        conversation = {
            "id": conversation_id,
            "patient_id": patient_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "duration": duration,
            "summary": summary,
            "detected_mood": detected_mood,
            "transcript": transcript,
            "cognitive_metrics": metrics
        }
        
        await self.data_store.save_conversation(conversation)
        logger.info(f"Conversation saved: {conversation_id}")
        
        # Step 3: Check if baseline exists, establish if ready
        baseline = await self.data_store.get_cognitive_baseline(patient_id)
        
        if not baseline or not baseline.get("established"):
            # Check if we have enough conversations to establish baseline
            if await self.baseline_tracker.check_baseline_ready(patient_id):
                logger.info("Sufficient conversations for baseline. Establishing...")
                baseline = await self.baseline_tracker.establish_baseline(patient_id)
            else:
                logger.info("Baseline not ready yet (need 7 conversations)")
                baseline = None
        
        # Step 4: Compare to baseline and detect deviations
        deviations = []
        alerts = []
        
        if baseline and baseline.get("established"):
            logger.info("Step 2: Comparing to baseline...")
            deviations = await self.baseline_tracker.compare_to_baseline(
                patient_id,
                metrics,
                baseline
            )
            
            # Step 5: Generate alerts if deviations are significant
            if deviations:
                logger.info(f"Step 3: Checking for alerts ({len(deviations)} deviations)...")
                alerts = await self.alert_engine.check_and_alert(
                    patient_id,
                    metrics,
                    deviations
                )
        
        # Step 6: Generate wellness digest
        logger.info("Step 4: Generating wellness digest...")
        digest = await self._generate_wellness_digest(
            patient_id,
            conversation_id,
            metrics,
            summary,
            detected_mood,
            baseline,
            analysis
        )
        
        # Step 7: Send daily digest email (if enabled)
        if digest and self.notification_service:
            await self._send_digest_notification(patient_id, digest)
        
        logger.info(f"Pipeline complete for {patient_id}. "
                   f"Metrics: ✓, Baseline: {'✓' if baseline else '⏳'}, "
                   f"Alerts: {len(alerts)}, Digest: ✓")
        
        # Extract cognitive score and trend from digest if available
        cognitive_score = digest.get("cognitive_score") if digest else None
        cognitive_trend = digest.get("cognitive_trend") if digest else None
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "metrics": metrics,
            "cognitive_score": cognitive_score,
            "cognitive_trend": cognitive_trend,
            "baseline_established": bool(baseline and baseline.get("established")),
            "deviations": deviations,
            "alerts": alerts,
            "digest": digest
        }
    
    async def _generate_wellness_digest(
        self,
        patient_id: str,
        conversation_id: str,
        metrics: dict,
        summary: str,
        mood: str,
        baseline: Optional[dict],
        analysis: Optional[dict] = None
    ) -> dict:
        """
        Generate wellness digest from conversation
        """
        # Calculate cognitive score (0-100)
        cognitive_score = self._calculate_cognitive_score(metrics)
        
        # Determine cognitive trend (compare last 3 scores)
        cognitive_trend = await self._determine_cognitive_trend(patient_id, cognitive_score)
        
        # Generate recommendations based on metrics
        recommendations = self._generate_recommendations(metrics, baseline)
        
        # Extract highlights from summary + analysis data
        highlights = self._extract_highlights(summary, analysis, metrics)
        
        # Create digest
        digest = {
            "id": f"digest-{uuid.uuid4().hex[:8]}",
            "patient_id": patient_id,
            "date": date.today().isoformat(),
            "overall_mood": mood,
            "highlights": highlights,
            "cognitive_score": cognitive_score,
            "cognitive_trend": cognitive_trend,
            "recommendations": recommendations,
            "conversation_id": conversation_id,
            "created_at": datetime.now(UTC).isoformat()
        }
        
        # Save digest
        await self.data_store.save_wellness_digest(digest)
        
        return digest
    
    def _calculate_cognitive_score(self, metrics: dict) -> int:
        """
        Calculate composite cognitive score (0-100)
        Delegates to shared utility function
        """
        return calculate_cognitive_score(metrics)
    
    async def _determine_cognitive_trend(self, patient_id: str, current_score: int) -> str:
        """
        Determine trend by comparing last 3 digest scores
        
        Returns:
            "improving", "stable", or "declining"
        """
        # Get last 3 digests
        recent_digests = await self.data_store.get_wellness_digests(patient_id, limit=3)
        
        if len(recent_digests) < 2:
            return "stable"  # Not enough data
        
        # Extract scores
        scores = [d["cognitive_score"] for d in recent_digests]
        scores.append(current_score)
        
        # Compare average of last 3 to current
        if len(scores) >= 3:
            prev_avg = sum(scores[:-1]) / len(scores[:-1])
            
            if current_score > prev_avg + 5:
                return "improving"
            elif current_score < prev_avg - 5:
                return "declining"
        
        return "stable"
    
    def _extract_highlights(self, summary: str, analysis: Optional[dict] = None, metrics: Optional[dict] = None) -> list[str]:
        """
        Extract key highlights from conversation summary and analysis data.
        Builds rich highlights using actual data instead of just splitting summary text.
        """
        highlights = []
        
        # 1. Use cleaned summary as first highlight
        if summary and len(summary) > 10:
            # Clean up and capitalize
            clean = summary.strip()
            if not clean.endswith(('.', '!', '?')):
                clean += '.'
            highlights.append(clean)
        
        # 2. Add mood context from analysis
        if analysis:
            mood_explanation = analysis.get("mood_explanation", "")
            if mood_explanation:
                highlights.append(mood_explanation)
            
            # 3. Add medication info
            med_status = analysis.get("medication_status", {})
            if med_status.get("discussed"):
                notes = med_status.get("notes", "")
                if notes:
                    highlights.append(f"Medication discussed: {notes}")
                else:
                    highlights.append("Medication was discussed during the call.")
            
            # 4. Add engagement level
            engagement = analysis.get("engagement_level", "")
            if engagement:
                engagement_text = {
                    "high": "Patient was highly engaged and talkative.",
                    "medium": "Patient had moderate engagement during the call.",
                    "low": "Patient was quieter than usual during the call."
                }
                highlights.append(engagement_text.get(engagement, f"Engagement level: {engagement}."))
            
            # 5. Add action items
            action_items = analysis.get("action_items", [])
            for item in action_items[:2]:
                highlights.append(f"Action needed: {item}")
            
            # 6. Add memory concern if detected
            memory_flags = analysis.get("memory_inconsistency", [])
            if memory_flags:
                highlights.append("⚠️ Memory inconsistency detected during conversation.")
        
        # 7. Add coherence info from metrics
        if metrics:
            coherence = metrics.get("topic_coherence")
            if coherence is not None and coherence < 0.40:
                highlights.append(f"⚠️ Low conversation coherence ({coherence:.2f}) — may indicate confusion.")
        
        # Fallback if nothing found
        if not highlights:
            highlights = [summary] if summary else ["Brief check-in call."]
        
        return highlights[:5]
    
    def _generate_recommendations(
        self,
        metrics: dict,
        baseline: Optional[dict]
    ) -> list[str]:
        """
        Generate recommendations based on metrics and baseline.
        Provides early recommendations even without baseline for new patients.
        """
        recommendations = []
        
        # ── Early recommendations (no baseline needed) ───────────────────
        # Low coherence warning
        coherence = metrics.get("topic_coherence")
        if coherence is not None and coherence < 0.40:
            recommendations.append(
                "Conversation coherence was low. Ensure adequate rest and a calm environment for calls."
            )
        
        # Word-finding pauses
        if metrics.get("word_finding_pauses", 0) > 3:
            recommendations.append(
                "Several word-finding pauses were noted. Monitor for patterns and consider mentioning to their doctor."
            )
        
        # High repetition
        if metrics.get("repetition_rate", 0) > 0.1:
            recommendations.append(
                "Some repetition was detected. Continue monitoring in upcoming conversations."
            )
        
        # ── Baseline-based recommendations (need 7+ conversations) ──────
        if baseline and baseline.get("established"):
            # Check vocabulary diversity
            if metrics.get("vocabulary_diversity") is not None and baseline.get("vocabulary_diversity"):
                vocab_dev = ((metrics["vocabulary_diversity"] - baseline["vocabulary_diversity"]) 
                             / baseline["vocabulary_diversity"] * 100)
                if vocab_dev < -15:
                    recommendations.append(
                        "Vocabulary diversity has decreased compared to baseline. Consider word games or varied topics."
                    )
            
            # Check coherence vs baseline
            if coherence is not None and baseline.get("topic_coherence"):
                coherence_dev = ((coherence - baseline["topic_coherence"]) 
                                / baseline["topic_coherence"] * 100)
                if coherence_dev < -15:
                    recommendations.append(
                        "Conversation coherence has declined compared to baseline. Monitor closely."
                    )
        
        return recommendations
    
    async def _send_digest_notification(self, patient_id: str, digest: dict) -> None:
        """
        Send wellness digest email to family contacts
        """
        try:
            contacts = await self.data_store.get_family_contacts(patient_id)
            
            if contacts and self.notification_service:
                await self.notification_service.send_daily_digest(patient_id, digest)
                logger.info(f"Daily digest sent to {len(contacts)} contact(s)")
        except Exception as e:
            logger.error(f"Error sending digest notification: {e}")
