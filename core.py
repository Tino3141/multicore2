from audioop import add
from collections import deque
from bus import BusMESIInput
from cache import Cache
from definitions import MESI_ACTIONS, MESI_STATES
from mesi import MESI

FLUSH_TIME = 99
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

    def step(self, bus_transaction: BusMESIInput):
        
        bus_output = []
        # snoop the bus
        if  bus_transaction and bus_transaction.action != MESI_ACTIONS.No_Action and bus_transaction.action != MESI_ACTIONS.Flush and bus_transaction.core != self.core_id:
            address_state = self.cache.get_state(bus_transaction.address)
            if bus_transaction.action == MESI_ACTIONS.BusRd:
                # if we have the data
                if address_state == MESI_STATES.Modified:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusMESIInput(MESI_ACTIONS.Flush, self.core_id, bus_transaction.address))
                elif address_state == MESI_STATES.Exclusive or address_state == MESI_STATES.Shared:
                    self.cache.update_state(bus_transaction.address, bus_transaction.action)
            elif bus_transaction.action == MESI_ACTIONS.BusRdx:
                if address_state != MESI_STATES.Invalid:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusMESIInput(MESI_ACTIONS.Flush, self.core_id, bus_transaction.address))
            else:
                raise Exception("Invalid Bus transaction input to core " + str(bus_transaction.action))

        # complete instruction for this cycle if needed
        if len(self.instr_stream) == 0:
            self.terminated = True
            return []
        else:
            self.terminated = False

        instr_type, addr = self.instr_stream[0]
       
        self.cycle_count += 1
    
        # Instr Read Case 
        if instr_type == 0:
            # check other core states 
            other_core_states = self.check_state(addr, self.core_id)
            someone_has_copy = False
            for _, state in other_core_states:
                if state != MESI_STATES.Invalid:
                    someone_has_copy = True
                if state == MESI_STATES.Exclusive or state == MESI_STATES.Modified:
                    # on the first instance push onto bus, else nothing
                    if addr not in self.bus_read_input.keys():
                        # this is first instance push on bus and add to dict
                        bus_output.append(BusMESIInput(MESI_ACTIONS.BusRd, self.core_id, addr))
                        self.bus_read_input[addr] = True
                    return bus_output
            
            # Del Key from BusReadInput
            if addr in self.bus_read_input.keys():             
                del self.bus_read_input[addr]

            self.cache_idle_count += 1
            if (self.cache.update_cache(addr)):
                self.cache_idle_count -= 1  # in case of the cache is done fetching or it is a cache hit, cache is not ideling
                
                # access analysis
                access_state = self.cache.get_state(addr)
                if access_state == MESI_STATES.Shared:
                    self.shared_access += 1
                elif access_state == MESI_STATES.Exclusive or access_state == MESI_STATES.Modified:
                    self.private_access += 1
                self.cache.update_state(addr, MESI_ACTIONS.PrRd, someone_has_copy=someone_has_copy)
                self.instr_stream.popleft()
                self.load_store_instr_count += 1
        # Instr Write Case
        elif instr_type == 1: 
            if self.cache.update_cache(addr):
                # access analysis
                access_state = self.cache.get_state(addr)
                if access_state == MESI_STATES.Shared:
                    self.shared_access += 1
                elif access_state == MESI_STATES.Exclusive or access_state == MESI_STATES.Modified:
                    self.private_access += 1

                bus_mesi_action = self.cache.update_state(addr, MESI_ACTIONS.PrWr)
                if bus_mesi_action != MESI_ACTIONS.No_Action:
                    bus_output.append(BusMESIInput(bus_mesi_action, self.core_id, addr))
                self.instr_stream.popleft()
                self.load_store_instr_count += 1
        elif instr_type == 2:
            if self.wait_counter == -1:
                self.add_wait(addr) # Addr adds wait time for type 2 instructions (naming issue)
            elif self.wait_counter > 0:
                self.dec_wait()
            if self.wait_counter == 0: # Counter is 0 i.e. continue
                _ , cycles = self.instr_stream.popleft()
                self.compute_cycle_count += cycles
                self.dec_wait()
        elif instr_type == 3:
            if self.wait_counter == -1:
                self.add_wait(FLUSH_TIME) # Addr adds wait time for type 2 instructions (naming issue)
            elif self.wait_counter > 0:
                self.dec_wait()
            if self.wait_counter == 0: # Counter is 0 i.e. continue
                self.instr_stream.popleft()
                flush_addr, mesi_action = self.flush_queue.popleft()
                self.dec_wait()           
                self.cache.update_state(flush_addr, mesi_action)
        else:
            raise "Core cannot process instruction type " + str(instr_type)
        return bus_output
 
