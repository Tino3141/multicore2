from audioop import add
from collections import deque
from bus import BusProtocolInput
from cache import Cache
from definitions import MESI_ACTIONS, MESI_STATES
from mesi import MESI


class Core:
    def __init__(self, instrStream, block, associativity, cache_size, check_state=lambda x, y: [], core_id=0, cores_cnt=4) -> None:
        self.instr_stream = deque(instrStream)
        self.flush_queue = deque()
        self.bus_read_input = {}
        self.cache = Cache(block, associativity, cache_size)
        self.terminated = False
        self.wait_counter = -1
        self.core_id = core_id
        self.core_count = cores_cnt
        self.check_state = check_state
        self.cycle_count = 0
        self.compute_cycle_count = 0
        self.load_store_instr_count = 0
        self.cache_idle_count = 0
        self.shared_access = 0
        self.private_access = 0
    
    def add_wait(self, wait_time):
        self.wait_counter += wait_time
    
    def dec_wait(self):
        self.wait_counter -= 1

    def flush(self, addr, bus_action):
        flush_instr = (3, addr)

        # We dont flush the same address again
        for flush_addr, _ in self.flush_queue:
            if flush_addr == addr:
                return
        self.instr_stream.insert(1, flush_instr)
        self.flush_queue.append((addr, bus_action))

    def step():
        raise Exception("Step not implemented")
