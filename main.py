"""
Step 2 — FastAPI backend that reads FHIR data and translates SNOMED -> ICD-10.
Run:  py -3.11 -m uvicorn main:app --reload
Then open:  http://127.0.0.1:8000/docs   (interactive API explorer)

Endpoints:
  GET /patients                 -> list patients
  GET /patients/{id}            -> patient + conditions, each with an ICD-10 translation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import requests

BASE = "https://r4.smarthealthit.org"  # SMART Health IT sandbox

app = FastAPI(title="FHIR Clinical Viewer", version="0.1")
# allow a frontend (React) to call this API during local dev
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- SNOMED CT -> ICD-10 mapping ---------------------------------------------
# At Virtual Hospitals Africa I built this over a ~214,900-row reference set.
# Here a curated illustrative map shows the same idea end-to-end; expand as needed.
SNOMED_TO_ICD10 = {
    "195662009": "J02.9",   # Acute viral pharyngitis
    "444814009": "J01.90",  # Viral sinusitis
    "10509002":  "J20.9",   # Acute bronchitis
    "55822004":  "E78.5",   # Hyperlipidemia
    "44054006":  "E11.9",   # Type 2 diabetes mellitus
    "38341003":  "I10",     # Essential hypertension
    "43878008":  "J02.0",   # Streptococcal sore throat
    "65363002":  "H66.90",  # Otitis media
    "82423001":  "G89.29",  # Chronic pain
    "239873007": "M17.9",   # Osteoarthritis of knee
    "162864005": "E66.9",   # Obesity (BMI 30+)
    "271737000": "D64.9",   # Anemia
    "64859006":  "M81.0",   # Osteoporosis
    "49436004":  "I48.91",  # Atrial fibrillation
    "88805009":  "I50.9",   # Chronic congestive heart failure
}

# --- ICD-10 -> recommended medication ----------------------------------------
# Mirrors VHA's ICD-10-keyed Essential Medicines List: a diagnosis code drives a
# medication recommendation. ILLUSTRATIVE ONLY — not clinical advice.
ICD10_TO_MEDICATION = {
    "E11.9":  "Metformin",
    "I10":    "Lisinopril",
    "E78.5":  "Atorvastatin",
    "J02.0":  "Penicillin V",
    "J01.90": "Amoxicillin",
    "H66.90": "Amoxicillin",
    "I50.9":  "Furosemide + ACE inhibitor",
    "I48.91": "Apixaban (anticoagulant)",
    "M81.0":  "Alendronate + Vitamin D",
    "D64.9":  "Iron supplementation",
    "M17.9":  "NSAID / Acetaminophen",
    "G89.29": "Analgesic per pain plan",
    "J02.9":  "Supportive care",
    "J20.9":  "Supportive care",
    "E66.9":  "Lifestyle & diet counseling",
}

@app.get("/")
def home():
    """Serve the frontend web page."""
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

def fhir_get(path, params=None):
    r = requests.get(f"{BASE}/{path}", params=params,
                     headers={"Accept": "application/fhir+json"}, timeout=30)
    r.raise_for_status()
    return r.json()

def patient_name(p):
    if p.get("name"):
        n = p["name"][0]
        return " ".join(n.get("given", []) + [n.get("family", "")]).strip()
    return "(no name)"

@app.get("/patients")
def list_patients(count: int = 10):
    bundle = fhir_get("Patient", {"_count": count})
    out = []
    for e in bundle.get("entry", []):
        p = e["resource"]
        out.append({"id": p.get("id"), "name": patient_name(p),
                    "gender": p.get("gender"), "birthDate": p.get("birthDate")})
    return out

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    try:
        p = fhir_get(f"Patient/{patient_id}")
    except requests.HTTPError:
        raise HTTPException(404, "Patient not found")

    conds = fhir_get("Condition", {"patient": patient_id, "_count": 20})
    conditions = []
    for e in conds.get("entry", []):
        c = e["resource"]
        coding = (c.get("code", {}).get("coding") or [{}])[0]
        snomed = coding.get("code")
        icd10 = SNOMED_TO_ICD10.get(snomed)
        medication = ICD10_TO_MEDICATION.get(icd10) if icd10 else None
        conditions.append({
            "snomed_code": snomed,
            "display": coding.get("display"),
            "icd10_code": icd10 or "(no mapping yet)",
            "recommended_medication": medication or "(no recommendation)",
        })
    return {"id": p.get("id"), "name": patient_name(p),
            "gender": p.get("gender"), "birthDate": p.get("birthDate"),
            "conditions": conditions}
