"""Generate dashboard mockup images for healthcare operations BI case study."""
import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

NAVY = "#1a1a2e"
BLUE = "#2563eb"
GREEN = "#10b981"
ORANGE = "#f59e0b"
RED = "#ef4444"
GRAY = "#e5e7eb"
LIGHT = "#f8fafc"
DARK_TEXT = "#374151"

os.makedirs("images", exist_ok=True)

# ---- Load data ----
rows = []
with open("../healthcare-operations/staffing_shifts.csv") as f:
    for r in csv.DictReader(f):
        r["staff_scheduled"] = int(r["staff_scheduled"])
        r["staff_actual"] = int(r["staff_actual"])
        r["patients"] = int(r["patients"])
        r["overtime_hours"] = float(r["overtime_hours"])
        r["agency_staff"] = int(r["agency_staff"])
        r["labor_cost_usd"] = float(r["labor_cost_usd"])
        r["gap"] = r["staff_scheduled"] - r["staff_actual"]
        r["patient_to_staff"] = r["patients"] / r["staff_actual"]
        r["month"] = r["date"][:7]
        rows.append(r)

units = ["ICU", "Med-Surg", "ER", "Stepdown", "Oncology"]
months = sorted(set(r["month"] for r in rows))

# ---- Helper: KPI card ----
def kpi_card(ax, title, value, subtitle, color=BLUE):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.02, 0.02), 0.96, 0.96,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor="white", edgecolor=GRAY, linewidth=1
    ))
    ax.text(0.5, 0.72, title, ha="center", va="center", fontsize=8.5,
            color=DARK_TEXT, fontweight="600", transform=ax.transAxes)
    ax.text(0.5, 0.42, value, ha="center", va="center", fontsize=20,
            color=color, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.18, subtitle, ha="center", va="center", fontsize=7.5,
            color="#6b7280", transform=ax.transAxes)

# ---- Dashboard overview image ----
fig = plt.figure(figsize=(14, 8), dpi=150)
fig.patch.set_facecolor("white")
gs = GridSpec(4, 4, figure=fig, wspace=0.15, hspace=0.3,
              left=0.02, right=0.98, top=0.92, bottom=0.06)

# Title
fig.text(0.02, 0.965, "Hospital Staffing Operations Dashboard", fontsize=16,
         fontweight="bold", color=NAVY)
fig.text(0.02, 0.935, "Staffing gaps · Overtime · Agency spend · Patient-to-staff ratio",
         fontsize=9, color="#6b7280")

# KPI cards (top row)
kpi_vals = {
    "Shifts Analyzed": (f"{len(rows):,}", "Jan–Jun 2025"),
    "Understaffed": (f"{100*len([r for r in rows if r['staff_actual'] < r['staff_scheduled']])/len(rows):.1f}%", "of all shifts"),
    "Overtime Hours": (f"{sum(r['overtime_hours'] for r in rows):,.0f}", "6-month total"),
    "Agency Shifts": (f"{sum(r['agency_staff'] for r in rows)}", "unfilled coverage"),
    "Labor Cost": (f"${sum(r['labor_cost_usd'] for r in rows):,.0f}", "6-month total"),
    "Avg Patient:Staff": (f"{sum(r['patient_to_staff'] for r in rows)/len(rows):.2f}", "across all units"),
}

kpi_positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
colors = [BLUE, RED, ORANGE, ORANGE, BLUE, GREEN]
for (title, (val, sub)), (r, c), color in zip(kpi_vals.items(), kpi_positions, colors):
    ax = fig.add_subplot(gs[r, c])
    kpi_card(ax, title, val, sub, color)

# Chart 1: Staffing gap by unit (bar)
ax1 = fig.add_subplot(gs[2:, 0:2])
unit_gaps = {u: sum(r["gap"] for r in rows if r["unit"] == u) / sum(1 for r in rows if r["unit"] == u) for u in units}
ax1.bar(units, list(unit_gaps.values()), color=BLUE, width=0.6)
ax1.set_title("Avg Staffing Gap by Unit", fontsize=11, fontweight="bold", color=NAVY, loc="left")
ax1.set_ylabel("Scheduled − Actual", fontsize=9)
ax1.tick_params(axis='both', labelsize=8)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

# Chart 2: Overtime by month (line)
ax2 = fig.add_subplot(gs[2:, 2:])
ot_by_month = [sum(r["overtime_hours"] for r in rows if r["month"] == m) for m in months]
ax2.plot(months, ot_by_month, marker="o", color=BLUE, linewidth=2, markersize=4)
ax2.set_title("Overtime Hours by Month", fontsize=11, fontweight="bold", color=NAVY, loc="left")
ax2.set_ylabel("OT Hours", fontsize=9)
ax2.tick_params(axis='both', labelsize=8)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
plt.setp(ax2.get_xticklabels(), rotation=45)

# Footer
fig.text(0.02, 0.02, "Data: Synthetic staffing dataset · Built with Tableau/Power BI · Not real hospital data",
         fontsize=7.5, color="#9ca3af")

plt.savefig("images/dashboard_overview.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Chart: Patient-to-staff by unit ----
fig2, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
pts_by_unit = [sum(r["patient_to_staff"] for r in rows if r["unit"] == u) / sum(1 for r in rows if r["unit"] == u) for u in units]
colors_bar = [RED if v > 2.5 else ORANGE if v > 2.0 else BLUE for v in pts_by_unit]
bars = ax.bar(units, pts_by_unit, color=colors_bar, width=0.6)
ax.set_title("Patient-to-Staff Ratio by Unit", fontsize=12, fontweight="bold", color=NAVY)
ax.set_ylabel("Patients per Staff", fontsize=10)
ax.set_ylim(0, max(pts_by_unit) * 1.25)
for b, v in zip(bars, pts_by_unit):
    ax.text(b.get_x() + b.get_width()/2, v + 0.05, f"{v:.2f}", ha="center", fontsize=9, color=DARK_TEXT)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig("images/patient_staff_ratio.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Chart: Cost by shift type ----
fig3, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
stypes = ["Day", "Evening", "Night"]
costs = [sum(r["labor_cost_usd"] for r in rows if r["shift_type"] == s) for s in stypes]
bars = ax.bar(stypes, costs, color=[BLUE, ORANGE, RED], width=0.6)
ax.set_title("Labor Cost by Shift Type", fontsize=12, fontweight="bold", color=NAVY)
ax.set_ylabel("Total Cost (USD)", fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
for b, v in zip(bars, costs):
    ax.text(b.get_x() + b.get_width()/2, v + 10000, f"${v:,.0f}", ha="center", fontsize=9, color=DARK_TEXT)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig("images/cost_by_shift.png", bbox_inches="tight", facecolor="white")
plt.close()

print("Dashboard images saved to images/")
