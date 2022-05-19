import unittest
from model_discover import declare_model_discover

class TestModel(unittest.TestCase):
    def test_init(self):
        model = declare_model_discover(path = "../example_log/example_log.xes")
        self.assertEqual(model['equivalence'],{('ER_Registration', 'IV_Antibiotics'), ('ER_Triage', 'IV_Antibiotics'), ('ER_Registration', 'ER_Triage'), ('IV_Antibiotics', 'ER_Triage'), ('IV_Antibiotics', 'ER_Registration'), ('ER_Triage', 'ER_Registration')})
        self.assertEqual(model['always_after'],{('ER_Triage', 'ER_Sepsis_Triage'), ('ER_Registration', 'ER_Sepsis_Triage'), ('IV_Antibiotics', 'ER_Triage'), ('ER_Registration', 'IV_Antibiotics'), ('IV_Antibiotics', 'ER_Sepsis_Triage'), ('ER_Registration', 'ER_Triage')})
        self.assertEqual(model['always_before'],{('ER_Triage', 'ER_Registration'), ('IV_Antibiotics', 'ER_Registration'), ('ER_Triage', 'IV_Antibiotics')})
        self.assertEqual(model['never_together'],set())
        self.assertEqual(model['directly_follows'],{('ER_Triage', 'ER_Sepsis_Triage'), ('ER_Registration', 'IV_Antibiotics')})
        self.assertEqual(model['activ_freq'],{'ER_Registration': {1}, 'IV_Antibiotics': {1}, 'ER_Triage': {1},'ER_Sepsis_Triage': {5, 6}})

if __name__ == '__main':
    unittest.main()