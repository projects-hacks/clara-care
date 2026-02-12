"""
API Routes Module
REST API endpoints for patient data, conversations, wellness digests, and alerts
"""

from .patients import router as patients_router
from .conversations import router as conversations_router
from .wellness import router as wellness_router
from .alerts import router as alerts_router

# P3 routes
try:
    from .insights import router as insights_router
    from .reports import router as reports_router
    __all__ = [
        "patients_router",
        "conversations_router", 
        "wellness_router",
        "alerts_router",
        "insights_router",
        "reports_router"
    ]
except ImportError:
    __all__ = [
        "patients_router",
        "conversations_router",
        "wellness_router",
        "alerts_router"
    ]
