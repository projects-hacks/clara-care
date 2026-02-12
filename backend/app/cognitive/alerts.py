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
        Check deviations and generate alerts if thresholds are met
        
        Args:
            patient_id: Patient identifier
            metrics: Current CognitiveMetrics dict
            deviations: List of BaselineDeviation dicts from baseline tracker
            
        Returns:
            List of Alert dicts that were created
        """
        if not deviations:
            return []
        
        # Get patient's consecutive trigger threshold
        patient = await self.data_store.get_patient(patient_id)
        consecutive_trigger = patient.get("cognitive_thresholds", {}).get(
            "consecutive_trigger",
            self.default_consecutive_trigger
        )
        
        alerts_created = []
        
        for deviation in deviations:
            # Only alert if consecutive count meets threshold
            if deviation["consecutive_count"] >= consecutive_trigger:
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
        
        # Create alert dict
        alert = {
            "id": f"alert-{uuid.uuid4().hex[:8]}",
            "patient_id": patient_id,
            "alert_type": alert_type,
            "severity": deviation["severity"],
            "description": description,
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
        """Generate human-readable alert description"""
        metric_name = deviation["metric_name"]
        dev_percent = abs(deviation["deviation_percent"])
        consecutive = deviation["consecutive_count"]
        
        metric_labels = {
            "vocabulary_diversity": "Vocabulary diversity",
            "topic_coherence": "Topic coherence",
            "repetition_rate": "Repetition rate",
            "word_finding_pauses": "Word-finding pauses",
            "response_latency": "Response latency"
        }
        
        label = metric_labels.get(metric_name, metric_name.replace("_", " ").title())
        
        direction = "declined" if deviation["deviation_percent"] < 0 else "increased"
        
        description = (
            f"{label} has {direction} by {dev_percent:.1f}% over the last "
            f"{consecutive} consecutive conversations"
        )
        
        return description
    
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
            "related_metrics": context,
            "timestamp": datetime.now(UTC).isoformat(),
            "acknowledged": False
        }
        
        # Save to data store
        alert_id = await self.data_store.save_alert(alert)
        alert["id"] = alert_id
        
        logger.critical(f"REALTIME ALERT: {alert_type} ({severity}) - {message}")
        
        # Dispatch notification immediately for high-severity real-time alerts
        if severity == "high" and self.notification_service:
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
        Mark an alert as acknowledged
        
        Args:
            alert_id: Alert identifier
            acknowledged_by: ID of person acknowledging (family member ID)
            
        Returns:
            True if successful
        """
        updates = {
            "acknowledged": True,
            "acknowledged_at": datetime.now(UTC).isoformat(),
            "acknowledged_by": acknowledged_by
        }
        
        success = await self.data_store.update_alert(alert_id, updates)
        
        if success:
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        
        return success
