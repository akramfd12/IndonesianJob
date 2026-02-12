import sqlite3

#Create sqlite for db and table
def create_sqlite(db_name:str, table_name:str, source_data):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        company_name TEXT,
        location TEXT,
        work_type TEXT,
        salary TEXT,
        job_description TEXT,
        scrape_timestamp TEXT,
        salary_min TEXT,
        salary_max TEXT
    )
    """
    cur.execute(query)

    data = source_data
    for item in data:
        cur.execute("""
            INSERT INTO jobs (
                job_title,
                company_name,
                location,
                work_type,
                salary,
                job_description,
                scrape_timestamp,
                salary_min,
                salary_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("job_title"),
            item.get("company_name"),
            item.get("location"),
            item.get("work_type"),
            item.get("salary"),
            item.get("job_description"),
            item.get("_scrape_timestamp"),
            item.get("salary_min"),
            item.get("salary_max")
        ))

    conn.commit()
    conn.close()

#read sqlite data jobs
def read_sql_jobs(db_name: str):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
    SELECT id, job_title, company_name, location, work_type, salary, salary_min, salary_max, job_description
    FROM jobs
    """)
    rows = cur.fetchall()
    conn.close()
    return rows