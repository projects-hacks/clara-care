"""Database access layer. Each repository handles one table group."""
from .patient_repo import PatientRepository
from .profile_repo import ProfileRepository
from .contact_repo import ContactRepository
from .conversation_repo import ConversationRepository
from .alert_repo import AlertRepository
from .wellness_repo import WellnessRepository
from .cognitive_repo import CognitiveRepository
