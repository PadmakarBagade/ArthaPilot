import os
import pandas as pd
import pymysql

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "berka")
os.makedirs(OUT, exist_ok=True)

conn = pymysql.connect(
    host="relational.fel.cvut.cz",
    port=3306,
    user="guest",
    password="ctu-relational",
    database="financial",
)

with conn.cursor() as cur:
    cur.execute("SHOW TABLES")
    tables = [r[0] for r in cur.fetchall()]
print("Tables found:", tables)

for t in tables:
    df = pd.read_sql(f"SELECT * FROM `{t}`", conn)
    df.to_csv(os.path.join(OUT, f"{t}.csv"), index=False)
    print(f"Saved {t}.csv  ({len(df)} rows)")

conn.close()
print("Done.")