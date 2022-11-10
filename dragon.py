from definitions import DRAGON_STATES, DRAGON_ACTIONS

class Dragon: 

  def __init__(self, init_state=DRAGON_STATES.Invalid) -> None:
    self.current_state = init_state
    pass

  def step(self, input: DRAGON_ACTIONS, someone_has_copy=False) -> DRAGON_ACTIONS:
    if self.current_state == DRAGON_STATES.Exclusive:
      if input == DRAGON_ACTIONS.PrWr:
        self.current_state = DRAGON_STATES.Modified
        return DRAGON_ACTIONS.No_Action
      elif input == DRAGON_ACTIONS.BusRd:
        self.current_state = DRAGON_STATES.SharedClean
        return DRAGON_ACTIONS.No_Action
      else:
        self.current_state = self.current_state
        return DRAGON_ACTIONS.No_Action
    elif self.current_state == DRAGON_STATES.Modified:
      if input == DRAGON_ACTIONS.BusRd:
        self.current_state = DRAGON_STATES.SharedModified
        return DRAGON_ACTIONS.Flush
      else:
        self.current_state = self.current_state
        return DRAGON_ACTIONS.No_Action
    elif self.current_state == DRAGON_STATES.SharedClean:
      if input == DRAGON_ACTIONS.PrWr and someone_has_copy:
        self.current_state = DRAGON_STATES.SharedModified
        return DRAGON_ACTIONS.BusUpd
      elif input == DRAGON_ACTIONS.PrWr and not someone_has_copy:
        self.current_state = DRAGON_STATES.Modified
        return DRAGON_ACTIONS.No_Action 
      else:
        self.current_state = self.current_state
        return DRAGON_ACTIONS.No_Action
    elif self.current_state == DRAGON_STATES.SharedModified:
      if input == DRAGON_ACTIONS.PrWr and not someone_has_copy:
        self.current_state = DRAGON_STATES.Modified
        return DRAGON_ACTIONS.BusUpd
      elif input == DRAGON_ACTIONS.PrWr and someone_has_copy:
        self.current_state = self.current_state
        return DRAGON_ACTIONS.BusUpd
      elif input == DRAGON_ACTIONS.BusRd:
        return DRAGON_ACTIONS.Flush
      elif input == DRAGON_ACTIONS.BusUpd:
        self.current_state = DRAGON_STATES.SharedClean
        return DRAGON_ACTIONS.No_Action
      else:
        return DRAGON_ACTIONS.No_Action
    else: # This case is the invalid case (not a real Dragon State but used as a helper)   
      if input == DRAGON_ACTIONS.PrRdMiss and not someone_has_copy:
        self.current_state = DRAGON_STATES.Exclusive
        return DRAGON_ACTIONS.BusRd
      elif input == DRAGON_ACTIONS.PrRdMiss and someone_has_copy:
        self.current_state = DRAGON_STATES.SharedClean
        return DRAGON_ACTIONS.BusRd
      elif input == DRAGON_ACTIONS.PrWrMiss and not someone_has_copy:
        self.current_state = DRAGON_STATES.Modified
        return DRAGON_ACTIONS.BusRd
      elif input == DRAGON_ACTIONS.PrWrMiss and someone_has_copy:
        self.current_state = DRAGON_STATES.SharedModified
        return DRAGON_ACTIONS.BusRd
      else:
        raise Exception("Invalid Dragon state reached.")