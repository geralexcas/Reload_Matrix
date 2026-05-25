import subprocess
import sys

try:
    import psycopg2
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

def main():
    conn = psycopg2.connect(
        dbname="reload_matrix",
        user="reload_user",
        password="reload_password",
        host="localhost",
        port="5434"
    )
    cur = conn.cursor()
    
    cur.execute("SELECT id, entry_date, description FROM journal_entries WHERE reference = 'SI-000014'")
    rows = cur.fetchall()
    print(f"Found {len(rows)} entries for SI-000014:")
    for r in rows:
        print(f"ID: {r[0]}, Date: {r[1]}, Description: {r[2]}")
        
    cur.execute("SELECT id, entry_date, description FROM journal_entries WHERE reference = 'SI-000031'")
    rows = cur.fetchall()
    print(f"Found {len(rows)} entries for SI-000031:")
    for r in rows:
        print(f"ID: {r[0]}, Date: {r[1]}, Description: {r[2]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
