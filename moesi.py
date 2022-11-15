from definitions import MOESI_ACTIONS, MOESI_STATES

class MOESI: 
    def __init__(self, init_state=MOESI_STATES.Invalid) -> None:
        self.current_state = init_state
        pass

    def step(self, input: MOESI_ACTIONS, someone_has_copy=False) -> MOESI_ACTIONS:

        if self.current_state == MOESI_STATES.Invalid:
            if input == MOESI_ACTIONS.PrRd and someone_has_copy:
                self.current_state = MOESI_STATES.Shared
                return MOESI_ACTIONS.BusRd
            elif input == MOESI_ACTIONS.PrRd and (not someone_has_copy):
                self.current_state = MOESI_STATES.Exclusive
                return MOESI_ACTIONS.No_Action
            elif input == MOESI_ACTIONS.PrWr:
                self.current_state = MOESI_STATES.Modified
                return MOESI_ACTIONS.BusRdx
            else:
                self.current_state = self.current_state
                return MOESI_ACTIONS.No_Action

        elif self.current_state == MOESI_STATES.Shared:
            if input == MOESI_ACTIONS.PrWr:
                self.current_state = MOESI_STATES.Modified
                return MOESI_ACTIONS.BusUpgr
            elif input == MOESI_ACTIONS.PrRd:
                return MOESI_ACTIONS.No_Action
            elif input == MOESI_ACTIONS.BusRdx:
                self.current_state = MOESI_STATES.Invalid
                return MOESI_ACTIONS.Flush
            elif input == MOESI_ACTIONS.BusUpgr:
                self.current_state = MOESI_STATES.Invalid
                return MOESI_ACTIONS.No_Action
            else:
                return MOESI_ACTIONS.No_Action

        elif self.current_state == MOESI_STATES.Exclusive:
            if input == MOESI_ACTIONS.BusRd:
                self.current_state = MOESI_STATES.Shared
                return MOESI_ACTIONS.No_Action
            elif input == MOESI_ACTIONS.PrWr:
                self.current_state = MOESI_STATES.Modified
                return MOESI_ACTIONS.No_Action
            elif input == MOESI_ACTIONS.BusRdx:
                self.current_state = MOESI_STATES.Invalid
                return MOESI_ACTIONS.Flush
            else:
                return MOESI_ACTIONS.No_Action

        elif self.current_state == MOESI_STATES.Modified: 
            if input == MOESI_ACTIONS.BusRd:
                self.current_state = MOESI_STATES.Owned
                return MOESI_ACTIONS.Flush
            elif input == MOESI_ACTIONS.BusRdx:
                self.current_state = MOESI_STATES.Invalid
                return MOESI_ACTIONS.Flush
            else:
                return MOESI_ACTIONS.No_Action
        
        else: # this is the owned state
            if input == MOESI_ACTIONS.PrWr:
                self.current_state = MOESI_STATES.Modified
                return MOESI_ACTIONS.Flush
            elif input == MOESI_ACTIONS.BusUpgr:
                self.current_state = MOESI_STATES.Invalid
                return MOESI_ACTIONS.No_Action
            elif input == MOESI_ACTIONS.BusRd:
                return MOESI_ACTIONS.Flush
            else:
                return MOESI_ACTIONS.No_Action
                