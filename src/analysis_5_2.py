# ==========================================================
# analysis_5_2.py — Compare 2 Provinces (Task 5.2) — FINAL
# With Business Type Search (เหมือน 5.3)
# ==========================================================

from analysis_queries import query_to_df

# ----------------------------------------------------------
# ดึงรายการประเภทธุรกิจทั้งหมด (TSIC2_DETAIL)
# ----------------------------------------------------------
def get_business_types():
    sql = """
        SELECT DISTINCT tsic2_detail
        FROM sme_detail
        ORDER BY tsic2_detail;
    """
    return query_to_df(sql)


# ----------------------------------------------------------
# Search + เลือกประเภทธุรกิจ (เหมือน 5.3)
# ----------------------------------------------------------
def choose_business_type():
    df = get_business_types()

    while True:
        print("\n===== Search Business Types =====")
        print("พิมพ์คำค้น (เช่น 'ส่ง', 'ซ่อม', 'อาหาร') หรือกด Enter เพื่อดูทั้งหมด")

        keyword = input("Search: ").strip()

        if keyword == "":
            filtered = df
        else:
            filtered = df[df["tsic2_detail"].str.contains(keyword, case=False, na=False)]

        if filtered.empty:
            print("\n❗ ไม่พบผลลัพธ์ ลองคำอื่นอีกครั้ง\n")
            continue

        print("\n--- Business Types Found ---")
        for i in range(len(filtered)):
            print(f"{i+1}) {filtered.iloc[i]['tsic2_detail']}")

        try:
            choice = int(input("\nเลือกหมายเลข: "))
            if 1 <= choice <= len(filtered):
                tsic2 = filtered.iloc[choice-1]["tsic2_detail"]
                print(f"\n✔ Selected Business Type: {tsic2}\n")
                return tsic2
        except:
            print("❗ กรุณาใส่หมายเลขให้ถูกต้อง\n")


# ----------------------------------------------------------
# Query province comparison data
# ----------------------------------------------------------
def compare_two_provinces(tsic2, provA, provB):
    sql = """
        SELECT 
            s.province,
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
          AND s.province IN (%s, %s)
        GROUP BY s.province, g.population_thousand, g.gpp_per_capita
    """
    return query_to_df(sql, (tsic2, provA, provB))


# ----------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------
def run_5_2():
    print("\n=== Compare Two Provinces (Task 5.2) ===")

    # 1) เลือกประเภทธุรกิจ (มี Search)
    tsic2 = choose_business_type()

    # 2) รับชื่อจังหวัด
    A = input("Enter Province A: ").strip()
    B = input("Enter Province B: ").strip()

    # 3) Query
    df = compare_two_provinces(tsic2, A, B)

    print("\n=== Data Table ===")
    print(df)

    if len(df) < 2:
        print("\n❗ ข้อมูลไม่ครบสองจังหวัด")
        return

    rowA = df.iloc[0]
    rowB = df.iloc[1]

    print("\n")
    print("📌 Business Type:", tsic2)
    print("📍 Comparison:", A, "VS", B)
    print("====================================================")

    def print_summary(name, row):
        eco = int(row["economic_value"])
        print(f"\n{name}:")
        print(f"- Demand = {eco:,}")
        print(f"- Competitors = {int(row['total_sme'])}")
        print(f"- Growth Gap = {row['growth_gap']:.2f}")

    print_summary(A, rowA)
    print_summary(B, rowB)

    # 4) Recommendation
    better = A if rowA["growth_gap"] > rowB["growth_gap"] else B
    print("\n💡 **Recommended:", better, "** (Growth Gap สูงกว่า)")
    print("====================================================\n")
