class PROTOCOL_STATES():
    Invalid = 0

class MESI_STATES(PROTOCOL_STATES):
    Shared = 1
    Exclusive = 2
    Modified = 3 

class DRAGON_STATES(PROTOCOL_STATES):
    Exclusive = 1
    SharedClean = 2
    SharedModified = 3
    Modified = 4

class PROTOCOL_ACTIONS(object):
    PrRd = 0
    PrWr = 1
    BusRd = 2
    Flush = 4
    No_Action = 5

class MESI_ACTIONS(PROTOCOL_ACTIONS):
    BusRdx = 6


class DRAGON_ACTIONS(PROTOCOL_ACTIONS):
    PrRdMiss = 6
    PrWrMiss = 7
    BusUpd = 8
# Constants
FLUSH_TIME = 99


