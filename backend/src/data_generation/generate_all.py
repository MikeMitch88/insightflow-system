"""
Synthetic data generator for the Kenyan NGO analytics platform.

Creates a realistic but intentionally messy set of CSV files under
``<project root>/data/raw``:

    beneficiaries.csv   ~10,000 unique programme beneficiaries
    scholarship.csv     university / college scholarship records
    plus.csv            personal development (life skills) records
    vocational.csv      vocational training records
    tech.csv            digital skills training records
    attendance.csv      per-quarter session attendance
    outcomes.csv        post-programme outcome tracking

Intentional data quality issues (so downstream cleaning has real work to do):

    * ~10% inconsistent county naming   ("NAIROBI", "nairobi", "Nairobi County")
    * ~8%  inconsistent gender encoding ("M", "F", "male", "FEMALE", "f")
    * ~10% inconsistent status wording  ("complete", "COMPLETED", "Active",
                                          "DROPPED", "dropped out")
    * ~2%  exact duplicate beneficiary rows
    * ~3%  inconsistent programme names ("SCHOLARSHIP", "scholarship program",
                                          "PLUS PROGRAM", "tech", ...)

Embedded analytical trends:

    * enrolment grows every quarter (Q3 2026 far exceeds Q1 2025)
    * Tech completion improves from ~75% to ~82%
    * Vocational completion declines from ~72% to ~68%
    * counties perform differently (Nairobi / Nyeri outperform,
      Kilifi / Kisumu lag behind)

Usage:

    python backend/src/data_generation/generate_all.py
"""

import csv
import os
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"

TODAY = date.today()

N_BENEFICIARIES = 10_000
MIN_AGE = 16
MAX_AGE = 35
FEMALE_SHARE = 0.55
PHONE_NULL_RATE = 0.05
EMAIL_NULL_RATE = 0.15

QUARTERS = [
    "Q1 2025",
    "Q2 2025",
    "Q3 2025",
    "Q4 2025",
    "Q1 2026",
    "Q2 2026",
    "Q3 2026",
]

QUARTER_GROWTH_WEIGHTS = [0.06, 0.09, 0.12, 0.14, 0.17, 0.20, 0.22]

COUNTY_WEIGHTS = {
    "Nairobi": 0.18,
    "Kiambu": 0.09,
    "Mombasa": 0.07,
    "Kisumu": 0.06,
    "Nakuru": 0.06,
    "Uasin Gishu": 0.05,
    "Kakamega": 0.05,
    "Machakos": 0.05,
    "Kajiado": 0.05,
    "Meru": 0.05,
    "Kilifi": 0.04,
    "Bungoma": 0.04,
    "Nyeri": 0.04,
    "Muranga": 0.04,
    "Kisii": 0.03,
}

SUB_COUNTIES = {
    "Nairobi": [
        "Westlands", "Kasarani", "Langata", "Dagoretti",
        "Starehe", "Embakasi", "Mathare", "Roysambu",
    ],
    "Kiambu": [
        "Thika Town", "Ruiru", "Limuru", "Kikuyu",
        "Juja", "Githunguri", "Kiambu Town",
    ],
    "Mombasa": [
        "Mvita", "Likoni", "Nyali", "Kisauni",
        "Changamwe", "Jomvu",
    ],
    "Kisumu": [
        "Kisumu Central", "Kisumu East", "Kisumu West",
        "Nyando", "Muhoroni", "Seme",
    ],
    "Nakuru": [
        "Nakuru Town East", "Nakuru Town West", "Naivasha",
        "Molo", "Njoro", "Gilgil", "Rongai",
    ],
    "Uasin Gishu": [
        "Eldoret North", "Eldoret South", "Soy",
        "Turbo", "Kapseret", "Ainabkoi",
    ],
    "Kakamega": [
        "Lurambi", "Malava", "Mumias East", "Mumias West",
        "Butere", "Ikolomani", "Shinyalu",
    ],
    "Machakos": [
        "Machakos Town", "Mavoko", "Kangundo",
        "Kathiani", "Yatta", "Masinga",
    ],
    "Kajiado": [
        "Kajiado Central", "Ngong", "Kitengela",
        "Loitokitok", "Ongata Rongai", "Isinya",
    ],
    "Meru": [
        "North Imenti", "South Imenti", "Central Imenti",
        "Tigania East", "Tigania West", "Buuri",
    ],
    "Kilifi": [
        "Kilifi North", "Kilifi South", "Malindi",
        "Magarini", "Rabai", "Kaloleni",
    ],
    "Bungoma": [
        "Bungoma Central", "Bungoma North", "Bungoma South",
        "Webuye East", "Webuye West", "Kimilili", "Sirisia",
    ],
    "Nyeri": [
        "Nyeri Central", "Nyeri Town", "Mukurweini",
        "Tetu", "Othaya", "Mathira",
    ],
    "Muranga": [
        "Muranga East", "Muranga West", "Kangema",
        "Kandara", "Maragua", "Kiharu",
    ],
    "Kisii": [
        "Kisii Central", "Nyaribari Masaba", "Nyaribari Chache",
        "Bomachoge Borabu", "Gucha South", "Sameta",
    ],
}

COUNTY_PERFORMANCE = {
    "Nairobi": 1.08,
    "Kiambu": 1.05,
    "Mombasa": 1.00,
    "Kisumu": 0.92,
    "Nakuru": 1.02,
    "Uasin Gishu": 1.03,
    "Kakamega": 0.95,
    "Machakos": 0.98,
    "Kajiado": 1.01,
    "Meru": 0.99,
    "Kilifi": 0.93,
    "Bungoma": 0.96,
    "Nyeri": 1.04,
    "Muranga": 1.02,
    "Kisii": 0.97,
}

FEMALE_NAMES = [
    "Wanjiru", "Njeri", "Nyambura", "Wangari", "Wanjiku", "Gathoni",
    "Achieng", "Atieno", "Akinyi", "Awuor", "Anyango", "Chebet",
    "Cherono", "Jerop", "Chepkoech", "Nasieku", "Naisula", "Halima",
    "Amina", "Zawadi", "Neema", "Grace", "Faith", "Mercy",
    "Joy", "Cynthia", "Emily", "Brenda", "Sharon", "Diana",
    "Caroline", "Beatrice", "Esther", "Purity", "Kendi", "Nkatha",
    "Kagure", "Mumbi",
]

MALE_NAMES = [
    "Kamau", "Otieno", "Odhiambo", "Onyango", "Omondi", "Kipchoge",
    "Kiptoo", "Cheruiyot", "Korir", "Rotich", "Mutua", "Musyoka",
    "Kilonzo", "Baraka", "Juma", "Barasa", "Wekesa", "Abdi",
    "Mohamed", "Ali", "Dennis", "Brian", "Kevin", "Kelvin",
    "Collins", "Victor", "Emmanuel", "Peter", "John", "James",
    "Joseph", "Samuel", "David", "Daniel", "Simon", "Anthony",
    "Francis", "Stephen", "Patrick", "Vincent", "Boniface", "Nicholas",
    "Timothy", "Isaac",
]

SURNAMES = [
    "Otieno", "Kamau", "Wafula", "Mwangi", "Njoroge", "Kiptoo",
    "Cheruiyot", "Mutiso", "Odhiambo", "Achieng", "Wanjiku", "Kariuki",
    "Omondi", "Chebet", "Korir", "Mutua", "Nduta", "Onyango",
    "Barasa", "Wekesa", "Juma", "Hassan", "Abdi", "Mohamed",
    "Kilonzo", "Musyoka", "Ngugi", "Rotich", "Bett", "Koech",
    "Maina", "Mbogo", "Kuria", "Gitau", "Njenga", "Kimani",
    "Muthoni", "Ochieng", "Owino", "Nyambane", "Matano", "Mwakio",
    "Charo", "Baya", "Katana",
]

INSTITUTIONS = [
    "University of Nairobi",
    "Kenyatta University",
    "Strathmore University",
    "Jomo Kenyatta University",
    "Moi University",
    "Maseno University",
    "Mount Kenya University",
    "Africa Nazarene University",
    "Daystar University",
    "Catholic University of Eastern Africa",
]

EDUCATION_LEVEL_WEIGHTS = [
    ("Diploma", 0.25),
    ("Bachelor", 0.60),
    ("Master", 0.15),
]

ACTIVITY_SESSIONS = {
    "Life Skills": (10, 14),
    "Financial Literacy": (8, 12),
    "Leadership": (8, 12),
    "Mentorship": (12, 20),
    "Community Service": (6, 10),
    "Entrepreneurship": (10, 16),
    "Health & Wellness": (6, 10),
}

VOCATIONAL_COURSES = [
    "Tailoring",
    "Carpentry",
    "Plumbing",
    "Electrical Installation",
    "Hairdressing",
    "Beauty Therapy",
    "Motor Vehicle Mechanics",
    "Welding",
    "Cooking & Catering",
    "Agriculture",
]

VOCATIONAL_CENTERS = [
    "Nairobi TVET",
    "Mombasa Technical Training Institute",
    "Kisumu Technical Training Institute",
    "Nakuru Vocational Training Centre",
    "Eldoret Polytechnic",
    "Kakamega Technical Training Institute",
    "Machakos Institute of Technology",
    "Meru Technical Training Institute",
    "Kilifi Vocational Training Centre",
    "Bungoma Technical Training Institute",
    "Nyeri Technical Training Institute",
    "Thika Technical Training Institute",
    "Kisii National Polytechnic",
]

COUNTY_VOCATIONAL_CENTER = {
    "Nairobi": "Nairobi TVET",
    "Mombasa": "Mombasa Technical Training Institute",
    "Kisumu": "Kisumu Technical Training Institute",
    "Nakuru": "Nakuru Vocational Training Centre",
    "Uasin Gishu": "Eldoret Polytechnic",
    "Kakamega": "Kakamega Technical Training Institute",
    "Machakos": "Machakos Institute of Technology",
    "Meru": "Meru Technical Training Institute",
    "Kilifi": "Kilifi Vocational Training Centre",
    "Bungoma": "Bungoma Technical Training Institute",
    "Nyeri": "Nyeri Technical Training Institute",
    "Kiambu": "Thika Technical Training Institute",
    "Kisii": "Kisii National Polytechnic",
}

TECH_COURSES = [
    "Web Development",
    "Data Science",
    "Mobile App Development",
    "Digital Marketing",
    "UI/UX Design",
    "Cybersecurity",
    "Cloud Computing",
    "AI & Machine Learning",
]

TECH_PROVIDERS = [
    "Andela",
    "Moringa School",
    "Akirachix",
    "Power Learn Project",
    "Gebeya",
    "eMobilis",
]

TECH_SKILLS = {
    "Web Development": ["HTML/CSS", "JavaScript", "React", "Node.js", "REST APIs", "Git"],
    "Data Science": ["Python", "SQL", "Pandas", "Machine Learning", "Data Visualization", "Statistics"],
    "Mobile App Development": ["Flutter", "Kotlin", "Swift", "React Native", "Firebase"],
    "Digital Marketing": ["SEO", "Social Media Marketing", "Google Ads", "Content Strategy", "Analytics"],
    "UI/UX Design": ["Figma", "Wireframing", "Prototyping", "User Research", "Design Systems"],
    "Cybersecurity": ["Network Security", "Ethical Hacking", "Risk Assessment", "Incident Response"],
    "Cloud Computing": ["AWS", "Azure", "Docker", "Kubernetes", "Linux Administration"],
    "AI & Machine Learning": ["Python", "TensorFlow", "NLP", "Computer Vision", "Model Deployment"],
}

OUTCOME_TYPE_WEIGHTS = [
    ("Employment", 0.35),
    ("Self-Employment", 0.20),
    ("Further Education", 0.25),
    ("Community Impact", 0.20),
]

OUTCOME_ACHIEVED_BASE = 0.55

SCHOLARSHIP_TAKE_UP = 0.35
PLUS_TAKE_UP = 0.45
VOCATIONAL_TAKE_UP = 0.15
TECH_TAKE_UP = 0.20

SCHOLARSHIP_COMPLETION = 0.85
PLUS_COMPLETION = 0.75
TECH_COMPLETION_START = 0.75
TECH_COMPLETION_END = 0.82
VOCATIONAL_COMPLETION_START = 0.72
VOCATIONAL_COMPLETION_END = 0.68

COUNTY_INCONSISTENCY_RATE = 0.10
GENDER_INCONSISTENCY_RATE = 0.08
STATUS_INCONSISTENCY_RATE = 0.10
PROGRAM_INCONSISTENCY_RATE = 0.03
DUPLICATE_RATE = 0.02

BENEFICIARY_COLUMNS = [
    "beneficiary_id", "first_name", "last_name", "gender",
    "date_of_birth", "age", "phone", "email",
    "county", "sub_county",
]

SCHOLARSHIP_COLUMNS = [
    "beneficiary_id", "first_name", "last_name", "gender", "county",
    "program", "institution", "education_level", "academic_year",
    "attendance_rate", "performance_score", "completion_status",
    "enrollment_date", "reporting_period", "status",
]

PLUS_COLUMNS = [
    "beneficiary_id", "first_name", "last_name", "gender", "county",
    "program", "activity", "sessions_attended", "sessions_expected",
    "participation_rate", "completion_status",
    "enrollment_date", "reporting_period", "status",
]

VOCATIONAL_COLUMNS = [
    "beneficiary_id", "first_name", "last_name", "gender", "county",
    "program", "course", "training_center", "attendance_rate",
    "completion_status", "certification_status", "employment_status",
    "enrollment_date", "reporting_period", "status",
]

TECH_COLUMNS = [
    "beneficiary_id", "first_name", "last_name", "gender", "county",
    "program", "course", "training_provider", "attendance_rate",
    "completion_status", "skills_acquired", "employment_status",
    "enrollment_date", "reporting_period", "status",
]

ATTENDANCE_COLUMNS = [
    "beneficiary_id", "program", "reporting_period",
    "sessions_expected", "sessions_attended", "attendance_rate",
]

OUTCOME_COLUMNS = [
    "beneficiary_id", "program", "reporting_period",
    "outcome_type", "outcome_status", "employment_status",
    "completion_status",
]


def weighted_choice(pairs):
    population = [item for item, weight in pairs]
    weights = [weight for item, weight in pairs]
    return random.choices(population, weights=weights, k=1)[0]


def clamp(value, low, high):
    return max(low, min(high, value))


def quarter_bounds(quarter_label):
    quarter_part, year_part = quarter_label.split(" ")
    quarter_number = int(quarter_part.replace("Q", ""))
    year = int(year_part)
    start_month = 3 * (quarter_number - 1) + 1
    start = date(year, start_month, 1)
    if quarter_number == 4:
        end = date(year, 12, 31)
    else:
        end = date(year, start_month + 3, 1) - timedelta(days=1)
    return start, end


def random_date_in_quarter(quarter_label):
    start, end = quarter_bounds(quarter_label)
    span_days = (end - start).days
    return start + timedelta(days=random.randint(0, span_days))


def academic_year_for(enrolled_on):
    if enrolled_on.month >= 9:
        return f"{enrolled_on.year}/{enrolled_on.year + 1}"
    return f"{enrolled_on.year - 1}/{enrolled_on.year}"


def build_email(first_name, last_name):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    handle = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
    return f"{handle}@{random.choice(domains)}"


def completion_probability(program, county, quarter_index):
    fraction = quarter_index / (len(QUARTERS) - 1)
    if program == "Scholarship":
        base = SCHOLARSHIP_COMPLETION
    elif program == "Plus":
        base = PLUS_COMPLETION
    elif program == "Tech":
        base = TECH_COMPLETION_START + (TECH_COMPLETION_END - TECH_COMPLETION_START) * fraction
    elif program == "Vocational":
        base = VOCATIONAL_COMPLETION_START + (VOCATIONAL_COMPLETION_END - VOCATIONAL_COMPLETION_START) * fraction
    else:
        base = 0.80
    adjusted = base * COUNTY_PERFORMANCE.get(county, 1.0)
    return clamp(adjusted, 0.05, 0.95)


def decide_completion(program, county, quarter_index, duration):
    end_index = quarter_index + duration
    if end_index >= len(QUARTERS):
        return "In Progress", "Active"
    probability = completion_probability(program, county, quarter_index)
    if random.random() < probability:
        return "Completed", "Completed"
    return "Dropped", "Dropped"


def employment_status_for(completion_status, county):
    performance = COUNTY_PERFORMANCE.get(county, 1.0)
    if completion_status == "Completed":
        roll = random.random() / max(performance, 0.1)
        if roll < 0.40:
            return "Employed"
        if roll < 0.62:
            return "Self-Employed"
        if roll < 0.72:
            return "Internship"
        return "Unemployed"
    roll = random.random()
    if roll < 0.55:
        return "Unemployed"
    if roll < 0.80:
        return "Self-Employed"
    return "Employed"


def build_attendance_rows(beneficiary_id, program, start_index, duration, completed):
    rows = []
    final_index = min(start_index + duration, len(QUARTERS) - 1)
    for quarter_index in range(start_index, final_index + 1):
        if program == "Scholarship":
            sessions_expected = random.randint(18, 28)
        elif program == "Plus":
            sessions_expected = random.randint(6, 14)
        else:
            sessions_expected = random.randint(8, 16)
        share_floor = 0.70 if completed else 0.50
        share = random.uniform(share_floor, 1.0)
        if not completed and quarter_index == final_index:
            share *= 0.6
        sessions_attended = int(round(sessions_expected * share))
        attendance_rate = round(sessions_attended / sessions_expected * 100, 1)
        rows.append({
            "beneficiary_id": beneficiary_id,
            "program": program,
            "reporting_period": QUARTERS[quarter_index],
            "sessions_expected": sessions_expected,
            "sessions_attended": sessions_attended,
            "attendance_rate": attendance_rate,
        })
    return rows


def generate_beneficiaries():
    records = []
    for sequence in range(1, N_BENEFICIARIES + 1):
        gender = "Female" if random.random() < FEMALE_SHARE else "Male"
        first_name = random.choice(FEMALE_NAMES if gender == "Female" else MALE_NAMES)
        last_name = random.choice(SURNAMES)
        target_age = random.randint(MIN_AGE, MAX_AGE)
        date_of_birth = TODAY - timedelta(days=target_age * 365 + random.randint(0, 364))
        age = int((TODAY - date_of_birth).days // 365.25)
        county = weighted_choice(list(COUNTY_WEIGHTS.items()))
        sub_county = random.choice(SUB_COUNTIES[county])
        phone = None if random.random() < PHONE_NULL_RATE else f"+2547{random.randint(10000000, 99999999)}"
        email = None if random.random() < EMAIL_NULL_RATE else build_email(first_name, last_name)
        records.append({
            "beneficiary_id": f"BEN-{sequence:06d}",
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "date_of_birth": date_of_birth.isoformat(),
            "age": age,
            "phone": phone,
            "email": email,
            "county": county,
            "sub_county": sub_county,
        })
    return records


def generate_scholarship(beneficiary_records):
    records = []
    attendance_rows = []
    for beneficiary in beneficiary_records:
        if random.random() >= SCHOLARSHIP_TAKE_UP:
            continue
        quarter_index = weighted_choice(list(enumerate(QUARTER_GROWTH_WEIGHTS)))
        duration = random.randint(2, 4)
        county = beneficiary["county"]
        completion_status, status = decide_completion("Scholarship", county, quarter_index, duration)
        enrolled_on = random_date_in_quarter(QUARTERS[quarter_index])
        attendance_rate = round(clamp(random.gauss(84, 9) * COUNTY_PERFORMANCE.get(county, 1.0), 40, 100), 1)
        performance_score = round(clamp(random.gauss(64, 11) * COUNTY_PERFORMANCE.get(county, 1.0), 30, 100), 1)
        records.append({
            "beneficiary_id": beneficiary["beneficiary_id"],
            "first_name": beneficiary["first_name"],
            "last_name": beneficiary["last_name"],
            "gender": beneficiary["gender"],
            "county": county,
            "program": "Scholarship",
            "institution": random.choice(INSTITUTIONS),
            "education_level": weighted_choice(EDUCATION_LEVEL_WEIGHTS),
            "academic_year": academic_year_for(enrolled_on),
            "attendance_rate": attendance_rate,
            "performance_score": performance_score,
            "completion_status": completion_status,
            "enrollment_date": enrolled_on.isoformat(),
            "reporting_period": QUARTERS[quarter_index],
            "status": status,
        })
        attendance_rows.extend(
            build_attendance_rows(
                beneficiary["beneficiary_id"],
                "Scholarship",
                quarter_index,
                duration,
                completion_status == "Completed",
            )
        )
    return pd.DataFrame(records, columns=SCHOLARSHIP_COLUMNS), attendance_rows


def generate_plus(beneficiary_records):
    records = []
    attendance_rows = []
    for beneficiary in beneficiary_records:
        if random.random() >= PLUS_TAKE_UP:
            continue
        quarter_index = weighted_choice(list(enumerate(QUARTER_GROWTH_WEIGHTS)))
        duration = random.randint(1, 3)
        county = beneficiary["county"]
        completion_status, status = decide_completion("Plus", county, quarter_index, duration)
        enrolled_on = random_date_in_quarter(QUARTERS[quarter_index])
        activity = random.choice(list(ACTIVITY_SESSIONS.keys()))
        low, high = ACTIVITY_SESSIONS[activity]
        sessions_expected = random.randint(low, high)
        share = clamp(random.gauss(0.78, 0.15) * COUNTY_PERFORMANCE.get(county, 1.0), 0.25, 1.0)
        if completion_status == "Dropped":
            share *= 0.65
        sessions_attended = int(round(sessions_expected * share))
        participation_rate = round(sessions_attended / sessions_expected * 100, 1)
        records.append({
            "beneficiary_id": beneficiary["beneficiary_id"],
            "first_name": beneficiary["first_name"],
            "last_name": beneficiary["last_name"],
            "gender": beneficiary["gender"],
            "county": county,
            "program": "Plus",
            "activity": activity,
            "sessions_attended": sessions_attended,
            "sessions_expected": sessions_expected,
            "participation_rate": participation_rate,
            "completion_status": completion_status,
            "enrollment_date": enrolled_on.isoformat(),
            "reporting_period": QUARTERS[quarter_index],
            "status": status,
        })
        attendance_rows.extend(
            build_attendance_rows(
                beneficiary["beneficiary_id"],
                "Plus",
                quarter_index,
                duration,
                completion_status == "Completed",
            )
        )
    return pd.DataFrame(records, columns=PLUS_COLUMNS), attendance_rows


def generate_vocational(beneficiary_records):
    records = []
    attendance_rows = []
    for beneficiary in beneficiary_records:
        if random.random() >= VOCATIONAL_TAKE_UP:
            continue
        quarter_index = weighted_choice(list(enumerate(QUARTER_GROWTH_WEIGHTS)))
        duration = random.randint(2, 4)
        county = beneficiary["county"]
        completion_status, status = decide_completion("Vocational", county, quarter_index, duration)
        enrolled_on = random_date_in_quarter(QUARTERS[quarter_index])
        course = random.choice(VOCATIONAL_COURSES)
        training_center = COUNTY_VOCATIONAL_CENTER.get(county) or random.choice(VOCATIONAL_CENTERS)
        attendance_rate = round(clamp(random.gauss(80, 10) * COUNTY_PERFORMANCE.get(county, 1.0), 35, 100), 1)
        if completion_status == "Completed":
            certification_status = "Certified" if random.random() < 0.85 else "Pending"
        elif completion_status == "In Progress":
            certification_status = "Pending"
        else:
            certification_status = "Not Certified"
        employment_status = employment_status_for(completion_status, county)
        records.append({
            "beneficiary_id": beneficiary["beneficiary_id"],
            "first_name": beneficiary["first_name"],
            "last_name": beneficiary["last_name"],
            "gender": beneficiary["gender"],
            "county": county,
            "program": "Vocational",
            "course": course,
            "training_center": training_center,
            "attendance_rate": attendance_rate,
            "completion_status": completion_status,
            "certification_status": certification_status,
            "employment_status": employment_status,
            "enrollment_date": enrolled_on.isoformat(),
            "reporting_period": QUARTERS[quarter_index],
            "status": status,
        })
        attendance_rows.extend(
            build_attendance_rows(
                beneficiary["beneficiary_id"],
                "Vocational",
                quarter_index,
                duration,
                completion_status == "Completed",
            )
        )
    return pd.DataFrame(records, columns=VOCATIONAL_COLUMNS), attendance_rows


def generate_tech(beneficiary_records):
    records = []
    attendance_rows = []
    for beneficiary in beneficiary_records:
        if random.random() >= TECH_TAKE_UP:
            continue
        quarter_index = weighted_choice(list(enumerate(QUARTER_GROWTH_WEIGHTS)))
        duration = random.randint(1, 3)
        county = beneficiary["county"]
        completion_status, status = decide_completion("Tech", county, quarter_index, duration)
        enrolled_on = random_date_in_quarter(QUARTERS[quarter_index])
        course = random.choice(TECH_COURSES)
        training_provider = random.choice(TECH_PROVIDERS)
        attendance_rate = round(clamp(random.gauss(82, 10) * COUNTY_PERFORMANCE.get(county, 1.0), 35, 100), 1)
        skill_pool = TECH_SKILLS.get(course, ["Digital Literacy"])
        skills_acquired = "; ".join(
            sorted(random.sample(skill_pool, k=min(len(skill_pool), random.randint(2, 4))))
        )
        employment_status = employment_status_for(completion_status, county)
        records.append({
            "beneficiary_id": beneficiary["beneficiary_id"],
            "first_name": beneficiary["first_name"],
            "last_name": beneficiary["last_name"],
            "gender": beneficiary["gender"],
            "county": county,
            "program": "Tech",
            "course": course,
            "training_provider": training_provider,
            "attendance_rate": attendance_rate,
            "completion_status": completion_status,
            "skills_acquired": skills_acquired,
            "employment_status": employment_status,
            "enrollment_date": enrolled_on.isoformat(),
            "reporting_period": QUARTERS[quarter_index],
            "status": status,
        })
        attendance_rows.extend(
            build_attendance_rows(
                beneficiary["beneficiary_id"],
                "Tech",
                quarter_index,
                duration,
                completion_status == "Completed",
            )
        )
    return pd.DataFrame(records, columns=TECH_COLUMNS), attendance_rows


def outcome_employment(outcome_type, outcome_status):
    if outcome_status == "Achieved":
        if outcome_type == "Employment":
            return "Employed"
        if outcome_type == "Self-Employment":
            return "Self-Employed"
        if outcome_type == "Further Education":
            return random.choice(["In Training", "Unemployed"])
        return random.choice(["Employed", "Self-Employed", "Unemployed"])
    return random.choice(["Unemployed", "Unemployed", "Self-Employed", "Employed"])


def generate_outcomes(program_frames):
    rows = []
    for program, frame in program_frames.items():
        completed = frame[frame["completion_status"] == "Completed"]
        for _, record in completed.iterrows():
            if random.random() > 0.90:
                continue
            county_value = record["county"]
            outcome_type = weighted_choice(OUTCOME_TYPE_WEIGHTS)
            achieved_probability = OUTCOME_ACHIEVED_BASE * COUNTY_PERFORMANCE.get(county_value, 1.0)
            if program == "Tech":
                achieved_probability *= 1.10
            elif program == "Vocational":
                achieved_probability *= 0.92
            roll = random.random()
            if roll < achieved_probability:
                outcome_status = "Achieved"
            elif roll < achieved_probability + 0.30:
                outcome_status = "In Progress"
            else:
                outcome_status = "Not Achieved"
            rows.append({
                "beneficiary_id": record["beneficiary_id"],
                "program": program,
                "reporting_period": record["reporting_period"],
                "outcome_type": outcome_type,
                "outcome_status": outcome_status,
                "employment_status": outcome_employment(outcome_type, outcome_status),
                "completion_status": "Completed",
            })
    return pd.DataFrame(rows, columns=OUTCOME_COLUMNS)


def corrupt_county_name(county):
    roll = random.random()
    if roll < 0.35:
        return county.upper().replace(" ", "_")
    if roll < 0.70:
        return county.lower()
    return f"{county} County"


def corrupt_gender(gender):
    variants = {
        "Female": ["F", "f", "FEMALE", "female"],
        "Male": ["M", "m", "male", "MALE"],
    }
    options = variants.get(gender)
    if not options:
        return gender
    return random.choice(options)


def corrupt_status(status):
    variants = {
        "Completed": ["complete", "COMPLETED"],
        "Active": ["Active", "active"],
        "Dropped": ["DROPPED", "dropped out"],
    }
    options = variants.get(status)
    if not options:
        return status
    return random.choice(options)


def corrupt_program_name(program):
    variants = {
        "Scholarship": ["SCHOLARSHIP", "scholarship program"],
        "Plus": ["PLUS PROGRAM", "plus"],
        "Vocational": ["vocational", "VOCATIONAL PROGRAM"],
        "Tech": ["tech", "TECH PROGRAM"],
    }
    options = variants.get(program)
    if not options:
        return program
    return random.choice(options)


def apply_corruption(frame, column, rate, corruptor, seed):
    dirty_indices = frame.sample(frac=rate, random_state=seed).index
    if len(dirty_indices) > 0:
        frame.loc[dirty_indices, column] = frame.loc[dirty_indices, column].map(corruptor)
    return int(len(dirty_indices))


def apply_data_quality_issues(beneficiaries_df, scholarship_df, plus_df, vocational_df, tech_df):
    report = {}

    report["county_beneficiaries"] = apply_corruption(
        beneficiaries_df, "county", COUNTY_INCONSISTENCY_RATE, corrupt_county_name, 11
    )
    report["gender_beneficiaries"] = apply_corruption(
        beneficiaries_df, "gender", GENDER_INCONSISTENCY_RATE, corrupt_gender, 12
    )

    program_frames = [
        ("Scholarship", scholarship_df),
        ("Plus", plus_df),
        ("Vocational", vocational_df),
        ("Tech", tech_df),
    ]

    for offset, (name, frame) in enumerate(program_frames, start=1):
        slug = name.lower()
        report[f"county_{slug}"] = apply_corruption(
            frame, "county", COUNTY_INCONSISTENCY_RATE, corrupt_county_name, 20 + offset
        )
        report[f"gender_{slug}"] = apply_corruption(
            frame, "gender", GENDER_INCONSISTENCY_RATE, corrupt_gender, 30 + offset
        )
        report[f"program_{slug}"] = apply_corruption(
            frame, "program", PROGRAM_INCONSISTENCY_RATE, corrupt_program_name, 40 + offset
        )
        report[f"completion_status_{slug}"] = apply_corruption(
            frame, "completion_status", STATUS_INCONSISTENCY_RATE, corrupt_status, 50 + offset
        )
        report[f"status_{slug}"] = apply_corruption(
            frame, "status", STATUS_INCONSISTENCY_RATE, corrupt_status, 60 + offset
        )

    duplicate_rows = beneficiaries_df.sample(frac=DUPLICATE_RATE, random_state=101)
    beneficiaries_with_duplicates = pd.concat(
        [beneficiaries_df, duplicate_rows], ignore_index=True
    )
    beneficiaries_final = beneficiaries_with_duplicates.sample(
        frac=1.0, random_state=202
    ).reset_index(drop=True)
    report["duplicate_beneficiary_rows"] = int(len(duplicate_rows))

    return beneficiaries_final, report


def print_trends(program_frames):
    print("-" * 70)
    print("Embedded trends (clean data, before quality issues)")
    for name in ["Tech", "Vocational"]:
        frame = program_frames[name]
        decided = frame[frame["completion_status"].isin(["Completed", "Dropped"])]
        totals = decided.groupby("reporting_period").size()
        completions = decided[decided["completion_status"] == "Completed"].groupby("reporting_period").size()
        summary = pd.DataFrame({"enrolled": totals, "completed": completions}).fillna(0).astype(int)
        summary["completion_rate"] = (summary["completed"] / summary["enrolled"]).round(3)
        print(f"\n{name} completion rate by quarter:")
        print(summary.to_string())
    all_enrollments = pd.concat(list(program_frames.values()), ignore_index=True)
    enrolment_by_quarter = all_enrollments.groupby("reporting_period")["beneficiary_id"].nunique()
    print("\nUnique beneficiaries enrolled per quarter (all programmes):")
    print(enrolment_by_quarter.to_string())
    print("-" * 70)


def write_summary(summary_rows):
    path = DATA_RAW_DIR / "generation_summary.csv"
    fieldnames = ["run_id", "generated_at", "file", "rows", "columns"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"wrote {path}")


def generate_all():
    run_id = str(uuid.uuid4())
    generated_at = datetime.now().isoformat(timespec="seconds")

    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    print("=" * 70)
    print("Kenyan NGO synthetic data generator")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Output dir   : {DATA_RAW_DIR}")
    print(f"Run id       : {run_id}")
    print(f"Generated at : {generated_at}")
    print("=" * 70)

    beneficiary_records = generate_beneficiaries()
    beneficiaries_df = pd.DataFrame(beneficiary_records, columns=BENEFICIARY_COLUMNS)
    print(f"beneficiaries : {len(beneficiaries_df)} rows (clean)")

    scholarship_df, scholarship_attendance = generate_scholarship(beneficiary_records)
    plus_df, plus_attendance = generate_plus(beneficiary_records)
    vocational_df, vocational_attendance = generate_vocational(beneficiary_records)
    tech_df, tech_attendance = generate_tech(beneficiary_records)

    print(f"scholarship   : {len(scholarship_df)} rows")
    print(f"plus          : {len(plus_df)} rows")
    print(f"vocational    : {len(vocational_df)} rows")
    print(f"tech          : {len(tech_df)} rows")

    attendance_rows = (
        scholarship_attendance
        + plus_attendance
        + vocational_attendance
        + tech_attendance
    )
    attendance_df = pd.DataFrame(attendance_rows, columns=ATTENDANCE_COLUMNS)
    print(f"attendance    : {len(attendance_df)} rows")

    clean_program_frames = {
        "Scholarship": scholarship_df,
        "Plus": plus_df,
        "Vocational": vocational_df,
        "Tech": tech_df,
    }
    outcomes_df = generate_outcomes(clean_program_frames)
    print(f"outcomes      : {len(outcomes_df)} rows")

    print_trends(clean_program_frames)

    beneficiaries_final, corruption_report = apply_data_quality_issues(
        beneficiaries_df, scholarship_df, plus_df, vocational_df, tech_df
    )

    print("Applied data quality issues:")
    for issue, affected in corruption_report.items():
        print(f"  {issue:<30} {affected:>5} rows")

    files_to_write = [
        ("beneficiaries.csv", beneficiaries_final),
        ("scholarship.csv", scholarship_df),
        ("plus.csv", plus_df),
        ("vocational.csv", vocational_df),
        ("tech.csv", tech_df),
        ("attendance.csv", attendance_df),
        ("outcomes.csv", outcomes_df),
    ]

    summary_rows = []
    for filename, frame in files_to_write:
        path = DATA_RAW_DIR / filename
        frame.to_csv(path, index=False)
        summary_rows.append({
            "run_id": run_id,
            "generated_at": generated_at,
            "file": filename,
            "rows": len(frame),
            "columns": len(frame.columns),
        })
        print(f"wrote {path} ({len(frame)} rows x {len(frame.columns)} cols)")

    write_summary(summary_rows)
    print("Done.")


if __name__ == "__main__":
    generate_all()
