import unittest
from model_discover import declare_model_discover
from celonis_connect import Celonis_Connect
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
import pm4py.objects.conversion.log.converter as log_converter
import pandas as pd



class TestModel(unittest.TestCase):
    def test_model(self):
        model = declare_model_discover(path = "../example_log/example_log.xes")
        self.assertEqual(model['equivalence'],{('ER_Registration', 'IV_Antibiotics'), ('ER_Triage', 'IV_Antibiotics'), ('ER_Registration', 'ER_Triage'), ('IV_Antibiotics', 'ER_Triage'), ('IV_Antibiotics', 'ER_Registration'), ('ER_Triage', 'ER_Registration')})
        self.assertEqual(model['always_after'],{('ER_Triage', 'ER_Sepsis_Triage'), ('ER_Registration', 'ER_Sepsis_Triage'), ('IV_Antibiotics', 'ER_Triage'), ('ER_Registration', 'IV_Antibiotics'), ('IV_Antibiotics', 'ER_Sepsis_Triage'), ('ER_Registration', 'ER_Triage')})
        self.assertEqual(model['always_before'],{('ER_Triage', 'ER_Registration'), ('IV_Antibiotics', 'ER_Registration'), ('ER_Triage', 'IV_Antibiotics')})
        self.assertEqual(model['never_together'],set())
        self.assertEqual(model['directly_follows'],{('ER_Triage', 'ER_Sepsis_Triage'), ('ER_Registration', 'IV_Antibiotics')})
        self.assertEqual(model['activ_freq'],{'ER_Registration': {1}, 'IV_Antibiotics': {1}, 'ER_Triage': {1},'ER_Sepsis_Triage': {5, 6}})

    def test_celnois_model(self):
        cn = Celonis_Connect()
        parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case ID'}
        datamodel = cn.c.datamodels.find("0c6b4617-c643-42b5-8377-e99c974e65bb")
        t = datamodel.tables.find("ffae6ece-292c-4425-bca2-37269bf77539")
        df = pd.DataFrame(t.get_data_frame())
        log = log_converter.apply(log=df, parameters=parameters)
        model = lsk_discovery.apply(log=log)
        self.assertEqual(model['equivalence'], {('ER_Registration', 'IV_Antibiotics'), ('ER_Triage', 'IV_Antibiotics'),
                                                ('ER_Registration', 'ER_Triage'), ('IV_Antibiotics', 'ER_Triage'),
                                                ('IV_Antibiotics', 'ER_Registration'),
                                                ('ER_Triage', 'ER_Registration')})
        self.assertEqual(model['always_after'],
                         {('ER_Triage', 'ER_Sepsis_Triage'), ('ER_Registration', 'ER_Sepsis_Triage'),
                          ('IV_Antibiotics', 'ER_Triage'), ('ER_Registration', 'IV_Antibiotics'),
                          ('IV_Antibiotics', 'ER_Sepsis_Triage'), ('ER_Registration', 'ER_Triage')})
        self.assertEqual(model['always_before'],
                         {('ER_Triage', 'ER_Registration'), ('IV_Antibiotics', 'ER_Registration'),
                          ('ER_Triage', 'IV_Antibiotics')})
        self.assertEqual(model['never_together'], set())
        self.assertEqual(model['directly_follows'],
                         {('ER_Triage', 'ER_Sepsis_Triage'), ('ER_Registration', 'IV_Antibiotics')})
        self.assertEqual(model['activ_freq'],
                         {'ER_Registration': {1}, 'IV_Antibiotics': {1}, 'ER_Triage': {1}, 'ER_Sepsis_Triage': {5, 6}})


if __name__ == '__main':
    suite = unittest.TestSuite()
    suite.addTest(TestModel("test_model"))
    suite.addTest(TestModel("test_celnois_model"))
    # suite.addTest(TestModel("test_celnois_model"))

    runner = unittest.TestSuiteRunner()
    runner.run(suite)