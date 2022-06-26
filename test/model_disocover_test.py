import unittest
from discovery.model_discover import declare_model_discover, declare_model_discover_by_template
from celonis_connect import Celonis_Connect
from discovery.templates_func import *
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer


class TestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cn = Celonis_Connect()
        test_log = xes_importer.apply("../example_log/synthetic event log.xes")
        cls.pm4py_sekelton_model = lsk_discovery.apply(test_log)
        for k in cls.pm4py_sekelton_model.keys():
            if k == TEMPLATE.Activity_Frequency.value:
                continue
            cls.pm4py_sekelton_model[k] = list(cls.pm4py_sekelton_model[k])
            cls.pm4py_sekelton_model[k].sort()

        cls.cn.set_datamodel("synthetic")
        cls.datamodel = cls.cn.get_datamodel()

        cls.cn.set_table("synthetic_event_log_xes")
        cls.table_name = cls.cn.get_table().name
        activities_query = PQL()
        activities_query.add(
            PQLColumn(
                name="activities", query='"' + cls.table_name + '"."concept:name"'
            )
        )
        activities_query.add(
            PQLColumn(name="frequency", query='COUNT_TABLE("' + cls.table_name + '")')
        )
        cls.activities_df = cls.datamodel.get_data_frame(activities_query)
        cls.activities_df.set_index("activities", inplace=True)

        # cls.activities = cls.cn.get_activities()

    def test_template_equivalence(self):
        """
        test for equivalence template

        """
        pm4py_skeleton = self.pm4py_sekelton_model["equivalence"]

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel,
            self.table_name,
            self.activities_df,
            template=TEMPLATE.Equivalence,
        )
        pql_skeleton.sort()

        self.assertEqual(pm4py_skeleton, pql_skeleton)

    def test_template_always_after(self):
        """

        Test for always after template
        """
        pm4py_skeleton = self.pm4py_sekelton_model["always_after"]

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel,
            self.table_name,
            self.activities_df,
            template=TEMPLATE.Always_After,
        )

        pql_skeleton.sort()
        self.assertEqual(pm4py_skeleton, pql_skeleton)


    def test_template_always_before(self):
        """

        Test for always before template
        """
        pm4py_skeleton = self.pm4py_sekelton_model["always_before"]

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel,
            self.table_name,
            self.activities_df,
            template=TEMPLATE.Always_Before,
        )

        pql_skeleton.sort()
        self.assertEqual(pm4py_skeleton, pql_skeleton)

    def test_template_never_together(self):

        """

        Test for never together template
        """
        pm4py_skeleton = self.pm4py_sekelton_model["never_together"]

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel,
            self.table_name,
            self.activities_df,
            template=TEMPLATE.Never_Together,
        )

        pql_skeleton.sort()
        self.assertEqual(pm4py_skeleton, pql_skeleton)

    def test_template_directly_follows(self):
        """

        Test for directly follow template
        """

        pm4py_skeleton = self.pm4py_sekelton_model["directly_follows"]

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel,
            self.table_name,
            self.activities_df,
            template=TEMPLATE.Directly_Follows,
        )

        pql_skeleton.sort()
        self.assertEqual(pm4py_skeleton, pql_skeleton)

    def test_template_activ_freq(self):
        """

        Test for activ frequncy template
        """
        pm4py_skeleton = self.pm4py_sekelton_model["activ_freq"]
        print(pm4py_skeleton)

        pql_skeleton = declare_model_discover_by_template(
            self.datamodel,
            self.table_name,
            self.activities_df,
            template=TEMPLATE.Activity_Frequency,
        )

        self.assertDictEqual(pm4py_skeleton,pql_skeleton)


    def test_skeleton_discovery(self):
        """
        Test the whole model discoverd by pql
        """
        pql_skeleton = declare_model_discover(self.datamodel,self.table_name)
        self.assertDictEqual(self.pm4py_sekelton_model,pql_skeleton)


if __name__ == "__main":
    suite = unittest.TestSuite()
    suite.addTest(TestModel("test_template_equivalence"))
    suite.addTest(TestModel("test_template_always_after"))
    # suite.addTest(TestModel("test_celnois_model"))

    runner = unittest.TestSuiteRunner()
    runner.run(suite)
