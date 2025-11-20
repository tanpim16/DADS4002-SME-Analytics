import mysql.connector
import csv

# ----------------------------------------------------
# 1) Connect Database
# ----------------------------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Tanpim16!",        # ถ้ามีรหัสผ่าน MySQL ให้ใส่ตรงนี้
    database="sme_analysis"
)

cursor = conn.cursor()

# ----------------------------------------------------
# 2) Path to CSV (แก้ตามตำแหน่งไฟล์ของ Tanya)
# ----------------------------------------------------
csv_path = "/Users/tanpimm/Desktop/DADS/Python 4002/DADS4002_Final/data/job_vacancy.csv"

# ----------------------------------------------------
# 3) Read CSV and Insert into Database
# ----------------------------------------------------
with open(csv_path, newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # skip header

    for row in reader:
        province = row[0].strip()
        avg_job_raw = row[1].strip()

        # ลบ comma ออกจากตัวเลข เช่น "13,792" → "13792"
        avg_job_raw = avg_job_raw.replace(",", "")

        # แปลงเป็น int
        try:
            avg_job = int(avg_job_raw)
        except:
            print(f"⚠️  Cannot convert to number: {row}")
            continue

        sql = """
            INSERT INTO job_vacancy (province, avg_job_vacancy)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE avg_job_vacancy = VALUES(avg_job_vacancy)
        """

        cursor.execute(sql, (province, avg_job))

# ----------------------------------------------------
# 4) Save changes + Close connection
# ----------------------------------------------------
conn.commit()
cursor.close()
conn.close()

print("🎉 Import job_vacancy.csv completed successfully!")