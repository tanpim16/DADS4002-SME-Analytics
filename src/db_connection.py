import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tanpim16!",
        database="sme_analysis"
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Connected to MySQL successfully!")
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
