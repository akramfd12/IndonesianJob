from db.sqlite import *
from db.jobs_prepared import *
from db.qdrant import *

#insert sqllite
# jobs = read_jsonl("data/jobs.jsonl")
# data = clean_salary()
# create_sqlite(db_name="jobs", table_name="jobs", source_data=data)

#insert qdrant
# a = read_sql_jobs(db_name="jobs.db")
# b = create_document_jobs(rows=a)
# create_qdrant_collection(collection_name="indonesianjobs_collection", documents=b)

def build_vector_database():
    a = read_sql_jobs(db_name="db/jobs.db")
    b = create_document_jobs(rows=a)

    create_qdrant_collection(
        collection_name="indonesianjobs_collection",
        documents=b
    )
    print("Vector DB successfully built.")

if __name__ == "__main__":
    build_vector_database()

