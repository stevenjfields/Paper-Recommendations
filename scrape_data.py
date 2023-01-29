import requests
import json
import pandas
import re

def get_url(per_page: int, page: int):
    return f"https://api.openalex.org/works?per-page={per_page}&page={page}&filter=concepts.id:C41008148&mailto=stevenjfields97@gmail.com"

def combine_abstract(abstract_dict: dict):
    abstract = dict()
    for k, v in abstract_dict.items():
        for i in v:
            abstract[i] = k

    final = ""
    for i in sorted(abstract.keys()):
        final += abstract[i] + " "
    return final

def main(num_to_scrape: int):
    per_page = 100
    cols = ["title", "abstract"]

    df = pandas.DataFrame(columns=cols)

    for i in range(1, int(num_to_scrape / per_page)+1):
        response = requests.get(get_url(per_page, i))
        serialized = json.loads(response.content)

        results = serialized["results"]
        results_list = list()
        for result in results:
            title = result["title"] if result['title'] else ""
            title = re.sub(r'[\t\n\r]+', '', title)
            title = re.sub(r'<\/*\w+>', '', title)

            abstract = combine_abstract(result["abstract_inverted_index"]) if result["abstract_inverted_index"] else ""
            abstract = re.sub(r'[\t\n\r]+', '', abstract)
            abstract = re.sub(r'<\/*\w+>', '', abstract)

            results_list.append(
                {
                    "title": title,
                    "abstract": abstract
                }
            )
        df = pandas.concat([df, pandas.DataFrame(results_list)])

        print(f"Processed {i*per_page} papers.")

    df.to_csv("examples.tsv", '\t')
     
if __name__ == "__main__":
    num_to_scrape = 10_000
    main(num_to_scrape)