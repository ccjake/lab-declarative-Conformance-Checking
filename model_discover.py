from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer
import os
import pandas as pd
# log = xes_importer(os.path.join("test","input_data",""))
import pm4py
from pycelonis import get_celonis
from pycelonis import pql
from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter

from celonis_connect import Celonis_Connect

from relation_templates import TEMPLATE
from relation_templates import template_func_dict

# def declare_model_discover(path):
#     """
#
#     @param path: the path of the log, that would be mined
#     @return: return the model
#     """
#     # variant = xes_importer.Variants.ITERPARSE
#     # parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
#     log = xes_importer.apply(path)
#
#     skolen = lsk_discovery.apply(log= log)
#     return skolen






def declare_model_discover_by_template(datamodel,table:str,activities, template = TEMPLATE.Responded_Existence,support = 1):
    # cn = Celonis_Connect()
    # activities = cn.get_activities()
    query = template_func_dict.get(template)(table,activities)
    df = datamodel.get_data_frame(query)
    return remove_unsupported_relation(template,df,activities,support = support)

def remove_unsupported_relation(template, dataframe,activities, support=1):
    '''

    @param template: the template need to calculate
    @param dataframe: the dataframe from the preliminary calculation
    @param support: constraints support
    @return:
    '''
    remove_list = []
    colums = dataframe.columns.values.tolist()[1:]
    colums.sort()
    template_dict = {}
    activities.sort()
    for activity in activities:
        template_dict[activity] = []
    for col in colums:
        su = dataframe[col].sum()
        if ((su / dataframe.shape[0]) < support):
            print(su)
            print(dataframe.shape[0])
            print("----")
            remove_list.append(col)
    pruned_df = dataframe.drop(columns=remove_list)

    supported_templates = pruned_df.columns.values.tolist()[1:]
    for t in supported_templates:
        A_B = t.split(" ")
        A = A_B[-3]
        B = A_B[-1]
        template_dict[A].append(B)
    pd_dict = {template: template_dict}

    return pd.DataFrame(data=pd_dict)



def declare_model_discover(datamodel,table:str,activities,templates):
    '''

    @param templates: the templates selected from users
    @param table: the table name of the activity table
    @return: the declare model showed in Dataframe
    '''
    template = templates[0]
    print(template)
    df = declare_model_discover_by_template(datamodel = datamodel,table = table,template=template,activities=activities)
    for template in templates[1:]:
        df = df.join(declare_model_discover_by_template(datamodel = datamodel,table = table,template=template,activities=activities))
    return df

cn = Celonis_Connect()
activities = cn.get_activities()
model = cn.get_datamodel()
tables = cn.get_tables("0c6b4617-c643-42b5-8377-e99c974e65bb")
table_name = list(tables.names.keys())[0]
# print(table_name)
dm = declare_model_discover(model,table_name,activities,templates=[TEMPLATE.Co_Excetence,TEMPLATE.Responded_Existence])
print(dm)

# template_func_dict.get("p1")(5)

