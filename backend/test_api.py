import json, urllib.request, urllib.error

B = "http://127.0.0.1:8000"

def call(method, path, data=None, token=None):
    url = B + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            try:
                return json.loads(raw.decode()), r.status
            except Exception:
                return raw, r.status
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode()), e.code
        except Exception:
            return e.read().decode(), e.code

results = []

# Login admin
body, code = call("POST", "/api/auth/login", {"email":"admin@finwise.app","password":"Admin@123456"})
token = body.get("access_token")
results.append(("admin login", code == 200 and bool(token), body.get("role"), code))

# Income
body, code = call("POST", "/api/income", {"amount":45000,"category":"Salary","description":"July salary","frequency":"monthly","date":"2026-07-01T00:00:00"}, token)
results.append(("create income", code == 201 and body.get("id") is not None, body.get("id"), code))
inc_id = body.get("id")

# Expense
body, code = call("POST", "/api/expenses", {"amount":31500,"category":"Rent","description":"July rent","date":"2026-07-02T00:00:00"}, token)
results.append(("create expense", code == 201 and body.get("id") is not None, body.get("id"), code))

# EMI calc
body, code = call("POST", "/api/emi/calculate", {"loan_amount":1000000,"interest_rate":8.5,"tenure_months":120})
results.append(("emi calc", code == 200 and body.get("monthly_emi",0) > 0, round(body.get("monthly_emi",0),2), code))

# EMI save
body, code = call("POST", "/api/emi/save", {"loan_amount":500000,"interest_rate":9,"tenure_months":60}, token)
emi_id = body.get("id")
results.append(("emi save", code == 201 and emi_id is not None, emi_id, code))

# EMI PDF export
body, code = call("GET", f"/api/emi/export/{emi_id}/pdf", token=token)
# FileResponse returns bytes; treat as success if 200
results.append(("emi pdf export", code == 200, "pdf bytes", code))

# Debt
body, code = call("POST", "/api/debts", {"name":"Credit Card","debt_type":"credit_card","total_amount":210000,"remaining_balance":210000,"monthly_payment":8000,"due_date":"2026-08-05T00:00:00"}, token)
results.append(("create debt", code == 201 and body.get("id") is not None, body.get("id"), code))

# Goal
body, code = call("POST", "/api/goals", {"name":"Laptop","target_amount":80000,"current_amount":32000,"deadline":"2026-12-31T00:00:00"}, token)
results.append(("create goal", code == 201 and body.get("progress_percent") == 40.0, body.get("progress_percent"), code))

# Budget
body, code = call("POST", "/api/budgets", {"month":"2026-07","category":"Food","limit_amount":8000}, token)
results.append(("create budget", code == 201 and body.get("id") is not None, body.get("id"), code))

# Dashboard
body, code = call("GET", "/api/dashboard/summary", token=token)
results.append(("dashboard", code == 200 and "financial_health" in body, {k:body.get(k) for k in ["total_income","total_expense","total_savings","total_debt","current_balance"]}, code))

# Health
body, code = call("GET", "/api/health", token=token)
results.append(("health", code == 200 and "score" in body, body.get("score"), code))

# Charts
body, code = call("GET", "/api/charts/monthly-analysis?months=6", token=token)
results.append(("charts", code == 200 and "labels" in body, len(body.get("labels",[])), code))

# Reports preview
body, code = call("GET", "/api/reports/preview?report_type=monthly", token=token)
results.append(("reports preview", code == 200 and "summary" in body, body.get("count"), code))

# Reports generate CSV
body, code = call("POST", "/api/reports/generate", {"report_type":"monthly","format":"csv"}, token)
results.append(("report csv", code == 200, "csv file", code))

# Notifications
body, code = call("GET", "/api/notifications", token=token)
results.append(("notifications", code == 200 and isinstance(body, list), len(body), code))

# Admin stats
body, code = call("GET", "/api/admin/stats", token=token)
results.append(("admin stats", code == 200 and "total_users" in body, body.get("total_users"), code))

# Categories
body, code = call("GET", "/api/categories", token=token)
results.append(("categories", code == 200 and len(body) >= 20, len(body), code))

# Transactions
body, code = call("GET", "/api/transactions?txn_type=income", token=token)
results.append(("transactions", code == 200 and isinstance(body, list), len(body), code))

# Negative value rejection
body, code = call("POST", "/api/income", {"amount":-500,"category":"Salary","date":"2026-07-01T00:00:00"}, token)
results.append(("reject negative", code == 422, code, code))

print("=== TEST RESULTS ===")
all_pass = True
for name, ok, detail, code in results:
    status = "PASS" if ok else "FAIL"
    if not ok: all_pass = False
    print(f"[{status}] {name:18s} code={code} detail={detail}")
print("\nALL PASS" if all_pass else "\nSOME FAILED")
