import os

try:
    if "windows" in os.environ.get("OS").lower():
        from .development_settings import *
    else:
        from .production_settings import *
except AttributeError:
    from .production_settings import *


