import unittest
from model_discover import declare_model_discover
from celonis_connect import Celonis_Connect
import pandas as pd
from pandas.util.testing import assert_frame_equal
from relation_templates import TEMPLATE


class TestModel(unittest.TestCase):
    def test_single_template_model(self):
        cn = Celonis_Connect()
        templates = [TEMPLATE.Co_Excetence]
        df_dict = {"ER_Registration": ["ER_Sepsis_Triage", "ER_Triage", "IV_Antibiotics"],
                   "ER_Sepsis_Triage": ["ER_Registration", "ER_Triage", "IV_Antibiotics"],
                   "ER_Triage": ["ER_Registration", "ER_Sepsis_Triage", "IV_Antibiotics"],
                   "IV_Antibiotics": ["ER_Registration", "ER_Sepsis_Triage", "ER_Triage"]}
        pd_dict = {TEMPLATE.Co_Excetence: df_dict}
        df = pd.DataFrame(pd_dict)
        activities = cn.get_activities()
        model = cn.get_datamodel()
        tables = cn.get_tables("0c6b4617-c643-42b5-8377-e99c974e65bb")
        table_name = list(tables.names.keys())[0]
        dm = declare_model_discover(model, table_name, activities,
                                    templates=templates)
        assert_frame_equal(df, dm)

    def test_multiple_templates_model(self):
        cn = Celonis_Connect()
        templates = [TEMPLATE.Co_Excetence, TEMPLATE.Responded_Existence]
        df_dict = {"ER_Registration": ["ER_Sepsis_Triage", "ER_Triage","IV_Antibiotics" ],
                   "ER_Sepsis_Triage": ["ER_Registration", "ER_Triage", "IV_Antibiotics"],
                   "ER_Triage": ["ER_Registration", "ER_Sepsis_Triage", "IV_Antibiotics"],
                   "IV_Antibiotics": ["ER_Registration", "ER_Sepsis_Triage", "ER_Triage"]}
        pd_dict = {TEMPLATE.Co_Excetence: df_dict, TEMPLATE.Responded_Existence: df_dict}
        df = pd.DataFrame(pd_dict)
        print(df)
        activities = cn.get_activities()
        model = cn.get_datamodel()
        tables = cn.get_tables("0c6b4617-c643-42b5-8377-e99c974e65bb")
        table_name = list(tables.names.keys())[0]
        dm = declare_model_discover(model, table_name, activities,
                                    templates=templates)
        print(dm)
        assert_frame_equal(df, dm)


if __name__ == '__main':
    suite = unittest.TestSuite()
    suite.addTest(TestModel("test_single_template_model"))
    suite.addTest(TestModel("test_multiple_templates_model"))
    # suite.addTest(TestModel("test_celnois_model"))

    runner = unittest.TestSuiteRunner()
    runner.run(suite)
