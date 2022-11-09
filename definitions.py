from enum import Enum

class ProtocolStates():
    Invalid = 0

class MESI_STATES(ProtocolStates):
    Shared = 1
    Exclusive = 2
    Modified = 3 

class DRAGON_STATES(ProtocolStates):
    Exclusive = 1
    SharedClean = 2
    SharedModified = 3
    Modified = 4

class BusActions(object):
    PrRd = 0
    PrWr = 1
    BusRd = 2
    Flush = 4
    No_Action = 5

class MESI_ACTIONS(BusActions):
    BusRdx = 6


class DRAGON_ACTIONS(BusActions):
    PrRdMiss = 6
    PrWrMiss = 7
    BusUpd = 8

