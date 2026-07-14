# 🦺 SafeVision AI — HSE Inspection & Incident Management System

A comprehensive, web-based Health, Safety & Environment (HSE) management platform built with **Python + Streamlit**. SafeVision AI digitizes workplace safety processes: incidents, hazards, inspections, risk assessments, PPE inventory, training, and corrective actions — all backed by a live analytics dashboard with AI-powered risk prediction.

---

## ✨ Key Features

| Module | Capabilities |
|---|---|
| 🔐 **Authentication & RBAC** | Secure bcrypt-hashed login, 4 roles (Admin, Safety Officer, Supervisor, Viewer) with granular permissions |
| 📊 **Dashboard** | Live KPIs, severity/status breakdowns, risk heatmaps, AI trend forecasts, high-risk area ranking |
| 🚨 **Incidents** | Log, investigate, filter, and close workplace incidents |
| ⚠️ **Hazards** | Hazard register with risk-level tracking and mitigation status |
| 🔍 **Inspections** | Checklist-based inspections with pass/fail scoring and area analytics |
| 🧮 **Risk Assessment** | 5×5 Likelihood × Severity risk matrix with auto-rated risk levels |
| 🧤 **PPE Inventory** | Stock tracking, minimum-threshold reorder alerts, restocking |
| 🎓 **Training** | Certification tracking with 30-day expiry alerts |
| ✅ **Corrective Actions (CAPA)** | Assign, prioritize, and track remediation actions to closure |
| 📄 **Reports** | One-click **PDF** (formatted management report) and **Excel** (multi-sheet data export) generation |
| 🤖 **AI Risk Prediction** | RandomForest severity prediction + linear-regression trend forecasting + composite location risk scoring |
| ⚙️ **Admin Panel** | User management, role assignment, activity audit log, system overview |

---

## 🏗️ Architecture

```
safevision_ai/
├── app.py                     # Main entry point: login + landing page
├── auth.py                    # Authentication & role-based access control
├── database.py                # SQLite schema, seeding, query helpers
├── requirements.txt
├── .streamlit/config.toml     # Theme configuration
├── utils/
│   ├── charts.py               # Plotly chart builders (bar, pie, heatmap, gauge, trend)
│   ├── ml_model.py             # AI risk prediction & trend forecasting (scikit-learn)
│   └── reports.py              # PDF (fpdf2) & Excel (openpyxl) report generation
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Incidents.py
│   ├── 3_Hazards.py
│   ├── 4_Inspections.py
│   ├── 5_Risk_Assessment.py
│   ├── 6_PPE_Inventory.py
│   ├── 7_Training.py
│   ├── 8_Corrective_Actions.py
│   ├── 9_Reports.py
│   └── 10_Admin.py
└── data/                       # SQLite DB file created at runtime
```

**Tech stack:** Streamlit (UI) · SQLite (storage) · Pandas (data handling) · Plotly (charts) · scikit-learn (ML) · bcrypt (password hashing) · fpdf2 (PDF) · openpyxl (Excel)

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The SQLite database (`data/safevision.db`) and demo data are created automatically on first run.

### 3. Log in with a demo account

| Role | Username | Password | Permissions |
|---|---|---|---|
| Admin | `admin` | `Admin@123` | Full access incl. user management |
| Safety Officer | `safety.officer` | `Safety@123` | Create/edit records, generate reports |
| Supervisor | `supervisor` | `Super@123` | Create records, view, generate reports |
| Viewer | `viewer` | `View@123` | Read-only |

> ⚠️ Change these default passwords before any real deployment.

---

## 🤖 How the AI Components Work

- **Severity Prediction:** A `RandomForestClassifier` is trained on the fly from historical incident records (location, incident type, injured-persons count → severity). Used on the Dashboard to estimate the likely severity of a hypothetical/new incident scenario.
- **Trend Forecasting:** A `LinearRegression` model fits monthly incident counts and projects the next 3 months, visualized alongside historical data.
- **Composite Risk Scoring:** Incidents and hazards are weighted by severity/risk level and aggregated per location to rank the highest-risk areas in the facility.

These models retrain automatically each time the Dashboard loads, so insights always reflect the latest data — no separate training pipeline needed for a project of this scale.

---

## 🔒 Security Notes

- Passwords are hashed with **bcrypt** (never stored in plaintext).
- Role-based access control (RBAC) gates create/edit/delete/report/admin actions.
- All user actions are written to an `activity_log` table for auditability.

---

## 📈 Possible Extensions

- Email/SMS notifications for overdue actions or expiring certifications
- QR-code-based mobile inspection checklists
- Integration with real IoT sensors (gas, temperature) for live hazard feeds
- Multi-tenant support for multi-site organizations
- Migration from SQLite to PostgreSQL for larger deployments

---

## 📝 License

This is a demonstration / portfolio project illustrating Python, Streamlit, data visualization, database management, and applied ML in an HSE context. Adapt and extend freely for coursework, prototypes, or internal tools.
