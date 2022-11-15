import datetime
import logging
import math
import sys

from coreMESI import CoreMESI
from coreDragon import CoreDragon
from coreMOESI import CoreMOESI
from bus import Bus, BusProtocolInput
from definitions import PROTOCOLS

class Computer:
    
    def __init__(self, instr, block=16, associativity=1, cache_size=1024, number_cores=4, protocol=PROTOCOLS.MESI) -> None:

        # if len(instr) != number_cores:
        #     raise "Wrong number of instructions streams"
        
        self.cores = []
        self.current_cycle = 0
        self.flush_directory = {}
        # Adding the cores
        for i in range(0, number_cores):
            if protocol == PROTOCOLS.MESI:
                self.cores.append(CoreMESI(instr[i], block, associativity, cache_size, self.check_state, i, cores_cnt=number_cores, check_flush=self.check_flush))
            elif protocol == PROTOCOLS.Dragon: 
                self.cores.append(CoreDragon(instr[i], block, associativity, cache_size, self.check_state, i, cores_cnt=number_cores, check_flush=self.check_flush))
            else:
                self.cores.append(CoreMOESI(instr[i], block, associativity, cache_size, self.check_state, i, cores_cnt=number_cores, check_flush=self.check_flush))

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
        counter = 0 
        while not self.is_done():
            if counter % 1000000 == 0:
                logging.debug(f"Time: {datetime.datetime.now()}Current Cycle: {self.current_cycle} and {len(self.cores[0].instr_stream)} instructions left on core 0")
            
            counter += 1
            bus_transaction = self.bus.get_transaction()
            bus_actions = self.step(bus_transaction)
            self.bus.create_transaction(bus_actions)
            # Check all core if they are waiting and if the bus is empty
            # self.current_cycle += 1
            min_wait_time = sys.maxsize
            all_wait = True
            for core in self.cores:
                if core.wait_counter>=0 and core.wait_counter < min_wait_time:
                    min_wait_time = min(core.wait_counter, min_wait_time) 
                if core.cache.wait_counter >= 0 and core.cache.wait_counter < min_wait_time:
                    min_wait_time =  min(core.cache.wait_counter, min_wait_time)

                if core.cache.wait_counter < 0 and core.wait_counter < 0 and (not core.terminated):
                    all_wait = False
            
            if all_wait and (not self.bus.queue) and (not self.is_done()):
                # print(f"Jump by {min_wait_time}")
                self.current_cycle += min_wait_time
                #print(f"Jump: {min_wait_time}")
                for core in self.cores:
                    core.wait_counter -= min_wait_time
                    core.cache.wait_counter -= min_wait_time
                    core.cycle_count += min_wait_time - 1
            else:
                #print("No jump")
                self.current_cycle += 1
            
                

            # if min_wait_time < 0 or (not self.bus.queue) or (not someone_wait):
            #     self.current_cycle += 1
            # else:
            #     # # DONE update idle cycles for each core
            #     print("Jump")
            #     for core in self.cores:
            #         core.wait_counter -= min_wait_time
            #         core.cache.wait_counter -= min_wait_time
            #     # print(min_wait_time)
            #     self.current_cycle += min_wait_time
        
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
            cache_miss_rate = core.cache.cache_miss_count / (core.load_store_instr_count) if core.load_store_instr_count > 0 else "Zero hits or misses"
            logging.debug(f"{core.core_id} hit is {core.cache.cache_hit_count}" )
            logging.info(f"Core {core.core_id} cache miss rate: {cache_miss_rate}")
            cache_hit_rate = 1-cache_miss_rate if core.load_store_instr_count > 0 else "Zero hits and misses"
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
    
    # core is asking core, not searching core !Core is no longer required as a parameter!
    def check_flush(self, addr, core):
        # Check directory if it contains a flush matching the address and from a different core
        # {addr: []}
        if addr in self.flush_directory.keys() and len(self.flush_directory[addr]) > 0:
            return True
        return False
