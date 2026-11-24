"""SQL analytics on a small SQLite schema: window functions, cohort retention, funnel."""
import random
import sqlite3
from datetime import date, timedelta

SCHEMA = """
CREATE TABLE users(user_id INTEGER PRIMARY KEY, signup_date TEXT);
CREATE TABLE events(user_id INTEGER, event_date TEXT, event TEXT);
"""


def build_db(seed: int = 1, n_users: int = 300) -> sqlite3.Connection:
    rnd = random.Random(seed)
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA)
    start = date(2026, 1, 1)
    for uid in range(1, n_users + 1):
        signup = start + timedelta(days=rnd.randint(0, 59))
        con.execute("INSERT INTO users VALUES (?,?)", (uid, signup.isoformat()))
        con.execute("INSERT INTO events VALUES (?,?,?)", (uid, signup.isoformat(), "signup"))
        if rnd.random() < 0.6:
            con.execute("INSERT INTO events VALUES (?,?,?)", (uid, (signup + timedelta(days=1)).isoformat(), "activate"))
            if rnd.random() < 0.5:
                con.execute("INSERT INTO events VALUES (?,?,?)", (uid, (signup + timedelta(days=3)).isoformat(), "purchase"))
        for _ in range(rnd.randint(0, 3)):  # later activity for retention
            if rnd.random() < 0.5:
                con.execute("INSERT INTO events VALUES (?,?,?)",
                            (uid, (signup + timedelta(days=rnd.randint(7, 40))).isoformat(), "visit"))
    con.commit()
    return con


FUNNEL = """
SELECT event, COUNT(DISTINCT user_id) AS users
FROM events WHERE event IN ('signup','activate','purchase')
GROUP BY event ORDER BY users DESC
"""

WEEKLY_SIGNUPS_RUNNING = """
SELECT week, signups, SUM(signups) OVER (ORDER BY week) AS cumulative
FROM (SELECT strftime('%Y-%W', signup_date) AS week, COUNT(*) AS signups FROM users GROUP BY week)
ORDER BY week
"""

# share of each signup-month cohort that has any event 7+ days after signup
RETENTION_D7 = """
SELECT substr(u.signup_date,1,7) AS cohort,
       COUNT(*) AS users,
       ROUND(1.0 * SUM(EXISTS(
           SELECT 1 FROM events e
           WHERE e.user_id = u.user_id AND julianday(e.event_date) - julianday(u.signup_date) >= 7
       )) / COUNT(*), 3) AS retained_d7
FROM users u GROUP BY cohort ORDER BY cohort
"""


def run(con, sql):
    return con.execute(sql).fetchall()
