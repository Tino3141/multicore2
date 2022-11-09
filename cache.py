import math
from collections import deque
from definitions import MESI_ACTIONS, MESI_STATES
from mesi import MESI

EVICTION_WAIT = 99
FETCH_WAIT = 99

class Cache:
    def __init__(self, block, associativity, cache_size) -> None:
        
        self.block = block
        self.associativity = associativity
        self.cache_size = cache_size
        self.offset = int(math.log2(self.block))
        self.rows = int(self.cache_size / (self.associativity * self.block))
        self.wait_counter = -1
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        
        self.indexes = [deque() for _ in range(self.rows)]
    
    def compute_index(self, address) -> int:
        block_number = int(address / self.offset)
        return block_number % self.rows

    def compute_tag(self, address) -> int:
        block_number = int(address / self.offset)
        return int(block_number / self.rows)

    def cache_hit(self, state, computed_tag, block_tag):
        return (computed_tag == block_tag) and (state.current_state!=MESI_STATES.Invalid) 

    def add_wait(self, wait) -> int:
        self.wait_counter += wait
        return self.wait_counter
    
    def decrement_wait(self) -> int:
        self.wait_counter -= 1
        return self.wait_counter
    
    # return true on cache_hit, return false on cache_miss or cache has to wait
    def update_cache(self, address, someone_has_address=True) -> bool:
        index = self.compute_index(address)
        tag = self.compute_tag(address)
        queue = self.indexes[index]

        if self.wait_counter > 0: 
            self.decrement_wait()
            return False
        elif self.wait_counter == 0: # When eviction is done
            # we need to evict
            if len(queue) == self.associativity:
                queue.popleft()
                # wait time for fetching from main memory
                self.add_wait(FETCH_WAIT)
                return False
            # we need to add to cache
            else:
                cache_entry = (MESI(), tag)
                queue.append(cache_entry)
                self.decrement_wait()
                return True
        else:
            for state, block_tag in queue:
                if self.cache_hit(state, tag, block_tag):
                    self.cache_hit_count += 1
                    queue.remove((state, block_tag))
                    queue.append((state, block_tag))
                    return True
            
            # Cache Miss
            self.cache_miss_count += 1
            # self.cache_hit_count -= 1 # to counter the future hit increment

            if len(queue) == self.associativity:
                # wait time for evicting
                self.add_wait(EVICTION_WAIT)
                return False
            # wait time for fetching from main memory
            self.add_wait(FETCH_WAIT)
            
            return False

    # return: The current state of the cached address. If address not in cache -> return Invalid State
    def get_state(self, address) -> MESI_STATES:
        index = self.compute_index(address)
        tag = self.compute_tag(address)
        queue = self.indexes[index]

        for state, block_tag in queue:
            if block_tag == tag:  
                return state.current_state
        
        return MESI_STATES.Invalid

    def update_state(self, address, bus_action, someone_has_copy=True):
        index = self.compute_index(address)
        tag = self.compute_tag(address)
        queue = self.indexes[index]

        for state, block_tag in queue:
            if block_tag == tag:  
                return state.step(bus_action, someone_has_copy=someone_has_copy)
        
        return MESI_ACTIONS.No_Action