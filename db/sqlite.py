# 1. Import Library 

import json
import sqlite3
import os 

# 2. Create new database directory for jobs.db 

jsonl_file = "data/jobs.jsonl"
db_file = "data/jobs.db"

# 3. Create sqlite connection
class SQLiteManager:
    def __init__(self, db_file="data/jobs.db"):
        """
        Function to initialize database connection to sqlite
        """
        # 3.1 Make sure file is exist, if not create it
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.db_file = db_file

        # 3.2 Connect to database
        self.con = sqlite3.connect(self.db_file, check_same_thread=False)
        self.con.row_factory = sqlite3.Row # -> We can call row for next usage

        # 3.3 Create table using hidden function
        self._create_table()

    # 4. Hidden function to create table
    def _create_table(self):
        """
        Function to create table if not exist
        """
        table_query = """
        CREATE TABLE IF NOT EXISTS jobs_posting(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company_name TEXT,
            location TEXT,
            work_type TEXT,
            salary TEXT,
            job_description TEXT
        )
        """
        try:
            with self.con:
                self.con.execute(table_query)
                print("Table created successfully")
        except Exception as e:
            print(f"Error: {e}")
    # 5. Input jobs.json to sqlite database
    def insert_jobs(self, jsonl_file="data/jobs.jsonl"):
        """
        Function to insert jobs data to sqlite database
        """
        # 5.1 Ensure file is exist
        if not os.path.exists(jsonl_file):
            print(f"Error: {jsonl_file} not found")
            return
        # 5.2 Print if data inserted    
        print(f"Inserting jobs from {jsonl_file} to sqlite database...")
        try:
            # 5.3 Ensure table has content, if it dont have, it can fill in the jobs.jsonl
            check_table = self.con.execute("SELECT 1 FROM jobs_posting LIMIT 1").fetchone()
            if check_table is not None:
                print("Table already has content")
                return
            else:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    with self.con:
                        count = 0
                        for line in f:
                            
        except Exception as e:
            print(f"Error: {e}")
            pass

    

try:
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            job = json.loads(line)
            cur.execute(
                """
                INSERT INTO jobs_posting(
                    job_title,
                    company_name,
                    location,
                    work_type,
                    salary,
                    job_description
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_title"],
                    job["company_name"],
                    job["location"],
                    job["work_type"],
                    job["salary"],
                    job["job_description"]
                )
            )
    con.commit()
    print("Jobs data inserted successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    con.close()
    print("Connection closed")