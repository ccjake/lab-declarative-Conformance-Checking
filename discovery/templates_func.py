from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter
from templates import TEMPLATE
import pandas as pd

def case_id_query(table):
    cases_table = '"' + table + "_CASES" + '"."CASE ID"'
    return PQLColumn(name="Case Id", query=cases_table)


def equivalence_activities(datamodel, table: str, activities_df,noise_threshold):
    """
    For 2 activities A and B, they are EQUIVALENCE iff they occur
    eqully often in every trace

    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: a list of pairs acitivities correspond equivalence
    """

    activities = list(activities_df.index.values)
    queries = PQL()
    queries.add(case_id_query(table))

    def sum_query(A):
        return (
            'SUM( CASE WHEN "'
            + table
            + '"."concept:name" = \''
            + A
            + "' THEN 1 ELSE 0 END)"
        )

    for A in activities:
        for B in activities:
            if A != B:
                col_name = "equivalence_activities " + A + " TO " + B
                query = (
                    "CASE WHEN ("
                    + sum_query(A)
                    + " = "
                    + sum_query(B)
                    + " AND "
                    + sum_query(A)
                    + " >0 )"
                    + "THEN 1 ELSE 0 END"
                )
                queries.add(PQLColumn(name=col_name, query=query))
    df = datamodel.get_data_frame(queries)

    return pql_table_to_relation(df, activities_df,noise_threshold)


def always_after(datamodel, table: str, activities_df,noise_threshold):
    """
    An occurrence of activity A always followed by acitivity B


    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: a list of pairs acitivities correspond always after
    """
    activities = list(activities_df.index.values)
    queries = PQL()
    queries.add(case_id_query(table))

    for A in activities:
        for B in activities:
            if A != B:
                col_name = "always_after " + A + " TO " + B
                query = (
                    "CASE WHEN PROCESS EQUALS '"
                    + A
                    + "' TO ANY TO '"
                    + B
                    + "' THEN 1 ELSE 0 END"
                )
                queries.add(PQLColumn(name=col_name, query=query))
    df = datamodel.get_data_frame(queries)

    return pql_table_to_relation(df, activities_df,noise_threshold)


def always_before(datamodel, table: str, activities_df,noise_threshold):
    """
    An occurrence of activity B always precceded by acitivity A


    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: a list of pairs acitivities correspond always before
    """


    activities = list(activities_df.index.values)
    queries = PQL()
    queries.add(case_id_query(table))

    # def match_after(A, B):
    #     return "CASE WHEN PROCESS EQUALS '" + A + "' TO '" + B + "' THEN 1 ELSE 0 END"

    for A in activities:
        for B in activities:
            if A != B:
                col_name = "always_before " + B + " TO " + A
                query = (
                    "CASE WHEN PROCESS EQUALS '"
                    + A
                    + "' TO ANY TO '"
                    + B
                    + "' THEN 1 ELSE 0 END"
                )
                queries.add(PQLColumn(name=col_name, query=query))
    df = datamodel.get_data_frame(queries)

    return pql_table_to_relation(df, activities_df,noise_threshold)


def never_together(datamodel, table: str, activities_df,noise_threshold):

    """

    Two acitivities A and B nerver occur in one trace


    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: a list of pairs acitivities correspond never together
    """

    activities = list(activities_df.index.values)
    queries = PQL()
    queries.add(case_id_query(table))
    for A in activities:
        for B in activities:
            if A != B:
                col_name = "never_together " + A + " TO " + B
                query = (
                    'CASE WHEN MATCH_ACTIVITIES("'
                    + table
                    + '"."concept:name", NODE[\''
                    + A
                    + "'],EXCLUDING['"
                    + B
                    + "']) = 1 THEN 1 ELSE 0 END"
                )
                queries.add(PQLColumn(name=col_name, query=query))
    df = datamodel.get_data_frame(queries)

    return pql_table_to_relation(df, activities_df,noise_threshold)


def directly_follows(datamodel, table: str, activities_df,noise_threshold):
    """

    Acitivity A directly followed by activity B

    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: a list of pairs acitivities correspond directly follows
    """
    activities = list(activities_df.index.values)
    queries = PQL()
    queries.add(case_id_query(table))
    for A in activities:
        for B in activities:
            col_name = "never_together " + A + " TO " + B
            query = (
                "CASE WHEN PROCESS EQUALS '" + A + "' TO '" + B + "' THEN 1 ELSE 0 END"
            )
            queries.add(PQLColumn(name=col_name, query=query))
    df = datamodel.get_data_frame(queries)

    return pql_table_to_relation(df, activities_df,noise_threshold)


def activ_freq(datamodel, table: str, activities_df, noise_threshold):
    """
    Activities frequency

    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: the activities freq of the log (considering the noise)
    """
    activities = list(activities_df.index.values)
    queries = PQL()
    # queries.add(case_id_query(table))
    queries.add(PQLColumn(name="trace", query="VARIANT(\"" + table + "\".\"concept:name\")"))
    queries.add(PQLColumn(name="frequency", query="COUNT(\"" + table + "_cases\".\"Case Id\")"))
    df = pd.DataFrame(datamodel.get_data_frame(queries))
    df.set_index('trace', inplace=True)
    trace_list = list(df.index.values)

    log_traces = sum(df['frequency'])

    activ_freq = {}
    for activity in activities:
        freq_number = {}
        for trace in trace_list:
            freq = trace.count(activity)
            if freq not in list(freq_number.keys()):
                freq_number[freq] = df.loc[trace, "frequency"]
            else:
                freq_number[freq] += df.loc[trace, "frequency"]
        threshold = 0
        freq_list = []
        numer_freq = dict(zip(freq_number.values(), freq_number.keys()))

        for key in sorted(list(numer_freq.keys()), reverse=True):
            threshold += key
            freq_list.append(numer_freq[key])
            if (threshold < log_traces * (1 - noise_threshold)):
                continue
            else:
                activ_freq[activity] = set(freq_list)
                break

    return activ_freq
    # df.set_index("activity",inplace=True)


def pql_table_to_relation(pql_df, activities_df,noise_threshold):
    """

    Transform the dataframe by PQL queried to the relation list

    @param datamodel: the datamodel from celonis
    @param table: the name of querying table
    @param activities_df: the activities variants of log
    @param noise_threshold: the noise
    @return: the relation list
    """
    remove_list = []
    colums = pql_df.columns.values.tolist()[1:]
    colums.sort()
    # template_dict = {}
    template_list = []
    activities = list(activities_df.index.values)
    activities.sort()
    for col in colums:
        A = col.split(" ")[-3]
        su = pql_df[col].sum()
        if su < activities_df.loc[A, "frequency"] * (1-noise_threshold):
            remove_list.append(col)
    pruned_df = pql_df.drop(columns=remove_list)

    supported_templates = pruned_df.columns.values.tolist()[1:]
    for t in supported_templates:
        A_B = t.split(" ")
        A = A_B[-3]
        B = A_B[-1]
        template_list.append((A, B))

    template_list.sort()
    return template_list


template_func_dict = {

    TEMPLATE.Equivalence: equivalence_activities,
    TEMPLATE.Always_After: always_after,
    TEMPLATE.Always_Before: always_before,
    TEMPLATE.Never_Together: never_together,
    TEMPLATE.Directly_Follows: directly_follows,
    TEMPLATE.Activity_Frequency: activ_freq,
}
