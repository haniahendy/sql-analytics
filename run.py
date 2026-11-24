from sqlan.queries import FUNNEL, RETENTION_D7, WEEKLY_SIGNUPS_RUNNING, build_db, run

con = build_db()
for name, q in [("funnel", FUNNEL), ("retention", RETENTION_D7), ("weekly", WEEKLY_SIGNUPS_RUNNING)]:
    print(name, run(con, q)[:6])
