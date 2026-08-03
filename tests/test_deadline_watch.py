from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from scripts.deadline_watch.core import Message, classify, extract_dates, sender_allowed
from scripts.deadline_watch.providers import outlook_messages


ALLOWED = ("sufs.org", "stepupforstudents.org", "fldoe.org", "espreschool@outlook.com")


def message(subject, body, sender="notices@sufs.org", message_id="m1"):
    return Message(
        mailbox="hotmail", message_id=message_id, sender=sender, subject=subject, body=body,
        received_at=datetime(2026, 7, 30, 12, tzinfo=timezone.utc),
        source_url="https://outlook.live.com/mail/0/id/m1",
    )


class DeadlineWatchTests(unittest.TestCase):
    def test_step_up_near_miss_is_detected(self):
        result = classify(
            message("Action Needed - Quarter 1 Public School Attestation", "Complete by August 15, 2026."),
            ALLOWED, date(2026, 8, 3),
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.due_date, date(2026, 8, 15))
        self.assertEqual(result.status, "ready")

    def test_unapproved_sender_is_ignored(self):
        result = classify(message("Action Needed", "Due August 15, 2026", "marketing@example.com"), ALLOWED, date(2026, 8, 3))
        self.assertIsNone(result)

    def test_display_name_cannot_spoof_approved_domain(self):
        self.assertFalse(sender_allowed('"Step Up <notices@sufs.org>" <attacker@example.com>', ALLOWED))

    def test_subdomain_is_allowed_but_lookalike_is_not(self):
        self.assertTrue(sender_allowed("a@alerts.sufs.org", ALLOWED))
        self.assertFalse(sender_allowed("a@sufs.org.attacker.com", ALLOWED))

    def test_multiple_dates_require_review(self):
        result = classify(message("Required", "Open August 10, 2026; due August 15, 2026."), ALLOWED, date(2026, 8, 3))
        self.assertIsNone(result.due_date)
        self.assertEqual(result.status, "review_needed")

    def test_keyword_without_date_requires_review(self):
        result = classify(message("Verification required", "Please complete this soon."), ALLOWED, date(2026, 8, 3))
        self.assertEqual(result.status, "review_needed")

    def test_past_and_far_future_dates_do_not_become_due_date(self):
        result = classify(message("Deadline", "July 1, 2026 and December 1, 2026"), ALLOWED, date(2026, 8, 3))
        self.assertIsNone(result.due_date)

    def test_invalid_dates_are_skipped(self):
        self.assertEqual(extract_dates("February 31, 2026 and 13/40/26", date(2026, 8, 3)), ())

    def test_alert_id_is_stable_and_changes_by_message(self):
        first = classify(message("Deadline", "August 15, 2026"), ALLOWED, date(2026, 8, 3))
        repeat = classify(message("Deadline", "August 15, 2026"), ALLOWED, date(2026, 8, 3))
        other = classify(message("Deadline", "August 15, 2026", message_id="m2"), ALLOWED, date(2026, 8, 3))
        self.assertEqual(first.alert_id, repeat.alert_id)
        self.assertNotEqual(first.alert_id, other.alert_id)

    @patch("scripts.deadline_watch.providers._query_outlook")
    def test_outlook_queries_inbox_and_junk_for_exact_senders(self, query):
        query.return_value = []
        env = {
            "COMPOSIO_KEY": "test-key",
            "DEADLINE_OUTLOOK_ALIAS": "outlook_dairy-tonjon",
            "DEADLINE_ALLOWED_SENDERS_JSON": '["no-reply@sufs.org", "sufs.org"]',
        }
        with patch.dict("os.environ", env, clear=False):
            self.assertEqual(outlook_messages(), [])
        self.assertEqual(
            [call.args[2:] for call in query.call_args_list],
            [("inbox", "no-reply@sufs.org"), ("junkemail", "no-reply@sufs.org")],
        )


if __name__ == "__main__":
    unittest.main()
