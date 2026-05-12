from fastapi import Request

def get_auth_service(request: Request):
    return request.app.state.auth_service

def get_onboarding_service(request: Request):
    return request.app.state.onboarding_service

def get_patient_service(request: Request):
    return request.app.state.patient_service

def get_invite_service(request: Request):
    return request.app.state.invite_service

def get_patient_repo(request: Request):
    return request.app.state.patient_repo

def get_profile_repo(request: Request):
    return request.app.state.profile_repo

def get_contact_repo(request: Request):
    return request.app.state.contact_repo

def get_conversation_repo(request: Request):
    return request.app.state.conversation_repo

def get_alert_repo(request: Request):
    return request.app.state.alert_repo

def get_wellness_repo(request: Request):
    return request.app.state.wellness_repo

def get_cognitive_repo(request: Request):
    return request.app.state.cognitive_repo

def get_cognitive_pipeline(request: Request):
    return request.app.state.cognitive_pipeline
