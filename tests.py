import unittest

import appids
import check_correlation
import cluster_reviews
import compute_bayesian_rating
import compute_wilson_score
import describe_reviews
import download_reviews
import estimate_hype
import identify_joke_reviews


class TestDownloadReviewsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(download_reviews.main(download_reference_hidden_gems_as_well=False))


class TestCheckCorrelationMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(check_correlation.main())


class TestAppidsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(appids.main())


class TestClusterReviewsMethods(unittest.TestCase):

    def test_main(self):
        download_reviews.main(download_reference_hidden_gems_as_well=False)

        self.assertTrue(cluster_reviews.main(['723090']))


class TestComputeBayesianRatingMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(compute_bayesian_rating.main())


class TestComputeWilsonScoreMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(compute_wilson_score.main())


class TestDescribeReviewsMethods(unittest.TestCase):

    def test_main(self):
        download_reviews.main(download_reference_hidden_gems_as_well=False)

        self.assertTrue(describe_reviews.main(['723090']))


class TestEstimateHypeMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(estimate_hype.main())


class TestIdentifyJokeReviewsMethods(unittest.TestCase):

    def test_main(self):
        download_reviews.main(download_reference_hidden_gems_as_well=False)

        self.assertTrue(identify_joke_reviews.main(['723090']))


if __name__ == '__main__':
    unittest.main()
