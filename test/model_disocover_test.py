import unittest
from model_discover import declare_model_discover, declare_model_discover_by_template
from celonis_connect import Celonis_Connect
from relation_templates import TEMPLATE
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer

class TestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cn = Celonis_Connect()
        test_log = xes_importer.apply("../example_log/example_log.xes")
        cls.pm4py_sekelton_model = lsk_discovery.apply(test_log)
        cls.datamodel = cls.cn.get_datamodel()
        cls.activities = cls.cn.get_activities()
        tables = cls.cn.get_tables("0c6b4617-c643-42b5-8377-e99c974e65bb")
        cls.table_name = list(tables.names.keys())[0]



    def test_template_equivalence(self):
        """
        test for equivalence realtion of the skeleton log from the pql calculation result


        """
        pm4py_skeleton = list(self.pm4py_sekelton_model['equivalence'])
        pm4py_skeleton.sort()

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel, self.table_name, self.activities, template=TEMPLATE.Equivalence
        )
        pql_skeleton.sort()

        pql_skeleton_no_self = []
        for l in pql_skeleton:
            if l[0] != l[1]:
                pql_skeleton_no_self.append(l)
        self.assertEqual(pql_skeleton_no_self, pm4py_skeleton)

    def test_template_always_after(self):
        pm4py_skeleton = list(self.pm4py_sekelton_model['always_after'])
        pm4py_skeleton.sort()

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel, self.table_name, self.activities, template=TEMPLATE.Always_After
        )

        pql_skeleton.sort()
        self.assertEqual(pql_skeleton, pm4py_skeleton)


    def test_template_always_before(self):
        pm4py_skeleton = list(self.pm4py_sekelton_model['always_before'])
        pm4py_skeleton.sort()

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel, self.table_name, self.activities, template=TEMPLATE.Always_Before
        )
        pql_skeleton_no_self = []
        for l in pql_skeleton:
            if l[0] != l[1]:
                pql_skeleton_no_self.append(l)

        pql_skeleton_no_self.sort()
        self.assertEqual(pql_skeleton_no_self, pm4py_skeleton)


if __name__ == "__main":
    suite = unittest.TestSuite()
    suite.addTest(TestModel("test_template_equivalence"))
    suite.addTest(TestModel("test_template_always_after"))
    # suite.addTest(TestModel("test_celnois_model"))

    runner = unittest.TestSuiteRunner()
    runner.run(suite)
