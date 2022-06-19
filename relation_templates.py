from enum import Enum, unique
from pycelonis.celonis_api.pql.pql import PQL, PQLColumn, PQLFilter


@unique
class TEMPLATE(Enum):
    Co_Excetence = "Co_Excetence"
    Responded_Existence = "Responded_Existence"


print(TEMPLATE.Responded_Existence)


def case_id_query(table):
    cases_table = "\"" + table + "_CASES" + "\".\"CASE ID\""
    return PQLColumn(name="Case Id", query=cases_table)


def responded_existence(table: str, activities):
    queries = PQL()
    ## case id query
    queries.add(case_id_query(table))
    for A in activities:
        for B in activities:
            if A == B:
                continue
            col_name = "Responded_Existence " + A + " TO " + B
            query = "1 - MATCH_ACTIVITIES(\"" + table + "\".\"concept:name\", NODE['" + A + "'], EXCLUDING['" + B + "'])"
            # queries.add(col_name)
            queries.add(PQLColumn(name=col_name, query=query))

    return queries


def co_excetence(table: str, activities):
    queries = PQL()
    ## case id query
    queries.add(case_id_query(table))
    for A in activities:
        for B in activities:
            if A == B:
                continue
            col_name = "Responded_Existence " + A + " TO " + B
            query = "CASE WHEN MATCH_ACTIVITIES(\"" + table + "\".\"concept:name\",NODE['" + A + "']) = MATCH_ACTIVITIES(\"" + table + "\".\"concept:name\",NODE['" + B + "']) THEN 1 ELSE 0 END"
            # queries.add(col_name)
            queries.add(PQLColumn(name=col_name, query=query))
    return queries

template_func_dict = {TEMPLATE.Responded_Existence: responded_existence,
                      TEMPLATE.Co_Excetence:co_excetence}
