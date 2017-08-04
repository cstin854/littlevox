"""
Important function of note here is "get_matches". Takes three arguments, two required, one optional.
"""
import difflib


def get_matches(query, query_set, num_matches=20):
    """
    Takes query (string) and query_set (list of objects that can be converted to strings) and returns the best
    (num_matches) number of matches, as a list of matching objects.
    :param query: string (search query)
    :param query_set: list of objects that have a str method (that which is being searched)
    :param num_matches: number of matches that should be return. Will return the best matches, sorted, up to this #.
    :return:
    """
    li = sorted(query_set, key=lambda q:
                difflib.SequenceMatcher(None, query, str(q)).ratio()
                )
    li.reverse()
    return li[:num_matches]
