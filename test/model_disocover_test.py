import unittest
from discovery.model_discover import declare_model_discover, declare_model_discover_by_template
from celonis_connect import Celonis_Connect
from discovery.templates_func import *
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer


class TestModel(unittest.TestCase):
    @classmethod
    def setTestLog(cls,path):
        test_log = xes_importer.apply(path)
        pm4py_sekelton_model = lsk_discovery.apply(test_log)
        for k in pm4py_sekelton_model.keys():
            if k == TEMPLATE.Activity_Frequency.value:
                continue
            pm4py_sekelton_model[k] = list(pm4py_sekelton_model[k])
            pm4py_sekelton_model[k].sort()

        return pm4py_sekelton_model
    @classmethod
    def setUpClass(cls):
        cls.cn = Celonis_Connect()

        cls.pm4py_sekelton_model = cls.setTestLog("../example_log/synthetic event log.xes")
        cls.cn.set_datamodel("synthetic")
        cls.cn.set_table("synthetic_event_log_xes")

        # cls.pm4py_sekelton_model = cls.setTestLog("../example_log/example_log.xes")
        # cls.cn.set_datamodel("rum_example")
        # cls.cn.set_table("example_log_xes")

        cls.datamodel = cls.cn.get_datamodel()
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
            template=TEMPLATE.Equivalence
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
        # print(pql_skeleton)
        # print("---")
        # print(self.pm4py_sekelton_model)
        self.assertDictEqual(self.pm4py_sekelton_model,pql_skeleton)



    def test_template_euqivalence_with_noise(self):
        """
        add noise to test the model by skeleton algo discovered model in pm4py
        @return:
        """
        # test_log = xes_importer.apply("../example_log/synthetic event log.xes")
        test_log = xes_importer.apply("../example_log/example_log.xes")

        for i in range(0,10,2):
            noise = i/10
            pm4py_sekelton_model = lsk_discovery.apply(test_log,parameters={lsk_discovery.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: noise})

            for k in pm4py_sekelton_model.keys():
                if k == TEMPLATE.Activity_Frequency.value:
                    continue
                pm4py_sekelton_model[k] = list(pm4py_sekelton_model[k])
                pm4py_sekelton_model[k].sort()
            pql_skeleton = declare_model_discover_by_template(
                self.datamodel,
                self.table_name,
                self.activities_df,
                template=TEMPLATE.Equivalence,
                noise_threshold=noise
            )
            pm4py_skeleton = pm4py_sekelton_model["equivalence"]
            pql_skeleton.sort()

            self.assertEqual(pm4py_skeleton, pql_skeleton)

    def test_skeleton_discovery_with_noise(self):
        # test_log = xes_importer.apply("../example_log/synthetic event log.xes")
        test_log = xes_importer.apply("../example_log/example_log.xes")
        for i in range(0,10,2):
            noise = i/10
            pm4py_sekelton_model = lsk_discovery.apply(test_log,parameters={lsk_discovery.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: noise})
            for k in pm4py_sekelton_model.keys():
                if k == TEMPLATE.Activity_Frequency.value:
                    continue
                pm4py_sekelton_model[k] = list(pm4py_sekelton_model[k])
                pm4py_sekelton_model[k].sort()
            pql_skeleton = declare_model_discover(self.datamodel,self.table_name,noise_threshold=noise)

            self.assertEqual(pm4py_sekelton_model, pql_skeleton)

if __name__ == "__main":
    suite = unittest.TestSuite()
    suite.addTest(TestModel("test_template_equivalence"))
    suite.addTest(TestModel("test_template_always_after"))
    # suite.addTest(TestModel("test_celnois_model"))

    runner = unittest.TestSuiteRunner()
    runner.run(suite)
