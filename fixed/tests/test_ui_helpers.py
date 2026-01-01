import unittest

from app.ui import calc_stats


class TestUiHelpers(unittest.TestCase):
    def test_calc_stats(self):
        min_v, max_v, avg_v = calc_stats([1.0, 2.0, 3.0])
        self.assertEqual(min_v, 1.0)
        self.assertEqual(max_v, 3.0)
        self.assertAlmostEqual(avg_v, 2.0)


if __name__ == "__main__":
    unittest.main()
