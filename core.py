from collections import deque
from cache import Cache

class Core:
    def __init__(self, instrStream, block, associativity, cache_size, check_state=lambda x, y: [], core_id=0, cores_cnt=4, check_flush= lambda addr, core_id: False, flush_directory={}) -> None:
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
        self.check_flush = check_flush
        self.flush_directory = flush_directory
        self.loading = False
        self.storing = False
        self.load_store_to_main = 0
    
    # Returns true if we ask for the first time if an instruction is loading from main cache
    def isLoadingFirstTime(self):
        if self.cache.wait_counter >= 0 and not self.loading:
            self.loading = True
            return True
        return False


    def isStoringFirstTime(self):
        if self.wait_counter >= 0 and not self.storing:
            self.storing = True
            return True
        return False
    
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

        if addr in self.flush_directory.keys():
            self.flush_directory[addr].append(self.core_id)
        else:
            self.flush_directory[addr] = [self.core_id]

        # Check if first instruction is a flush if so -> complete it and put new flush after that 
        # Otherwise put at the front
        if len(self.instr_stream)>0 and self.instr_stream[0][0] == 3:
            self.instr_stream.insert(1, flush_instr)
            self.flush_queue.insert(1, (addr, bus_action))
        else:
            self.instr_stream.appendleft(flush_instr)
            self.flush_queue.appendleft((addr, bus_action))

    def step(self):
        raise Exception("Step not implemented")
