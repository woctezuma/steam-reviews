from describe_reviews import analyzeAppIDinEnglish, getReviewContent

from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest

#TODO https://github.com/scikit-learn-contrib/sklearn-pandas

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

    # Reference: https://stackoverflow.com/a/32152755
    exclude = ["language", "recommendationid"]
    D = df.ix[:, df.columns.difference(exclude)]

    #Reference: https://stackoverflow.com/a/22653050
    X = D.reset_index().values

    # Reference: http://scikit-learn.org/stable/auto_examples/covariance/plot_outlier_detection.html
    outliers_fraction = 0.25
    # clf = svm.OneClassSVM(nu=0.95 * outliers_fraction + 0.05, kernel="rbf", gamma=0.1)

    n_samples = 100
    rng = np.random.RandomState(42)
    clf = IsolationForest(max_samples=n_samples,
                    contamination=outliers_fraction,
                    random_state=rng)

    clf.fit(X)
    scores_pred = clf.decision_function(X)
    y_pred = clf.predict(X)

    sum([1 for i in y_pred if i > 0])

    return

if __name__ == "__main__":
    main()
