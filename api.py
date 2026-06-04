import psycopg2
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI(title="MoH CHW Ingestion API")

# --- DATABASE CONNECTION ---
def get_db():
    return psycopg2.connect(
        host="localhost", port=5435, database="epidemiological_data",
        user="health_admin", password="HealthPassword2026"
    )

# --- INITIALIZE TABLES ---
def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Create the raw reports table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chw_reports (
            report_id VARCHAR(50) PRIMARY KEY,
            chw_id VARCHAR(50),
            timestamp TIMESTAMP,
            county VARCHAR(50),
            sub_county VARCHAR(50),
            patient_age INT,
            symptom_fever BOOLEAN,
            symptom_cough BOOLEAN,
            symptom_diarrhea BOOLEAN,
            symptom_vomiting BOOLEAN
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("[✓] PostGIS Database Initialized.")

init_db()

# --- DATA SCHEMA ---
class CHWReport(BaseModel):
    report_id: str
    chw_id: str
    county: str
    sub_county: str
    patient_age: int
    symptom_fever: bool = False
    symptom_cough: bool = False
    symptom_diarrhea: bool = False
    symptom_vomiting: bool = False

# --- ASYNC DATABASE INSERTION ---
def insert_report(report: CHWReport):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chw_reports 
        (report_id, chw_id, timestamp, county, sub_county, patient_age, 
         symptom_fever, symptom_cough, symptom_diarrhea, symptom_vomiting)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        report.report_id, report.chw_id, datetime.utcnow().isoformat(),
        report.county, report.sub_county, report.patient_age,
        report.symptom_fever, report.symptom_cough, 
        report.symptom_diarrhea, report.symptom_vomiting
    ))
    conn.commit()
    cur.close()
    conn.close()

# --- THE ENDPOINT ---
@app.post("/ingest")
async def ingest_chw_report(report: CHWReport, background_tasks: BackgroundTasks):
    """
    Receives JSON payload from CHW mobile app and inserts it into PostGIS asynchronously.
    """
    # Using background tasks ensures the API responds instantly to the mobile app
    background_tasks.add_task(insert_report, report)
    return {"status": "success", "message": "Report logged"}

if __name__ == "__main__":
    print(" Starting MoH Ingestion API on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)