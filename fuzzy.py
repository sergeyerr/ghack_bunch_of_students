from json.encoder import INFINITY
from google.cloud import bigquery
from difflib import get_close_matches
from Levenshtein import distance


def match_names(names):
    credentials = service_account.Credentials.from_service_account_file(
    'recipe-detector-b4791741606a.json')
    client = bigquery.Client(credentials= credentials, location='europe-west6')
    table_names = [row[0] for row in client.query("SELECT Name FROM products.products").result()]

    def _str_dist(s1, s2):
        best = INFINITY
        for beg in range(len(s1) - 1):
            for end in range(1, len(s1)):
                substr = s1[beg:end + 1]
                dist = distance(substr, s2)
                best = min(dist, best)
        return best

    def _match_name(name):
        close = get_close_matches(name, table_names)
        if (close):
            return min(close, key=lambda s: _str_dist(s.lower(), name.lower()))
        matches = {}
        for tn in table_names:
            dist = _str_dist(tn, name)
            if dist < 2:
                matches[tn] = dist
        if matches:
            return min(matches.keys(), key=lambda m : matches[m])
        return []

    corrected = [_match_name(n) for n in names]
    return corrected
