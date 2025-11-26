# =============================================================
# main.py — Full SME Analytics Management Program (FINAL)
# =============================================================

import mysql.connector
import os
from datetime import datetime

# เก็บข้อมูลล่าสุดที่ถูกลบ (สำหรับ Undo/Restore)
last_deleted = None


# -------------------------------------------------------------
# IMPORT ANALYSIS MODULES
# -------------------------------------------------------------
try:
    from analysis_5_1 import run_5_1
except:
    run_5_1 = None

try:
    from analysis_5_2 import run_5_2
except:
    run_5_2 = None

try:
    from analysis_5_3 import run_5_3, auto_find_best_province
except:
    run_5_3 = None
    auto_find_best_province = None


# -------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tanpim16!", 
        database="sme_analysis"
    )


# -------------------------------------------------------------
# LOG SYSTEM — เขียนลงไฟล์ logs/history.txt
# -------------------------------------------------------------
def log_message(message):
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "history.txt")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")


# -------------------------------------------------------------
# VIEW LOG FILES
# -------------------------------------------------------------
def view_logs():
    log_path = "logs/history.txt"

    print("\n===== SYSTEM LOGS =====\n")

    if not os.path.exists(log_path):
        print("No logs found.\n")
        return

    # อ่านและแสดงผลบน Terminal
    with open(log_path, "r", encoding="utf-8") as f:
        print(f.read())

    # เปิดไฟล์ใน TextEdit (สำหรับ macOS)
    try:
        os.system(f"open {log_path}")
        print("\n📄 Log file opened in TextEdit.\n")
    except:
        print("\n⚠ ไม่สามารถเปิดไฟล์อัตโนมัติได้\n")


# -------------------------------------------------------------
# CRUD — READ / UPDATE / DELETE job_vacancy
# -------------------------------------------------------------
def read_job_vacancy():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT province, avg_job_vacancy
        FROM job_vacancy
        ORDER BY avg_job_vacancy DESC;
    """)

    rows = cursor.fetchall()

    print("\n=== JOB VACANCY (ALL PROVINCES) ===")
    for p, v in rows:
        print(f"- {p}: {v}")
    print("====================================\n")

    log_message("READ: job_vacancy")

    cursor.close()
    conn.close()


def update_job_vacancy():
    province = input("\nจังหวัดที่ต้องการแก้ไข: ").strip()
    new_val = input("ค่า avg_job_vacancy ใหม่: ").strip()

    try:
        new_val = int(new_val.replace(",", ""))
    except:
        print("❌ กรุณาใส่เป็นตัวเลข")
        return

    conn = get_connection()
    cursor = conn.cursor()

    sql = "UPDATE job_vacancy SET avg_job_vacancy = %s WHERE province = %s"
    cursor.execute(sql, (new_val, province))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ อัปเดตสำเร็จ: {province} → {new_val}")
        log_message(f"UPDATE job_vacancy: {province} -> {new_val}")
    else:
        print("❗ ไม่พบจังหวัดนี้")

    cursor.close()
    conn.close()


def delete_job_vacancy():
    global last_deleted

    province = input("\nจังหวัดที่ต้องการลบ: ").strip()
    confirm = input(f"ยืนยันลบ {province}? (y/n): ").lower()

    if confirm != "y":
        print("🚫 ยกเลิกการลบ")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # ดึงข้อมูลก่อนลบ
    cursor.execute("SELECT avg_job_vacancy FROM job_vacancy WHERE province = %s", (province,))
    row = cursor.fetchone()

    if not row:
        print("❗ ไม่พบจังหวัดนี้")
        cursor.close()
        conn.close()
        return

    old_value = row[0]

    # ลบข้อมูล
    cursor.execute("DELETE FROM job_vacancy WHERE province = %s", (province,))
    conn.commit()

    print(f"🗑 ลบ {province} (value={old_value})")

    # เก็บข้อมูลล่าสุดที่ถูกลบ
    last_deleted = {"province": province, "value": old_value}

    log_message(f"DELETE job_vacancy: {province}, old_value={old_value}")

    cursor.close()
    conn.close()


# -------------------------------------------------------------
# RESTORE LAST DELETED (UNDO)
# -------------------------------------------------------------
def restore_last_deleted():
    global last_deleted

    if not last_deleted:
        print("\n❗ ไม่มีข้อมูลที่กู้คืนได้")
        return

    province = last_deleted["province"]
    value = last_deleted["value"]

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO job_vacancy (province, avg_job_vacancy)
        VALUES (%s, %s)
    """

    cursor.execute(sql, (province, value))
    conn.commit()

    print(f"\n♻️ กู้คืนข้อมูลสำเร็จ: {province} (value={value})")
    log_message(f"RESTORE job_vacancy: {province} -> {value}")

    last_deleted = None

    cursor.close()
    conn.close()


# -------------------------------------------------------------
# MAIN MENU LOOP
# -------------------------------------------------------------
def main_menu():
    while True:
        print("\n=========== SME ANALYTICS MAIN MENU ===========")
        print("1) Market Overview Analysis")
        print("2) Province Comparison")
        print("3) SME Growth Gap Analysis (Manual / AI)")
        print("----------------------------------")
        print("4) Read job vacancy")
        print("5) Update job vacancy")
        print("6) Delete job vacancy")
        print("7) Restore last deleted job vacancy")
        print("8) View system logs")
        print("----------------------------------")
        print("0) Exit")
        print("===============================================\n")

        ch = input("เลือกเมนู: ").strip()

        # -------------- Analysis Menu --------------
        if ch == "1":
            if run_5_1:
                run_5_1()
                log_message("Run Market Overview Analysis")
            else:
                print("❗ Market Overview Analysis ยังไม่พร้อม")

        elif ch == "2":
            if run_5_2:
                run_5_2()
                log_message("Run Province Comparison")
            else:
                print("❗ Province Comparison ยังไม่พร้อม")

        elif ch == "3":
            print("\n=== SME Growth Gap Analysis ===")
            print("1) Manual Mode")
            print("2) AI Recommendation (Gemini)")

            sub = input("เลือกโหมด: ").strip()

            if sub == "1":
                run_5_3()
                log_message("Run SME Growth Gap Analysis (Manual)")

            elif sub == "2":
                auto_find_best_province()
                log_message("Run SME Growth Gap Analysis (AI)")

            else:
                print("❗ เมนูไม่ถูกต้อง")

        # -------------- CRUD Menu --------------
        elif ch == "4":
            read_job_vacancy()

        elif ch == "5":
            update_job_vacancy()

        elif ch == "6":
            delete_job_vacancy()

        elif ch == "7":
            restore_last_deleted()

        elif ch == "8":
            view_logs()

        # Exit
        elif ch == "0":
            print("\n ออกจากโปรแกรม")
            break

        else:
            print("❗ เมนูไม่ถูกต้อง ลองใหม่")


# -------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------
if __name__ == "__main__":
    main_menu()
