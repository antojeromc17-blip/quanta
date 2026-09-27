# Quantum Loan Portfolio Optimizer (Quanta)
### PS05 — Thrissur District Cooperative Bank Hackathon Solution

An institutional-grade, full-stack Quantum Computing web application designed to solve the **NP-hard Combinatorial Loan Portfolio Optimization** problem using **Qiskit** and the **Quantum Approximate Optimization Algorithm (QAOA)**.

---

## Overview

Thrissur District Cooperative Bank faces the challenge of selecting an optimal subset of loan applications ($k = 3$ out of $5$ candidates) to maximize financial return while minimizing systemic inter-sector correlation and default risks.

As portfolio size scales, classical combinatorial brute-force approaches encounter combinatorial explosion ($O(2^N)$). This application maps the portfolio selection problem onto an **Ising QUBO (Quadratic Unconstrained Binary Optimization) Hamiltonian** and solves it using hybrid quantum-classical algorithms on simulated QPUs.

---

## Key Features

1. **Live Editable Portfolio Ledger**:
   - Real-time editable sector names, profit forecasts, and requested loan amounts.
2. **Interactive $5 \times 5$ Symmetric Risk Covariance Matrix**:
   - Zero-diagonal locked ($\sigma_{ii} = 0$).
   - Upper triangle cells directly editable with real-time automatic symmetric mirroring.
3. **Rigorous QUBO Formulation with Auto-Scaled Constraints**:
   - Cost Hamiltonian:
     $$H = -\sum_{i=1}^5 \text{profit}_i x_i + \lambda \sum_{i,j} \text{risk}_{ij} x_i x_j + \mu \left(\sum_{i=1}^5 x_i - 3\right)^2$$
   - Dynamic Auto-Scaling for $\mu$: $\mu_{\text{auto}} \ge 2\sum |p_i| + \lambda \sum |\sigma_{ij}| + 10$, mathematically guaranteeing strict enforcement of the $k=3$ cardinality constraint regardless of arbitrary input values.
4. **Certified Ground Truth Verification**:
   - Computes classical brute-force evaluation over all $\binom{5}{3} = 10$ triplets side-by-side with QAOA to certify global optimality and divergence metrics ($0.0\%$ delta).
5. **Exact Stitch Design System (Dark Theme)**:
   - High-contrast, institutional palette with solid surface containers (zero transparency or glassmorphism).
   - Tailored typography: *Plus Jakarta Sans*, *Anton*, *Bebas Neue*, and *JetBrains Mono*.
   - Live telemetry logs, eigenstate sample distribution histograms, and mathematical intuition walk-throughs.

---

## Tech Stack

- **Backend**: Python 3.13, Flask 3.1, Flask-CORS
- **Quantum Computing**: Qiskit 2.5, Qiskit Optimization 0.7, Qiskit Algorithms 0.4
- **Classical Numerics**: NumPy, SciPy
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript (ES6+), Google Fonts, Material Symbols Outlined

---

## Local Installation & Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/antojeromc17-blip/quanta.git
cd quanta
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## API Documentation

### `POST /optimize`
Accepts 5 loan applications and a $5 \times 5$ symmetric covariance matrix to recalculate the optimal portfolio.

#### Request Body
```json
{
  "loans": [
    { "id": "LN-101", "sector": "Textiles", "profit": 1.8, "principal": 2.8 },
    { "id": "LN-102", "sector": "Agri-processing", "profit": 1.5, "principal": 4.2 },
    { "id": "LN-103", "sector": "Retail", "profit": 2.0, "principal": 3.5 },
    { "id": "LN-104", "sector": "Transport", "profit": 1.2, "principal": 1.8 },
    { "id": "LN-105", "sector": "Construction", "profit": 2.4, "principal": 2.5 }
  ],
  "risk_matrix": [
    [0.0, 0.3, 0.5, 0.2, 0.4],
    [0.3, 0.0, 0.3, 0.6, 0.2],
    [0.5, 0.3, 0.0, 0.3, 0.5],
    [0.2, 0.6, 0.3, 0.0, 0.3],
    [0.4, 0.2, 0.5, 0.3, 0.0]
  ],
  "lambda": 1.0,
  "reps": 2,
  "auto_scale_mu": true
}
```

#### Response Payload
```json
{
  "status": "success",
  "matched": true,
  "selected_loans_qaoa": ["LN-101", "LN-102", "LN-105"],
  "selected_loans_brute_force": ["LN-101", "LN-102", "LN-105"],
  "selected_sectors_qaoa": ["Textiles", "Agri-processing", "Construction"],
  "total_profit": 5.7,
  "total_risk": 1.8,
  "objective_value": -3.9,
  "data": { ... }
}
```

---

## Testing
Run the automated end-to-end verification test suite:
```bash
python test_e2e.py
```
