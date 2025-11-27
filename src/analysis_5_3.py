# ==========================================================
# analysis_5_3_gemini.py
# SME Growth Gap Analysis
# ==========================================================

import google.generativeai as genai
from analysis_queries import query_to_df

# ----------------------------------------------------------
# 0) Configure Gemini API
# ----------------------------------------------------------
genai.configure(api_key="AIzaSyB3lOs8_0YL8Xzux_Qac_5WbgaMoeRUhzs")

# เลือกโมเดลที่รองรับ generate_content() บนระบบของผู้ใช้
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)


# ----------------------------------------------------------
# 1) ดึงรายการประเภทธุรกิจทั้งหมด (TSIC2_DETAIL)
# ----------------------------------------------------------
def get_business_types():
    sql = """
        SELECT DISTINCT tsic2_detail
        FROM sme_detail
        ORDER BY tsic2_detail;
    """
    return query_to_df(sql)


# ----------------------------------------------------------
# 2) Manual Mode — ให้ผู้ใช้เลือก Type เอง
# ----------------------------------------------------------
def ask_business_type():
    df = get_business_types()

    while True:
        print("\n===== Search Business Types =====")
        print("พิมพ์คำค้น (เช่น 'ส่ง', 'ซ่อม', 'อาหาร') หรือกด Enter เพื่อแสดงทั้งหมด")

        keyword = input("Search: ").strip()

        if keyword == "":
            filtered = df
        else:
            filtered = df[df["tsic2_detail"].str.contains(keyword, case=False, na=False)]

        if filtered.empty:
            print("\n❗ ไม่พบผลลัพธ์ ลองคำอื่นอีกครั้งค่ะ\n")
            continue

        print("\nผลลัพธ์ที่พบ:\n")
        for i in range(len(filtered)):
            print(f"{i+1}) {filtered.iloc[i]['tsic2_detail']}")

        try:
            choice = int(input("\nEnter number: "))
            if 1 <= choice <= len(filtered):
                tsic2 = filtered.iloc[choice-1]["tsic2_detail"]
                print(f"\nYou selected: {tsic2}\n")
                return tsic2
            else:
                print("❗ ตัวเลขไม่ถูกต้อง ลองใหม่อีกครั้งค่ะ\n")
        except:
            print("❗ กรุณาพิมพ์เป็นตัวเลขค่ะ\n")



# ----------------------------------------------------------
# 3) Core Query — คำนวณ Growth Gap (เฉลี่ยรายปีจริง)
# ----------------------------------------------------------
def find_high_potential_gap(tsic2):
    sql = """
        SELECT 
            y.province,
            AVG(y.year_sme) AS avg_sme,   -- ค่า SME เฉลี่ยรายปี (Correct Logic)
            g.population_thousand,
            g.gpp_per_capita,
            (g.population_thousand * g.gpp_per_capita) AS economic_value,
            
            CASE 
                WHEN AVG(y.year_sme) > 0 THEN
                    (g.population_thousand * g.gpp_per_capita) / AVG(y.year_sme)
                ELSE NULL
            END AS growth_gap

        FROM (
            -- รวม SME รายปี (ถ้าปีหนึ่งมีหลายแถว จะ SUM ให้เป็นปีละ 1 ค่า)
            SELECT 
                province,
                year,
                SUM(number_sme) AS year_sme
            FROM sme_detail
            WHERE tsic2_detail = %s
            GROUP BY province, year
        ) AS y

        JOIN gpp_data g
            ON y.province = g.province

        GROUP BY 
            y.province, 
            g.population_thousand, 
            g.gpp_per_capita
        
        ORDER BY growth_gap DESC
        LIMIT 10;
    """
    return query_to_df(sql, (tsic2,))


# ----------------------------------------------------------
# 4) Summary — จังหวัดที่เหมาะที่สุด (เวอร์ชันใหม่)
# ----------------------------------------------------------
def summarize_gap_result(tsic2, df):
    if df.empty:
        return f"\n❗ No data found for Business Type: {tsic2}"

    top = df.iloc[0]

    province = top["province"]
    avg_sme = round(top["avg_sme"], 2)
    gap = round(top["growth_gap"], 2)
    pop = top["population_thousand"]
    gpp = top["gpp_per_capita"]
    eco_val = int(pop * gpp)

    return f"""
============================================================
📌 Recommendation for Business Type: {tsic2}
============================================================
จังหวัดที่เหมาะที่สุด:
➡️  **{province}**

เหตุผลหลัก:
- Demand สูง (ประชากร × GPP = {eco_val:,})
- จำนวนคู่แข่งเฉลี่ยต่อปี = {avg_sme} ราย  
- Growth Gap = **{gap:,}**

Growth Gap คือ “ดัชนีช่องว่างตลาด”  
ที่ใช้วัดว่า **ตลาดใหญ่แค่ไหนเมื่อเทียบกับจำนวนผู้เล่นจริงในแต่ละปี**

สูตรที่ใช้:
   (ประชากร × รายได้ต่อหัว) ÷ SME เฉลี่ยรายปี


💡 สรุปเชิงวิเคราะห์:
ธุรกิจประเภท "{tsic2}" มีโอกาสเติบโตสูงมากในจังหวัด **{province}**  
เพราะขนาดตลาดสูงเมื่อเทียบกับจำนวนคู่แข่งเฉลี่ยต่อปี ทำให้ยังมีช่องว่างตลาดเหลืออีกมาก
============================================================
"""


# ----------------------------------------------------------
# 5) AI Province Recommendation (เวอร์ชันใหม่ — Deep Insight)
# ----------------------------------------------------------
def ai_recommend_province(tsic2, top5_df):
    prompt = f"""
    You are a senior Thai SME market analyst with access to deep contextual knowledge.
    Analyze both:
    - The data table provided below (Growth Gap metrics)
    - General real-world knowledge about each province (economy, tourism, logistics, population behavior, SME ecosystem)

    Business Type: {tsic2}

    Below are the TOP 5 provinces with the highest Growth Gap:

    {top5_df.to_string(index=False)}

    Your tasks:
    1) เลือกจังหวัดเดียวที่เหมาะสมที่สุด (อิงข้อมูลจากตารางเป็นหลัก + เสริมด้วยข้อมูลทั่วไปของจังหวัด)
    2) ให้เหตุผลแบบ Manager Summary (3–4 ประโยค) รวมทั้ง insight ที่อาจไม่ได้อยู่ในตาราง เช่น:
       - จุดเด่นเศรษฐกิจ
       - ภูมิศาสตร์
       - แหล่งท่องเที่ยวหลัก
       - อุตสาหกรรมที่เกี่ยวข้อง
       - ความพร้อมด้านแรงงาน/โครงสร้างพื้นฐาน
    3) ระบุจุดขายของจังหวัดจำนวน 3 ข้อ (short bullet points)
    4) ข้อควรระวัง 1–2 ข้อ (risk factors)
    5) ข้อแนะนำเชิงกลยุทธ์ 1–2 ข้อ (strategic suggestions)
    6) ปิดท้ายด้วยประโยคสรุป (1 ประโยค)
    7) ห้ามใช้ตัวหนา หรือสัญลักษณ์ ** ใดๆ

    Output format (สำคัญมาก):
    จังหวัดที่แนะนำ: <ชื่อจังหวัด>

    เหตุผลแบบสรุป:
    - <ประโยคสั้น>
    - <ประโยคสั้น>
    - <ประโยคสั้น>

    จุดขายของจังหวัด:
    1) <จุดขาย 1>
    2) <จุดขาย 2>
    3) <จุดขาย 3>

    ข้อควรระวัง:
    - <ข้อควรระวัง 1>
    - <ข้อควรระวัง 2>

    ข้อแนะนำเชิงกลยุทธ์:
    - <คำแนะนำ 1>
    - <คำแนะนำ 2>

    สรุปท้าย:
    <1 ประโยค>
    """

    response = model.generate_content(prompt)
    return response.text.strip()




# ----------------------------------------------------------
# 6) AI Auto Recommendation Workflow (ใหม่)
# ----------------------------------------------------------
def auto_find_best_province():
    print("\n=== 🤖 AI Recommendation Mode ===")

    # ผู้ใช้เลือกประเภทธุรกิจเอง
    tsic2 = ask_business_type()
    print(f"\n📌 Selected Business Type: {tsic2}\n")

    # คำนวณช่องว่างตลาด
    df = find_high_potential_gap(tsic2)

    if df.empty:
        print("❗ Data not found for this business type.")
        return

    # แสดง Top 10
    print("\nTop 10 Provinces with Highest Growth Gap:")
    print(df)

    # ส่งแค่ Top 5 ให้ AI วิเคราะห์ให้ละเอียด
    top5 = df.head(5)
    print("\nSending Top 5 to Gemini for recommendation...\n")

    ai_summary = ai_recommend_province(tsic2, top5)

    print("\n=========== 🧠 Gemini Recommendation ===========")
    print(ai_summary)
    print("================================================\n")

    return df


# ----------------------------------------------------------
# 7) Manual Workflow
# ----------------------------------------------------------
def run_5_3():
    print("\n=== Manual Mode: SME Growth Gap Analysis ===")

    tsic2 = ask_business_type()
    df = find_high_potential_gap(tsic2)

    print("\nTop 10 Provinces:")
    print(df)

    summary = summarize_gap_result(tsic2, df)
    print(summary)


# ----------------------------------------------------------
# 8) Main Menu
# ----------------------------------------------------------
def menu():
    print("\n===== SME Analytics Menu =====")
    print("1) Manual Mode (เลือกหมวดเอง)")
    print("2) AI Auto Recommendation (Gemini)")
    print("0) Exit")

    choice = input("\nEnter choice: ")

    if choice == "1":
        run_5_3()
    elif choice == "2":
        auto_find_best_province()
    elif choice == "0":
        print("\nBye!")
    else:
        print("Invalid choice")


# ----------------------------------------------------------
# 9) Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    menu()
