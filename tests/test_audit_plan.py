"""Regression checks use synthetic schedules and costs, not travel advice."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_plan", ROOT / "scripts/audit_plan.py")
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


def event(kind, start, end, **kwargs):
    return dict(kind=kind, name=kind, start=start, end=end, **kwargs)


def plan():
    return {
        "trip": {"days": 1, "people": 2, "budget_per_person": 500},
        "fixed_costs_per_person": {"lodging": 100},
        "days": [{"day": 1, "events": [
            event("meal", "09:00", "09:30", meal="breakfast", cost_per_person=20),
            event("attraction", "10:00", "11:30", must=True, verified=True),
            event("meal", "12:00", "13:00", meal="lunch", cost_per_person=40),
            event("meal", "18:00", "19:00", meal="dinner", cost_per_person=40),
        ]}],
    }


class AuditTests(unittest.TestCase):
    def issues(self, data):
        return "\n".join(w['issue'] for w in audit_module.audit(data)['warnings'])

    def driving_plan(self, pause_kind="rest", pause_start="15:00", pause_end="15:20"):
        data = plan()
        data['days'][0]['events'][3:3] = [
            event("transit", "13:00", "15:00", drive_min=120),
            event(pause_kind, pause_start, pause_end),
            event("transit", pause_end, "17:20", drive_min=120),
        ]
        return data

    def test_valid_budget(self):
        result = audit_module.audit(plan())
        self.assertEqual(result['warning_count'], 0)
        self.assertEqual(result['estimated_per_person'], 200)
        self.assertEqual(result['estimated_total_party'], 400)
        self.assertEqual(result['remaining_per_person'], 300)

    def test_time_boundaries(self):
        self.assertEqual(audit_module.minute('00:00'), 0)
        self.assertEqual(audit_module.minute('23:59'), 1439)

    def test_invalid_times(self):
        for value in ('10:99', '24:00', '09:60', '9:00', '-1:00', '10:-1', '09:30 ', None, 930):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit_module.minute(value)

    def test_all_time_fields_validated(self):
        for field in ('start', 'end', 'open', 'close', 'latest_entry'):
            data = plan()
            data['days'][0]['events'][1][field] = '10:99'
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit_module.audit(data)

    def test_empty_and_malformed_plans(self):
        for data in ({}, [], None, {'trip': {}}, {'trip': {'days': 1, 'people': 2}, 'days': []}, {'trip': {'days': 1, 'people': 2}, 'days': [{'day': 1, 'events': []}]}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                audit_module.audit(data)

    def test_invalid_counts(self):
        for field in ('days', 'people', 'rest_interval_min', 'min_rest_min'):
            for value in (0, -1, 1.5, True, '1'):
                data = plan()
                data['trip'][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    audit_module.audit(data)

    def test_budget_and_time_warnings(self):
        data = plan()
        data['trip']['budget_per_person'] = 150
        data['days'][0]['events'][1].update(start='09:15', open='10:00', close='11:00', latest_entry='09:00', verified=False)
        data['days'][0]['events'].pop()
        issues = self.issues(data)
        for phrase in ('over budget', 'overlaps', 'before opening', 'after closing', 'after last entry', 'not verified', 'missing dinner'):
            self.assertIn(phrase, issues)

    def test_short_rest_does_not_reset(self):
        for end in ('15:01', '15:19'):
            self.assertIn('continuous driving', self.issues(self.driving_plan(pause_end=end)))

    def test_twenty_minute_rest_resets(self):
        self.assertNotIn('continuous driving', self.issues(self.driving_plan()))

    def test_meal_can_be_rest(self):
        self.assertNotIn('continuous driving', self.issues(self.driving_plan(pause_kind='meal')))

    def test_sightseeing_is_not_automatic_rest(self):
        for kind in ('attraction', 'hotel'):
            self.assertIn('continuous driving', self.issues(self.driving_plan(pause_kind=kind)))

    def test_overlapping_rest_does_not_reset(self):
        self.assertIn('continuous driving', self.issues(self.driving_plan(pause_start='14:50', pause_end='15:10')))

    def test_configurable_rest_threshold(self):
        data = self.driving_plan()
        data['trip']['min_rest_min'] = 30
        self.assertIn('continuous driving', self.issues(data))

    def test_invalid_drive_duration(self):
        for drive in (-1, float('nan'), 121):
            data = self.driving_plan()
            data['days'][0]['events'][3]['drive_min'] = drive
            with self.subTest(drive=drive), self.assertRaises(ValueError):
                audit_module.audit(data)

    def test_missing_day_and_duplicate_day(self):
        data = plan()
        data['trip']['days'] = 2
        self.assertIn('day count', self.issues(data))
        data['days'].append(copy.deepcopy(data['days'][0]))
        with self.assertRaises(ValueError):
            audit_module.audit(data)

    def test_cli_exit_codes(self):
        over_budget = plan()
        over_budget['trip']['budget_per_person'] = 150
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'plan.json'
            for data, strict, expected in ((plan(), True, 0), (over_budget, True, 1), (over_budget, False, 0), ({}, True, 2), ([], False, 2)):
                path.write_text(json.dumps(data))
                args = [sys.executable, str(ROOT/'scripts/audit_plan.py'), str(path)] + (['--strict'] if strict else [])
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertIsInstance(json.loads(result.stdout), dict)
                self.assertNotIn('Traceback', result.stderr)

    def test_initializer_and_draft_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            args = [sys.executable, str(ROOT/'scripts/init_trip.py'), folder, '--destination', '新疆', '--days', '12', '--people', '2', '--budget-per-person', '5000']
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
            path = Path(folder)/'plan.json'
            before = path.read_bytes()
            data = json.loads(before)
            self.assertEqual(len(data['days']), 12)
            self.assertEqual(data['trip']['people'], 2)
            with self.assertRaises(ValueError):
                audit_module.audit(data)
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 2)
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
