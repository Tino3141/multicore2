from collections import deque
# from definitions import MESI_ACTIONS
from definitions import PROTOCOL_ACTIONS

BYTES_PER_WORD = 4
class BusProtocolInput:
  def __init__(self, action, core: int, address: int) -> None:
    self.action = action
    self.core = core
    self.address = address


class Bus:
  def __init__(self) -> None:
    self.queue = deque['BusProtocolInput']()
    self.data_processed = 0 # this is in bytes
    self.data_invalidated = 0

  def create_transaction(self, input) -> None:
    # accounting for bus delay
    while len(input) != 0 and len(self.queue) < 2:
      self.queue.append(BusProtocolInput(PROTOCOL_ACTIONS.No_Action, -1, 0))
    for action in input:
      self.queue.append(action)

  def get_transaction(self) -> BusProtocolInput:
    if len(self.queue) > 0:
      if self.queue[0].action != PROTOCOL_ACTIONS.No_Action:
        self.data_processed += BYTES_PER_WORD 
      # if self.queue[0].action == MESI_ACTIONS.BusRdx:
        # self.data_invalidated += 1
      return self.queue.popleft()
    return None
  
  def empty_bus(self) -> bool:
    return len(self.queue) == 0
