
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
        self.datamodel = self.c.datamodels.find("0c6b4617-c643-42b5-8377-e99c974e65bb")

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
        if (self.datamodel == []):
            return False
        else:
            return True
    def get_datamodel(self):
        '''

        @return: datamodel selected datamodel
        '''
        return self.datamodel

    def get_table_dataframe(self,table_id):
        """

        @param table_id: table id
        @return: accoding the table id return dataframe
        """
        return self.datamodel.tables.find(table_id).get_data_frame()


    def get_activities(self):
        '''

        @param datamodel_id: datamodel id, can be checked in pools
        @return: the list of activities(kinds of event) in the log
        '''
        if self.datamodel == []:
            return "no datamodel"
        activities_pql = PQL()
        activities_pql.add(PQLColumn(name='event', query="\"example_log_xes\".\"concept:name\""))
        activities = self.datamodel.get_data_frame(activities_pql)
        activities = activities.loc[:, 'event'].drop_duplicates().values.tolist()
        # print(len(activities))

        return activities

# log_converter.TO_EVENT_LOG

# c = get_celonis(url=celonis_url, api_token=api_token, key_type="USER_KEY", permissions=False)


# cn = Celonis_Connect()
# parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case ID'}
# cn.set_datamodel("0c6b4617-c643-42b5-8377-e99c974e65bb")
# print(cn.get_activities())
