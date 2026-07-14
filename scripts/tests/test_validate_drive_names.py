import unittest

from scripts import validate_drive_names


class _FakeExecute:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class _FakeDrives:
    def __init__(self, names):
        self.names = names

    def get(self, driveId, fields):
        return _FakeExecute({"id": driveId, "name": self.names[driveId]})


class _FakeDriveService:
    def __init__(self, names):
        self.names = names

    def drives(self):
        return _FakeDrives(self.names)


class ValidateDriveNamesTests(unittest.TestCase):
    def test_collect_expected_names_includes_routing_and_drive_map(self):
        expected = validate_drive_names.collect_expected_names()

        self.assertIn("0AN7aea2IZzE0Uk9PVA", expected)
        self.assertIn("Higashi Imobiliária - Claude", expected["0AN7aea2IZzE0Uk9PVA"])
        self.assertFalse(validate_drive_names.find_internal_conflicts(expected))

    def test_internal_conflict_reports_same_drive_id_with_two_names(self):
        expected = {
            "drive-1": {
                "Old Name": {"routing.ROUTES['x'].drive_name"},
                "New Name": {"drive_map_builder.DRIVES"},
            }
        }

        conflicts = validate_drive_names.find_internal_conflicts(expected)

        self.assertEqual(len(conflicts), 1)
        self.assertIn("drive-1", conflicts[0])
        self.assertIn("Old Name", conflicts[0])
        self.assertIn("New Name", conflicts[0])

    def test_live_mismatch_reports_source_and_live_name(self):
        expected = {
            "drive-1": {
                "Configured Name": {"routing.ROUTES['x'].drive_name"},
            }
        }

        mismatches = validate_drive_names.find_live_mismatches(
            expected,
            {"drive-1": "Live Name"},
        )

        self.assertEqual(len(mismatches), 1)
        self.assertIn("Configured Name", mismatches[0])
        self.assertIn("Live Name", mismatches[0])

    def test_fetch_live_names_reads_drive_api_response(self):
        live, errors = validate_drive_names.fetch_live_names(
            _FakeDriveService({"drive-1": "Live Name"}),
            ["drive-1"],
        )

        self.assertEqual(live, {"drive-1": "Live Name"})
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
