import unittest

import analyze_language


class TestAnalyzeLanguageMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(analyze_language.main())


if __name__ == '__main__':
    unittest.main()
