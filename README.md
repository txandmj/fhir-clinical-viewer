# FHIR Clinical Viewer

A small full-stack app that reads patient clinical data from a FHIR server and
translates SNOMED CT diagnosis codes to ICD-10 — the same interoperability
problem I own at Virtual Hospitals Africa, built here as a standalone demo.

**Stack:** Python · FastAPI · FHIR (R4) · SNOMED CT → ICD-10 mapping · (React frontend)
**Data source:** SMART Health IT sandbox (`https://r4.smarthealthit.org`) — synthetic patients.

---

## How to run

```bash
py -3.11 -m pip install -r requirements.txt

# 1) quick data check
py -3.11 explore.py

# 2) run the API
py -3.11 -m uvicorn main:app --reload
# then open http://127.0.0.1:8000/docs  (try GET /patients, then GET /patients/{id})
```

---

## Build plan / progress

- [x] **Step 1 — Talk to a FHIR server** (`explore.py`): fetch patients + their Conditions.
- [x] **Step 2 — FastAPI backend** (`main.py`): `/patients` and `/patients/{id}`.
- [x] **Step 3 — Mapping tables.** SNOMED→ICD-10 (expanded) and ICD-10→recommended
      medication, mirroring VHA's ICD-10-keyed Essential Medicines List.
- [x] **Step 4 — Frontend** (`index.html`): pick a patient → full pipeline table.
- [ ] **Step 5 — Expand mappings further** (optional): add more SNOMED/ICD-10/drug entries,
      or load a real crosswalk file, so fewer rows show "(no mapping yet)".
- [ ] **Step 6 — Polish + ship.** README screenshots, record a 1–2 min demo, push to GitHub.

---

## Talking point (for interviews)
"I built a FastAPI service that reads patient records from a FHIR server and translates the
SNOMED CT diagnosis codes to ICD-10 at request time. It's the same clinical-vocabulary
interoperability problem I solve at Virtual Hospitals Africa — here as a self-contained demo
against synthetic FHIR data."
