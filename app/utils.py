import uuid

def make_id(prefix="n"):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
