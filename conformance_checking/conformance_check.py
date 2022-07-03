import pm4py.algo.discovery.log_skeleton.algorithm as lsk_check
import pm4py.algo.conformance.log_skeleton.algorithm
from templates import TEMPLATE
from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter


def variant_table(datamodel, table: str):
    """

    @param datamode: the datamodel in celonis
    @param table: the selected table in celonis
    @return: the variant table(dataframe) for different traces, and the activities list
    """
    ## table for variant table
    pql = PQL()
    pql.add(
        PQLColumn(name="variant", query='VARIANT ( "' + table + '"."concept:name"  )')
    )
    pql.add(PQLColumn(name="freq", query='COUNT("' + table + '_CASES"."Case ID")'))

    pql.add(PQLColumn(name="id", query='MIN("' + table + '_CASES"."Case ID")'))
    df = datamodel.get_data_frame(pql)
    df.set_index('id', inplace=True)

    return df


def conformance_checking(datamodel, table: str, model):
    scc_df = stric_conformance(datamodel, table, model)
    v_df = variant_table(datamodel, table)

    return conf_df_to_dics(scc_df, v_df)


def get_act_order(acties, con, l):
    #     al = [a.strip() for a in  acties.split(',')]

    if ("not_in_model" in con):
        s = []
        for i in range(len(acties)):
            if acties[i] not in l:
                s.append(i)
        return s
    elif ("never_together" in con):
        b = con.split(' ')[-1]
        a = con.split(' ')[-3]
        if (a in acties and b in acties):
            return [acties.index(a), acties.index(b)]
        elif (a in acties):
            return [acties.index(a)]
        else:
            return [acties.index(b)]
    elif ('TO' not in con):
        a = con.split('_')[0]
        return [i for i, x in enumerate(acties) if x == a]
    else:
        b = con.split(' ')[-1]
        a = con.split(' ')[-3]
        return [acties.index(a), acties.index(b)]


def conf_df_to_dics(con_df, v_df):
    scc_df = con_df.set_index('id')
    cols = scc_df.iloc[:, 1:].columns

    l = set([l.strip() for l in ','.join(v_df['variant']).split(',')])

    sum_trace = int(sum(v_df['freq']))
    fulfill_trace = 0
    cc_dic = {}
    for id in scc_df.index.values.tolist():
        violations = []
        fulfill = []
        dic = {}
        acties = [s.strip() for s in scc_df.at[id, 'variant'].split(',')]
        dic['variant'] = acties
        for con in cols:
            if (scc_df.at[id, con] < 0):
                violations.append({con: sorted(get_act_order(acties, con, l))})
            if (scc_df.at[id, con] > 0):
                fulfill.append({con: (sorted(get_act_order(acties, con, l)), acties)})
        if (len(violations) == 0):
            fulfill_trace += v_df.at[id, 'freq']
        fulfill_trace = int(fulfill_trace)
        dic['violations'] = violations
        dic['fulfill'] = fulfill
        activations = int(sum(scc_df.loc[id][1:].map(abs)))
        fulfills = sum(scc_df.loc[id][1:])
        dev = int(activations - fulfills)

        dic['fitness'] = 1 - dev / activations
        dic['activations'] = activations
        dic['fit'] = (fulfill == activations)

        cc_dic[id] = dic
    vio_trace = sum_trace - fulfill_trace
    return cc_dic, [sum_trace, fulfill_trace, vio_trace]


def stric_conformance(datamodel, table, model):
    ## get the variant table
    v_df = variant_table(datamodel, table)
    variant_dic = v_df.groupby("id")["freq"].apply(int).to_dict()

    select_id = str("','".join(v_df.index.values.tolist()))
    filter_query = (
            'FILTER DOMAIN "'+ table+'"."Case ID" IN ( \''
            + select_id
            + "' )"
    )
    pql = PQL()
    pql.add(PQLFilter(filter_query))
    pql.add(PQLColumn(name="id", query='"' + table + '_CASES"."Case Id"'))
    pql.add(PQLColumn(name='variant', query='VARIANT ( "' + table + '"."concept:name" ) '))
    # for key in model.keys():

    # always_after_set = model["always_after"]
    for activities in model[TEMPLATE.Always_After.value]:
        pql += conformance_always_after(activities)
    for activities in model[TEMPLATE.Always_Before.value]:
        pql += conformance_always_before(activities)
    for activities in model[TEMPLATE.Never_Together.value]:
        pql += conformance_never_together(activities, table)
    for activities in model[TEMPLATE.Directly_Follows.value]:
        pql += conformance_directly_follow(activities)
    for activities in model[TEMPLATE.Equivalence.value]:
        pql += conformance_equivalence(activities, table)
    for pqlc in conformance_frequency(model['activ_freq'], table):
        pql += pqlc
    df = datamodel.get_data_frame(pql)
    return df
    # for pair in always_after_set:


def conformance_always_after(activities):
    activities = list(activities)
    a = str(activities[0])
    b = str(activities[1])

    return PQLColumn(
        name="always_after " + a + " TO " + b,
        query="CASE WHEN PROCESS NOT EQUALS '"
              + a
              + "' THEN 0 WHEN PROCESS EQUALS '"
              + a
              + "' TO ANY TO '"
              + b
              + "' THEN 1 ELSE -1 END",
    )


def conformance_always_before(activities):
    activities = list(activities)
    a = str(activities[0])
    b = str(activities[1])

    return PQLColumn(
        name="always_before " + a + " TO " + b,
        query="CASE WHEN PROCESS NOT EQUALS '"
              + a
              + "' THEN 0 WHEN PROCESS EQUALS '"
              + b
              + "' TO ANY TO '"
              + a
              + "' THEN 1 ELSE -1 END",
    )


def conformance_never_together(activities, table):
    activities = list(activities)
    a = str(activities[0])
    b = str(activities[1])
    query = (
            "CASE WHEN PROCESS NOT EQUALS '"
            + a
            + "'THEN 0 WHEN MATCH_ACTIVITIES(\""
            + table
            + '"."concept:name", NODE[\''
            + a
            + "'],EXCLUDING['"
            + b
            + "']) = 1 THEN 1 ELSE -1 END"
    )
    return PQLColumn(name="never_together " + a + " TO " + b, query=query)


def conformance_directly_follow(activities):
    activities = list(activities)
    a = str(activities[0])
    b = str(activities[1])
    query = (
            "CASE WHEN PROCESS NOT EQUALS '"
            + a
            + "' THEN 0 WHEN PROCESS EQUALS '"
            + a
            + "' TO '"
            + b
            + "' THEN 1 ELSE -1 END"
    )
    return PQLColumn(name="directly_follow " + a + " TO " + b, query=query)


def conformance_frequency(activity, table):
    all_act_in_model = "('" + "','".join(list(activity.keys())) + "')"
    pql_list = []
    pql_list.append(PQLColumn(name='not_in_model',
                              query='SUM(CASE WHEN ("' + table + '"."concept:name") in ' + all_act_in_model + "THEN 0 ELSE -1 END)"))
    for ac in activity.keys():
        calc_reworl = 'CALC_REWORK("' + table + '"."concept:name" IN (\'' + ac + '\'))'
        freq = "(" + ",".join(map(str, list(activity[ac]))) + ")"
        query = "CASE WHEN " + calc_reworl + "=0 AND 0 IN " + freq + " THEN 0 WHEN " + calc_reworl + ">0 AND " + calc_reworl + " IN " + freq + "THEN 1 ELSE -1 END"
        #         print(calc_reworl)
        #         print(freq)
        #         print(query)
        pql_list.append(PQLColumn(name=ac + "_" + freq, query=query))
    return pql_list


def conformance_equivalence(activities, table):
    activities = list(activities)
    a = str(activities[0])
    b = str(activities[1])

    def sum_query(a):
        return (
                'SUM( CASE WHEN "'
                + table
                + '"."concept:name" = \''
                + a
                + "' THEN 1 ELSE 0 END)"
        )

    query = (
            "CASE WHEN "
            + sum_query(a)
            + "  = 0 "
            + "THEN 0 WHEN "
            + sum_query(a)
            + " = "
            + sum_query(b)

            + "THEN 1 ELSE -1 END"
    )
    col_name = "equivalence " + a + " TO " + b
    return (PQLColumn(name=col_name, query=query))