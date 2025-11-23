# ==========================================================
# analysis_5_1.py — Market Overview Analysis
# ==========================================================

from analysis_queries import query_to_df

# ----------------------------------------------------------
# 1) Max Business Size (Micro/S/M/L)
# ----------------------------------------------------------
def get_max_business_size():
    """
    Find which business size category has the highest total across all provinces
    """
    sql = """
        SELECT 
            business_size,
            SUM(number_sme) AS total_count,
            ROUND(SUM(number_sme) * 100.0 / (SELECT SUM(number_sme) FROM sme_detail), 2) AS proportion_pct
        FROM sme_detail
        WHERE business_size IN ('Micro', 'S', 'M', 'L')
        GROUP BY business_size
        ORDER BY total_count DESC;
    """
    
    return query_to_df(sql)

# ----------------------------------------------------------
# 2) Min Business Size
# ----------------------------------------------------------
def get_min_business_size():
    """
    Find which business size category has the lowest total across all provinces
    """
    sql = """
        SELECT 
            business_size,
            SUM(number_sme) AS total_count,
            ROUND(SUM(number_sme) * 100.0 / (SELECT SUM(number_sme) FROM sme_detail), 2) AS proportion_pct
        FROM sme_detail
        WHERE business_size IN ('Micro', 'S', 'M', 'L')
        GROUP BY business_size
        ORDER BY total_count ASC;
    """
    
    return query_to_df(sql)

# ----------------------------------------------------------
# 3) Max Frequency of Business Type
# ----------------------------------------------------------
def get_max_business_type_frequency():
    """
    Find which business type has the highest total number of SMEs (sum across all provinces)
    """
    sql = """
        SELECT 
            tsic2_detail,
            SUM(number_sme) AS total_sme
        FROM sme_detail
        GROUP BY tsic2_detail
        ORDER BY total_sme DESC
        LIMIT 1;
    """
    
    return query_to_df(sql)

# ----------------------------------------------------------
# 4) Min Frequency of Business Type
# ----------------------------------------------------------
def get_min_business_type_frequency():
    """
    Find which business type has the lowest total number of SMEs (sum across all provinces)
    """
    sql = """
        SELECT 
            tsic2_detail,
            SUM(number_sme) AS total_sme
        FROM sme_detail
        GROUP BY tsic2_detail
        ORDER BY total_sme ASC
        LIMIT 1;
    """
    
    return query_to_df(sql)

# ----------------------------------------------------------
# 5) Province with Highest SME-to-Population Ratio
# ----------------------------------------------------------
def get_highest_sme_density():
    """
    Find province with highest SME-to-Population Ratio (total SMEs / total population)
    """
    sql = """
        SELECT 
            s.province,
            SUM(s.number_sme) AS total_sme,
            g.population_thousand,
            ROUND(SUM(s.number_sme) / NULLIF(g.population_thousand, 0), 2) AS sme_to_population_ratio
        FROM sme_detail s
        JOIN gpp_data g ON s.province = g.province
        GROUP BY s.province, g.population_thousand
        ORDER BY sme_to_population_ratio DESC
        LIMIT 1;
    """
    
    return query_to_df(sql)

# ----------------------------------------------------------
# 6) Province with Lowest SME-to-Population Ratio
# ----------------------------------------------------------
def get_lowest_sme_density():
    """
    Find province with lowest SME-to-Population Ratio (total SMEs / total population)
    """
    sql = """
        SELECT 
            s.province,
            SUM(s.number_sme) AS total_sme,
            g.population_thousand,
            ROUND(SUM(s.number_sme) / NULLIF(g.population_thousand, 0), 2) AS sme_to_population_ratio
        FROM sme_detail s
        JOIN gpp_data g ON s.province = g.province
        GROUP BY s.province, g.population_thousand
        HAVING sme_to_population_ratio > 0
        ORDER BY sme_to_population_ratio ASC
        LIMIT 1;
    """
    
    return query_to_df(sql)

# ----------------------------------------------------------
# MAIN FUNCTION - Market Overview
# ----------------------------------------------------------
def run_5_1():
    print("\n=== Market Overview Analysis (Task 5.1) ===\n")
    
    # 1) Max Business Size
    print("📊 1. Max Business Size (Highest Proportion)")
    print("-" * 50)
    df_max_size = get_max_business_size()
    if not df_max_size.empty:
        max_row = df_max_size.iloc[0]
        total_all = df_max_size['total_count'].sum()
        proportion = (max_row['total_count'] / total_all * 100) if total_all > 0 else 0
        print(f"Business Size: {max_row['business_size']}")
        print(f"Total Count: {int(max_row['total_count']):,}")
        print(f"Proportion: {proportion:.2f}%")
        print("\nAll Business Sizes:")
        print(df_max_size)
    else:
        print("❗ No data found")
    print("\n")
    
    # 2) Min Business Size
    print("📊 2. Min Business Size (Lowest Proportion)")
    print("-" * 50)
    df_min_size = get_min_business_size()
    if not df_min_size.empty:
        min_row = df_min_size.iloc[0]
        total_all = df_min_size['total_count'].sum()
        proportion = (min_row['total_count'] / total_all * 100) if total_all > 0 else 0
        print(f"Business Size: {min_row['business_size']}")
        print(f"Total Count: {int(min_row['total_count']):,}")
        print(f"Proportion: {proportion:.2f}%")
    else:
        print("❗ No data found")
    print("\n")
    
    # 3) Max Frequency Business Type
    print("📊 3. Max Frequency Business Type")
    print("-" * 50)
    df_max_freq = get_max_business_type_frequency()
    if not df_max_freq.empty:
        row = df_max_freq.iloc[0]
        print(f"Business Type: {row['tsic2_detail']}")
        print(f"Total SMEs: {int(row['total_sme']):,}")
    else:
        print("❗ No data found")
    print("\n")
    
    # 4) Min Frequency Business Type
    print("📊 4. Min Frequency Business Type")
    print("-" * 50)
    df_min_freq = get_min_business_type_frequency()
    if not df_min_freq.empty:
        row = df_min_freq.iloc[0]
        print(f"Business Type: {row['tsic2_detail']}")
        print(f"Total SMEs: {int(row['total_sme']):,}")
    else:
        print("❗ No data found")
    print("\n")
    
    # 5) Highest SME-to-Population Ratio Province
    print("📊 5. Province with Highest SME-to-Population Ratio")
    print("-" * 50)
    df_high_density = get_highest_sme_density()
    if not df_high_density.empty:
        row = df_high_density.iloc[0]
        print(f"Province: {row['province']}")
        print(f"Total SMEs: {int(row['total_sme']):,}")
        print(f"Population: {row['population_thousand']:.1f} thousand")
        print(f"SME-to-Population Ratio: {row['sme_to_population_ratio']:.2f} SMEs per 1,000 people")
    else:
        print("❗ No data found")
    print("\n")
    
    # 6) Lowest SME-to-Population Ratio Province
    print("📊 6. Province with Lowest SME-to-Population Ratio")
    print("-" * 50)
    df_low_density = get_lowest_sme_density()
    if not df_low_density.empty:
        row = df_low_density.iloc[0]
        print(f"Province: {row['province']}")
        print(f"Total SMEs: {int(row['total_sme']):,}")
        print(f"Population: {row['population_thousand']:.1f} thousand")
        print(f"SME-to-Population Ratio: {row['sme_to_population_ratio']:.2f} SMEs per 1,000 people")
    else:
        print("❗ No data found")
    print("\n")
    
    print("=" * 50)
    print("✅ Market Overview Analysis Complete!")
    print("=" * 50)

# ----------------------------------------------------------
# Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    run_5_1()

