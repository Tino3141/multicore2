import unittest
from dragon import Dragon
from definitions import DRAGON_ACTIONS, DRAGON_STATES

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
        

        


if __name__ == '__main__':
    unittest.main()