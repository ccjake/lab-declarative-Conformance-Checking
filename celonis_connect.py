import pandas as pd
from pycelonis import get_celonis
from pycelonis import pql
from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter
import pm4py.objects.conversion.log.converter as log_converter
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
celonis_url = "https://academic-baichao-ye-rwth-aachen-de.eu-2.celonis.cloud"
api_token = "MTRjZTE2YjYtNmNlYi00ZTk5LWI2NjItOTliMDI1YTkyMTJhOlVlTU80NU1aRnNyU0xYd0ZJSkx1bzgvTDJUd1c4L0h6bThiSmZIYUk2V1RR"


# app_toke = "OGUzYWRhMjUtZDcxOS00ODAwLTk5NWQtNzk3Yjk2NWU0MDc2OjlOVnN5bExad0ZPd1N0cXJEK3N2WkNzYXpCTHhXcHlGclVZTXJWQ2ZHRXdX"


class Celonis_Connect:
    # celonis_url = "https://academic-baichao-ye-rwth-aachen-de.eu-2.celonis.cloud"
    # api_token = "MTRjZTE2YjYtNmNlYi00ZTk5LWI2NjItOTliMDI1YTkyMTJhOlVlTU80NU1aRnNyU0xYd0ZJSkx1bzgvTDJUd1c4L0h6bThiSmZIYUk2V1RR"

    def __init__(self, celonis_url="https://academic-baichao-ye-rwth-aachen-de.eu-2.celonis.cloud",
                 api_token="MTRjZTE2YjYtNmNlYi00ZTk5LWI2NjItOTliMDI1YTkyMTJhOlVlTU80NU1aRnNyU0xYd0ZJSkx1bzgvTDJUd1c4L0h6bThiSmZIYUk2V1RR"):
        """

        @param celonis_url: the celonis url
        @param api_token:  the token from celonis user
        """

        self.celonis_url = celonis_url
        self.api_token = api_token
        self.c = get_celonis(url=celonis_url, api_token=api_token, key_type="USER_KEY", permissions=False)


    def get_pools(self):
        """

        @return: the all data pools from the celonis url
        """
        return self.c.pools


    def get_datamodels(self):
        """

        @return: the all datamodels from the celonis url
        """
        return self.c.datamodels

    def get_tables(self,datamodel_id):
        """
        accoding to a datamodel, return all the data tables belong to that

        @param datamodel: the selected datamodel
        @return: the all data tables according to the datamodels
        """
        datamodel = self.c.datamodels.find(datamodel_id)
        return datamodel.tables

    def set_datamodel(self,datamodel_id):
        """
        set the datamodel with datamodel id
        @param datamodel_id: datamodel id, can be checked in pools
        """
        self.datamodel = self.c.datamodels.find(datamodel_id)
        if (datamodel_id == []):
            return False
        else:
            return True

    def get_table_dataframe(self,table_id):
        """

        @param table_id: table id
        @return: accoding the table id return dataframe
        """
        return self.datamodel.tables.find(table_id).get_data_frame()

# log_converter.TO_EVENT_LOG

# c = get_celonis(url=celonis_url, api_token=api_token, key_type="USER_KEY", permissions=False)


# cn = Celonis_Connect()
# parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case ID'}
# datamodel = cn.c.datamodels.find("0c6b4617-c643-42b5-8377-e99c974e65bb")
# t = datamodel.tables.find("ffae6ece-292c-4425-bca2-37269bf77539")
# df = pd.DataFrame(t.get_data_frame())
# log = log_converter.apply(log=df, parameters=parameters)
# model = lsk_discovery.apply(log=log)
# print(model)

# cn = Celonis_Connect()
# print(cn.get_datamodels())
# cn.set_datamodel("0c6b4617-c643-42b5-8377-e99c974e65bb")
# print(cn.get_table_dataframe("1c2acc5b-b636-4d13-b5c9-f8a38e5dc4bf"))
# df =pd.DataFrame(cn.get_table_dataframe("1c2acc5b-b636-4d13-b5c9-f8a38e5dc4bf"))
# df.to_csv("rum_log",sep=",")
# print(cn.get_table_dataframe())
# print(cn.c.datamodels.find("0c6b4617-c643-42b5-8377-e99c974e65bb").tables)
# parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY:'Case ID'}
              # log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ATTRIBUTE_PREFIX:"concept:"}
# print(df.columns)
# print(log)

# skolen = lsk_discovery.apply(log= log)
# print(skolen)

#
# datamodel = cn.c.datamodels.find("0c6b4617-c643-42b5-8377-e99c974e65bb")
# # print(datamodel.tables)
# t = datamodel.tables.find("ffae6ece-292c-4425-bca2-37269bf77539")
# df = pd.DataFrame(t.get_data_frame())
# log = log_converter.apply(log=df,parameters=parameters)

# print(log)
# skolen = lsk_discovery.apply(log= log)
# print(skolen)

# print(t.get_data_frame())

# print(df.columns)
# data = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8], 'C': [9, 10, 11, 12]})
# data.head()
# data_pool = c.pools.find("d0c84d9c-23e0-4da8-ac52-3eac5c8aec45")
# print(data_pool.tables)

# print(analysis.data)
# print(c.analyses.find("rum table").data)
