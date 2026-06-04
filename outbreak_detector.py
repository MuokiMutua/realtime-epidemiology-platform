import pandas as pd
from sklearn.ensemble import IsolationForest
import psycopg2
import warnings

warnings.filterwarnings("ignore")

# --- DATABASE CONNECTION ---
def get_db():
    return psycopg2.connect(
        host="localhost", port=5435, database="epidemiological_data",
        user="health_admin", password="HealthPassword2026"
    )

def run_anomaly_detection():
    print("🧬 Initializing Isolation Forest Anomaly Detection...")
    
    # 1. Fetch the aggregated data built by dbt
    conn = get_db()
    query = """
        SELECT report_week, county, sub_county, total_visits, 
               total_fever, total_cough, total_diarrhea, total_vomiting
        FROM analytical_marts.mart_weekly_symptoms
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if len(df) < 5:
        print("[!] Not enough aggregated data yet. Let the simulator run longer!")
        return

    # 2. Feature Engineering: Convert raw counts to percentages
    # A county with 10,000 visits will naturally have more diarrhea than a county with 100 visits.
    # We must look at the *rate* of symptoms to find true anomalies.
    df['fever_rate'] = df['total_fever'] / df['total_visits']
    df['diarrhea_rate'] = df['total_diarrhea'] / df['total_visits']
    df['vomiting_rate'] = df['total_vomiting'] / df['total_visits']

    # Define the features the ML model will look at
    features = ['fever_rate', 'diarrhea_rate', 'vomiting_rate']
    X = df[features].fillna(0)

    # 3. Train the Isolation Forest
    # contamination=0.05 means we assume roughly 5% of our data might be outbreaks
    model = IsolationForest(contamination=0.05, random_state=42)
    
    # Fit the model and predict anomalies (-1 is an anomaly, 1 is normal)
    df['anomaly_score'] = model.fit_predict(X)

    # 4. Filter and Output the Results
    outbreaks = df[df['anomaly_score'] == -1]

    print("\n" + "="*60)
    print("🚨 EPIDEMIOLOGICAL ALERTS DETECTED 🚨")
    print("="*60)
    
    if outbreaks.empty:
        print("[✅] No significant localized outbreaks detected. Disease rates normal.")
    else:
        for idx, row in outbreaks.iterrows():
            print(f"⚠️  CRITICAL ANOMALY: {row['county'].upper()} County ({row['sub_county']})")
            print(f"   Week of: {row['report_week']}")
            print(f"   Diarrhea Rate: {row['diarrhea_rate']*100:.1f}% | Vomiting Rate: {row['vomiting_rate']*100:.1f}%")
            print(f"   Total Patient Visits: {row['total_visits']}")
            print("-" * 60)

if __name__ == "__main__":
    run_anomaly_detection()