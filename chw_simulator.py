import requests
import random
import uuid
import time

API_URL = "http://localhost:8000/ingest"

# Kenyan Counties and Sub-Counties
LOCATIONS = {
    "Nairobi": ["Kibra", "Westlands", "Makadara"],
    "Mombasa": ["Nyali", "Likoni", "Mvita"],
    "Kisumu": ["Kisumu Central", "Kisumu East", "Nyando"],
    "Turkana": ["Turkana Central", "Turkana West", "Loima"]
}

def generate_normal_report():
    """Generates standard, baseline health reports (mostly healthy, some common colds/fever)."""
    county = random.choice(list(LOCATIONS.keys()))
    sub_county = random.choice(LOCATIONS[county])
    
    return {
        "report_id": f"REP_{uuid.uuid4().hex[:8].upper()}",
        "chw_id": f"CHW_{random.randint(100, 999)}",
        "county": county,
        "sub_county": sub_county,
        "patient_age": random.randint(1, 80),
        "symptom_fever": random.random() < 0.15,  # 15% chance of routine fever
        "symptom_cough": random.random() < 0.20,  # 20% chance of cough
        "symptom_diarrhea": random.random() < 0.05, # Very low baseline
        "symptom_vomiting": random.random() < 0.02  # Very low baseline
    }

def inject_cholera_outbreak():
    """Injects a severe anomaly (Cholera symptoms) in Turkana."""
    return {
        "report_id": f"REP_{uuid.uuid4().hex[:8].upper()}",
        "chw_id": f"CHW_TURK_{random.randint(10, 50)}",
        "county": "Turkana",
        "sub_county": random.choice(LOCATIONS["Turkana"]),
        "patient_age": random.randint(1, 60),
        "symptom_fever": random.random() < 0.40,
        "symptom_cough": random.random() < 0.10,
        "symptom_diarrhea": True, # 100% chance for this payload
        "symptom_vomiting": True  # 100% chance for this payload
    }

if __name__ == "__main__":
    print(" Starting CHW App Simulator...")
    print("Sending reports to FastAPI Endpoint (http://localhost:8000/ingest)")
    
    try:
        while True:
            # 90% normal background disease rates across Kenya
            if random.random() < 0.90:
                payload = generate_normal_report()
                response = requests.post(API_URL, json=payload)
                print(f"[Routine] {payload['county']} - {payload['sub_county']} | Fever: {payload['symptom_fever']} | Diarrhea: {payload['symptom_diarrhea']}")
            
            # 10% localized Cholera outbreak in Turkana
            else:
                payload = inject_cholera_outbreak()
                response = requests.post(API_URL, json=payload)
                print(f"[ OUTBREAK] {payload['county']} - {payload['sub_county']} | Diarrhea: {payload['symptom_diarrhea']} | Vomiting: {payload['symptom_vomiting']}")
            
            # Simulate real-time delay
            time.sleep(random.uniform(0.1, 0.5))
            
    except KeyboardInterrupt:
        print("\n[!] Simulation stopped.")