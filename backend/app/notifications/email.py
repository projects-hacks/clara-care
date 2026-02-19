"""
Email Notification Service
Sends alert emails and daily wellness digests using async SMTP + Jinja2 templates
"""

import logging
import os
from typing import Optional
from datetime import datetime, UTC
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Handles email notifications for alerts and wellness digests
    Uses aiosmtplib for async sending and Jinja2 for templates
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        dashboard_url: Optional[str] = None,
        data_store = None
    ):
        """
        Initialize email notifier
        
        Args:
            smtp_host: SMTP server hostname (defaults to env var SMTP_HOST)
            smtp_port: SMTP port (defaults to env var SMTP_PORT or 587)
            smtp_user: SMTP username (defaults to env var SMTP_USER)
            smtp_password: SMTP password (defaults to env var SMTP_PASSWORD)
            from_email: From email address (defaults to env var FROM_EMAIL)
            dashboard_url: URL to family dashboard (defaults to env var DASHBOARD_URL)
            data_store: DataStore instance for patient/contact lookups
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "clara@claracare.ai")
        self.dashboard_url = dashboard_url or os.getenv("DASHBOARD_URL", "https://claracare.ai/dashboard")
        self.data_store = data_store
        
        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent / "templates"
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Check if SMTP is configured
        self.configured = bool(self.smtp_user and self.smtp_password)
        if not self.configured:
            logger.warning("SMTP not configured. Email notifications will be logged only.")
    
    async def send_alert_notification(self, patient_id: str, alert: dict) -> bool:
        """
        Send alert email to family contacts
        
        Args:
            patient_id: Patient ID
            alert: Alert dict with type, severity, description, etc.
            
        Returns:
            True if sent successfully (or logged if SMTP not configured)
        """
        # Get patient and family contacts
        patient = await self._get_patient(patient_id) if self.data_store else None
        patient_name = patient.get("name") if patient else patient_id
        
        family_contacts = await self._get_family_contacts(patient_id) if self.data_store else []
        
        if not family_contacts:
            logger.warning(f"No family contacts to notify for patient {patient_id}")
            return False
        
        try:
            # Get human-friendly alert type
            alert_type_friendly = self._get_friendly_alert_type(alert.get("alert_type", ""))
            
            # Format timestamp
            timestamp_formatted = self._format_timestamp(alert.get("timestamp"))
            
            # Render email from template
            template = self.template_env.get_template("alert_email.html")
            
            # Human-friendly subject line
            severity_label = alert.get("severity", "medium").upper()
            subject = f"[{severity_label}] ClaraCare: {alert_type_friendly} noticed for {patient_name}"
            
            # Send to each contact
            for contact in family_contacts:
                email = contact.get("email")
                if not email:
                    continue
                
                html_content = template.render(
                    alert=alert,
                    patient_name=patient_name,
                    recipient_name=contact.get("name"),
                    alert_type_friendly=alert_type_friendly,
                    timestamp_formatted=timestamp_formatted,
                    severity_color=self._get_severity_color(alert.get("severity", "medium")),
                    dashboard_url=self.dashboard_url,
                    unsubscribe_url=self._get_unsubscribe_url(contact.get("id"))
                )
                
                if self.configured:
                    await self._send_email(email, subject, html_content)
                    logger.info(f"Alert email sent to {contact['name']} ({email})")
                else:
                    logger.info(f"[MOCK EMAIL] To: {email}, Subject: {subject}")
                    logger.info(f"[MOCK EMAIL] Content: {alert['description']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert email: {e}")
            return False
    
    async def send_daily_digest(self, patient_id: str, digest: dict) -> bool:
        """
        Send daily wellness digest email to family contacts
        
        Args:
            patient_id: Patient ID
            digest: WellnessDigest dict
            
        Returns:
            True if sent successfully
        """
        # Get patient and family contacts
        patient = await self._get_patient(patient_id) if self.data_store else None
        patient_name = patient.get("name") if patient else patient_id
        
        family_contacts = await self._get_family_contacts(patient_id) if self.data_store else []
        
        if not family_contacts:
            logger.warning(f"No family contacts for daily digest for patient {patient_id}")
            return False
        
        try:
            # Format date
            date_formatted = self._format_date(digest.get("date"))
            
            # Get score context
            score_context_label, score_context_class = self._get_score_context(digest.get("cognitive_score", 0))
            
            # Render email from template
            template = self.template_env.get_template("daily_digest.html")
            
            subject = f"ClaraCare Daily Digest for {patient_name} - {date_formatted}"
            
            # Send to contacts who want daily digests
            for contact in family_contacts:
                if not contact.get("notification_preferences", {}).get("daily_digest", True):
                    continue
                
                email = contact.get("email")
                if not email:
                    continue
                
                html_content = template.render(
                    digest=digest,
                    patient_name=patient_name,
                    recipient_name=contact.get("name"),
                    date_formatted=date_formatted,
                    mood_emoji=self._get_mood_emoji(digest.get("overall_mood", "neutral")),
                    trend_icon=self._get_trend_icon(digest.get("cognitive_trend", "stable")),
                    score_context_label=score_context_label,
                    score_context_class=score_context_class,
                    dashboard_url=self.dashboard_url,
                    unsubscribe_url=self._get_unsubscribe_url(contact.get("id"))
                )
                
                if self.configured:
                    await self._send_email(email, subject, html_content)
                    logger.info(f"Daily digest sent to {contact['name']} ({email})")
                else:
                    logger.info(f"[MOCK EMAIL] Daily digest to: {email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily digest: {e}")
            return False
    
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> None:
        """
        Send email via SMTP with both HTML and plain-text alternatives
        """
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import re
            
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Create plain-text version by stripping HTML
            plain_text = re.sub('<[^<]+?>', '', html_content)
            plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)  # Clean up whitespace
            
            # Add both plain-text and HTML parts
            text_part = MIMEText(plain_text, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise
    
    async def _get_patient(self, patient_id: str) -> dict:
        """Get patient info from data store"""
        if not self.data_store:
            return {"patient_id": patient_id, "name": patient_id}
        try:
            return await self.data_store.get_patient(patient_id) or {"patient_id": patient_id, "name": patient_id}
        except Exception:
            return {"patient_id": patient_id, "name": patient_id}
    
    async def _get_family_contacts(self, patient_id: str) -> list:
        """Get family contacts from data store"""
        if not self.data_store:
            return []
        try:
            return await self.data_store.get_family_contacts(patient_id) or []
        except Exception:
            return []
    
    def _format_timestamp(self, timestamp_str: Optional[str]) -> str:
        """Format ISO timestamp as human-readable string"""
        if not timestamp_str:
            return datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except (ValueError, TypeError):
            return timestamp_str
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format ISO date as human-readable string"""
        if not date_str:
            return datetime.now().strftime("%A, %B %d, %Y")
        
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%A, %B %d, %Y")
        except (ValueError, TypeError):
            return date_str
    
    def _get_friendly_alert_type(self, alert_type: str) -> str:
        """Convert technical alert type to family-friendly message"""
        friendly_names = {
            "vocabulary_shrinkage": "Changes in speech patterns",
            "repetitive_speech": "Repetitive conversation patterns",
            "word_finding_difficulty": "Difficulty finding words",
            "cognitive_decline": "Memory inconsistency detected",
            "coherence_drop": "Conversation clarity concern",
            "coherence_issues": "Changes in conversation clarity",
            "baseline_deviation": "Unusual patterns detected",
            "distress": "Signs of distress detected",
            "social_connection": "Social Connection Opportunity"
        }
        return friendly_names.get(alert_type, alert_type.replace('_', ' ').title())
    
    def _get_score_context(self, score: int) -> tuple[str, str]:
        """
        Get human-friendly context for cognitive score
        
        Returns:
            (label, css_class) tuple
        """
        if score >= 80:
            return ("Good", "score-good")
        elif score >= 60:
            return ("Fair", "score-fair")
        else:
            return ("Needs Attention", "score-needs-attention")
    
    def _get_unsubscribe_url(self, contact_id: Optional[str]) -> Optional[str]:
        """Generate unsubscribe URL for contact"""
        if not contact_id:
            return None
        return f"{self.dashboard_url}/unsubscribe?contact={contact_id}"
    
    def _get_severity_color(self, severity: str) -> str:
        """Map severity to color for email styling"""
        colors = {
            "low": "#FFA500",    # Orange
            "medium": "#FF6B00", # Dark Orange
            "high": "#DC143C"    # Crimson
        }
        return colors.get(severity, "#666666")
    
    def _get_mood_emoji(self, mood: str) -> str:
        """Map mood to emoji"""
        emojis = {
            "happy": "😊",
            "neutral": "😐",
            "sad": "😢",
            "confused": "😕",
            "distressed": "😰",
            "nostalgic": "🌅"
        }
        return emojis.get(mood, "😐")
    
    def _get_trend_icon(self, trend: str) -> str:
        """Map trend to icon"""
        icons = {
            "improving": "📈",
            "stable": "➡️",
            "declining": "📉"
        }
        return icons.get(trend, "➡️")
