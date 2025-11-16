def find_high_potential_gap(tsic5):
    sql = """
    SELECT 
        s.province,
        SUM(s.number_sme) AS total_sme,
        g.population_thousand,
        g.gpp_per_capita,
        (g.gpp_per_capita * g.population_thousand) / NULLIF(SUM(s.number_sme),0) AS growth_gap
    FROM sme_detail s
    JOIN gpp_data g
        ON s.province = g.province
    WHERE s.tsic5 = %s
    GROUP BY s.province
    ORDER BY growth_gap DESC
    LIMIT 10;
    """
    return query_to_df(sql, (tsic5,))
