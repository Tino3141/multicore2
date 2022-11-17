from core import Core
from bus import BusProtocolInput
from definitions import MOESI_ACTIONS, MOESI_STATES, FLUSH_TIME, PROTOCOLS
from cache import Cache

class CoreMOESI(Core):
    def __init__(self, instrStream, block, associativity, cache_size, check_state=lambda x, y: [], core_id=0, cores_cnt=4, check_flush=lambda x,y: False,) -> None:
        super().__init__(instrStream, block, associativity, cache_size, check_state, core_id, cores_cnt, check_flush)
        self.cache = Cache(block, associativity, cache_size, protocol=PROTOCOLS.MOESI)

    def step(self, bus_transaction: BusProtocolInput):
        bus_output = []

        # snoop the bus. this time pull flushes as well
        if  bus_transaction and bus_transaction.action != MOESI_ACTIONS.No_Action and bus_transaction.core != self.core_id:
            address_state = self.cache.get_state(bus_transaction.address)
            if bus_transaction.action == MOESI_ACTIONS.BusRd:
                # if we have the data
                if address_state == MOESI_STATES.Modified:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusProtocolInput(MOESI_ACTIONS.Flush, self.core_id, bus_transaction.address))
                    self.cache.update_state(bus_transaction.address, bus_transaction.action) # should take the state from modified to owned
                elif address_state == MOESI_STATES.Exclusive or address_state == MOESI_STATES.Shared:
                    self.cache.update_state(bus_transaction.address, bus_transaction.action)
                elif address_state == MOESI_STATES.Owned:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusProtocolInput(MOESI_ACTIONS.Flush, self.core_id, bus_transaction.address))
            elif bus_transaction.action == MOESI_ACTIONS.BusRdx:
                if address_state != MOESI_STATES.Invalid:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusProtocolInput(MOESI_ACTIONS.Flush, self.core_id, bus_transaction.address))
            elif bus_transaction.action == MOESI_ACTIONS.BusUpgr:
                if address_state == MOESI_STATES.Exclusive:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusProtocolInput(MOESI_ACTIONS.Flush, self.core_id, bus_transaction.address))
                    self.cache.update_state(bus_transaction.address, bus_transaction.action)
                elif address_state == MOESI_STATES.Owned or address_state == MOESI_STATES.Shared:
                    self.cache.update_state(bus_transaction.address, bus_transaction.action)
            elif bus_transaction.action == MOESI_ACTIONS.Flush:
                current_state = self.cache.get_state(bus_transaction.address)
                if len(self.instr_stream) != 0 and self.instr_stream[0] == (0, bus_transaction.address) and (current_state == MOESI_STATES.Exclusive or current_state == MOESI_STATES.Shared):
                    self.instr_stream.popleft()
                    return bus_output
            else:
                raise Exception("Invalid Bus transaction input to core " + str(bus_transaction.action))

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
                if state != MOESI_STATES.Invalid:
                    someone_has_copy = True
                if state == MOESI_STATES.Exclusive or state == MOESI_STATES.Modified:
                    # on the first instance push onto bus, else nothing
                    if addr not in self.bus_read_input.keys():
                        # this is first instance push on bus and add to dict
                        bus_output.append(BusProtocolInput(MOESI_ACTIONS.BusRd, self.core_id, addr))
                        self.bus_read_input[addr] = True
                    return bus_output
            
            # Del Key from BusReadInput
            if addr in self.bus_read_input.keys():             
                del self.bus_read_input[addr]

            self.cache_idle_count += 1
            if self.isLoadingFirstTime():
                self.load_store_to_main += 1
            if (self.cache.update_cache(addr)):
                self.cache_idle_count -= 1  # in case of the cache is done fetching or it is a cache hit, cache is not ideling
                
                # access analysis
                access_state = self.cache.get_state(addr)
                if access_state == MOESI_STATES.Shared:
                    self.shared_access += 1
                elif access_state == MOESI_STATES.Exclusive or access_state == MOESI_STATES.Modified:
                    self.private_access += 1
                self.cache.update_state(addr, MOESI_ACTIONS.PrRd, someone_has_copy=someone_has_copy)
                self.instr_stream.popleft()
                # Reset loading status, next load from main memory will be counted as new load
                self.loading = False
                self.load_store_instr_count += 1
        # Instr Write Case
        elif instr_type == 1: 
            
            if self.cache.update_cache(addr):
                # access analysis
                access_state = self.cache.get_state(addr)
                if access_state == MOESI_STATES.Shared:
                    self.shared_access += 1
                elif access_state == MOESI_STATES.Exclusive or access_state == MOESI_STATES.Modified:
                    self.private_access += 1
                bus_mesi_action = self.cache.update_state(addr, MOESI_ACTIONS.PrWr)
                if bus_mesi_action != MOESI_ACTIONS.No_Action:
                    bus_output.append(BusProtocolInput(bus_mesi_action, self.core_id, addr))
                self.instr_stream.popleft()
                
                self.load_store_instr_count += 1
        elif instr_type == 2:
            if self.wait_counter < 0:
                self.wait_counter = -1
                self.add_wait(addr) # Addr adds wait time for type 2 instructions (naming issue)
            elif self.wait_counter > 0:
                self.dec_wait()
            if self.wait_counter == 0: # Counter is 0 i.e. continue
                _ , cycles = self.instr_stream.popleft()
                self.compute_cycle_count += cycles
                self.dec_wait()
        elif instr_type == 3:
            if self.wait_counter < 0:
                self.wait_counter = -1
                self.load_store_to_main += 1
                self.add_wait(FLUSH_TIME) # Addr adds wait time for type 2 instructions (naming issue)
            elif self.wait_counter > 0:
                self.dec_wait()
            if self.wait_counter == 0: # Counter is 0 i.e. continue
                self.instr_stream.popleft()
                flush_addr, mesi_action = self.flush_queue.popleft()
                self.storing = False
                self.dec_wait()           
                self.cache.update_state(flush_addr, mesi_action)
        else:
            raise "Core cannot process instruction type " + str(instr_type)
        return bus_output
       
 