"""Analysis + charts for healthcare operations case study."""
import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

NAVY = "#1a1a2e"
BLUE = "#2563eb"
GRAY = "#e5e7eb"
os.makedirs("images", exist_ok=True)

# ---- Load data ----
rows = []
with open("staffing_shifts.csv") as f:
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

n = len(rows)
under = [r for r in rows if r["staff_actual"] < r["staff_scheduled"]]

def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.tick_params(colors="#374151", labelsize=9)
    ax.title.set_color(NAVY)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")

# ---- Chart 1: Staffing gap by unit ----
units = sorted(set(r["unit"] for r in rows))
gaps = [sum(r["gap"] for r in rows if r["unit"] == u) / sum(1 for r in rows if r["unit"] == u) for u in units]
fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=150)
bars = ax.bar(units, gaps, color=BLUE, width=0.6)
ax.set_ylabel("Avg staff gap (scheduled − actual)")
ax.set_title("Average staffing gap by unit")
ax.set_ylim(0, max(gaps) * 1.25)
for b, v in zip(bars, gaps):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8, color="#374151")
style_ax(ax)
plt.tight_layout()
plt.savefig("images/01_gap_by_unit.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Chart 2: Patient-to-staff ratio by unit ----
pts = [sum(r["patient_to_staff"] for r in rows if r["unit"] == u) / sum(1 for r in rows if r["unit"] == u) for u in units]
fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=150)
bars = ax.bar(units, pts, color=BLUE, width=0.6)
ax.set_ylabel("Avg patients per staff member")
ax.set_title("Patient-to-staff ratio by unit")
ax.set_ylim(0, max(pts) * 1.25)
for b, v in zip(bars, pts):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v:.2f}", ha="center", fontsize=8, color="#374151")
style_ax(ax)
plt.tight_layout()
plt.savefig("images/02_patient_to_staff.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Chart 3: Overtime hours by month ----
months = sorted(set(r["month"] for r in rows))
ot = [sum(r["overtime_hours"] for r in rows if r["month"] == m) for m in months]
fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=150)
ax.plot(months, ot, marker="o", color=BLUE, linewidth=2, markersize=5)
ax.set_ylabel("Overtime hours")
ax.set_title("Overtime hours by month")
ax.set_ylim(0, max(ot) * 1.15)
for x, v in zip(months, ot):
    ax.annotate(f"{v:.0f}", (x, v), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8, color="#374151")
style_ax(ax)
plt.tight_layout()
plt.savefig("images/03_overtime_by_month.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Chart 4: Understaffed share by unit ----
under_pct = [
    100 * sum(1 for r in rows if r["unit"] == u and r["staff_actual"] < r["staff_scheduled"]) /
    sum(1 for r in rows if r["unit"] == u)
    for u in units
]
fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=150)
bars = ax.bar(units, under_pct, color=BLUE, width=0.6)
ax.set_ylabel("% of shifts understaffed")
ax.set_title("Share of understaffed shifts by unit")
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for b, v in zip(bars, under_pct):
    ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}%", ha="center", fontsize=8, color="#374151")
style_ax(ax)
plt.tight_layout()
plt.savefig("images/04_understaffed_pct.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Chart 5: Labor cost by shift type ----
stypes = ["Day", "Evening", "Night"]
costs = [sum(r["labor_cost_usd"] for r in rows if r["shift_type"] == s) for s in stypes]
fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=150)
bars = ax.bar(stypes, costs, color=BLUE, width=0.6)
ax.set_ylabel("Total labor cost (USD)")
ax.set_title("Labor cost by shift type")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
for b, v in zip(bars, costs):
    ax.text(b.get_x() + b.get_width() / 2, v + 5000, f"${v:,.0f}", ha="center", fontsize=8, color="#374151")
style_ax(ax)
plt.tight_layout()
plt.savefig("images/05_cost_by_shift.png", bbox_inches="tight", facecolor="white")
plt.close()

# ---- Print key metrics for the case study ----
print(f"Total shifts: {n}")
print(f"Understaffed: {len(under)} ({100*len(under)/n:.1f}%)")
print(f"Avg gap when understaffed: {sum(r['gap'] for r in under)/len(under):.2f}")
print(f"Total OT: {sum(r['overtime_hours'] for r in rows):.0f} hrs")
print(f"Total agency shifts: {sum(r['agency_staff'] for r in rows)}")
print(f"Total labor cost: ${sum(r['labor_cost_usd'] for r in rows):,.0f}")
print()
for u in units:
    urs = [r for r in rows if r["unit"] == u]
    print(f"{u}: avg_gap={sum(r['gap'] for r in urs)/len(urs):.2f}, "
          f"avg_pts={sum(r['patient_to_staff'] for r in urs)/len(urs):.2f}, "
          f"ot={sum(r['overtime_hours'] for r in urs):.0f}, agency={sum(r['agency_staff'] for r in urs)}, "
          f"cost=${sum(r['labor_cost_usd'] for r in urs):,.0f}")
print("Charts saved to images/")
