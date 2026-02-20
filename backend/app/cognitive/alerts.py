"""
Alert Engine
Generates and manages alerts based on cognitive deviations and real-time triggers
"""

import logging
import uuid
from datetime import datetime, UTC
from typing import Optional

logger = logging.getLogger(__name__)


class AlertEngine:
    """
    Generates alerts from baseline deviations and dispatches notifications
    """
    
    def __init__(self, data_store, notification_service=None):
        """
        Args:
            data_store: DataStore implementation
            notification_service: Optional NotificationService for dispatching alerts
        """
        self.data_store = data_store
        self.notification_service = notification_service
        self.default_consecutive_trigger = 3
    
    async def check_and_alert(
        self,
        patient_id: str,
        metrics: dict,
        deviations: list[dict]
    ) -> list[dict]:
        """
        Check deviations and generate alerts if thresholds are met.
        De-duplicates: skips if an unacknowledged alert already exists
        for the same alert_type. Upgrades severity if new is worse.
        """
        if not deviations:
            return []
        
        # Get patient's consecutive trigger threshold
        patient = await self.data_store.get_patient(patient_id)
        consecutive_trigger = patient.get("cognitive_thresholds", {}).get(
            "consecutive_trigger",
            self.default_consecutive_trigger
        )
        
        # Fetch existing unacknowledged alerts for dedup
        existing_alerts = await self.data_store.get_alerts(patient_id, limit=50)
        active_by_type = {}
        for a in existing_alerts:
            if not a.get("acknowledged"):
                active_by_type[a.get("alert_type")] = a
        
        # Map metric names → alert types
        alert_type_map = {
            "vocabulary_diversity": "vocabulary_shrinkage",
            "topic_coherence": "coherence_drop",
            "repetition_rate": "repetition_increase",
            "word_finding_pauses": "word_finding_difficulty",
            "response_latency": "response_delay"
        }
        
        alerts_created = []
        
        for deviation in deviations:
            # Only alert if consecutive count meets threshold
            if deviation["consecutive_count"] >= consecutive_trigger:
                a_type = alert_type_map.get(deviation["metric_name"], "cognitive_decline")
                
                # Dedup: skip if active alert already exists for this type
                if a_type in active_by_type:
                    existing = active_by_type[a_type]
                    if self._severity_rank(deviation["severity"]) > self._severity_rank(existing.get("severity", "low")):
                        # Upgrade severity on existing alert
                        await self.data_store.update_alert(existing["id"], {
                            "severity": deviation["severity"]
                        })
                        logger.info(f"Upgraded alert {existing['id']} to {deviation['severity']}")
                    else:
                        logger.info(f"Skipping duplicate alert for {a_type} (active alert exists)")
                    continue
                
                alert = await self._create_alert_from_deviation(
                    patient_id,
                    deviation,
                    metrics
                )
                alerts_created.append(alert)
        
        # Dispatch notifications if service is available
        if alerts_created and self.notification_service:
            await self._dispatch_notifications(patient_id, alerts_created)
        
        return alerts_created
    
    @staticmethod
    def _severity_rank(severity: str) -> int:
        """Rank severity for comparison: higher = worse."""
        return {"low": 1, "medium": 2, "high": 3}.get(severity, 0)
    
    async def _create_alert_from_deviation(
        self,
        patient_id: str,
        deviation: dict,
        metrics: dict
    ) -> dict:
        """
        Create an alert from a baseline deviation
        """
        metric_name = deviation["metric_name"]
        
        # Map metric to alert type
        alert_type_map = {
            "vocabulary_diversity": "vocabulary_shrinkage",
            "topic_coherence": "coherence_drop",
            "repetition_rate": "repetition_increase",
            "word_finding_pauses": "word_finding_difficulty",
            "response_latency": "response_delay"
        }
        
        alert_type = alert_type_map.get(metric_name, "cognitive_decline")
        
        # Generate description
        description = self._generate_alert_description(deviation)
        suggested_action = self._get_suggested_action(alert_type)
        
        # Create alert dict
        alert = {
            "id": f"alert-{uuid.uuid4().hex[:8]}",
            "patient_id": patient_id,
            "alert_type": alert_type,
            "severity": deviation["severity"],
            "description": description,
            "suggested_action": suggested_action,
            "related_metrics": {
                "metric_name": metric_name,
                "current_value": deviation["current_value"],
                "baseline_value": deviation["baseline_value"],
                "deviation_percent": deviation["deviation_percent"],
                "consecutive_count": deviation["consecutive_count"]
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "acknowledged": False
        }
        
        # Save to data store
        alert_id = await self.data_store.save_alert(alert)
        alert["id"] = alert_id
        
        logger.warning(f"Alert created: {alert_type} ({deviation['severity']}) for patient {patient_id}")
        
        return alert

    
    def _generate_alert_description(self, deviation: dict) -> str:
        """Generate plain-English alert description for family members — no jargon or raw numbers."""
        metric_name = deviation["metric_name"]
        consecutive = deviation["consecutive_count"]
        severity = deviation.get("severity", "medium")

        # Human-readable severity qualifier
        severity_qualifier = {
            "low": "a small",
            "medium": "a noticeable",
            "high": "a significant",
        }.get(severity, "a")

        # How many conversations back the pattern spans
        if consecutive <= 1:
            pattern_phrase = "her most recent conversation"
        elif consecutive == 2:
            pattern_phrase = "the last 2 conversations"
        else:
            pattern_phrase = f"the last {consecutive} conversations in a row"

        descriptions = {
            "vocabulary_diversity": (
                f"She has been using a more limited range of words than usual across {pattern_phrase}. "
                "This can sometimes happen when someone is feeling tired, stressed, or experiencing subtle memory changes. "
                "It's worth keeping an eye on."
            ),
            "topic_coherence": (
                f"Her conversations have been harder to follow than usual across {pattern_phrase}. "
                "She may be jumping between topics or losing the thread of what she was saying more than is typical for her. "
                "This can indicate moments of confusion or difficulty concentrating."
            ),
            "repetition_rate": (
                f"She has been repeating certain stories or phrases more often than usual across {pattern_phrase}. "
                "Repetition can sometimes be a sign of something on her mind, or it may reflect short-term memory changes worth watching."
            ),
            "word_finding_pauses": (
                f"She has been stopping more often to search for words during {pattern_phrase}. "
                "You might notice phrases like \"um,\" \"you know,\" or sentences that trail off. "
                "While this can be normal with age, the increase compared to her usual pattern is worth noting."
            ),
            "response_latency": (
                f"She has been taking longer than usual to respond in conversations across {pattern_phrase}. "
                "This can be a sign of fatigue, reduced concentration, or difficulty processing what was said."
            ),
        }

        return descriptions.get(
            metric_name,
            (
                f"We noticed {severity_qualifier} change in her conversation patterns across {pattern_phrase}. "
                "This may be worth monitoring."
            ),
        )

    def _get_suggested_action(self, alert_type: str) -> str:
        """Return a concrete action the FAMILY MEMBER can take for this alert type."""
        actions = {
            "vocabulary_shrinkage": (
                "Give her a call and chat about something she loves — "
                "a favourite memory, a family story, or what's been on her mind."
            ),
            "coherence_drop": (
                "Call her yourself today. Keep the conversation light and ask one thing at a time — "
                "a familiar voice makes a real difference."
            ),
            "repetition_increase": (
                "Give her a ring and introduce a new topic like upcoming family plans or a shared memory — "
                "it gives her something fresh to talk about."
            ),
            "word_finding_difficulty": (
                "Call her and let the conversation flow at her pace. "
                "If this keeps happening, mention it to her doctor at the next visit."
            ),
            "response_delay": (
                "Check in with her — a short call to ask how she's feeling today goes a long way."
            ),
            "distress": (
                "Call her right away and let her know you're thinking of her. "
                "If she seems very distressed, consider arranging a visit or contacting her caregiver."
            ),
            "confusion_detected": (
                "Give her a reassuring call or, if possible, pop in for a visit. "
                "Let her doctor know if this is becoming more frequent."
            ),
            "fall": (
                "Call her immediately to confirm she is safe. "
                "If you can't reach her, contact her caregiver or a neighbour right away."
            ),
            "emergency": (
                "Call her immediately. If you can't reach her, contact emergency services or her on-site caregiver."
            ),
            "cognitive_decline": (
                "Bring this up at her next doctor's appointment — mention the dates and what you noticed."
            ),
            "social_connection": (
                "She's missing you. Give her a call or plan a visit soon — even just 10 minutes together means a lot."
            ),
        }
        return actions.get(
            alert_type,
            "Give her a call to check in, and mention this to her doctor if it keeps happening."
        )
    
    async def create_realtime_alert(
        self,
        patient_id: str,
        alert_type: str,
        severity: str,
        message: str,
        context: Optional[dict] = None
    ) -> dict:
        """
        Create a real-time alert (e.g., from voice triggers like distress or fall)
        
        Args:
            patient_id: Patient identifier
            alert_type: Type of alert (distress, fall, emergency, etc.)
            severity: low, medium, high
            message: Human-readable alert message
            context: Optional additional context
            
        Returns:
            Created Alert dict
        """
        alert = {
            "id": f"alert-{uuid.uuid4().hex[:8]}",
            "patient_id": patient_id,
            "alert_type": alert_type,
            "severity": severity,
            "description": message,
            "suggested_action": self._get_suggested_action(alert_type),
            "related_metrics": context,
            "timestamp": datetime.now(UTC).isoformat(),
            "acknowledged": False
        }
        
        # Save to data store
        alert_id = await self.data_store.save_alert(alert)
        alert["id"] = alert_id
        
        logger.critical(f"REALTIME ALERT: {alert_type} ({severity}) - {message}")
        
        # Dispatch notification for high and medium severity real-time alerts
        if severity in ("high", "medium") and self.notification_service:
            await self._dispatch_notifications(patient_id, [alert])
        
        return alert

    
    async def _dispatch_notifications(self, patient_id: str, alerts: list[dict]) -> None:
        """
        Send notifications to family members for alerts
        """
        try:
            # Get family contacts
            contacts = await self.data_store.get_family_contacts(patient_id)
            
            if not contacts:
                logger.warning(f"No family contacts found for patient {patient_id}")
                return
            
            # Filter contacts who want instant alerts
            instant_contacts = [
                c for c in contacts
                if c.get("notification_preferences", {}).get("instant_alerts", True)
            ]
            
            if not instant_contacts:
                logger.info("No contacts have instant alerts enabled")
                return
            
            # Send alert notification
            for alert in alerts:
                await self.notification_service.send_alert_notification(
                    patient_id,
                    alert
                )
            
            logger.info(f"Dispatched {len(alerts)} alert(s) to {len(instant_contacts)} contact(s)")
            
        except Exception as e:
            logger.error(f"Error dispatching notifications: {e}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Mark an alert as acknowledged.
        Resolves family member ID to their display name before storing.
        """
        # Resolve family member name from patient's contacts
        display_name = acknowledged_by
        try:
            # Get the alert first to find the patient
            all_alerts = await self.data_store.get_alerts("", limit=100)
            alert_record = next((a for a in all_alerts if a.get("id") == alert_id), None)
            if alert_record:
                patient = await self.data_store.get_patient(alert_record.get("patient_id", ""))
                if patient:
                    for contact in patient.get("family_contacts", []):
                        if contact.get("id") == acknowledged_by:
                            display_name = contact.get("name", acknowledged_by)
                            break
        except Exception as e:
            logger.debug(f"Could not resolve family name for {acknowledged_by}: {e}")
        
        updates = {
            "acknowledged": True,
            "acknowledged_by": display_name,
            "acknowledged_at": datetime.now(UTC).isoformat()
        }
        
        success = await self.data_store.update_alert(alert_id, updates)
        if success:
            logger.info(f"Alert {alert_id} acknowledged by {display_name}")
        return success
