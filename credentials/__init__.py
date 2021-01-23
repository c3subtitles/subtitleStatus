AMARA_USER = None
AMARA_API_KEY = None
TRINT_API_KEY = None

try:
    from .credentials import *
except ImportError:
    pass
