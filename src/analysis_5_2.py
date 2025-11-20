# ==========================================================
# analysis_5_2.py
# Task 5.2 — Compare Two Provinces for Business Potential
# ==========================================================

from analysis_queries import query_to_df


def compare_two_provinces(tsic2, province_a, province_b):
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
          AND s.province IN (%s, %s)
        GROUP BY s.province, g.population_thousand, g.gpp_per_capita;
    """

    return query_to_df(sql, (tsic2, province_a, province_b))


def summarize_compare(tsic2, df, province_a, province_b):

    row_a = df[df["province"] == province_a].iloc[0]
    row_b = df[df["province"] == province_b].iloc[0]

    better = province_a if row_a["growth_gap"] > row_b["growth_gap"] else province_b

    return f"""
============================================================
📌 Business Type: {tsic2}
📍 Comparison: {province_a}  VS  {province_b}
============================================================

{province_a}:
- Demand = {int(row_a['economic_value']):,}
- Competitors = {int(row_a['total_sme'])}
- Growth Gap = {row_a['growth_gap']:.2f}

{province_b}:
- Demand = {int(row_b['economic_value']):,}
- Competitors = {int(row_b['total_sme'])}
- Growth Gap = {row_b['growth_gap']:.2f}

➡️  **Recommended: {better}**
จังหวัดนี้มีศักยภาพสูงกว่า (Growth Gap สูงกว่า)
============================================================
"""


def run_5_2():
    print("\n=== Compare Two Provinces (Task 5.2) ===")

    tsic2 = input("Enter Business Type (TSIC2_DETAIL): ")
    province_a = input("Enter Province A: ")
    province_b = input("Enter Province B: ")

    df = compare_two_provinces(tsic2, province_a, province_b)

    print("\n--- Data Table ---")
    print(df)

    summary = summarize_compare(tsic2, df, province_a, province_b)
    print(summary)


# ----------------------------------------------------------
# 4) Run (for standalone execution)
# ----------------------------------------------------------
if __name__ == "__main__":
    run_5_2()
