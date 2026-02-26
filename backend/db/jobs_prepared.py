import json
import re

# =========================================================
# DATA PREPARATION MODULE
# =========================================================
# Responsible for:
# - Reading raw JSONL scraped data
# - Cleaning salary field
# - Splitting salary into salary_min & salary_max
# =========================================================


# ---------------------------------------------------------
# READ JSONL FILE
# ---------------------------------------------------------
def read_jsonl (path_file: str):
    """
    Read .jsonl file (one JSON object per line)
    and return list of dictionaries.

    Parameters:
    - path_file: path to jsonl file

    Returns:
    - List[dict]
    """
    data = []
    with open(path_file, "r", encoding="utf-8") as f:
        for line in f:
            # Skip empty lines
            if line.strip():
                data.append(json.loads(line))
    return data


# ---------------------------------------------------------
# PARSE SALARY STRING → (MIN, MAX)
# ---------------------------------------------------------
def parse_salary(salary_raw):
    """
    Extract numeric salary range from raw salary string.

    Example:
    "Rp 5.000.000 - 7.000.000" → (5000000, 7000000)

    Rules:
    - If salary is None / invalid → return (0, 0)
    - If only one value found → min = max
    """

    # If salary is empty or string "None"
    if not salary_raw or salary_raw == "None":
        return 0, 0

    # Normalize string
    s = salary_raw.replace('\xa0', ' ').lower()

    # Ensure it contains Indonesian Rupiah marker
    if 'rp' not in s:
        return 0, 0

    # Extract numeric parts (handles dot & comma formats)
    numbers = re.findall(r'\d[\d.,]*', s)
    if not numbers:
        return 0, 0

    values = []
    for n in numbers:
        # Remove thousand separators
        n = n.replace('.', '').replace(',', '')
        values.append(int(n))

    # If only one number → treat as fixed salary
    if len(values) == 1:
        return values[0], values[0]

    # If range detected → return first two values
    return values[0], values[1]


# ---------------------------------------------------------
# CLEAN SALARY FOR ALL JOB RECORDS
# ---------------------------------------------------------
def clean_salary():
    """
    Load jobs from JSONL file,
    parse salary field,
    and append:
        - salary_min
        - salary_max

    Returns:
    - List of updated job dictionaries
    """

    # Read raw scraped data
    jobs = read_jsonl("data/jobs.jsonl")

    for job in jobs:
        salary_raw = job.get("salary")

        # Parse salary string into numeric min & max
        salary_min, salary_max = parse_salary(salary_raw)

        # Append structured salary fields
        job["salary_min"] = salary_min
        job["salary_max"] = salary_max

    return jobs