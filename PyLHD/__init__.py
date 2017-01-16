from . import eg
from . import instruments, igetfile

try: # This module requires psycopg2 that is somehow specific.
    from . import pgdb
except ImportError:
    pass
