import re

from sys import maxsize
from google.cloud import bigquery
from fuzzywuzzy import fuzz
from google.oauth2 import service_account
from models import Product


class StringSearchService:
    def get_most_likely_articles(lines):
        client = bigquery.Client(location='europe-west6')

        q_res = client.query('SELECT * FROM products.products').result()
        table_names = []
        products = {}
        for row in q_res:
            table_names.append(row[0])
            products[row[0]] = Product(*row)

        def _subs(arr):
            for beg in range(len(arr)):
                for end in range(beg, len(arr)):
                    yield arr[beg:end + 1]

        def _str_dist(s1, s2):
            s1, s2 = s1.lower(), s2.lower()
            best = maxsize
            for substr in _subs(s1):
                ratio = fuzz.ratio(substr, s2)
                dist = 1 if ratio == 0 else 0.1 / ratio
                best = min(dist, best)
            return best

        def _match_name(name):
            matches = {n: _str_dist(n, name) for n in table_names}
            return [(name, n, matches[n]) for n in sorted(matches.keys(), key=lambda k: matches[k])[:5]]

        def _match_line(line):
            matches = []
            for subline in _subs(line):
                matches += _match_name(' '.join(subline))
            return sorted(matches, key=lambda m: m[-1])[:5]

        line_matches = [_match_line(line) for line in lines]
        results = []
        for line in line_matches:
            line_res = []
            for match in line:
                line_res.append((match[2], products[match[1]]))
            results.append(line_res)
        print(results)
        return results
