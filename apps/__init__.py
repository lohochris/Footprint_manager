import importlib
import sys

# Import the actual backend.apps package
_backend_apps = importlib.import_module('backend.apps')
# Replace this module in sys.modules with the backend.apps module
sys.modules[__name__] = _backend_apps
