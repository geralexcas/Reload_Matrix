import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

engine = create_engine('postgresql://user:password@db:5432/business_db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Journal entries with SI- prefix:")
res = db.execute(text("SELECT id, reference, entry_date FROM journal_entries WHERE reference LIKE 'SI-%' ORDER BY reference;"))
for row in res:
    print(f"id: {row.id}, reference: {row.reference}, entry_date: {row.entry_date}")

print("\nDuplicates in DB?")
res3 = db.execute(text("SELECT reference, count(*) FROM journal_entries WHERE reference LIKE 'SI-%' GROUP BY reference HAVING count(*) > 1;"))
for row in res3:
    print(f"reference: {row.reference}, count: {row.count}")

