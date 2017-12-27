#!/usr/env/bin python

"""Create idprocessed.txt, and review_APPID.json for each APPID in idlist.txt."""

# Heavily inspired from: https://raw.githubusercontent.com/CraigKelly/steam-data/master/data/games.py

import csv
import json
import time
import requests
import logging


def parse_id(i):
    """Since we deal with both strings and ints, force appid to be correct."""
    try:
        return int(str(i).strip())
    except ValueError:
        return None


def id_reader():
    """Read the previous created idlist.csv."""
    with open("idlist.txt") as basefile:
        reader = csv.reader(basefile)
        for row in reader:
            yield parse_id(row[0])


def previous_results():
    """Return a set of all previous found ID's."""
    all_ids = set()
    with open("idprocessed.txt", "r") as f:
        for line in f:
            appid = parse_id(line)
            if appid:
                all_ids.add(appid)
    return all_ids


def main():
    """Entry point."""
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    log = logging.getLogger(__name__)

    defaults = {
        # Copied from: https://gist.github.com/adambuczek/95906b0c899c5311daeac515f740bf33
        'json': '1',
        'language': "all",  # e.g. english or schinese
        'filter': "recent",  # e.g. funny or helpful
        'review_type': "all",
        'purchase_type': "all",
    }
    log.info("Default parameters: %s", repr(defaults))

    api_url = "http://store.steampowered.com/appreviews/"
    query_limit = 150
    wait_time = (5 * 60) + 10  # 5 minutes plus a cushion

    max_num_reviews = pow(10, 4)

    log.info("Getting previous results from idprocessed.txt")
    previos_ids = previous_results()

    log.info("Opening idprocessed.txt")
    with open("idprocessed.txt", "a") as f:
        query_count = 0
        game_count = 0
        game = dict()

        log.info("Opening idlist.csv")
        for appid in id_reader():
            if appid in previos_ids:
                log.info("Skipping previously found id %d", appid)
                continue

            url = api_url + str(appid)

            req_data = dict(defaults)
            req_data['appids'] = str(appid)

            review_dict = dict()
            reviews = []

            # Initialize
            offset = 0
            num_reviews = max_num_reviews
            try_count = 0
            while (offset < num_reviews) and (try_count < 3):
                req_data['start_offset'] = str(offset)

                resp_data = requests.get(url, params=req_data)

                result = resp_data.json()

                reviews.extend(result["reviews"])

                num_reviews_with_this_request = result["query_summary"]["num_reviews"]
                offset += num_reviews_with_this_request

                if num_reviews_with_this_request == 0:
                    try_count += 1

                if num_reviews == max_num_reviews:
                    # Real number of reviews for the given appID
                    num_reviews = result["query_summary"]["total_reviews"]

                    print(result["query_summary"])

                    # To be saved to JSON
                    review_dict["query_summary"] = result["query_summary"]

                query_count += 1

                if query_count >= query_limit:
                    log.info("query count is %d, waiting for %d secs", query_count, wait_time)
                    time.sleep(wait_time)
                    query_count = 0

            review_dict["reviews"] = dict()
            for review in reviews:
                reviewID = review["recommendationid"]
                review_dict["reviews"][reviewID] = review

            output_file = "review_" + str(appid) + ".json"

            with open(output_file, "w") as g:
                g.write(json.dumps(review_dict) + '\n')

            log.info("Review records written for %s: %d (expected: %d)",
                     appid, len(review_dict["reviews"]), num_reviews)

            game_count += 1

            f.write(str(appid) + '\n')

    log.info("Game records written: %d", game_count)


if __name__ == "__main__":
    main()
