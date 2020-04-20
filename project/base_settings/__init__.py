from .common import *
from .auth_settings import *
from .restclients_settings import *
from .prometheus_settings import *

# deleting any setting utility functions
from .setting_utils import list_of_attributes

for attr in list_of_attributes:
    if attr in globals():
        del globals()[attr]
