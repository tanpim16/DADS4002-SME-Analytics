
CREATE DATABASE IF NOT EXISTS sme_analysis;
USE sme_analysis;

CREATE TABLE IF NOT EXISTS gpp_data (
    province VARCHAR(100),
    gpp_total_million FLOAT,
    population_thousand FLOAT,
    gpp_per_capita FLOAT
);

CREATE TABLE IF NOT EXISTS sme_detail (
    province VARCHAR(100),
    region VARCHAR(100),
    sector VARCHAR(100),
    tsic2 VARCHAR(10),
    tsic2_detail VARCHAR(255),
    tsic5 VARCHAR(10),
    tsic5_detail VARCHAR(255),
    business_size VARCHAR(50),
    number_sme INT,
    data_source VARCHAR(100),
    year INT
);

