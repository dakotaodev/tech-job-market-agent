import json
import os
import sqlite3


DATABASE="jobs.db"

def init_db():
    conn=sqlite3.connect(DATABASE)
    cursor=conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE NOT NULL
                   )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
                   id TEXT PRIMARY KEY,
                   title TEXT NOT NULL,
                   company TEXT NOT NULL,
                   location TEXT,
                   remote_ok INTEGER,
                   salary_min INTEGER,
                   salary_max INTEGER,
                   role_level TEXT,
                   full_description TEXT,
                   posted_date TEXT,
                   company_stage TEXT,
                   team_size_estimate TEXT,
                   interview_process TEXT
                   )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_required_skills (
                   job_id TEXT,
                   skill_id TEXT,
                   FOREIGN KEY (job_id) REFERENCES jobs (id),
                   FOREIGN KEY (skill_id) REFERENCES skills (id),
                   PRIMARY KEY (job_id, skill_id)
                   )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_nice_skills (
                   job_id TEXT,
                   skill_id TEXT,
                   FOREIGN KEY (job_id) REFERENCES jobs (id),
                   FOREIGN KEY (skill_id) REFERENCES skills (id),
                   PRIMARY KEY (job_id, skill_id)
                   )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company on jobs (company)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_role_level on jobs (role_level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_location on jobs (location)")


    conn.commit()
    conn.close()



def load_jobs(path: str):

    if not os.path.exists(path):
        raise FileNotFoundError(f"File was not found @ {path}")
    
    with open(path,"r") as file:
        data = json.load(file)

    
    conn=sqlite3.connect(DATABASE)
    cursor=conn.cursor()

    
    for job in data:
        # Upsert into jobs table
        cursor.execute("""
            INSERT OR REPLACE INTO jobs (
                id, title, company, location, remote_ok, salary_min, salary_max,
                role_level, full_description, posted_date, company_stage,
                team_size_estimate, interview_process
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["id"], job["title"], job["company"], job["location"],
            1 if job.get("remote_ok", False) else 0,  # Convert bool to int
            job["salary_min"], job["salary_max"], job["role_level"],
            job["full_description"], job["posted_date"], job["company_stage"],
            job["team_size_estimate"], job.get("interview_process")
        ))
        
        # Helper to upsert skills and link to job
        def upsert_skills(skill_list, junction_table):
            for skill_name in skill_list:
                # Insert skill if not exists
                cursor.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill_name,))
                # Get skill_id (use lastrowid if inserted, otherwise query)
                if cursor.lastrowid:
                    skill_id = cursor.lastrowid
                else:
                    cursor.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
                    skill_id = cursor.fetchone()[0]
                # Link job to skill in junction table
                cursor.execute(f"INSERT OR IGNORE INTO {junction_table} (job_id, skill_id) VALUES (?, ?)",
                               (job["id"], skill_id))
        
        # Upsert required skills
        upsert_skills(job["required_skills"], "job_required_skills")
        # Upsert nice-to-have skills
        upsert_skills(job["nice_to_have_skills"], "job_nice_skills")

    conn.commit()
    conn.close()