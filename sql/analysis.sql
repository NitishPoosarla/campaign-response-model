-- 05-marketing-campaign — conversion & cost in SQL.
-- Loads: data/processed/bank_cleaned.csv -> `calls` (y, converted, campaign, previous, month, job, contact).

-- Headline conversion economics (assumes $2.50/dial, $120 margin — parameterize as desired)
SELECT
  COUNT(*) AS dials,
  ROUND(AVG(converted) * 100, 2) AS conversion_pct,
  ROUND(COUNT(*) * 2.50, 0) AS dial_cost,
  ROUND(SUM(converted) * 120.0, 0) AS conversion_revenue,
  ROUND(SUM(converted) * 120.0 / (COUNT(*) * 2.50), 2) AS roi
FROM calls;

-- Conversion vs volume by month (the calendar rebalance)
SELECT month, COUNT(*) AS dials, ROUND(AVG(converted) * 100, 2) AS conversion_pct
FROM calls GROUP BY month ORDER BY month;

-- Prior-outcome effect (success list is near-destiny)
SELECT poutcome, COUNT(*) AS dials, ROUND(AVG(converted) * 100, 2) AS conversion_pct
FROM calls GROUP BY poutcome ORDER BY conversion_pct DESC;

-- Profession segmentation
SELECT job, COUNT(*) AS dials, ROUND(AVG(converted) * 100, 2) AS conversion_pct
FROM calls GROUP BY job ORDER BY conversion_pct DESC;
