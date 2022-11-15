class PROTOCOLS():
    MESI = "MESI"
    MOESI = "MOESI"
    Dragon = "Dragon"

class PROTOCOL_STATES():
    Invalid = "Invalid"

class MESI_STATES(PROTOCOL_STATES):
    Shared = "Shared"
    Exclusive = "Exclusive"
    Modified = "Modified"

class DRAGON_STATES(PROTOCOL_STATES):
    Loaded = "Loaded"
    Exclusive = "Exclusive"
    SharedClean = "SharedClean"
    SharedModified = "SharedModified"
    Modified = "Modified"

class MOESI_STATES(PROTOCOL_STATES):
    Shared = "Shared"
    Exclusive = "Exclusive"
    Modified = "Modified"
    Owned = "Owned"

class PROTOCOL_ACTIONS(object):
    PrRd = "PrRd"
    PrWr = "PrWr"
    BusRd = "BusRd"
    Flush = "Flush"
    No_Action = "No_Action"

class MESI_ACTIONS(PROTOCOL_ACTIONS):
    BusRdx = "BusRdx"

class DRAGON_ACTIONS(PROTOCOL_ACTIONS):
    PrRdMiss = "PrRdMiss"
    PrWrMiss = "PrWrMiss"
    BusUpd = "BusUpd"

class MOESI_ACTIONS(PROTOCOL_ACTIONS):
    BusRdx = "BusRdx"
    BusUpgr = "BusUpgr"

# Constants
FLUSH_TIME = 99


