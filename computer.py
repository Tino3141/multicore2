import logging

from coreMESI import CoreMESI
from coreDragon import CoreDragon
from bus import Bus, BusProtocolInput

class Computer:
    
    def __init__(self, instr, block=16, associativity=1, cache_size=1024, number_cores=4, MESI=True) -> None:

        if len(instr) != number_cores:
            raise "Wrong number of instructions streams"
        
        self.cores = []
        self.current_cycle = 0
        
        # Adding the cores
        for i in range(0, number_cores):
            if MESI:
                self.cores.append(CoreMESI(instr[i], block, associativity, cache_size, self.check_state, i, cores_cnt=number_cores))
            else: 
                self.cores.append(CoreDragon(instr[i], block, associativity, cache_size, self.check_state, i, cores_cnt=number_cores))

        # Adding the bus
        self.bus = Bus()
    
    def step(self, bus_transaction: BusProtocolInput):
        bus_actions = list['BusProtocolInput']()
        for core in self.cores:
            potential_input = core.step(bus_transaction)
            for input in potential_input:
                bus_actions.append(input)
        return bus_actions

    def is_done(self) -> bool:
        for c in self.cores:
            if not c.terminated:
                return False
        if not self.bus.empty_bus():
            return False
        return True
    
    def start(self):
        while not self.is_done():
            if self.current_cycle % 500000 == 0:
                logging.debug(f"Current Cycle: {self.current_cycle}")
            bus_transaction = self.bus.get_transaction()
            bus_actions = self.step(bus_transaction)
            self.bus.create_transaction(bus_actions)
            self.current_cycle += 1
        
        # log all of the data out
        logging.info(f"Overall Execution Cycle: {self.current_cycle}")

        for core in self.cores:
            logging.info(f"Core {core.core_id} cycle: {core.cycle_count}")

        for core in self.cores:
            logging.info(f"Core {core.core_id} compute cycles: {core.compute_cycle_count}")
        
        for core in self.cores:
            logging.info(f"Core {core.core_id} load/store count: {core.load_store_instr_count}")
        
        for core in self.cores:
            logging.info(f"Core {core.core_id} idle cycle count: {core.cache_idle_count}")
        
        for core in self.cores:
            cache_miss_rate = core.cache.cache_miss_count / (core.cache.cache_hit_count + core.cache.cache_miss_count) if core.cache.cache_hit_count + core.cache.cache_miss_count > 0 else "Zero hits or misses"
            logging.debug(f"{core.core_id} hit is {core.cache.cache_hit_count}" )
            logging.info(f"Core {core.core_id} cache miss rate: {cache_miss_rate}")
            cache_hit_rate = 1-cache_miss_rate if core.cache.cache_hit_count + core.cache.cache_miss_count > 0 else "Zero hits and misses"
            logging.info(f"Core {core.core_id} cache hit rate: {cache_hit_rate}")

        logging.info(f"Data traffic on bus: {self.bus.data_processed} bytes")

        logging.info(f"Invalidations or updates on bus: {self.bus.data_invalidated}")

        for core in self.cores:
            access_distribution = core.shared_access / (core.shared_access + core.private_access) if core.shared_access + core.private_access > 0 else "No accesses"
            logging.info(f"Core {core.core_id} shared access: {core.shared_access}")
            logging.info(f"Core {core.core_id} private access: {core.private_access}")
            logging.info(f"Core {core.core_id} access distribution (shared / private): {access_distribution}")

        logging.info("Logging complete!")
   
    # core is asking core, not searching core
    def check_state(self, addr, core):
        core_states = []
        for c in self.cores:
            if c.core_id != core:
                core_states.append((c.core_id, c.cache.get_state(addr)))
        return core_states
