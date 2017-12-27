from describe_reviews import analyzeAppIDinEnglish, getReviewContent

def main():
    appID_list = ["723090", "639780", "573170"]

    appID = appID_list[-1]

    df = analyzeAppIDinEnglish(appID)

    review_content = getReviewContent(appID, "38674426")

    print(review_content)

    return

if __name__ == "__main__":
    main()
