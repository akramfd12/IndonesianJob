import sqlite3

# ============================================
# CREATE SQLITE DATABASE & TABLE + INSERT DATA
# ============================================
def create_sqlite(db_name: str, table_name: str, source_data):
    """
    Create SQLite database and table (if not exists),
    then insert scraped job data into the table.

    Parameters:
    - db_name: name of sqlite database file (e.g., jobs.db)
    - table_name: name of table to create
    - source_data: iterable of dictionaries containing job data
    """

    # Connect to SQLite database (creates file if not exists)
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    # Create table dynamically (only if not exists)
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

    # Insert scraped data into table
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

    # Save changes to database
    conn.commit()

    # Close connection to free resources
    conn.close()


# ============================================
# READ DATA FROM JOBS TABLE
# ============================================
def read_sql_jobs(db_name: str):
    """
    Read all job records from 'jobs' table.

    Returns:
    - List of tuples containing selected job fields
    """

    # Open database connection
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # Select important job fields (used by SQL Agent / analysis)
    cur.execute("""
    SELECT id, job_title, company_name, location, work_type,
           salary, salary_min, salary_max, job_description
    FROM jobs
    """)

    rows = cur.fetchall()

    # Close connection
    conn.close()

    return rows