def parse_id(i):
    """Since we deal with both strings and ints, force appid to be correct."""
    try:
        return int(str(i).strip())
    except:
        return None


def id_reader():
    """Read the previous created idlist.csv."""
    import csv

    with open("hidden_gems_only_appids.txt") as basefile:
        reader = csv.reader(basefile)
        for row in reader:
            yield parse_id(row[0])

def main():
    appID = 603960

    review_description = "all"  # e.g. funny or helpful
    language = "all"  # e.g. english or schinese
    offset = 0

    api_url = "http://store.steampowered.com/appreviews/"

    ##

    import json
    import requests
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    log = logging.getLogger('games')

    defaults = {
        'json': '1',
        'language': language,
        'filter': review_description,
    }
    log.info("Default parameters: %s", repr(defaults))

    LIMIT = 150
    WAIT_TIME = (5 * 60) + 10  # 5 minutes plus a cushion

    log.info("Opening games.json")
    with open("games.json", "w") as f:
        count, batch_count = 0, 0

        log.info("Opening hidden_gems_only_appids.txt")
        for appid_test in id_reader():
            print(appid_test)

        URL = api_url + str(appID)

        req_data = dict(defaults)

        max_num_reviews = pow(10, 3)
        # Initialize
        num_reviews = max_num_reviews

        while offset<num_reviews:
            req_data['start_offset'] = str(offset)

            resp_data = requests.get(URL, params=req_data)

            result = resp_data.json()

            if num_reviews == max_num_reviews:
                print(result["query_summary"])
                num_reviews = result["query_summary"]["total_reviews"]

            num_reviews_with_this_request = result["query_summary"]["num_reviews"]

            review_dict = result["reviews"]
            f.write(json.dumps(review_dict) + '\n')

            print(offset)
            offset += num_reviews_with_this_request

    # TODO batch and query limit per minute


if __name__ == "__main__":
    main()
