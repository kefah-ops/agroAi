from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def optional_jwt(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except:
            pass
        return fn(*args, **kwargs)
    return wrapper
