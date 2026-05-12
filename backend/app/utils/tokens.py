import uuid


def generate_invite_token() -> str:
    return str(uuid.uuid4())
