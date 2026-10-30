# Maharajothi Ledger 🚜🏗️📊
### Python-Powered Vehicle Expense, Daily Profit & Loss Analytics, and Document Compliance System
**மகாராஜோதி லெட்ஜர் - பைதான் வாகன வரவு செலவு & ஆவண மேலாண்மை**

---

## 🌟 Overview / கண்ணோட்டம்
**Maharajothi Ledger** is a complete, clean-slate fleet management and financial analytics system built with **Python 3** as its primary programming language. It is designed for vehicle operators, agricultural contractors, and transport business owners managing **Tractors, JCB Excavators, Cars, Vans, and Buses**.

This project comes with **zero sample or pre-loaded data**—giving you a 100% clean ledger ready for your own vehicles, daily work runs, and expenses.

---

## 🐍 Python Backend Architecture / பைதான் கட்டமைப்பு

* **Core Language**: **Python 3** (`app.py`)
* **Web Framework**: **Flask** (RESTful API architecture)
* **Database**: **SQLite** (`maharajothi.db`) — zero configuration, auto-initializing database
* **Analytics Engine**: Python functions compute real-time Profit & Loss (`Revenue - Total Expenses`), operating margin %, cost driver distributions, and document compliance audits.
* **REST API Endpoints**:
  - `GET /` : Serves the clean bilingual Maharajothi Ledger user interface.
  - `GET /api/vehicles` : Retrieves all registered vehicles from SQLite.
  - `POST /api/vehicles` : Inserts or updates vehicles and document records.
  - `DELETE /api/vehicles/<id>` : Removes a vehicle and its logs.
  - `GET /api/transactions` : Retrieves itemized daily trip logs and P&L entries.
  - `POST /api/transactions` : Computes net margin in Python and persists to database.
  - `DELETE /api/transactions/<id>` : Deletes a transaction entry.
  - `GET /api/analytics` : Returns aggregate KPIs, vehicle profitability matrix, and compliance status.
  - `GET /api/export-csv` : Streams dynamically generated CSV report from Python.

---

## ✨ Features & Rules / முக்கிய அம்சங்கள்

1. **Clean Slate (No Demo Data)**:
   - Starts completely empty (`0 Vehicles`, `0 Transactions`, `₹0 Revenue`, `₹0 Expenses`).
   - Register your exact fleet vehicles and log your genuine daily work from day one.

2. **Official Emblem Logo**:
   - Features your custom roaring tiger, bow & arrow, and mountain star emblem in the brand header, report headers, and browser favicon.

3. **Fleet Types & Document Rules**:
   - 🚜 **Tractor (டிராக்டர்)**: RC Book & Insurance soft copy tracking.
   - 🏗️ **JCB (ஜேசிபி / எக்ஸ்கவேட்டர்)**: RC Book & Insurance soft copy tracking.
   - 🚗 **Car (கார்)**: RC Book & Insurance soft copy tracking.
   - 🚐 **Van (வேன்)**: RC Book, Insurance, PUCC, and Permit soft copy tracking.
   - 🚌 **Bus (பேருந்து)**: RC Book, Insurance, PUCC, and Permit soft copy tracking.
   *(Pollution certificates and Vehicle Permits are required ONLY for Van and Bus; Tractor, JCB, and Car are exempt).*

4. **Soft Copy Document Viewer**:
   - Upload soft copies (`.png`, `.jpg`, `.pdf`) and preview them in the built-in document viewer modal.
   - Automatic expiry tracking: 🟢 Valid, 🟡 Expiring within 30 days, 🔴 Expired.

5. **Direct Standalone Access**:
   - Zero login or password friction. Instant access upon launching.

6. **Bilingual Support (தமிழ் & English)**:
   - One-click toggle between English and Tamil across all inputs, tables, charts, and reports.

---

## 💻 How to Run in VS Code with Python

### Step 1: Open the Project in VS Code
1. Unzip `fleet_expense_tracker.zip` (or `maharajothi-ledger`).
2. Open **Visual Studio Code**.
3. Click **File > Open Folder...** and select the project folder.

### Step 2: Set Up Python Virtual Environment
Open the VS Code Terminal (press `` Ctrl + ` `` or click **Terminal > New Terminal**) and run:

**On Windows:**
```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\activate

# 3. Install Flask dependency
pip install -r requirements.txt
```

**On Mac / Linux:**
```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install Flask dependency
pip install -r requirements.txt
```

### Step 3: Run the Python Application
In your terminal, start the Python server:
```bash
python app.py
```
*(or `python3 app.py` on Mac/Linux)*

You will see:
```text
============================================================
MAHARAJOTHI LEDGER - PYTHON APPLICATION SERVER
Main Programming Language: Python 3
SQLite Database: maharajothi.db (Clean & Empty state)
Serving on: http://127.0.0.1:5000
============================================================
```
Open **`http://127.0.0.1:5000`** in your browser to start entering your vehicles and daily accounts!

---

## 🚀 How to Push this Python Project to GitHub

In your VS Code terminal (with your virtual environment or project root):

```bash
# 1. Initialize Git
git init

# 2. Stage all files (virtual environment and database are automatically ignored by .gitignore)
git add .

# 3. Commit your Python project
git commit -m "Initial commit: Maharajothi Ledger Python backend and clean fleet analytics"

# 4. Set main branch
git branch -M main

# 5. Link to your GitHub repository and push
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/maharajothi-ledger.git
git push -u origin main
```
*(Replace `<YOUR_GITHUB_USERNAME>` with your GitHub username).*

---

## 📁 Project Structure
```
maharajothi-ledger/
│
├── app.py              # Main Python Flask server, SQLite models, REST API & Analytics engine
├── requirements.txt    # Python dependencies (Flask>=3.0.0)
├── maharajothi.db      # SQLite local database (auto-generated upon running app.py)
├── index.html          # Clean Single Page Application (Bilingual Tamil/English, Tailwind, Chart.js)
├── logo.png            # Optimized web emblem logo
├── logo_full.png       # High-resolution original emblem logo
├── uploads/            # Local directory storing soft copy document uploads
│   └── .gitkeep
├── sample-data.json    # Clean initial data configuration (empty arrays)
├── README.md           # Complete Python guide, VS Code instructions, and GitHub commands
└── .gitignore          # Python and editor ignore rules
```
