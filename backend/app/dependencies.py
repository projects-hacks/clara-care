"""
FastAPI dependency injection for shared services.
Replaces module-level globals with app.state-backed dependencies.
"""

from fastapi import HTTPException, Request


def get_data_store(request: Request):
    """Dependency: retrieve the data store from app state."""
    store = getattr(request.app.state, "data_store", None)
    if store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    return store


def get_cognitive_pipeline(request: Request):
    """Dependency: retrieve the cognitive pipeline from app state (may be None)."""
    return getattr(request.app.state, "cognitive_pipeline", None)
