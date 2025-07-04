import sqlite3
from sqlite3 import Error

def create_connection():
    """Создаём подключение к SQLite."""
    conn = None
    try:
        conn = sqlite3.connect('carbon_footprint.db')
        return conn
    except Error as e:
        print(e)
    return conn

def init_db():
    """Создаём таблицу для хранения результатов."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transport_km REAL NOT NULL,
                    flight_hours REAL NOT NULL,
                    diet_type TEXT NOT NULL,
                    energy_kwh REAL NOT NULL,
                    total_co2 REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()