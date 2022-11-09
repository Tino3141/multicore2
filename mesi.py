from definitions import MESI_STATES
from definitions import MESI_ACTIONS

class MESI:

    def __init__(self, init_state=MESI_STATES.Invalid) -> None:
        self.current_state = init_state
        pass

    def step(self, input: MESI_ACTIONS, someone_has_copy=False) -> MESI_ACTIONS:

        if self.current_state == MESI_STATES.Invalid:
            if input == MESI_ACTIONS.PrRd and someone_has_copy:
                self.current_state = MESI_STATES.Shared
                return MESI_ACTIONS.BusRd
            elif input == MESI_ACTIONS.PrRd and (not someone_has_copy):
                self.current_state = MESI_STATES.Exclusive
                return MESI_ACTIONS.No_Action
            elif input == MESI_ACTIONS.PrWr:
                self.current_state = MESI_STATES.Modified
                return MESI_ACTIONS.BusRdx
            else:
                self.current_state = self.current_state
                return MESI_ACTIONS.No_Action

        elif self.current_state == MESI_STATES.Shared:
            if input == MESI_ACTIONS.PrWr:
                self.current_state = MESI_STATES.Modified
                return MESI_ACTIONS.BusRdx
            elif input == MESI_ACTIONS.PrRd:
                return MESI_ACTIONS.No_Action
            elif input == MESI_ACTIONS.BusRdx:
                self.current_state = MESI_STATES.Invalid
                return MESI_ACTIONS.Flush
            else:
                return MESI_ACTIONS.No_Action

        elif self.current_state == MESI_STATES.Exclusive:
            if input == MESI_ACTIONS.BusRd:
                self.current_state = MESI_STATES.Shared
                return MESI_ACTIONS.No_Action
            elif input == MESI_ACTIONS.PrWr:
                self.current_state = MESI_STATES.Modified
                return MESI_ACTIONS.No_Action
            elif input == MESI_ACTIONS.BusRdx:
                self.current_state = MESI_STATES.Invalid
                return MESI_ACTIONS.Flush
            else:
                return MESI_ACTIONS.No_Action

        else: # This is the modified state
            if input == MESI_ACTIONS.BusRd:
                self.current_state = MESI_STATES.Shared
                return MESI_ACTIONS.Flush
            elif input == MESI_ACTIONS.BusRdx:
                self.current_state = MESI_STATES.Invalid
                return MESI_ACTIONS.Flush
            else:
                return MESI_ACTIONS.No_Action