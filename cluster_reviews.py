from describe_reviews import analyzeAppIDinEnglish, getReviewContent

def test_imported_module():
    appID = "573170"
    reviewID = "38674426"

    review_content = getReviewContent(appID, reviewID)

    print(review_content)

    return

def main():
    appID_list = ["723090", "639780", "573170"]

    appID = appID_list[-1]

    df = analyzeAppIDinEnglish(appID)

    return

if __name__ == "__main__":
    main()
