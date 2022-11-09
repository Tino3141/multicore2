from enum import Enum


class MESI_STATES(Enum):
    Invalid  = 0
    Shared   = 1
    Exclusive = 2
    Modified  = 3 

class MESI_ACTIONS(Enum):
    PrRd = 0
    PrWr = 1
    BusRd = 2
    BusRdx = 3
    Flush = 4
    No_Action = 5
 

