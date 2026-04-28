import sqlite3

def update_db():
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE hackathons ADD COLUMN registration_closed INTEGER DEFAULT 0')
        print("Column 'registration_closed' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'registration_closed' already exists.")
        else:
            print(f"Error: {e}")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_db()
