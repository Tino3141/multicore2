from bus import BusProtocolInput
from definitions import DRAGON_ACTIONS, DRAGON_STATES, FLUSH_TIME
from core import Core

class CoreDragon(Core):
    def __init__(self, instrStream, block, associativity, cache_size, check_state=..., core_id=0, cores_cnt=4) -> None:
        super().__init__(instrStream, block, associativity, cache_size, check_state, core_id, cores_cnt)

    def step(self, bus_transaction: BusProtocolInput):
        pass