from . import data_prepare
from .satcatclass import SatCatlog
from .query import discos_query,celestrak_query,targets_query

# Load and update the files
data_prepare.satcat_load() 
data_prepare.qsmag_load()