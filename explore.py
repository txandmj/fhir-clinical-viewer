"""
Step 1 — Talk to a public FHIR server and print real patient data.
Run:  py -3.11 explore.py
No account, no setup — uses the free HAPI FHIR public test server.
"""
import requests

BASE = "https://r4.smarthealthit.org"  # SMART Health IT sandbox — stable synthetic patients

def get(path, params=None):
    r = requests.get(f"{BASE}/{path}", params=params,
                     headers={"Accept": "application/fhir+json"}, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    # 1) Fetch a few patients
    print("=== Fetching patients ===")
    bundle = get("Patient", {"_count": 5})
    entries = bundle.get("entry", [])
    if not entries:
        print("No patients returned; try re-running (public server data changes).")
        return

    for e in entries:
        p = e["resource"]
        pid = p.get("id")
        # name can be missing/varied on test data
        name = "(no name)"
        if p.get("name"):
            n = p["name"][0]
            name = " ".join(n.get("given", []) + [n.get("family", "")]).strip()
        print(f"  Patient id={pid}  name={name}  gender={p.get('gender')}")

    # 2) For the first patient, fetch their Conditions (diagnoses)
    first_id = entries[0]["resource"]["id"]
    print(f"\n=== Conditions for patient {first_id} ===")
    conds = get("Condition", {"patient": first_id, "_count": 10})
    centries = conds.get("entry", [])
    if not centries:
        print("  (this patient has no Condition records on the test server)")
    for e in centries:
        c = e["resource"]
        coding = (c.get("code", {}).get("coding") or [{}])[0]
        print(f"  code={coding.get('code')}  system={coding.get('system')}  "
              f"display={coding.get('display')}")

    print("\nDone. You just pulled live FHIR data. Next: wrap this in a FastAPI backend.")

if __name__ == "__main__":
    main()
