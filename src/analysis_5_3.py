from analysis_queries import query_to_df

# ------------------------------------------------
# 1) ดึงรายชื่อประเภทธุรกิจ (TSIC2_DETAIL)
# ------------------------------------------------
def get_business_types():
    sql = """
    SELECT DISTINCT tsic2_detail
    FROM sme_detail
    ORDER BY tsic2_detail;
    """
    return query_to_df(sql)


# ------------------------------------------------
# 2) ขอ user เลือกประเภทธุรกิจ (TSIC2_DETAIL)
# ------------------------------------------------
def ask_business_type():
    df = get_business_types()
    print("\nAvailable Business Types (TSIC2_DETAIL):")
    print(df)

    tsic2 = input("\nEnter Business Type (TSIC2_DETAIL): ")
    return tsic2


# ------------------------------------------------
# 3) Query คำนวณ Growth Gap โดยใช้ TSIC2_DETAIL
# ------------------------------------------------
def find_high_potential_gap(tsic2):
    sql = """
    SELECT 
        s.province AS province,
        SUM(s.number_sme) AS total_sme,
        g.population_thousand,
        g.gpp_per_capita,

        (g.population_thousand * g.gpp_per_capita) AS economic_value,

        CASE 
            WHEN SUM(s.number_sme) > 0 THEN 
                (g.population_thousand * g.gpp_per_capita) / SUM(s.number_sme)
            ELSE NULL
        END AS growth_gap

    FROM sme_detail s
    JOIN gpp_data g
        ON s.province = g.province
    WHERE s.tsic2_detail = %s
    GROUP BY s.province, g.population_thousand, g.gpp_per_capita
    ORDER BY growth_gap DESC
    LIMIT 10;
    """

    return query_to_df(sql, (tsic2,))


# ------------------------------------------------
# 4) สรุปผลสำหรับจังหวัดที่ “ควรเปิดกิจการที่สุด”
# ------------------------------------------------
def summarize_gap_result(tsic2, df):
    if df.empty:
        return f"\n❗ No data found for Business Type {tsic2}"

    top = df.iloc[0]

    province = top["province"]
    gap = round(top["growth_gap"], 2)
    sme = int(top["total_sme"])
    pop = top["population_thousand"]
    gpp = top["gpp_per_capita"]
    eco_val = int(pop * gpp)

    summary = f"""
============================================================
📌 Recommendation for Business Type: {tsic2}
============================================================

จังหวัดที่เหมาะที่สุด:
➡️  **{province}**

เหตุผล:
- Demand สูง (ประชากร × GPP = {eco_val:,})
- คู่แข่ง (SME ประเภทนี้) ยังน้อย ({sme} ราย)
- Growth Gap = **{gap}** (ยิ่งสูง → ช่องว่างการเติบโตสูง)

💡 ข้อสรุปสำคัญ:
ธุรกิจประเภท {tsic2} เหมาะอย่างยิ่งในการไปเปิดที่ **{province}**
เพราะ Demand สูง แต่คู่แข่งยังน้อย → มีโอกาสครองตลาดก่อนรายอื่น

============================================================
"""
    return summary


# ------------------------------------------------
# 5) ฟังก์ชันหลักของข้อ 5.3
# ------------------------------------------------
def run_5_3():
    print("\n=== SME Growth Gap Analysis (Task 5.3 using TSIC2_DETAIL) ===")

    tsic2 = ask_business_type()
    df = find_high_potential_gap(tsic2)

    print("\nTop 10 Provinces with Highest Growth Gap:")
    print(df)

    summary = summarize_gap_result(tsic2, df)
    print(summary)

    return df
