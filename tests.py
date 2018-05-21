import unittest

import appids
import check_correlation
import cluster_reviews
import compute_bayesian_rating
import compute_wilson_score
import describe_reviews
import estimate_hype
import identify_joke_reviews


class TestCheckCorrelationMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(check_correlation.main())


class TestAppidsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(appids.main())


class TestClusterReviewsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(cluster_reviews.main())


class TestComputeBayesianRatingMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(compute_bayesian_rating.main())


class TestComputeWilsonScoreMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(compute_wilson_score.main())


class TestDescribeReviewsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(describe_reviews.main())


class TestEstimateHypeMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(estimate_hype.main())


class TestIdentifyJokeReviewsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(identify_joke_reviews.main())


if __name__ == '__main__':
    unittest.main()
