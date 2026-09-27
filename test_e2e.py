import urllib.request
import json

def test(name, fn):
    try:
        fn()
        print(f"PASS: {name}")
    except Exception as e:
        print(f"FAIL: {name} -> {e}")

# 1. GET /
def test_get_root():
    res = urllib.request.urlopen("http://127.0.0.1:5000/")
    assert res.status == 200
    html = res.read().decode()
    assert 'id="sector-0"' in html
    assert 'id="profit-0"' in html
    assert 'id="risk-0-1"' in html
    assert 'id="resultsBentoGrid"' in html
    assert 'triggerOptimization' in html

# 2. GET /api/portfolio
def test_get_portfolio():
    res = urllib.request.urlopen("http://127.0.0.1:5000/api/portfolio")
    data = json.loads(res.read().decode())
    assert data["status"] == "success"
    assert "selected_loans_qaoa" in data["data"]

# 3. POST /optimize with default loans
def test_post_optimize_default():
    payload = {
        "loans": [
            {"id": "LN-101", "sector": "Textiles", "profit": 1.8},
            {"id": "LN-102", "sector": "Agri-processing", "profit": 1.5},
            {"id": "LN-103", "sector": "Retail", "profit": 2.0},
            {"id": "LN-104", "sector": "Transport", "profit": 1.2},
            {"id": "LN-105", "sector": "Construction", "profit": 2.4}
        ],
        "risk_matrix": [
            [0.0, 0.3, 0.5, 0.2, 0.4],
            [0.3, 0.0, 0.3, 0.6, 0.2],
            [0.5, 0.3, 0.0, 0.3, 0.5],
            [0.2, 0.6, 0.3, 0.0, 0.3],
            [0.4, 0.2, 0.5, 0.3, 0.0]
        ],
        "lambda": 1.0,
        "reps": 2
    }
    req = urllib.request.Request("http://127.0.0.1:5000/optimize", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req).read().decode())
    assert res["status"] == "success"
    assert len(res["selected_loans_qaoa"]) == 3
    assert len(res["selected_loans_brute_force"]) == 3
    assert res["matched"] == True
    print(f"   -> QAOA: {res['selected_loans_qaoa']} ({res['selected_sectors_qaoa']})")
    print(f"   -> BF:   {res['selected_loans_brute_force']} ({res['selected_sectors_brute_force']})")
    print(f"   -> Total Profit: {res['total_profit']}, Total Risk: {res['total_risk']}, Objective: {res['objective_value']}")

# 4. POST /optimize with modified profit (Live recalculation)
def test_post_optimize_recalc():
    payload = {
        "loans": [
            {"id": "LN-101", "sector": "Textiles", "profit": 1.8},
            {"id": "LN-102", "sector": "Agri-processing", "profit": 1.5},
            {"id": "LN-103", "sector": "Retail", "profit": 10.0}, # Huge profit jump for Retail
            {"id": "LN-104", "sector": "Transport", "profit": 1.2},
            {"id": "LN-105", "sector": "Construction", "profit": 2.4}
        ],
        "risk_matrix": [
            [0.0, 0.3, 0.5, 0.2, 0.4],
            [0.3, 0.0, 0.3, 0.6, 0.2],
            [0.5, 0.3, 0.0, 0.3, 0.5],
            [0.2, 0.6, 0.3, 0.0, 0.3],
            [0.4, 0.2, 0.5, 0.3, 0.0]
        ]
    }
    req = urllib.request.Request("http://127.0.0.1:5000/optimize", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req).read().decode())
    assert "LN-103" in res["selected_loans_qaoa"]
    print(f"   -> With Retail profit=10.0: QAOA selected {res['selected_loans_qaoa']} (Matched: {res['matched']})")

if __name__ == "__main__":
    test("Root Endpoint & HTML Check", test_get_root)
    test("Portfolio Endpoint Check", test_get_portfolio)
    test("Default Optimization Check", test_post_optimize_default)
    test("Live Recalculation Check", test_post_optimize_recalc)
