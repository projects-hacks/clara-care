"""
Baseline Tracker
Establishes cognitive baselines and detects deviations
"""

import logging
from datetime import datetime, date, UTC
from typing import Optional
import statistics

logger = logging.getLogger(__name__)


class BaselineTracker:
    """
    Tracks cognitive baselines and detects significant deviations
    """
    
    def __init__(self, data_store):
        """
        Args:
            data_store: DataStore implementation (InMemoryDataStore or SanityDataStore)
        """
        self.data_store = data_store
        self.default_deviation_threshold = 0.20  # 20%
        self.default_consecutive_trigger = 3
    
    async def check_baseline_ready(self, patient_id: str) -> bool:
        """
        Check if patient has enough conversations to establish baseline
        
        Returns:
            True if 7+ conversations exist
        """
        conversations = await self.data_store.get_conversations(patient_id, limit=7)
        return len(conversations) >= 7
    
    async def establish_baseline(self, patient_id: str) -> dict:
        """
        Establish cognitive baseline from first 7+ conversations
        
        Returns:
            CognitiveBaseline dict
        """
        logger.info(f"Establishing baseline for patient: {patient_id}")
        
        # Get first 7 conversations with metrics
        conversations = await self.data_store.get_conversations(patient_id, limit=7)
        
        if len(conversations) < 7:
            logger.warning(f"Insufficient conversations ({len(conversations)}/7) for baseline")
            return self._empty_baseline(patient_id)
        
        # Extract metrics from conversations
        metrics_list = []
        for conv in conversations:
            metrics = conv.get("cognitive_metrics")
            # Skip partial metrics AND skip any with None values (from short conversations)
            if (metrics and 
                not metrics.get("_partial") and 
                metrics.get("vocabulary_diversity") is not None and
                metrics.get("topic_coherence") is not None):
                metrics_list.append(metrics)
        
        if len(metrics_list) < 7:
            logger.warning(f"Insufficient valid metrics ({len(metrics_list)}/7)")
            return self._empty_baseline(patient_id)
        
        # Calculate mean and std for each metric
        baseline = {
            "patient_id": patient_id,
            "established": True,
            "baseline_date": date.today().isoformat(),
            "conversation_count": len(metrics_list),
            "last_updated": datetime.now(UTC).isoformat()
        }
        
        # Vocabulary diversity
        vocab_values = [m["vocabulary_diversity"] for m in metrics_list]
        baseline["vocabulary_diversity"] = statistics.mean(vocab_values)
        baseline["vocabulary_diversity_std"] = statistics.stdev(vocab_values) if len(vocab_values) > 1 else 0.0
        
        # Topic coherence
        coherence_values = [m["topic_coherence"] for m in metrics_list]
        baseline["topic_coherence"] = statistics.mean(coherence_values)
        baseline["topic_coherence_std"] = statistics.stdev(coherence_values) if len(coherence_values) > 1 else 0.0
        
        # Repetition rate
        repetition_values = [m["repetition_rate"] for m in metrics_list]
        baseline["repetition_rate"] = statistics.mean(repetition_values)
        baseline["repetition_rate_std"] = statistics.stdev(repetition_values) if len(repetition_values) > 1 else 0.0
        
        # Word-finding pauses
        pause_values = [m["word_finding_pauses"] for m in metrics_list]
        baseline["word_finding_pauses"] = statistics.mean(pause_values)
        baseline["word_finding_pauses_std"] = statistics.stdev(pause_values) if len(pause_values) > 1 else 0.0
        
        # Response latency (optional)
        latency_values = [m["response_latency"] for m in metrics_list if m.get("response_latency") is not None]
        if latency_values:
            baseline["avg_response_time"] = statistics.mean(latency_values)
            baseline["response_time_std"] = statistics.stdev(latency_values) if len(latency_values) > 1 else 0.0
        else:
            baseline["avg_response_time"] = None
            baseline["response_time_std"] = None
        
        # Save baseline
        await self.data_store.save_cognitive_baseline(patient_id, baseline)
        
        logger.info(f"Baseline established: TTR={baseline['vocabulary_diversity']:.3f}, "
                   f"Coherence={baseline['topic_coherence']:.3f}, "
                   f"Repetition={baseline['repetition_rate']:.3f}")
        
        return baseline
    
    def _empty_baseline(self, patient_id: str) -> dict:
        """Return empty baseline structure"""
        return {
            "patient_id": patient_id,
            "established": False,
            "baseline_date": None,
            "vocabulary_diversity": 0.0,
            "vocabulary_diversity_std": 0.0,
            "topic_coherence": 0.0,
            "topic_coherence_std": 0.0,
            "repetition_rate": 0.0,
            "repetition_rate_std": 0.0,
            "avg_response_time": None,
            "response_time_std": None,
            "conversation_count": 0,
            "last_updated": datetime.now(UTC).isoformat()
        }
    
    async def compare_to_baseline(
        self,
        patient_id: str,
        metrics: dict,
        baseline: Optional[dict] = None
    ) -> list[dict]:
        """
        Compare current metrics to baseline and detect deviations
        
        Args:
            patient_id: Patient identifier
            metrics: Current CognitiveMetrics dict
            baseline: Optional baseline (fetched if not provided)
            
        Returns:
            List of BaselineDeviation dicts
        """
        if baseline is None:
            baseline = await self.data_store.get_cognitive_baseline(patient_id)
        
        if not baseline or not baseline.get("established"):
            logger.info(f"No baseline for patient {patient_id}, skipping comparison")
            return []
        
        # Get patient's deviation threshold
        patient = await self.data_store.get_patient(patient_id)
        threshold = patient.get("cognitive_thresholds", {}).get(
            "deviation_threshold",
            self.default_deviation_threshold
        )
        
        deviations = []
        
        # Check each metric
        metrics_to_check = [
            ("vocabulary_diversity", metrics["vocabulary_diversity"], baseline["vocabulary_diversity"], "lower_is_worse"),
            ("topic_coherence", metrics["topic_coherence"], baseline["topic_coherence"], "lower_is_worse"),
            ("repetition_rate", metrics["repetition_rate"], baseline["repetition_rate"], "higher_is_worse"),
            ("word_finding_pauses", metrics["word_finding_pauses"], baseline.get("word_finding_pauses", 0), "higher_is_worse"),
        ]
        
        # Get consecutive deviation counters
        consecutive = await self.data_store.get_consecutive_deviations(patient_id)
        
        for metric_name, current, baseline_val, direction in metrics_to_check:
            # Skip if either value is None (partial metrics) or baseline is zero
            if current is None or baseline_val is None or baseline_val == 0:
                continue
            
            # Calculate percentage deviation
            deviation_percent = ((current - baseline_val) / baseline_val) * 100
            
            # Check if deviation exceeds threshold (directional)
            is_deviation = False
            if direction == "lower_is_worse" and deviation_percent < -(threshold * 100):
                is_deviation = True
            elif direction == "higher_is_worse" and deviation_percent > (threshold * 100):
                is_deviation = True
            
            if is_deviation:
                # Increment consecutive counter
                consecutive[metric_name] = consecutive.get(metric_name, 0) + 1
                
                # Determine severity
                abs_dev = abs(deviation_percent)
                if abs_dev >= 50:
                    severity = "high"
                elif abs_dev >= 30:
                    severity = "medium"
                else:
                    severity = "low"
                
                deviations.append({
                    "metric_name": metric_name,
                    "baseline_value": baseline_val,
                    "current_value": current,
                    "deviation_percent": round(deviation_percent, 1),
                    "severity": severity,
                    "consecutive_count": consecutive[metric_name]
                })
            else:
                # Reset consecutive counter for this metric
                consecutive[metric_name] = 0
        
        # Update consecutive deviation counters
        await self.data_store.update_consecutive_deviations(patient_id, consecutive)
        
        if deviations:
            logger.warning(f"Detected {len(deviations)} baseline deviations for {patient_id}")
            for dev in deviations:
                logger.warning(f"  {dev['metric_name']}: {dev['deviation_percent']:.1f}% "
                             f"(consecutive: {dev['consecutive_count']})")
        
        return deviations
    
    async def update_rolling_baseline(self, patient_id: str) -> Optional[dict]:
        """
        Update baseline using rolling window (last 30 conversations)
        Optional: use after initial baseline is established
        
        Returns:
            Updated baseline or None if insufficient data
        """
        logger.info(f"Updating rolling baseline for patient: {patient_id}")
        
        # Get last 30 conversations
        conversations = await self.data_store.get_conversations(patient_id, limit=30)
        
        if len(conversations) < 10:
            logger.warning(f"Insufficient conversations ({len(conversations)}) for rolling update")
            return None
        
        # Use same logic as establish_baseline
        metrics_list = []
        for conv in conversations:
            metrics = conv.get("cognitive_metrics")
            if metrics and not metrics.get("_partial"):
                metrics_list.append(metrics)
        
        if len(metrics_list) < 10:
            logger.warning(f"Insufficient valid metrics ({len(metrics_list)})")
            return None
        
        # Calculate new baseline
        baseline = {
            "patient_id": patient_id,
            "established": True,
            "baseline_date": date.today().isoformat(),
            "conversation_count": len(metrics_list),
            "last_updated": datetime.now(UTC).isoformat()
        }
        
        # Recalculate all metrics
        vocab_values = [m["vocabulary_diversity"] for m in metrics_list]
        baseline["vocabulary_diversity"] = statistics.mean(vocab_values)
        baseline["vocabulary_diversity_std"] = statistics.stdev(vocab_values) if len(vocab_values) > 1 else 0.0
        
        coherence_values = [m["topic_coherence"] for m in metrics_list]
        baseline["topic_coherence"] = statistics.mean(coherence_values)
        baseline["topic_coherence_std"] = statistics.stdev(coherence_values) if len(coherence_values) > 1 else 0.0
        
        repetition_values = [m["repetition_rate"] for m in metrics_list]
        baseline["repetition_rate"] = statistics.mean(repetition_values)
        baseline["repetition_rate_std"] = statistics.stdev(repetition_values) if len(repetition_values) > 1 else 0.0
        
        # Word-finding pauses
        pause_values = [m["word_finding_pauses"] for m in metrics_list]
        baseline["word_finding_pauses"] = statistics.mean(pause_values)
        baseline["word_finding_pauses_std"] = statistics.stdev(pause_values) if len(pause_values) > 1 else 0.0
        
        latency_values = [m["response_latency"] for m in metrics_list if m.get("response_latency") is not None]
        if latency_values:
            baseline["avg_response_time"] = statistics.mean(latency_values)
            baseline["response_time_std"] = statistics.stdev(latency_values) if len(latency_values) > 1 else 0.0
        else:
            baseline["avg_response_time"] = None
            baseline["response_time_std"] = None
        
        # Save updated baseline
        await self.data_store.save_cognitive_baseline(patient_id, baseline)
        
        logger.info(f"Rolling baseline updated with {len(metrics_list)} conversations")
        return baseline
