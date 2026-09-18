import os
import sys
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mnemo.scheduler import Card, schedule, is_due


def test_first_success_interval_1():
    c = Card(front="a", back="b")
    c2 = schedule(c, 4, "2026-01-01")
    assert c2.interval == 1.0
    assert c2.reps == 1
    assert c2.due == "2026-01-02"


def test_second_success_interval_6():
    c = Card(front="a", back="b", reps=1, interval=1.0)
    c2 = schedule(c, 4, "2026-01-01")
    assert c2.interval == 6.0
    assert c2.reps == 2


def test_third_success_interval_multiplies():
    c = Card(front="a", back="b", reps=2, interval=6.0, ease=2.5)
    c2 = schedule(c, 5, "2026-01-01")
    assert c2.interval == 15.0
    assert c2.reps == 3


def test_failure_resets():
    c = Card(front="a", back="b", reps=3, interval=20.0, ease=2.5)
    c2 = schedule(c, 1, "2026-01-01")
    assert c2.reps == 0
    assert c2.interval == 1.0


def test_ease_never_below_1_3():
    c = Card(front="a", back="b", reps=2, interval=6.0, ease=1.3)
    c2 = schedule(c, 3, "2026-01-01")
    assert c2.ease >= 1.3


def test_ease_decreases_on_low_quality():
    c = Card(front="a", back="b", reps=2, interval=6.0, ease=2.5)
    c2 = schedule(c, 3, "2026-01-01")
    assert c2.ease < 2.5


def test_ease_increases_on_perfect():
    c = Card(front="a", back="b", reps=2, interval=6.0, ease=2.5)
    c2 = schedule(c, 5, "2026-01-01")
    assert c2.ease > 2.5


def test_is_due():
    c = Card(front="a", back="b", due="2026-01-01")
    assert is_due(c, "2026-01-01")
    assert is_due(c, "2026-01-02")
    assert not is_due(c, "2025-12-31")


def test_invalid_quality():
    c = Card(front="a", back="b")
    try:
        schedule(c, 6, "2026-01-01")
        assert False, "should raise"
    except ValueError:
        pass


def test_does_not_mutate_input():
    c = Card(front="a", back="b")
    _ = schedule(c, 4, "2026-01-01")
    assert c.reps == 0
    assert c.interval == 0.0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
