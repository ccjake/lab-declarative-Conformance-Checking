from pycelonis.celonis_api.pql.pql import PQL, PQLColumn

from templates import TEMPLATE
from discovery.templates_func import template_func_dict


def declare_model_discover(datamodel, table: str, noise_threshold = 0.0):
    """

    @param templates: the templates selected from users
    @param table: the table name of the activity table
    @return: the declare model showed in Dataframe
    """

    activities_query = PQL()
    activities_query.add(
        PQLColumn(name="activities", query='"' + table + '"."concept:name"')
    )
    activities_query.add(
        PQLColumn(name="frequency", query='COUNT_TABLE("' + table + '_CASES")')
    )
    activities_df = datamodel.get_data_frame(activities_query)
    # event_sum = sum(activities_df['frequency'])
    # activities_df = activities_df[activities_df['frequency'] >= event_sum / 100]
    activities_df.set_index("activities", inplace=True)

    templates = [
        TEMPLATE.Equivalence,
        TEMPLATE.Always_After,
        TEMPLATE.Always_Before,
        TEMPLATE.Never_Together,
        TEMPLATE.Directly_Follows,
        TEMPLATE.Activity_Frequency,
    ]

    skeleton_dict = {}
    for template in templates:
        skeleton_dict[template.value] = declare_model_discover_by_template(
            datamodel=datamodel,
            table=table,
            activities_df=activities_df,
            template=template,
            noise_threshold=noise_threshold
        )

    return skeleton_dict


def declare_model_discover_by_template(
    datamodel, table: str, activities_df, template, noise_threshold = 0.0
):
    """
    discovery the model by templates, after that, all templates can be assembled into a skeleton model

    @param datamodel: the target datamodel in celonis cloud
    @param table: the target table in celonis cloud
    @param activities_df: the activities dataframe of the whole log
    @param template: the templates need to calculate
    @return:
    """

    return template_func_dict.get(template)(datamodel, table, activities_df,noise_threshold)

