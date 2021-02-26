from functools import lru_cache


@lru_cache(maxsize=500, typed=False)
def levenshtein_distance(string_a, string_b):
    if string_a == "":
        return len(string_b)
    if string_b == "":
        return len(string_a)
    if string_a[-1] == string_b[-1]:
        cost = 0
    else:
        cost = 1

    result = min([
        levenshtein_distance(string_a[:-1], string_b)+1, # Deletion
        levenshtein_distance(string_a, string_b[:-1])+1, # Insertion
        levenshtein_distance(string_a[:-1], string_b[:-1]) + cost, # Substitution
    ])

    return result


def similarity(string_a, string_b):
    string_a = (string_a or '')
    string_b = (string_b or '')
    return 1 - (levenshtein_distance(string_a.lower(), string_b.lower())/ max(len(string_a), len(string_b)))


def decode_list_string(value):
    if value is None or len(value.strip()) == 0:
        return []
    else:
        return [i.strip() for i in value.split(',')]


def encode_list_string(value):
    if value:
        return ",".join(value)
    else:
        return None


def decode_dictionary_string(value):
    return {k: v for k, v in [i.split(':') for i in decode_list_string(value)]}


def encode_dictionary_string(value):
    if value is None:
        return None
    else:
        return ','.join([f'{k}:{v}' for k, v in value.items()])
