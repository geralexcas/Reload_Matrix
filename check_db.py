import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.core.database import SessionLocal
from app.models.sql.accounting import JournalEntry

def main():
    db = SessionLocal()
    try:
        entries = db.query(JournalEntry).filter(JournalEntry.reference == 'SI-000014').all()
        print(f"Found {len(entries)} entries for SI-000014")
        for e in entries:
            print(f"ID: {e.id}, Date: {e.entry_date}, Description: {e.description}")
            
        entries31 = db.query(JournalEntry).filter(JournalEntry.reference == 'SI-000031').all()
        print(f"Found {len(entries31)} entries for SI-000031")
        for e in entries31:
            print(f"ID: {e.id}, Date: {e.entry_date}, Description: {e.description}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
