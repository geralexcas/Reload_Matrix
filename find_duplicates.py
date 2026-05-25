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
    
    # Check SI- duplicates
    cur.execute("""
        SELECT reference, COUNT(*) 
        FROM journal_entries 
        WHERE reference LIKE 'SI-%' 
        GROUP BY reference 
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    
    for ref, count in duplicates:
        print(f"Duplicates for {ref} ({count}):")
        cur.execute("SELECT id, description FROM journal_entries WHERE reference = %s ORDER BY id", (ref,))
        for row in cur.fetchall():
            print(f"  - ID: {row[0]}, Desc: {row[1]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
