-- Healthcare Staffing Operations Analysis
-- Synthetic dataset: 1,890 shifts across 5 units, Jan–Jun 2025
-- Columns: shift_id, date, unit, shift_type, staff_scheduled, staff_actual,
--          patients, overtime_hours, agency_staff, labor_cost_usd

-- Overall summary
SELECT
  COUNT(*) AS total_shifts,
  ROUND(AVG(staff_scheduled), 1) AS avg_scheduled,
  ROUND(AVG(staff_actual), 1) AS avg_actual,
  ROUND(AVG(patients), 1) AS avg_patients,
  ROUND(SUM(overtime_hours), 1) AS total_overtime,
  SUM(agency_staff) AS total_agency_shifts,
  ROUND(SUM(labor_cost_usd), 0) AS total_labor_cost
FROM shifts;

-- Staffing gap by unit
SELECT
  unit,
  COUNT(*) AS shifts,
  ROUND(AVG(staff_scheduled - staff_actual), 2) AS avg_gap,
  ROUND(AVG(patients * 1.0 / NULLIF(staff_actual, 0)), 2) AS avg_patient_to_staff,
  ROUND(SUM(overtime_hours), 1) AS total_ot,
  SUM(agency_staff) AS agency_shifts,
  ROUND(SUM(labor_cost_usd), 0) AS total_cost
FROM shifts
GROUP BY unit
ORDER BY total_cost DESC;

-- Overtime and cost by shift type
SELECT
  shift_type,
  COUNT(*) AS shifts,
  ROUND(AVG(overtime_hours), 2) AS avg_ot,
  SUM(overtime_hours) AS total_ot,
  SUM(agency_staff) AS agency_shifts,
  ROUND(SUM(labor_cost_usd), 0) AS total_cost
FROM shifts
GROUP BY shift_type
ORDER BY total_ot DESC;

-- Monthly trend
SELECT
  substr(date, 1, 7) AS month,
  COUNT(*) AS shifts,
  ROUND(AVG(staff_scheduled - staff_actual), 2) AS avg_gap,
  ROUND(SUM(overtime_hours), 1) AS total_ot,
  ROUND(SUM(labor_cost_usd), 0) AS total_cost
FROM shifts
GROUP BY month
ORDER BY month;

-- Understaffed shifts
SELECT
  COUNT(*) AS understaffed_shifts,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shifts), 1) AS pct_of_all_shifts,
  ROUND(AVG(staff_scheduled - staff_actual), 2) AS avg_gap_when_understaffed
FROM shifts
WHERE staff_actual < staff_scheduled;
