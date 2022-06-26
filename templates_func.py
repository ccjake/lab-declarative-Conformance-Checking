from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter
from templates import TEMPLATE



def case_id_query(table):
    cases_table = '"' + table + "_CASES" + '"."CASE ID"'
    return PQLColumn(name="Case Id", query=cases_table)


def equivalence_activities(datamodel, table: str, activities_df):
    """
    For 2 activities A and B, they are EQUIVALENCE iff they occur
    eqully often in every trace

    @param table: the name of querying table
    @param activities: the activities variants of log
    @return: list for query result
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

    return pql_table_to_relation(df, activities_df)


def always_after(datamodel, table: str, activities_df):
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

    return pql_table_to_relation(df, activities_df)


def always_before(datamodel, table: str, activities_df):
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

    return pql_table_to_relation(df, activities_df)


def never_together(datamodel, table: str, activities_df):
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

    return pql_table_to_relation(df, activities_df)


def directly_follows(datamodel, table: str, activities_df):
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

    return pql_table_to_relation(df, activities_df)


def activ_freq(datamodel, table: str, activities_df):
    activities = list(activities_df.index.values)
    queries = PQL()
    queries.add(case_id_query(table))
    queries.add(PQLColumn(name="activity",query= "VARIANT(\""+table+"\".\"concept:name\")"))
    queries.add(PQLColumn(name="frequency",query="COUNT(\"" + table+"_cases\".\"Case Id\")"))
    df = datamodel.get_data_frame(queries)
    activities_list = list(df['activity'].values)
    activ_freq = {}
    for activity in activities:
        ac_freq = []
        for trace in activities_list:
            ac_freq.append(trace.count(activity))
        activ_freq[activity] = set([min(ac_freq), max(ac_freq)])



    return activ_freq
    # df.set_index("activity",inplace=True)


def pql_table_to_relation(pql_df, activities_df):
    """

    @param template: the template need to calculate
    @param dataframe: the dataframe from the preliminary calculation
    @param support: constraints support
    @return:
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
        if su < activities_df.loc[A, "frequency"]:
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
