from definitions import DRAGON_STATES, DRAGON_ACTIONS

class Dragon: 

  def __init__(self, init_state=DRAGON_STATES.Invalid) -> None:
    self.current_state = init_state
    pass

  def step(self, input: DRAGON_ACTIONS, someone_has_copy=False) -> DRAGON_ACTIONS:
    
    #TODO: Implement this
    pass