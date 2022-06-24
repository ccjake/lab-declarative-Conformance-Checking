from enum import Enum, unique
from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter


@unique
class TEMPLATE(Enum):
    # Co_Excetence = "Co_Excetence"
    # Responded_Existence = "Responded_Existence"
    # Responded = "Responded"
    Equivalence = "equivalence"
    Always_After = "always_after"
    Always_Before = "always_before"
    Never_Together = "never_together"
    Directly_Follows = "directly_follows"
    Activity_Frequency = "activ_freq"


# print(TEMPLATE.Responded_Existence)


def case_id_query(table):
    cases_table = '"' + table + "_CASES" + '"."CASE ID"'
    return PQLColumn(name="Case Id", query=cases_table)


def equivalence_activities(table:str,activities):
    """
        For 2 activities A and B, they are EQUIVALENCE iff they occur
        eqully often in every trace

        @param table: the name of querying table
        @param activities: the activities variants of log
        @return: list for query result
    """
    queries = PQL()
    queries.add(case_id_query(table))

    def sum_query(A):
        return "SUM( CASE WHEN \"" + table + "\".\"concept:name\" = '" + A + "' THEN 1 ELSE 0 END)"

    for A in activities:
        for B in activities:
            col_name = "equivalence_activities " + A + " TO " + B
            query = (
                "CASE WHEN "+ sum_query(A) + " = " + sum_query(B) + "THEN 1 ELSE 0 END"
            )
            queries.add(PQLColumn(name = col_name,query = query))
    return queries



def responded_existence(table: str, activities):
    """
    For 2 activities, when activity a occurs, also b occurs.

    @param table: the name of querying table
    @param activities: the activities variants of log
    @return: dataframe for query result
    """
    queries = PQL()
    queries.add(case_id_query(table))


    for A in activities:
        for B in activities:
            if A == B:
                continue
            col_name = "Responded_Existence " + A + " TO " + B


            query = (
                '1 - MATCH_ACTIVITIES("'
                + table
                + '"."concept:name", NODE[\''
                + A
                + "'], EXCLUDING['"
                + B
                + "'])"
            )
            # queries.add(col_name)
            queries.add(PQLColumn(name=col_name, query=query))

    return queries


def co_excetence(table: str, activities):
    """
    For 2 activities a and b, the occurs at same time.

    @param table: the name of querying table
    @param activities: the activities variants of log
    @return: dataframe for query result
    """
    queries = PQL()
    queries.add(case_id_query(table))
    for A in activities:
        for B in activities:
            if A == B:
                continue
            col_name = "Responded_Existence " + A + " TO " + B
            query = (
                'CASE WHEN MATCH_ACTIVITIES("'
                + table
                + '"."concept:name",NODE[\''
                + A
                + "']) = MATCH_ACTIVITIES(\""
                + table
                + '"."concept:name",NODE[\''
                + B
                + "']) THEN 1 ELSE 0 END"
            )
            # queries.add(col_name)
            queries.add(PQLColumn(name=col_name, query=query))
    return queries


def responded(table: str, activities):
    queries = PQL()
    queries.add(case_id_query(table))
    for A in activities:
        for B in activities:
            if A == B:
                continue
            col_name = "Responded " + A + " TO " + B
            query = (
                'CASE WHEN MATCH_PROCESS_REGEX ("'
                + table
                + '"."concept:name", (\''
                + A
                + "' >> ('*')* >> '"
                + B
                + "' ))  = 1 THEN 1 WHEN MATCH_PROCESS_REGEX ( \""
                + table
                + '"."concept:name", (([!\''
                + A
                + "'])* >> '"
                + B
                + "')) = 1 THEN 1 ELSE 0 END"
            )
            queries.add(PQLColumn(name=col_name, query=query))
    return queries


template_func_dict = {
    # TEMPLATE.Responded_Existence: responded_existence,
    # TEMPLATE.Co_Excetence: co_excetence,
    # TEMPLATE.Responded: responded,
    TEMPLATE.Equivalence:equivalence_activities
}
