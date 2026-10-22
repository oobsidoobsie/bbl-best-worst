"""Regression tests: Manager of the Night ignores reserve players only for the award."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NIGHTLY = ROOT / "bbl" / "nightly.py"


def box_player(name: str, points: int) -> str:
    # name, NBA team, minutes + 13 standard stat values, position
    stats = [30, points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    return "|".join([name, "NBA", *(str(x) for x in stats), "G"])


def roster_row(name: str, team: str, status: str | None = "ACTIVE") -> str:
    fields = [name, "NBA", "G", f"TAKEN:{team}"]
    if status is not None:
        fields.append(status)
    return "|".join(fields)


class ManagerOfNightActiveRosterTests(unittest.TestCase):
    def run_report(self, with_status: bool = True) -> str:
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            shutil.copy2(NIGHTLY, work / "nightly.py")

            box_lines = ["#1|1|0"]
            roster_lines = ["# synthetic test rosters"]
            # A huge-scoring reserve should remain in player rankings, but not count for
            # SOGGY's Manager of the Night total.
            box_lines.append(box_player("Bench Star", 238))
            roster_lines.append(roster_row("Bench Star", "SOGGY", "RESERVE" if with_status else None))

            for i in range(1, 6):
                name = f"SOGGY Active {i}"
                box_lines.append(box_player(name, 10))
                roster_lines.append(roster_row(name, "SOGGY", "ACTIVE" if with_status else None))
            for i in range(1, 6):
                name = f"Alpha Active {i}"
                box_lines.append(box_player(name, 12))
                roster_lines.append(roster_row(name, "Alpha", "ACTIVE" if with_status else None))

            box_path = work / "box.txt"
            pool_path = work / "pool.txt"
            box_path.write_text("\n".join(box_lines) + "\n", encoding="utf-8")
            pool_path.write_text("\n".join(roster_lines) + "\n", encoding="utf-8")

            subprocess.run(
                [sys.executable, str(work / "nightly.py"), str(box_path), str(pool_path), "Test Night"],
                cwd=work,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            return (work / "nightly.html").read_text(encoding="utf-8")

    def test_bench_points_do_not_count_toward_manager_award(self):
        report = self.run_report(with_status=True)
        self.assertRegex(
            report,
            r'MANAGER OF THE NIGHT</span> <b style="font-size:16px">Alpha</b> · <b>60</b>',
        )
        # The benchmark remains in the general player rankings; only the award is filtered.
        self.assertIn("Bench Star", report)
        self.assertIn("238", report)

    def test_legacy_roster_without_status_warns_instead_of_guessing(self):
        report = self.run_report(with_status=False)
        self.assertIn("Manager of the Night not calculated.", report)
        self.assertIn("missing active/bench status", report)
        self.assertNotRegex(report, r'MANAGER OF THE NIGHT</span> <b style="font-size:16px">')

if __name__ == "__main__":
    unittest.main()
