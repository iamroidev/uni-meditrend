"""
=============================================================
    University Clinic — Synthetic Dataset Generator
    AI-Based Analysis and Prediction of Student Clinic Visits
=============================================================

ETHICS:
    No Personal Identifiable Information (PII) in output.
    Fully anonymised — no student IDs, names, or traceable fields.

COVERAGE:
    Year 1  : Jan 2024 – Sep 2024  (full academic year)
    Year 2  : Jan 2025 – Sep 2025  (full academic year)
    Year 3  : Jan 2026 – Mar 2026  (partial — lectures only)

OUTPUT COLUMNS (in order):
    visit_date, level, gender, department, hostel, diagnosis, severity

INTERNAL COLUMNS (used for logic, dropped before output):
    _phase (prefixed with underscore to make intent clear)

TWEAKING:
    All parameters live in CONFIG below.
    pattern_strength: 0.0 = pure random, 1.0 = fully deterministic.
    At 0.7 patterns are discoverable but not obvious.
=============================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import copy

# ─────────────────────────────────────────────────────────────
#  MASTER CONFIG — tweak anything here, logic stays untouched
# ─────────────────────────────────────────────────────────────

CONFIG = {

    # ── Pattern strength ──────────────────────────────────────
    "pattern_strength": 0.7,

    # ── Random seed (None = different output each run) ────────
    "seed": 42,

    # ── Academic year definitions ─────────────────────────────
    # phases: (start, end, label, visit_rate_multiplier)
    # multiplier: 1.0 = normal, >1 = busier, <0.1 = trickle
    "academic_years": [
        {
            "label": "2023/2024",
            "phases": [
                ("2024-01-15", "2024-03-31", "1st_sem_lectures", 1.0),
                ("2024-04-01", "2024-04-30", "1st_sem_exams", 1.4),
                ("2024-05-01", "2024-05-31", "semester_vacation", 0.08),
                ("2024-06-01", "2024-08-10", "2nd_sem_lectures", 1.0),
                ("2024-08-15", "2024-09-15", "2nd_sem_exams", 1.4),
                ("2024-09-16", "2025-01-12", "long_vacation", 0.9),
            ],
            "target_records": 2414,
        },
        {
            "label": "2024/2025",
            "phases": [
                ("2025-01-13", "2025-03-31", "1st_sem_lectures", 1.0),
                ("2025-04-01", "2025-04-30", "1st_sem_exams", 1.4),
                ("2025-05-01", "2025-05-31", "semester_vacation", 0.08),
                ("2025-06-01", "2025-08-10", "2nd_sem_lectures", 1.0),
                ("2025-08-15", "2025-09-15", "2nd_sem_exams", 1.4),
                ("2025-09-16", "2026-01-11", "long_vacation", 0.9),
            ],
            "target_records": 2509,
        },
        {
            "label": "2025/2026",
            "phases": [
                ("2026-01-12", "2026-03-31", "1st_sem_lectures", 1.0),
            ],
            # Partial academic year: only first semester lectures are present.
            # Use an explicit smaller target so the year is partial (~900 records).
            "target_records": 876,
        },
    ],

    # ── Date jitter: softens exact phase boundary clustering ──
    "date_jitter_days": 4,

    # ── Diagnoses ─────────────────────────────────────────────
    "diagnoses": [
        "Malaria",
        "Typhoid",
        "Common Cold",
        "Food Poisoning",
        "Stress/Fatigue",
        "Physical Injury",
    ],

    # ── Severity weights per diagnosis ────────────────────────
    # Probabilities for levels [1, 2, 3, 4, 5]
    # 1=Mild/OTC  2=Nurse  3=Doctor+rest  4=IV/ward  5=Referral
    "severity_weights": {
        "Malaria":         [0.05, 0.15, 0.50, 0.20, 0.10],
        "Common Cold":     [0.60, 0.30, 0.10, 0.00, 0.00],
        "Physical Injury": [0.20, 0.30, 0.30, 0.15, 0.05],
        "Typhoid":         [0.00, 0.10, 0.40, 0.40, 0.10],
        "Food Poisoning":  [0.10, 0.30, 0.40, 0.15, 0.05],
        "Stress/Fatigue":  [0.40, 0.40, 0.20, 0.00, 0.00],
    },

    # ── Student levels ────────────────────────────────────────
    "levels": [100, 200, 300, 400],

    # ── Genders ───────────────────────────────────────────────
    "genders": ["Male", "Female"],

    # ── Departments & illness tendencies ──────────────────────
    "departments": {
        "Mining Engineering":                  {"Malaria": 3.0, "Physical Injury": 2.5, "Typhoid": 1.5, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Food Poisoning": 1.0},
        "Geological Engineering":              {"Malaria": 2.5, "Physical Injury": 2.0, "Typhoid": 2.0, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Food Poisoning": 1.0},
        "Petroleum Engineering":               {"Malaria": 2.0, "Physical Injury": 2.0, "Typhoid": 1.5, "Common Cold": 1.0, "Stress/Fatigue": 1.5, "Food Poisoning": 1.0},
        "Geomatic Engineering":                {"Malaria": 2.5, "Typhoid": 2.5, "Physical Injury": 1.5, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Food Poisoning": 1.0},
        "Electrical & Electronic Engineering": {"Stress/Fatigue": 3.0, "Physical Injury": 2.0, "Common Cold": 1.5, "Malaria": 1.0, "Typhoid": 1.0, "Food Poisoning": 0.8},
        "Computer Science & Engineering":      {"Stress/Fatigue": 3.5, "Common Cold": 1.5, "Malaria": 0.8, "Typhoid": 0.8, "Physical Injury": 0.8, "Food Poisoning": 0.8},
        "Mechanical Engineering":              {"Physical Injury": 3.0, "Stress/Fatigue": 2.0, "Common Cold": 1.0, "Malaria": 1.0, "Typhoid": 1.0, "Food Poisoning": 1.0},
        "Mathematics":                         {"Stress/Fatigue": 3.0, "Common Cold": 2.0, "Malaria": 0.8, "Typhoid": 0.8, "Physical Injury": 0.5, "Food Poisoning": 0.8},
    },

    # ── Hostels & illness tendencies ─────────────────────────
    "hostels": {
        "Chamber of Mines Hall": {"Malaria": 2.5, "Physical Injury": 2.0, "Typhoid": 1.0, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Food Poisoning": 1.0},
        "K.T. Hall":             {"Malaria": 4.0, "Typhoid": 1.0, "Physical Injury": 1.0, "Common Cold": 1.0, "Stress/Fatigue": 0.8, "Food Poisoning": 1.0},
        "Gold Refinery Hall":    {"Food Poisoning": 3.0, "Typhoid": 2.5, "Malaria": 1.0, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Physical Injury": 0.8},
        "The Point Hostel":      {"Common Cold": 3.0, "Malaria": 1.0, "Typhoid": 1.0, "Food Poisoning": 1.5, "Stress/Fatigue": 1.5, "Physical Injury": 0.8},
        "Osborn":                {"Stress/Fatigue": 2.5, "Common Cold": 2.0, "Malaria": 1.0, "Typhoid": 1.0, "Food Poisoning": 0.8, "Physical Injury": 0.8},
        "Hilda":                 {"Stress/Fatigue": 3.0, "Common Cold": 1.5, "Malaria": 0.8, "Typhoid": 1.0, "Food Poisoning": 1.0, "Physical Injury": 0.5},
        "Castle Gate":           {"Typhoid": 2.5, "Food Poisoning": 2.5, "Malaria": 1.5, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Physical Injury": 1.0},
        "Off Campus":            {"Typhoid": 3.0, "Malaria": 2.5, "Food Poisoning": 2.0, "Common Cold": 1.0, "Stress/Fatigue": 1.0, "Physical Injury": 1.0},
        "Kabi's Hostel":         {"Malaria": 1.8, "Common Cold": 1.5, "Typhoid": 1.5, "Food Poisoning": 1.5, "Stress/Fatigue": 1.0, "Physical Injury": 1.0},
        "New Excellence":        {"Common Cold": 2.5, "Stress/Fatigue": 2.0, "Malaria": 1.0, "Typhoid": 1.0, "Food Poisoning": 1.0, "Physical Injury": 0.8},
    },

    # ── Level-based patterns ──────────────────────────────────
    "levels_config": {
        100: {
            "illness_weights": {"Malaria": 2.0, "Common Cold": 2.0, "Food Poisoning": 1.5,
                                "Typhoid": 1.0, "Stress/Fatigue": 1.0, "Physical Injury": 1.0},
            "early_semester_vulnerability": 1.8,
        },
        200: {
            "illness_weights": {"Malaria": 1.0, "Common Cold": 1.0, "Food Poisoning": 1.5,
                                "Typhoid": 1.5, "Stress/Fatigue": 1.2, "Physical Injury": 1.2},
            "early_semester_vulnerability": 1.1,
        },
        300: {
            "illness_weights": {"Stress/Fatigue": 2.0, "Malaria": 1.0, "Common Cold": 1.0,
                                "Typhoid": 1.0, "Food Poisoning": 1.0, "Physical Injury": 1.3},
            "early_semester_vulnerability": 1.0,
        },
        400: {
            "illness_weights": {"Stress/Fatigue": 3.0, "Malaria": 1.0, "Common Cold": 1.0,
                                "Typhoid": 0.8, "Food Poisoning": 0.8, "Physical Injury": 1.0},
            "early_semester_vulnerability": 1.0,
        },
    },

    # ── Gender bias (subtle) ──────────────────────────────────
    "gender_illness_bias": {
        "Male":   {"Malaria": 1.2, "Physical Injury": 1.4, "Stress/Fatigue": 0.9,
                   "Common Cold": 0.9, "Typhoid": 1.0, "Food Poisoning": 1.0},
        "Female": {"Stress/Fatigue": 1.3, "Common Cold": 1.2, "Malaria": 0.85,
                   "Physical Injury": 0.6, "Typhoid": 1.0, "Food Poisoning": 1.0},
    },

    # ── Exam phase boosts ─────────────────────────────────────
    "exam_illness_boost": {
        "Stress/Fatigue":  2.5,
        "Common Cold":     1.3,
        "Malaria":         0.8,
        "Food Poisoning":  0.9,
        "Typhoid":         0.9,
        "Physical Injury": 0.7,
    },

    # ── Rainy season (Ghana: Apr–Jun, Aug–Sep) ────────────────
    "rainy_season_months": [4, 5, 6, 8, 9],
    "rainy_season_illness_boost": {
        "Malaria":         1.8,
        "Common Cold":     1.3,
        "Typhoid":         1.2,
        "Stress/Fatigue":  1.0,
        "Physical Injury": 1.0,
        "Food Poisoning":  1.0,
    },

    # ── Early semester window ─────────────────────────────────
    "early_semester_week_count": 4,
}


# ─────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def normalise(weights: dict) -> dict:
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def blend_weights(patterned: dict, strength: float) -> dict:
    diagnoses = list(patterned.keys())
    uniform   = {d: 1.0 / len(diagnoses) for d in diagnoses}
    blended   = {d: (1 - strength) * uniform[d] + strength * patterned[d] for d in diagnoses}
    return normalise(blended)


def combine_weights(*weight_dicts) -> dict:
    keys     = list(weight_dicts[0].keys())
    combined = {k: 1.0 for k in keys}
    for wd in weight_dicts:
        for k in keys:
            combined[k] *= wd.get(k, 1.0)
    return normalise(combined)


def build_phase_calendar(phases):
    calendar = []
    for start_str, end_str, label, multiplier in phases:
        start   = datetime.strptime(start_str, "%Y-%m-%d")
        end     = datetime.strptime(end_str,   "%Y-%m-%d")
        current = start
        while current <= end:
            calendar.append((current, label, multiplier))
            current += timedelta(days=1)
    return calendar


def pick_date(calendar, rng, jitter_days):
    multipliers = np.array([m for _, _, m in calendar])
    probs       = multipliers / multipliers.sum()
    idx         = rng.choice(len(calendar), p=probs)
    date, label, _ = calendar[idx]
    jitter      = int(rng.integers(-jitter_days, jitter_days + 1))
    jittered    = date + timedelta(days=jitter)
    min_date    = calendar[0][0]
    max_date    = calendar[-1][0]
    jittered    = max(min_date, min(max_date, jittered))
    # Re-resolve the phase label after applying jitter so the label
    # always corresponds to the actual (possibly jittered) date.
    phase_label = label
    for d, l, _ in calendar:
        # calendar dates use datetime objects with midnight time; compare dates
        if d.date() == jittered.date():
            phase_label = l
            break

    return jittered, phase_label


def get_semester_week(date, label, phases):
    for start_str, _, phase_label, _ in phases:
        if phase_label == label:
            start = datetime.strptime(start_str, "%Y-%m-%d")
            delta = (date - start).days
            return max(1, delta // 7 + 1)
    return 1


def pick_diagnosis(hostel, department, level, gender,
                   phase_label, date, phases, rng, strength):
    diagnoses = CONFIG["diagnoses"]

    hostel_w = normalise(CONFIG["hostels"][hostel])
    dept_w   = normalise(CONFIG["departments"][department])
    level_w  = normalise(CONFIG["levels_config"][level]["illness_weights"])
    gender_w = normalise(CONFIG["gender_illness_bias"][gender])

    phase_mod = {d: 1.0 for d in diagnoses}
    if "exam" in phase_label:
        for d, boost in CONFIG["exam_illness_boost"].items():
            phase_mod[d] = boost

    rain_mod = {d: 1.0 for d in diagnoses}
    if date.month in CONFIG["rainy_season_months"]:
        for d, boost in CONFIG["rainy_season_illness_boost"].items():
            rain_mod[d] = boost

    week      = get_semester_week(date, phase_label, phases)
    early_mod = {d: 1.0 for d in diagnoses}
    if "lectures" in phase_label and week <= CONFIG["early_semester_week_count"]:
        vuln = CONFIG["levels_config"][level]["early_semester_vulnerability"]
        early_mod["Malaria"]     *= vuln
        early_mod["Common Cold"] *= vuln

    patterned = combine_weights(hostel_w, dept_w, level_w, gender_w,
                                phase_mod, rain_mod, early_mod)
    final     = blend_weights(patterned, strength)

    return rng.choice(list(final.keys()), p=list(final.values()))


def assign_severity(diagnosis, level, phase_label, rng):
    levels  = [1, 2, 3, 4, 5]
    weights = np.array(
        CONFIG["severity_weights"].get(diagnosis, [0.2] * 5),
        dtype=float
    )

    if "exam" in phase_label:
        weights[2] *= 1.2
        weights[3] *= 1.1

    if level == 100:
        weights[0] *= 0.8
        weights[3] *= 1.15

    if level == 400:
        weights[0] *= 1.1
        weights[3] *= 0.9

    weights /= weights.sum()
    return int(rng.choice(levels, p=weights))


def calculate_partial_records(full_records, full_phases, partial_phases):
    def weighted_days(phases):
        total = 0
        for s, e, _, m in phases:
            start = datetime.strptime(s, "%Y-%m-%d")
            end   = datetime.strptime(e, "%Y-%m-%d")
            total += (end - start).days * m
        return total

    ratio = weighted_days(partial_phases) / weighted_days(full_phases)
    return max(1, round(full_records * ratio))


# ─────────────────────────────────────────────────────────────
#  MAIN GENERATOR
# ─────────────────────────────────────────────────────────────

def generate_dataset():
    cfg      = CONFIG
    rng      = np.random.default_rng(cfg["seed"])
    strength = cfg["pattern_strength"]
    jitter   = cfg["date_jitter_days"]

    hostels     = list(cfg["hostels"].keys())
    departments = list(cfg["departments"].keys())
    levels      = cfg["levels"]
    genders     = cfg["genders"]

    # Work on a local deep copy of academic_years to avoid mutating CONFIG
    years = copy.deepcopy(cfg["academic_years"])
    ref_year = years[0]
    for year in years:
        if year.get("target_records") is None:
            year["target_records"] = calculate_partial_records(
                ref_year["target_records"],
                ref_year["phases"],
                year["phases"]
            )

    # Ensure long_vacation phases do not cross into the next calendar year.
    # Clamp any long_vacation end date to Dec 31 of the phase's start year.
    for year in years:
        new_phases = []
        for start_str, end_str, label, multiplier in year["phases"]:
            if label == "long_vacation":
                start_dt = datetime.strptime(start_str, "%Y-%m-%d")
                clamped_end = datetime(start_dt.year, 12, 31)
                new_phases.append((start_str, clamped_end.strftime("%Y-%m-%d"), label, multiplier))
            else:
                new_phases.append((start_str, end_str, label, multiplier))
        year["phases"] = new_phases

    all_records = []

    for year in years:
        phases   = year["phases"]
        calendar = build_phase_calendar(phases)
        n        = year["target_records"]

        for _ in range(n):
            hostel     = rng.choice(hostels)
            department = rng.choice(departments)
            level      = int(rng.choice(levels))
            gender     = rng.choice(genders)

            date, phase_label = pick_date(calendar, rng, jitter)

            diagnosis = pick_diagnosis(
                hostel, department, level, gender,
                phase_label, date, phases, rng, strength
            )

            severity = assign_severity(diagnosis, level, phase_label, rng)

            all_records.append({
                "visit_date": date.strftime("%Y-%m-%d"),
                "level":      level,
                "gender":     gender,
                "department": department,
                "hostel":     hostel,
                "diagnosis":  diagnosis,
                "severity":   severity,
            })

    df = pd.DataFrame(all_records)
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    df = df.sort_values("visit_date").reset_index(drop=True)

    return df


# ─────────────────────────────────────────────────────────────
#  RUN & INSPECT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = generate_dataset()

    print("=" * 60)
    print("  DATASET GENERATED")
    print("=" * 60)
    print(f"  Total records : {len(df):,}")
    print(f"  Date range    : {df['visit_date'].min().date()} → {df['visit_date'].max().date()}")
    print(f"  Columns       : {list(df.columns)}")
    print()

    print("── Records per year ─────────────────────────────────")
    print(df["visit_date"].dt.year.value_counts().sort_index().to_string())
    print()

    print("── Diagnosis distribution ───────────────────────────")
    print(df["diagnosis"].value_counts().to_string())
    print()

    print("── Severity distribution ────────────────────────────")
    print(df["severity"].value_counts().sort_index().to_string())
    print()

    print("── Avg severity by diagnosis ────────────────────────")
    print(df.groupby("diagnosis")["severity"].mean().round(2)
            .sort_values(ascending=False).to_string())
    print()

    print("── Malaria by hostel ────────────────────────────────")
    print(
        df[df["diagnosis"] == "Malaria"]
        .groupby("hostel").size()
        .sort_values(ascending=False)
        .to_string()
    )
    print()

    print("── Stress/Fatigue % by department ───────────────────")
    for dept in CONFIG["departments"]:
        pct = (
            df[df["department"] == dept]["diagnosis"]
            .value_counts(normalize=True)
            .get("Stress/Fatigue", 0) * 100
        )
        print(f"  {dept:<44} {pct:.1f}%")
    print()

    print("── First 5 rows ──────────────────────────────────────")
    print(df.head().to_string())
    print()
    print("─" * 60)
    print("  MONGODB INSERT (run after inspection):")
    print("─" * 60)
    print("  from pymongo import MongoClient")
    print("  client = MongoClient('mongodb://localhost:27017/')")
    print("  db = client['your_db_name']")
    print("  records = df.to_dict('records')")
    print("  db.student_visits.insert_many(records)")
