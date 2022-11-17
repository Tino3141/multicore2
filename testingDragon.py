import unittest
from dragon import Dragon
from definitions import DRAGON_ACTIONS, DRAGON_STATES, PROTOCOLS
from coreDragon import CoreDragon
from bus import BusProtocolInput
from computer import Computer

test_bus_input = BusProtocolInput(DRAGON_ACTIONS.No_Action, 0, 0x1)
class TestSuite(unittest.TestCase):
    def test_dragon_protocol(self):
        d = Dragon()

        d.step(DRAGON_ACTIONS.PrRdMiss, someone_has_copy=False)
        self.assertEqual(d.current_state, DRAGON_STATES.Exclusive)

        d.step(DRAGON_ACTIONS.BusRd)
        self.assertEqual(d.current_state, DRAGON_STATES.SharedClean)

        d.step(DRAGON_ACTIONS.PrWr, someone_has_copy=True)
        self.assertEqual(d.current_state, DRAGON_STATES.SharedModified)
       
        d = Dragon()
        new_action = d.step(DRAGON_ACTIONS.PrRdMiss, someone_has_copy=True)
        self.assertEqual(new_action, DRAGON_ACTIONS.BusRd)
        self.assertEqual(d.current_state, DRAGON_STATES.SharedClean)

        new_action = d.step(DRAGON_ACTIONS.PrWr, someone_has_copy=True)
        self.assertEqual(new_action, DRAGON_ACTIONS.BusUpd)
        self.assertEqual(d.current_state, DRAGON_STATES.SharedModified)

        new_action = d.step(DRAGON_ACTIONS.PrWr, someone_has_copy=False)
        self.assertEqual(new_action, DRAGON_ACTIONS.BusUpd)
        self.assertEqual(d.current_state, DRAGON_STATES.Modified)

        new_action = d.step(DRAGON_ACTIONS.BusRd, someone_has_copy=True)
        self.assertEqual(new_action, DRAGON_ACTIONS.Flush)
        self.assertEqual(d.current_state, DRAGON_STATES.SharedModified)
        

    def test_dragon_single_read(self):
        instructions = [
            (0, 0x1),
            (0, 0x1),
            (0, 0x1)
        ]
        core = CoreDragon(instructions, 16, 4, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1
        
        self.assertEqual(current_cycle, 103)
        self.assertEqual(core.cache.indexes[0][0][0].current_state, DRAGON_STATES.Exclusive)
    
    def test_dragon_single_write(self):
        instructions = [
            (1, 0x1),
            (1, 0x1),
            (1, 0x1)
        ]
        core = CoreDragon(instructions, 16, 4, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 103)
        self.assertEqual(core.cache.indexes[0][0][0].current_state, DRAGON_STATES.Modified)

    def test_cache_eviction(self):
        instructions = [
            (0, 0x100001),
            (0, 0x200001),
            (0, 0x300001),
            (0, 0x100001)
        ]
        core = CoreDragon(instructions, 16, 2, 1024, cores_cnt=1)

        while not core.terminated:
            core.step(test_bus_input)

        self.assertEqual(len(core.cache.indexes[0]), 2)
        self.assertEqual(core.cache.indexes[0][0][0].current_state, DRAGON_STATES.Exclusive)
        self.assertEqual(core.cache.indexes[0][0][1], core.cache.compute_tag(0x300001))
        self.assertEqual(core.cache.indexes[0][1][0].current_state, DRAGON_STATES.Exclusive)
        self.assertEqual(core.cache.indexes[0][1][1], core.cache.compute_tag(0x100001))
   
    def test_wait_type2(self):
        instructions = [
            (2, 0x5),
            (0, 0x100001)
        ]
        core = CoreDragon(instructions, 16, 2, 1024, cores_cnt=1)
        
        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 106)

    def test_single_core_Dragon_full(self):
        instructions = [
            (1, 0x200001), 
            (2, 0x5),
            (0, 0x100001), 
            (2, 0x5), 
            (1, 0x300001)
        ]

        core = CoreDragon(instructions, 16, 2, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 410)  

    def test_single_simple(self):
        instr_1 = [
            (1, 0x817ae8),
            (2, 0x1b),
        ]   

        instructions = [instr_1]
        computer = Computer(instructions, number_cores=1, protocol=PROTOCOLS.Dragon)
        computer.start()
        self.assertEqual(computer.current_cycle, 127)
        # self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.Exclusive)

    def test_single_simple2(self):
        instr_1 = [
            (1, 0x100001)
        ]   

        instructions = [instr_1]
        computer = Computer(instructions, number_cores=1, protocol=PROTOCOLS.Dragon)
        computer.start()
        self.assertEqual(computer.current_cycle, 100)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.Modified)

    
    def test_multi_simple_bug(self):

        instr_1 = [
            (1, 0x100001),
            (0, 0x2111)
            
        ]

        instr_2 = [
            (1, 0x2111),           
            (0, 0x100001),
        ]
        
        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 302)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)

    def test_multi_reads(self):
        instr_1 = [
            (0, 0x100001)
        ]

        instr_2 = [
            (0, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 103)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)


    def test_multi_writes(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (1, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 202)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)

    def test_mutli_write2(self):
        instr_1 = [
            (2, 0x10),
            (1, 0x100001)
        ]

        instr_2 = [
            (1, 0x100001)
        ]
        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 222)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)


    def test_multi_read_write(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (0, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 216)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)


    def test_multi_write_read(self):
        instr_1 = [
            (0, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (1, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 118)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)
    
    def test_state_swap(self):
        instr_1 = [
            (0, 0x100001),
            (2, 0x12),
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (1, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        # self.assertEqual(computer.current_cycle, 123)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)
    
    def test_4_cores_read_with_delay(self):
        instr_1 = [
            (0, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (0, 0x100001)
        ]

        instr_3 = [
            (2, 0x20),
            (0, 0x100001)
        ]

        instr_4 = [
            (2, 0x30),
            (0, 0x100001)           
        ]
        

        instructions = [instr_1, instr_2, instr_3, instr_4]

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 143)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)

    def test_4_cores_read_with_delay(self):
        instr_1 = [
            (0, 0x100001)
        ]

        instr_2 = [
            (0, 0x100001)
        ]

        instr_3 = [
            (0, 0x100001)
        ]

        instr_4 = [
            (0, 0x100001)           
        ]
        

        instructions = [instr_1, instr_2, instr_3, instr_4]

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 104)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)

    def test_4_cores_read_write(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (0, 0x100001)
        ]

        instr_3 = [
            (2, 0x10),
            (0, 0x100001)
        ]

        instr_4 = [
            (2, 0x20),
            (0, 0x100001)           
        ]
        

        instructions = [instr_1, instr_2, instr_3, instr_4]

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 215)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedModified)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)

    def test_4_cores_writes_delayed(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (1, 0x100001)
        ]

        instr_3 = [
            (2, 0x20),
            (1, 0x100001)
        ]

        instr_4 = [
            (2, 0x30),
            (1, 0x100001)           
        ]
        

        instructions = [instr_1, instr_2, instr_3, instr_4]

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 227)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, DRAGON_STATES.SharedClean)

    def test_4_core_write_delayed(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (1, 0x2000001)
        ]

        instr_3 = [
            (1, 0x3000001)
        ]

        instr_4 = [
            (1, 0x4000001)           
        ]
        

        instructions = [instr_1, instr_2, instr_3, instr_4]

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 105)
 
    def test_multi_bug(self):

        instr_1 = [
            (1, 0x100001),
            (0, 0x2111)
            
        ]

        instr_2 = [
            (1, 0x2111),           
            (0, 0x100001),
        ]
        
        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 302)

    def test_faster_than_mesi(self):
        instr_1 = [
            (1, 0x100001),
            (2, 0x10),
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (1, 0x100001),
            (1, 0x100001),
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.Dragon)
        computer.start()

        self.assertEqual(computer.current_cycle, 220)

if __name__ == '__main__':
    unittest.main()
