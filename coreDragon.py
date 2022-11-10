from bus import BusProtocolInput
from definitions import DRAGON_ACTIONS, DRAGON_STATES, FLUSH_TIME
from core import Core

class CoreDragon(Core):
    def __init__(self, instrStream, block, associativity, cache_size, check_state=..., core_id=0, cores_cnt=4, check_flush=lambda addr, core_id: False) -> None:
        super().__init__(instrStream, block, associativity, cache_size, check_state, core_id, cores_cnt, check_flush=check_flush)

    def step(self, bus_transaction: BusProtocolInput):
        bus_output = []

        # Handle bus transactions
        if bus_transaction and bus_transaction.action != DRAGON_ACTIONS.No_Action and bus_transaction.action != DRAGON_ACTIONS.Flush and bus_transaction.core != self.core_id:
            address_state = self.cache.get_state(bus_transaction.address)
            if bus_transaction.action == DRAGON_ACTIONS.BusRd:
                if address_state == DRAGON_STATES.Modified or address_state == DRAGON_STATES.SharedModified:
                    self.flush(bus_transaction.address, bus_transaction.action)
                    bus_output.append(BusProtocolInput(DRAGON_ACTIONS.Flush, self.core_id, bus_transaction.address))
                elif address_state == DRAGON_STATES.Exclusive:
                    # Transition to Shared Clean
                    self.cache.update_state(bus_transaction.address, bus_transaction.action, someone_has_copy=True)
            elif bus_transaction.action == DRAGON_ACTIONS.BusUpd:
                if address_state == DRAGON_STATES.SharedModified:
                    self.cache.update_state(bus_transaction.address, bus_transaction.action, someone_has_copy=True)
            else:
                raise Exception("Invalid Bus Action: " + str(bus_transaction.action))
        # complete instructions for cycle
        if len(self.instr_stream) == 0:
            self.terminated = True
            return []
        else:
            self.terminated = False

        instr_type, addr = self.instr_stream[0]
       
        self.cycle_count += 1

        # Instr Read Case
        if instr_type == 0:
            other_cores_states = self.check_state(addr, self.core_id)
            someone_has_copy = False
            
            for _, state in other_cores_states:
                if state != DRAGON_STATES.Invalid:
                    someone_has_copy = True
                if state == DRAGON_STATES.SharedModified or state == DRAGON_STATES.Modified:
                    if addr not in self.bus_read_input.keys():
                        bus_output.append(BusProtocolInput(DRAGON_ACTIONS.BusRd, self.core_id))
                        return bus_output
                # check if the flush state didn't change for others. then
            if self.check_flush(addr, self.core_id):
                return bus_output
            if addr in self.bus_read_input.keys():
                del self.bus_read_input[addr]
        elif instr_type == 1:
            pass
        elif instr_type == 2:
            pass
        elif instr_type == 3:
            pass
        return bus_output