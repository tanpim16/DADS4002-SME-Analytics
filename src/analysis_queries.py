from db_connection import get_connection
import pandas as pd

def query_to_df(sql, params=None):
    conn = get_connection()
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df


from db_connection import get_connection
import pandas as pd

# ---------------------------
# 5.1 Best province
# ---------------------------
def get_best_province_for_business(tsic5):
    conn = get_connection()
    query = f"""
        SELECT province,
               SUM(number_sme) AS total_sme,
               SUM(gpp_per_capita) AS gpp_score
        FROM sme_detail AS s
        JOIN gpp_data AS g ON s.province = g.province
        WHERE s.tsic5 = '{tsic5}'
        GROUP BY province
        ORDER BY gpp_score DESC
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------------------
# 5.2 Compare two provinces
# ---------------------------
def compare_two_provinces(tsic5, province_a, province_b):
    conn = get_connection()
    query = f"""
        SELECT province,
               SUM(number_sme) AS total_sme,
               SUM(gpp_per_capita) AS gpp_score
        FROM sme_detail AS s
        JOIN gpp_data AS g ON s.province = g.province
        WHERE s.tsic5 = '{tsic5}'
          AND s.province IN ('{province_a}', '{province_b}')
        GROUP BY province;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------------------
# 5.3 High potential gap
# ---------------------------
def find_high_potential_gap(tsic5):
    conn = get_connection()
    query = f"""
        SELECT s.province,
               SUM(number_sme) AS competitors,
               g.gpp_total_million AS market_size,
               (g.gpp_total_million / NULLIF(SUM(number_sme),0)) AS gap_score
        FROM sme_detail AS s
        JOIN gpp_data AS g ON s.province = g.province
        WHERE s.tsic5 = '{tsic5}'
        GROUP BY s.province, g.gpp_total_million
        ORDER BY gap_score DESC
        LIMIT 10;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df



