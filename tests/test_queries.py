import sqlite3

from sqlan.queries import FUNNEL, RETENTION_D7, WEEKLY_SIGNUPS_RUNNING, build_db, run


def test_funnel_is_monotonic_and_signup_is_everyone():
    rows = dict(run(build_db(), FUNNEL))
    assert rows["signup"] == 300
    assert rows["signup"] >= rows["activate"] >= rows["purchase"] > 0


def test_cumulative_ends_at_total_users():
    rows = run(build_db(), WEEKLY_SIGNUPS_RUNNING)
    assert rows[-1][2] == 300
    assert all(b[2] >= a[2] for a, b in zip(rows, rows[1:]))


def test_retention_on_hand_built_data():
    con = sqlite3.connect(":memory:")
    con.executescript("CREATE TABLE users(user_id INTEGER, signup_date TEXT);"
                      "CREATE TABLE events(user_id INTEGER, event_date TEXT, event TEXT);"
                      "INSERT INTO users VALUES (1,'2026-01-01'),(2,'2026-01-02');"
                      "INSERT INTO events VALUES (1,'2026-01-10','visit'),(2,'2026-01-03','visit');")
    assert run(con, RETENTION_D7) == [("2026-01", 2, 0.5)]


def test_retention_rates_between_0_and_1():
    for _, n, r in run(build_db(), RETENTION_D7):
        assert n > 0 and 0 <= r <= 1
