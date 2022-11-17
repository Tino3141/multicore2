import unittest
from moesi import MOESI
from definitions import MOESI_ACTIONS, MOESI_STATES, PROTOCOLS
from coreMOESI import CoreMOESI
from bus import BusProtocolInput
from computer import Computer

test_bus_input = BusProtocolInput(MOESI_ACTIONS.No_Action, 0, 0x1)
class TestSuite(unittest.TestCase):
    def test_MOESI_protocol(self):
        m = MOESI()
        m.step(MOESI_ACTIONS.PrRd, someone_has_copy=True)
        self.assertEqual(m.current_state, MOESI_STATES.Shared)

        m.step(MOESI_ACTIONS.PrWr, someone_has_copy=False)
        self.assertEqual(m.current_state, MOESI_STATES.Modified)

        m.step(MOESI_ACTIONS.BusRd, someone_has_copy=True)
        self.assertEqual(m.current_state, MOESI_STATES.Owned)

        m.step(MOESI_ACTIONS.BusUpgr, someone_has_copy=True)
        self.assertEqual(m.current_state, MOESI_STATES.Invalid)

    def test_cache_hit(self):
        instructions = [
            (0, 0x1),
            (0, 0x1),
            (0, 0x1)
        ]
        core = CoreMOESI(instructions, 16, 4, 1024, cores_cnt=1)

        while not core.terminated:
            core.step(test_bus_input)
        
        
        self.assertEqual(len(core.cache.indexes[0]), 1)
    
    
    def test_cache_eviction(self):
        instructions = [
            (0, 0x100001),
            (0, 0x200001),
            (0, 0x300001),
            (0, 0x100001)
        ]
        core = CoreMOESI(instructions, 16, 2, 1024, cores_cnt=1)

        while not core.terminated:
            core.step(test_bus_input)

        self.assertEqual(len(core.cache.indexes[0]), 2)
        self.assertEqual(core.cache.indexes[0][0][0].current_state, MOESI_STATES.Exclusive)
        self.assertEqual(core.cache.indexes[0][0][1], core.cache.compute_tag(0x300001))
        self.assertEqual(core.cache.indexes[0][1][0].current_state, MOESI_STATES.Exclusive)
        self.assertEqual(core.cache.indexes[0][1][1], core.cache.compute_tag(0x100001))
        
    def test_fetching(self):
        instructions = [
            (0, 0x100001)
        ]

        core = CoreMOESI(instructions, 16, 2, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 101)

    def test_fetching_multiple(self):
        instructions = [
            (0, 0x100001),
            (0, 0x300001)
        ]

        core = CoreMOESI(instructions, 16, 2, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 201)

    def test_eviction(self):
        instructions = [
            (0, 0x100001),
            (0, 0x200001),
            (0, 0x300001),
            (0, 0x100001)
        ]
        core = CoreMOESI(instructions, 16, 2, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 599)
    def test_wait_type2(self):
        instructions = [
            (2, 0x5),
            (0, 0x100001)
        ]
        core = CoreMOESI(instructions, 16, 2, 1024, cores_cnt=1)
        
        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 106)

    def test_single_core_MESI_full(self):
        instructions = [
            (1, 0x200001), 
            (2, 0x5),
            (0, 0x100001), 
            (2, 0x5), 
            (1, 0x300001)
        ]

        core = CoreMOESI(instructions, 16, 2, 1024, cores_cnt=1)

        current_cycle = 0
        while not core.terminated:
            core.step(test_bus_input)
            current_cycle += 1

        self.assertEqual(current_cycle, 410)
    
    def test_check_state(self):

        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
        ]
        
        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 102)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Modified)
        self.assertEqual(computer.cores[1].check_state(0x100001, 1)[0][1],MOESI_STATES.Modified)
    
    def test_multi_simple(self):

        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (0, 0x100001)
        ]
        
        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 202)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Owned)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)

    def test_multi_reads(self):
        instr_1 = [
            (0, 0x100001)
        ]

        instr_2 = [
            (0, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 103)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)

    def test_multi_writes(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (1, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 201)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)

    def test_multi_write_2(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (1, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        #self.assertEqual(computer.current_cycle, 200)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Modified)

    def test_multi_write_read_flush_inter(self):
        instr_1 = [
            (1, 0x100001)
        ]

        instr_2 = [
            (2, 0x10),
            (0, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 200)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Owned)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)

    
    def test_multi_write_read(self):
        instr_1 = [
            (1, 0x100001),
            (2, 0x20)
        ]

        instr_2 = [
            (2, 0x10),
            (0, 0x100001),
            (1, 0x100001)
        ]

        instructions = [instr_1, instr_2]

        computer = Computer(instructions, number_cores=2, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 162)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Modified)

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

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 146)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)

    def test_4_cores_read(self):
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

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 104)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)

    def test_4_core_read_write(self):
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

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 199)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Owned)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, MOESI_STATES.Shared)

    def test_4_core_write_delayed(self):
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

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 250)
        self.assertEqual(computer.cores[0].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)
        self.assertEqual(computer.cores[1].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)
        self.assertEqual(computer.cores[2].cache.indexes[0][0][0].current_state, MOESI_STATES.Invalid)
        self.assertEqual(computer.cores[3].cache.indexes[0][0][0].current_state, MOESI_STATES.Modified)
 
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

        computer = Computer(instructions, number_cores=4, protocol=PROTOCOLS.MOESI)
        computer.start()

        self.assertEqual(computer.current_cycle, 105)
 




if __name__ == '__main__':
    unittest.main()