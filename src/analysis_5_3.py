# ==========================================================
# analysis_5_3_gemini.py
# SME Growth Gap Analysis
# ==========================================================

import google.generativeai as genai
from analysis_queries import query_to_df

# ----------------------------------------------------------
# 0) Configure Gemini API
# ----------------------------------------------------------
genai.configure(api_key="AIzaSyDdQG8PncklU0ZChl3oeN2brk8vq1Hz4ho")

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
# 5) AI Mode — ให้ Gemini เลือกประเภทธุรกิจให้
# ----------------------------------------------------------
def ai_select_business_type():
    sql = """
        SELECT tsic2_detail, AVG(number_sme) AS avg_sme
        FROM sme_detail
        GROUP BY tsic2_detail
        HAVING AVG(number_sme) > 0
        ORDER BY avg_sme ASC
        LIMIT 20;
    """
    df = query_to_df(sql)

    prompt = f"""
    You are an expert in Thai SME market analysis.

    Below is the average SME count (3-year average) for each business type:

    {df.to_string()}

    Please choose ONE tsic2_detail with:
    - Low competition (few SMEs on average)
    - High opportunity to enter
    - High potential demand

    Reply with ONLY the tsic2_detail.
    """

    response = model.generate_content(prompt)
    return response.text.strip()


# ----------------------------------------------------------
# 6) AI Auto Recommendation Workflow
# ----------------------------------------------------------
def auto_find_best_province():
    print("\n=== 🤖 AI Auto Recommendation Mode ===")

    ai_tsic2 = ai_select_business_type()
    print(f"\n🤖 Gemini selected: {ai_tsic2}")

    df = find_high_potential_gap(ai_tsic2)

    print("\nTop 10 Provinces with Highest Growth Gap:")
    print(df)

    summary = summarize_gap_result(ai_tsic2, df)
    print(summary)

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
