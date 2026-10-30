"""
Maharajothi Ledger - Backend Application Engine
Main Programming Language: Python 3
Framework: Flask (RESTful Architecture) with SQLite Database Persistence
"""

import os
import sqlite3
import csv
import io
from datetime import datetime, date
from flask import Flask, request, jsonify, send_from_directory, Response

app = Flask(__name__, static_folder=".", static_url_path="")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maharajothi.db")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def get_db_connection():
    """Establish connection to SQLite database with dictionary-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables for Vehicles and Transactions if not already created."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vehicles Table: Supports Tractor, JCB, Car, Van, Bus
    # Note: PUCC and Permit fields apply strictly to Van and Bus
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id TEXT PRIMARY KEY,
            number TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            model TEXT,
            driver TEXT,
            rc_expiry TEXT,
            rc_filename TEXT,
            rc_data_url TEXT,
            ins_expiry TEXT,
            ins_filename TEXT,
            ins_data_url TEXT,
            pucc_expiry TEXT,
            pucc_filename TEXT,
            pucc_data_url TEXT,
            permit_type TEXT,
            permit_expiry TEXT,
            permit_filename TEXT,
            permit_data_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Transactions Table: Daily Work, Trip Income, and Itemized Expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            vehicle_number TEXT NOT NULL,
            route TEXT,
            revenue REAL DEFAULT 0,
            fuel REAL DEFAULT 0,
            bata REAL DEFAULT 0,
            toll REAL DEFAULT 0,
            repair REAL DEFAULT 0,
            police REAL DEFAULT 0,
            misc REAL DEFAULT 0,
            total_expense REAL DEFAULT 0,
            net_profit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        )
    """)

    conn.commit()
    conn.close()


# Initialize database upon startup
init_db()


# ---------------------------------------------------------
# FRONTEND ROUTE
# ---------------------------------------------------------
@app.route("/")
def index():
    """Serve the Maharajothi Ledger Single Page Web Application."""
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    """Serve static assets like logo images or local scripts."""
    return send_from_directory(".", path)


# ---------------------------------------------------------
# VEHICLE API ENDPOINTS
# ---------------------------------------------------------
@app.route("/api/vehicles", methods=["GET"])
def get_vehicles():
    """Retrieve all registered vehicles from the SQLite database."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM vehicles ORDER BY created_at DESC").fetchall()
    vehicles = []
    for r in rows:
        v = {
            "id": r["id"],
            "number": r["number"],
            "type": r["type"],
            "model": r["model"] or "",
            "driver": r["driver"] or "",
            "rc": {
                "fileName": r["rc_filename"],
                "expiry": r["rc_expiry"],
                "dataUrl": r["rc_data_url"]
            },
            "insurance": {
                "fileName": r["ins_filename"],
                "expiry": r["ins_expiry"],
                "dataUrl": r["ins_data_url"]
            },
            "pollution": {
                "fileName": r["pucc_filename"],
                "expiry": r["pucc_expiry"],
                "dataUrl": r["pucc_data_url"]
            } if r["type"] in ["Van", "Bus"] and r["pucc_expiry"] else None,
            "permit": {
                "type": r["permit_type"],
                "fileName": r["permit_filename"],
                "expiry": r["permit_expiry"],
                "dataUrl": r["permit_data_url"]
            } if r["type"] in ["Van", "Bus"] and r["permit_expiry"] else None
        }
        vehicles.append(v)
    conn.close()
    return jsonify(vehicles)


@app.route("/api/vehicles", methods=["POST"])
def save_vehicle():
    """Create or update a vehicle with soft copy document records."""
    data = request.json or {}
    veh_id = data.get("id") or f"veh-{int(datetime.now().timestamp() * 1000)}"
    number = (data.get("number") or "").strip().upper()
    veh_type = data.get("type") or "Tractor"
    model = (data.get("model") or "").strip()
    driver = (data.get("driver") or "").strip()

    rc = data.get("rc") or {}
    ins = data.get("insurance") or {}
    
    # PUCC and Permits strictly apply to Van and Bus
    is_van_bus = veh_type in ["Van", "Bus"]
    pucc = data.get("pollution") or {} if is_van_bus else {}
    permit = data.get("permit") or {} if is_van_bus else {}

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vehicles (
            id, number, type, model, driver,
            rc_expiry, rc_filename, rc_data_url,
            ins_expiry, ins_filename, ins_data_url,
            pucc_expiry, pucc_filename, pucc_data_url,
            permit_type, permit_expiry, permit_filename, permit_data_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            number = excluded.number,
            type = excluded.type,
            model = excluded.model,
            driver = excluded.driver,
            rc_expiry = excluded.rc_expiry,
            rc_filename = excluded.rc_filename,
            rc_data_url = excluded.rc_data_url,
            ins_expiry = excluded.ins_expiry,
            ins_filename = excluded.ins_filename,
            ins_data_url = excluded.ins_data_url,
            pucc_expiry = excluded.pucc_expiry,
            pucc_filename = excluded.pucc_filename,
            pucc_data_url = excluded.pucc_data_url,
            permit_type = excluded.permit_type,
            permit_expiry = excluded.permit_expiry,
            permit_filename = excluded.permit_filename,
            permit_data_url = excluded.permit_data_url
    """, (
        veh_id, number, veh_type, model, driver,
        rc.get("expiry"), rc.get("fileName"), rc.get("dataUrl"),
        ins.get("expiry"), ins.get("fileName"), ins.get("dataUrl"),
        pucc.get("expiry") if is_van_bus else None,
        pucc.get("fileName") if is_van_bus else None,
        pucc.get("dataUrl") if is_van_bus else None,
        permit.get("type") if is_van_bus else None,
        permit.get("expiry") if is_van_bus else None,
        permit.get("fileName") if is_van_bus else None,
        permit.get("dataUrl") if is_van_bus else None
    ))

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "id": veh_id, "message": "Vehicle saved successfully"})


@app.route("/api/vehicles/<veh_id>", methods=["DELETE"])
def delete_vehicle(veh_id):
    """Delete a vehicle and its associated transactions."""
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE vehicle_id = ?", (veh_id,))
    conn.execute("DELETE FROM vehicles WHERE id = ?", (veh_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Vehicle deleted successfully"})


# ---------------------------------------------------------
# TRANSACTION & P&L API ENDPOINTS
# ---------------------------------------------------------
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    """Retrieve all daily transactions and calculated profit & loss logs."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC, created_at DESC").fetchall()
    transactions = []
    for r in rows:
        t = {
            "id": r["id"],
            "date": r["date"],
            "vehicleId": r["vehicle_id"],
            "vehicleNumber": r["vehicle_number"],
            "route": r["route"] or "",
            "revenue": r["revenue"],
            "expenses": {
                "fuel": r["fuel"],
                "bata": r["bata"],
                "toll": r["toll"],
                "repair": r["repair"],
                "police": r["police"],
                "misc": r["misc"]
            },
            "totalExpense": r["total_expense"],
            "netProfit": r["net_profit"]
        }
        transactions.append(t)
    conn.close()
    return jsonify(transactions)


@app.route("/api/transactions", methods=["POST"])
def save_transaction():
    """Log a trip, calculate net profit/loss via Python arithmetic, and save."""
    data = request.json or {}
    tx_id = data.get("id") or f"tx-{int(datetime.now().timestamp() * 1000)}"
    date_str = data.get("date") or date.today().isoformat()
    vehicle_id = data.get("vehicleId")
    vehicle_number = data.get("vehicleNumber") or ""
    route = (data.get("route") or "").strip()

    revenue = float(data.get("revenue") or 0)
    expenses = data.get("expenses") or {}
    fuel = float(expenses.get("fuel") or 0)
    bata = float(expenses.get("bata") or 0)
    toll = float(expenses.get("toll") or 0)
    repair = float(expenses.get("repair") or 0)
    police = float(expenses.get("police") or 0)
    misc = float(expenses.get("misc") or 0)

    # Core Profit and Loss Calculation in Python
    total_expense = fuel + bata + toll + repair + police + misc
    net_profit = revenue - total_expense

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            id, date, vehicle_id, vehicle_number, route,
            revenue, fuel, bata, toll, repair, police, misc,
            total_expense, net_profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            date = excluded.date,
            vehicle_id = excluded.vehicle_id,
            vehicle_number = excluded.vehicle_number,
            route = excluded.route,
            revenue = excluded.revenue,
            fuel = excluded.fuel,
            bata = excluded.bata,
            toll = excluded.toll,
            repair = excluded.repair,
            police = excluded.police,
            misc = excluded.misc,
            total_expense = excluded.total_expense,
            net_profit = excluded.net_profit
    """, (
        tx_id, date_str, vehicle_id, vehicle_number, route,
        revenue, fuel, bata, toll, repair, police, misc,
        total_expense, net_profit
    ))

    conn.commit()
    conn.close()
    return jsonify({
        "status": "success",
        "id": tx_id,
        "totalExpense": total_expense,
        "netProfit": net_profit
    })


@app.route("/api/transactions/<tx_id>", methods=["DELETE"])
def delete_transaction(tx_id):
    """Delete a transaction entry."""
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Transaction deleted successfully"})


# ---------------------------------------------------------
# DATA ANALYST REPORT CALCULATION API
# ---------------------------------------------------------
@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Python Analytics Engine: Aggregates financial KPIs, cost drivers, and compliance status."""
    conn = get_db_connection()
    
    # Financial Totals
    agg = conn.execute("""
        SELECT 
            COUNT(*) as total_trips,
            COALESCE(SUM(revenue), 0) as total_revenue,
            COALESCE(SUM(total_expense), 0) as total_expense,
            COALESCE(SUM(net_profit), 0) as net_profit,
            COALESCE(SUM(fuel), 0) as total_fuel,
            COALESCE(SUM(bata), 0) as total_bata,
            COALESCE(SUM(toll), 0) as total_toll,
            COALESCE(SUM(repair), 0) as total_repair,
            COALESCE(SUM(police), 0) as total_police,
            COALESCE(SUM(misc), 0) as total_misc
        FROM transactions
    """).fetchone()

    total_revenue = float(agg["total_revenue"])
    total_expense = float(agg["total_expense"])
    net_profit = float(agg["net_profit"])
    profit_margin = round((net_profit / total_revenue * 100), 2) if total_revenue > 0 else 0.0

    # Vehicle Matrix
    vehicles = conn.execute("SELECT * FROM vehicles").fetchall()
    matrix = []
    today = date.today()
    expired_docs_count = 0
    expiring_soon_count = 0

    for v in vehicles:
        v_agg = conn.execute("""
            SELECT 
                COUNT(*) as trips,
                COALESCE(SUM(revenue), 0) as rev,
                COALESCE(SUM(total_expense), 0) as exp,
                COALESCE(SUM(net_profit), 0) as profit
            FROM transactions WHERE vehicle_id = ?
        """, (v["id"],)).fetchone()

        v_rev = float(v_agg["rev"])
        v_profit = float(v_agg["profit"])
        v_margin = round((v_profit / v_rev * 100), 1) if v_rev > 0 else 0.0

        # Check compliance
        is_van_bus = v["type"] in ["Van", "Bus"]
        dates_to_check = [v["rc_expiry"], v["ins_expiry"]]
        if is_van_bus:
            dates_to_check.extend([v["pucc_expiry"], v["permit_expiry"]])

        doc_status = "Compliant"
        for d_str in dates_to_check:
            if d_str:
                try:
                    exp_date = datetime.strptime(d_str, "%Y-%m-%d").date()
                    delta = (exp_date - today).days
                    if delta < 0:
                        doc_status = "Expired"
                        expired_docs_count += 1
                        break
                    elif delta <= 30:
                        doc_status = "Renew Soon"
                        expiring_soon_count += 1
                except ValueError:
                    pass

        matrix.append({
            "id": v["id"],
            "number": v["number"],
            "type": v["type"],
            "driver": v["driver"] or "N/A",
            "trips": v_agg["trips"],
            "revenue": v_rev,
            "expenses": float(v_agg["exp"]),
            "netProfit": v_profit,
            "marginPct": v_margin,
            "docStatus": doc_status
        })

    conn.close()

    report = {
        "summary": {
            "totalRevenue": total_revenue,
            "totalExpense": total_expense,
            "netProfit": net_profit,
            "profitMarginPct": profit_margin,
            "totalTrips": agg["total_trips"],
            "activeVehiclesCount": len(vehicles)
        },
        "costDrivers": {
            "fuel": float(agg["total_fuel"]),
            "bata": float(agg["total_bata"]),
            "toll": float(agg["total_toll"]),
            "repair": float(agg["total_repair"]),
            "police": float(agg["total_police"]),
            "misc": float(agg["total_misc"])
        },
        "compliance": {
            "expiredDocsCount": expired_docs_count,
            "expiringSoonCount": expiring_soon_count
        },
        "vehicleMatrix": matrix
    }

    return jsonify(report)


# ---------------------------------------------------------
# CSV EXPORT STREAMING (GENERATED IN PYTHON)
# ---------------------------------------------------------
@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    """Stream dynamic CSV generated directly from Python."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Date", "Vehicle Number", "Work / Route Note",
        "Revenue (INR)", "Fuel (INR)", "Driver Bata (INR)",
        "Toll (INR)", "Repairs (INR)", "Challan (INR)", "Misc (INR)",
        "Total Expenses (INR)", "Net Profit/Loss (INR)"
    ])

    for r in rows:
        writer.writerow([
            r["date"], r["vehicle_number"], r["route"] or "",
            r["revenue"], r["fuel"], r["bata"], r["toll"],
            r["repair"], r["police"], r["misc"],
            r["total_expense"], r["net_profit"]
        ])

    conn.close()
    output.seek(0)
    
    filename = f"maharajothi_ledger_{date.today().isoformat()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("MAHARAJOTHI LEDGER - PYTHON APPLICATION SERVER")
    print("Main Programming Language: Python 3")
    print("SQLite Database: maharajothi.db (Clean & Empty state)")
    print(f"Serving on: http://0.0.0.0:{port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
