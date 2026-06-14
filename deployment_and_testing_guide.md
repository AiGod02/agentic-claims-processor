# Deployment and Manual Testing Guide — Plum Claims

This guide provides step-by-step instructions for:
1. **Manual Testing Scenarios:** Exact inputs, uploaded documents, and expected results to verify all claim outcomes (Approval, Partial, Rejection, Manual Review, Early Document Checks).
2. **Deployment Steps:** How to deploy the application on free hosting platforms (e.g. Render, Railway, Vercel) as a single unified service.

---

## 1. Manual Testing Scenarios (12 Official Cases)

To test the system manually via the React Frontend UI, use the following parameters. 

> [!NOTE]
> Ensure the backend has **`PLUM_EVAL_MODE="true"`** active in your `.env` or environment variables so that dates automatically align to the current testing year.

| Test Case | Member ID | Category | Claimed Amt | Hospital Name | Docs to Upload (from `sample_docs/`) | Expected Outcome & Rejection Reason |
|:---|:---|:---|:---|:---|:---|:---|
| **TC001** | `EMP001` | `CONSULTATION` | `1500` | Any | `prescription_clean` + `prescription_rajesh_2` | **Blocked:** *"You submitted ['PRESCRIPTION'] but a HOSPITAL_BILL is required..."* |
| **TC002** | `EMP004` | `PHARMACY` | `800` | Any | `prescription_sneha` + `pharmacy_bill_blurry` | **Blocked:** *"Your PHARMACY_BILL could not be read clearly. Please re-upload..."* |
| **TC003** | `EMP001` | `CONSULTATION` | `1500` | Any | `prescription_clean` (Rajesh Kumar) + `hospital_bill_dental` (Priya Singh) | **Blocked:** *"Patient name reads 'Rajesh Kumar' but hospital bill shows 'Priya Singh'..."* |
| **TC004** | `EMP001` | `CONSULTATION` | `1500` | City Clinic | `prescription_clean` + `hospital_bill_clean` | **APPROVED** for **₹1350.00** (10% co-pay deducted from ₹1500). |
| **TC005** | `EMP005` | `CONSULTATION` | `3000` | Any | `prescription_diabetes` + `hospital_bill_vikram` | **REJECTED** due to `WAITING_PERIOD_DIABETES` (Member joined 2024-09-01, treatment on 2024-10-15 is within 90 days). |
| **TC006** | `EMP002` | `DENTAL` | `12000` | Smile Dental | `prescription_priya` + `hospital_bill_dental` | **PARTIAL** approval for **₹8000.00** (Root canal covered, teeth whitening excluded). |
| **TC007** | `EMP007` | `DIAGNOSTIC` | `15000` | Apollo Hospitals | `prescription_suresh_mri` + `diagnostic_report_mri` + `hospital_bill_mri` | **REJECTED** due to `PRE_AUTH_MISSING` (MRI/CT Scan/PET Scan above ₹10,000 requires pre-authorization). |
| **TC008** | `EMP007` | `CONSULTATION` | `6000` | Any | `prescription_suresh_consult` + `hospital_bill_suresh` | **REJECTED** due to `PER_CLAIM_LIMIT_EXCEEDED` (OPD consultation limit is ₹5,000 per claim). |
| **TC009** | `EMP008` | `CONSULTATION` | `4800` | Any | `prescription_ravi` + `hospital_bill_ravi` | **MANUAL REVIEW** due to `SAME_DAY_CLAIM_PATTERN` (Member submits 4th claim on the same day). |
| **TC010** | `EMP010` | `CONSULTATION` | `4500` | Apollo Hospitals | `prescription_deepak` + `hospital_bill_apollo` | **APPROVED** for **₹3240.00** (20% network discount applied first = ₹3600, then 10% co-pay = ₹360 deducted). |
| **TC011** | `EMP006` | `ALTERNATIVE_MEDICINE` | `4000` | Any | `prescription_kavita` + `hospital_bill_ayur` | **APPROVED** (with reduced confidence of `0.55` and a flag indicating simulated `fraud_agent` skip / failure). |
| **TC012** | `EMP009` | `CONSULTATION` | `8000` | Any | `prescription_anita` + `hospital_bill_obesity` | **REJECTED** with standard key `EXCLUDED_CONDITION`. The UI displays a bulleted list detailing all 3 policy violations (Exclusion, Obesity waiting period, and Per-claim limit). |

> [!TIP]
> **Simulating TC009 (Same-Day Fraud Pattern) in Manual Testing:**
> Because the server starts with an empty in-memory database, you can simulate this pattern manually by submitting **three claims** first for member `EMP008` with treatment date `2024-10-30`. When you submit the **4th claim** (the actual TC009 input of `₹4,800`), the backend will automatically pull the 3 previous claims from the `claims_store` database, detect the pattern, and route the claim to **MANUAL REVIEW** with `SAME_DAY_CLAIM_PATTERN` flagged in the trace.

---

## 2. Deployment Instructions (Single-Service Deployment)

We have configured the FastAPI backend to serve the compiled React frontend static files. This allows you to host both the frontend and backend together on a single web service instance (perfect for free tiers like Render or Railway).

### A. Deploying on Render (Unified Python Web Service)
1. **Push your code to GitHub.**
2. **Create a new Web Service on Render:**
   - Connect your GitHub repository.
   - Render will automatically detect the `render.yaml` file in the root directory.
3. **Configurations in Render Dashboard:**
   - **Environment:** `Python`
   - **Build Command:** `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:**
   - Add your API Keys:
     - `GEMINI_API_KEY`: `<Your Gemini API Key>`
     - `GROQ_API_KEY`: `<Your Groq API Key>`
   - Add default variables:
     - `PLUM_EVAL_MODE`: `true`
     - `POLICY_FILE_PATH`: `./policy_terms.json`
     - `TEST_CASES_PATH`: `./test_cases.json`
     - `LOG_LEVEL`: `INFO`
5. Click **Deploy Web Service**. Render will build the React frontend, install backend requirements, and start serving the app on a single public URL.

### B. Deploying on Railway
1. **Create a new Project on Railway** and connect your GitHub repository.
2. Railway will automatically detect the python environment.
3. Set the **Custom Build Command** to:
   ```bash
   cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt
   ```
4. Set the **Start Command** to:
   ```bash
   cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Add the environment variables: `GEMINI_API_KEY`, `GROQ_API_KEY`, `PLUM_EVAL_MODE="true"`.
6. Click Deploy.

### C. Local Production Build Testing
To test the production build locally exactly as it will run on Render:
1. Build the React frontend:
   ```powershell
   cd frontend
   npm run build
   ```
2. Start the FastAPI backend:
   ```powershell
   cd ../backend
   uvicorn main:app --reload --port 8000
   ```
3. Open `http://localhost:8000` in your browser. FastAPI will now serve the compiled React SPA directly at the root URL!
