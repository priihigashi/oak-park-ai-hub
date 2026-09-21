import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ads_monthly_cap_monitor import account_spend, decide_cap_state


class CapDecisionTests(unittest.TestCase):
    def test_below_warning(self):
        decision = decide_cap_state(1200)
        self.assertEqual(decision.state, "BELOW_WARNING")
        self.assertEqual(decision.remaining_to_cap_dollars, 300)

    def test_warning_boundary(self):
        decision = decide_cap_state(1450)
        self.assertEqual(decision.state, "PAUSE_REVIEW_REQUIRED")

    def test_cap_boundary(self):
        decision = decide_cap_state(1500)
        self.assertEqual(decision.state, "CAP_EXCEEDED")
        self.assertEqual(decision.remaining_to_cap_dollars, 0)

    def test_invalid_threshold_order_fails_closed(self):
        with self.assertRaises(ValueError):
            decide_cap_state(100, warning_dollars=1500, cap_dollars=1500)

    def test_empty_api_result_fails_closed(self):
        with self.assertRaises(RuntimeError):
            account_spend([])

    def test_multiple_rows_are_summed(self):
        rows = [
            {"metrics": {"costMicros": "1250000000"}},
            {"metrics": {"costMicros": "125000000"}},
        ]
        self.assertEqual(account_spend(rows), 1375)


if __name__ == "__main__":
    unittest.main()
