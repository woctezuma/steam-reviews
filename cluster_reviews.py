from describe_reviews import analyzeAppIDinEnglish, getReviewContent

def test_imported_module():
    appID_list = ["723090", "639780", "573170"]

    appID = appID_list[-1]

    df = analyzeAppIDinEnglish(appID)

    review_content = getReviewContent(appID, "38674426")

    print(review_content)

    return

def main():
    return

if __name__ == "__main__":
    main()
