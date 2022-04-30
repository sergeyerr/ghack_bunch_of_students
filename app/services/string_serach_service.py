from json.encoder import INFINITY
from google.cloud import bigquery
from Levenshtein import distance


class StringSearchService:
    def get_most_likely_articles(names):
        client = bigquery.Client(location='europe-west6')
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
            matches = {}
            for tn in table_names:
                dist = _str_dist(tn, name)
                if dist < 2:
                    matches[tn] = dist
            if matches:
                keys = sorted(matches.keys(), key=lambda m : matches[m])[:min(5, len(matches))]
                return [(k, matches[k]) for k in keys]
            return ""

        corrected = [_match_name(n) for n in names]
        return corrected
