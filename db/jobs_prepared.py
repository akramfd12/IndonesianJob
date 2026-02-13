import json
import re
#Prepared Data 

#Read jsonl
def read_jsonl (path_file: str):
    data = []
    with open(path_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

#clean salary data and split min and max
def parse_salary(salary_raw):
    if not salary_raw or salary_raw == "None":
        return 0, 0

    s = salary_raw.replace('\xa0', ' ').lower()

    if 'rp' not in s:
        return 0, 0

    numbers = re.findall(r'\d[\d.,]*', s)
    if not numbers:
        return 0, 0

    values = []
    for n in numbers:
        n = n.replace('.', '').replace(',', '')
        values.append(int(n))

    if len(values) == 1:
        return values[0], values[0]

    return values[0], values[1]

#get clean salary
def clean_salary():
    jobs = read_jsonl("data/jobs.jsonl")
    for job in jobs:
        salary_raw = job.get("salary")

        salary_min, salary_max = parse_salary(salary_raw)

        job["salary_min"] = salary_min
        job["salary_max"] = salary_max


    return jobs