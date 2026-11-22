"""Generate synthetic hospital staffing dataset for case study.

Columns:
- shift_id, date, unit, shift_type, staff_scheduled, staff_actual,
  patients, overtime_hours, agency_staff, labor_cost_usd
"""
import random
from datetime import date, timedelta

random.seed(42)

UNITS = ["ICU", "Med-Surg", "ER", "Stepdown", "Oncology"]
SHIFT_TYPES = ["Day", "Night", "Evening"]

start = date(2025, 1, 6)
end = date(2025, 6, 30)

rows = []
sid = 1
d = start
while d <= end:
    if d.weekday() >= 5:  # skip weekends for this simplified dataset
        d += timedelta(days=1)
        continue
    for unit in UNITS:
        for shift in SHIFT_TYPES:
            base = {"ICU": 12, "Med-Surg": 14, "ER": 13, "Stepdown": 11, "Oncology": 10}[unit]
            scheduled = base + random.randint(-2, 2)
            actual = scheduled + random.randint(-3, 1)  # usually under-staffed
            patients = {
                "ICU": random.randint(8, 12),
                "Med-Surg": random.randint(24, 32),
                "ER": random.randint(28, 40),
                "Stepdown": random.randint(16, 22),
                "Oncology": random.randint(14, 20),
            }[unit]
            ot = max(0, random.randint(0, 8)) if actual < scheduled else 0
            agency = 1 if actual < scheduled - 1 and random.random() < 0.4 else 0
            cost = round(scheduled * 58 + ot * 87 + agency * 320, 2)
            rows.append([
                sid, d.isoformat(), unit, shift, scheduled, actual,
                patients, ot, agency, cost
            ])
            sid += 1
    d += timedelta(days=1)

header = [
    "shift_id", "date", "unit", "shift_type", "staff_scheduled",
    "staff_actual", "patients", "overtime_hours", "agency_staff", "labor_cost_usd"
]

with open("staffing_shifts.csv", "w") as f:
    f.write(",".join(header) + "\n")
    for r in rows:
        f.write(",".join(str(x) for x in r) + "\n")

print(f"Wrote {len(rows)} rows to staffing_shifts.csv")
