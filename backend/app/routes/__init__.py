"""
API Routes Module
REST API endpoints for patient data, conversations, wellness digests, and alerts
"""

from .patients import router as patients_router
from .conversations import router as conversations_router
from .wellness import router as wellness_router
from .alerts import router as alerts_router
from .live_status import router as live_status_router
from .call_events import router as call_events_router
from .auth_routes import router as auth_router
from .onboarding import router as onboarding_router
from .invite import router as invite_router

# Data insight and report routes
try:
    from .insights import router as insights_router
    from .reports import router as reports_router
    __all__ = [
        "patients_router",
        "conversations_router",
        "wellness_router",
        "alerts_router",
        "live_status_router",
        "call_events_router",
        "insights_router",
        "reports_router",
        "auth_router",
        "onboarding_router",
        "invite_router"
    ]
except ImportError:
    __all__ = [
        "patients_router",
        "conversations_router",
        "wellness_router",
        "alerts_router",
        "live_status_router",
        "call_events_router",
        "auth_router",
        "onboarding_router",
        "invite_router"
    ]
