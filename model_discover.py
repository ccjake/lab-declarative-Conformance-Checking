import pandas as pd
from relation_templates import TEMPLATE
from relation_templates import template_func_dict
from celonis_connect import Celonis_Connect


def declare_model_discover_by_template(
    datamodel, table: str, activities, template=TEMPLATE.Equivalence
):
    """
    discovery the model by templates, after that, all templates can be assembled into a skeleton model

    @param datamodel: the dataframe from the preliminary calculation
    @param table: the name of the selected table
    @param activities: the activities of the whole log (as list)
    @param template: the templates need to calculate
    @return:
    """
    # cn = Celonis_Connect()
    # activities = cn.get_activities()

    ## get the calcalation result by pql
    query = template_func_dict.get(template)(table, activities)
    df = datamodel.get_data_frame(query)
    return pql_table_to_relation(df, activities)


def pql_table_to_relation(dataframe, activities):
    """

    @param template: the template need to calculate
    @param dataframe: the dataframe from the preliminary calculation
    @param support: constraints support
    @return:
    """
    remove_list = []
    colums = dataframe.columns.values.tolist()[1:]
    colums.sort()
    # template_dict = {}
    template_list = []
    activities.sort()

    # for activity in activities:
    #     template_dict[activity] = []
    for col in colums:
        su = dataframe[col].sum()
        if su < dataframe.shape[0]:
            remove_list.append(col)
    pruned_df = dataframe.drop(columns=remove_list)

    supported_templates = pruned_df.columns.values.tolist()[1:]
    for t in supported_templates:
        A_B = t.split(" ")
        A = A_B[-3]
        B = A_B[-1]
        template_list.append((A, B))

        # template_dict[A].append(B)
        # template_dict[A].sort()
    # pd_dict = {template: template_dict}

    # return pd.DataFrame(data=pd_dict)
    template_list.sort()
    return template_list


def declare_model_discover(datamodel, table: str, activities, templates):
    """

    @param templates: the templates selected from users
    @param table: the table name of the activity table
    @return: the declare model showed in Dataframe
    """

    template = templates[0]
    print(template)

    # df = declare_model_discover_by_template(
    #     datamodel=datamodel, table=table, template=template, activities=activities
    # )
    skeleton_dict = {}
    for template in templates:
        skeleton_dict[template.value] = declare_model_discover_by_template(
            datamodel=datamodel, table=table, template=template, activities=activities
        )


    return skeleton_dict


