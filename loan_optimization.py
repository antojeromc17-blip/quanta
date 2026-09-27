import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA

try:
    from qiskit.primitives import StatevectorSampler as Sampler
except ImportError:
    from qiskit.primitives import Sampler

LOANS = [
    {"id": "L1", "code": "LN-101", "sector": "Textiles", "profit": 1.8, "principal": 2.8, "principal_fmt": "₹2.80 Cr", "profit_fmt": "₹18.0 L", "rating": "A+", "collateral": "140%"},
    {"id": "L2", "code": "LN-102", "sector": "Agri-processing", "profit": 1.5, "principal": 4.2, "principal_fmt": "₹4.20 Cr", "profit_fmt": "₹15.0 L", "rating": "AA", "collateral": "160%"},
    {"id": "L3", "code": "LN-103", "sector": "Retail", "profit": 2.0, "principal": 3.5, "principal_fmt": "₹3.50 Cr", "profit_fmt": "₹20.0 L", "rating": "A", "collateral": "130%"},
    {"id": "L4", "code": "LN-104", "sector": "Transport", "profit": 1.2, "principal": 1.8, "principal_fmt": "₹1.80 Cr", "profit_fmt": "₹12.0 L", "rating": "BBB+", "collateral": "110%"},
    {"id": "L5", "code": "LN-105", "sector": "Construction", "profit": 2.4, "principal": 2.5, "principal_fmt": "₹2.50 Cr", "profit_fmt": "₹24.0 L", "rating": "A+", "collateral": "150%"}
]

RISK_MATRIX = [
    [0.0, 0.3, 0.5, 0.2, 0.4],
    [0.3, 0.0, 0.3, 0.6, 0.2],
    [0.5, 0.3, 0.0, 0.3, 0.5],
    [0.2, 0.6, 0.3, 0.0, 0.3],
    [0.4, 0.2, 0.5, 0.3, 0.0]
]

def build_qubo(lam=1.0, mu=3.0, capital=None, nu=1.0, custom_profits=None, custom_risks=None, custom_principals=None):
    profits = custom_profits if custom_profits is not None else [l["profit"] for l in LOANS]
    risks = custom_risks if custom_risks is not None else RISK_MATRIX
    
    principals = custom_principals if custom_principals is not None else [l["principal"] for l in LOANS]
    
    qp = QuadraticProgram("Loan_Portfolio_Optimization")
    for i in range(5):
        qp.binary_var(name=f"x_{i}")
        
    linear = {}
    for i in range(5):
        linear[f"x_{i}"] = -profits[i] - 5.0 * mu
        
    quadratic = {}
    for i in range(5):
        for j in range(i + 1, 5):
            coupling = lam * (risks[i][j] + risks[j][i]) + 2.0 * mu
            quadratic[(f"x_{i}", f"x_{j}")] = coupling
            
    if capital is not None:
        C = float(capital)
        for i in range(5):
            pi = principals[i]
            linear[f"x_{i}"] += nu * (pi**2 - 2 * C * pi)
        for i in range(5):
            for j in range(i + 1, 5):
                pi = principals[i]
                pj = principals[j]
                quadratic[(f"x_{i}", f"x_{j}")] += 2.0 * nu * pi * pj
        constant = 9.0 * mu + nu * (C**2)
    else:
        constant = 9.0 * mu

    qp.minimize(constant=constant, linear=linear, quadratic=quadratic)
    return qp

def evaluate_portfolio(bitstring, lam=1.0, mu=3.0, capital=None, nu=1.0, custom_profits=None, custom_risks=None, custom_principals=None):
    profits = custom_profits if custom_profits is not None else [l["profit"] for l in LOANS]
    risks = custom_risks if custom_risks is not None else RISK_MATRIX
    principals = custom_principals if custom_principals is not None else [l["principal"] for l in LOANS]
    
    x = [int(b) for b in bitstring]
    profit = sum(p * xi for p, xi in zip(profits, x))
    risk = sum(risks[i][j] * x[i] * x[j] for i in range(5) for j in range(5))
    k = sum(x)
    total_principal = sum(principals[i] * x[i] for i in range(5))
    
    penalty = mu * ((k - 3) ** 2)
    cap_penalty = 0.0
    is_valid = bool(k == 3)
    
    if capital is not None:
        if total_principal > capital:
            is_valid = False
        cap_penalty = nu * ((total_principal - capital) ** 2)
        
    obj = -profit + lam * risk + penalty + cap_penalty
    return {
        "bitstring": bitstring,
        "selected_indices": [i for i, b in enumerate(x) if b == 1],
        "selected_loans": [LOANS[i]["id"] for i, b in enumerate(x) if b == 1],
        "k": int(k),
        "is_valid": is_valid,
        "total_profit": float(round(profit, 4)),
        "total_risk": float(round(risk, 4)),
        "total_principal": float(round(total_principal, 4)),
        "penalty": float(round(penalty + cap_penalty, 4)),
        "objective": float(round(obj, 4))
    }

def solve_classical(lam=1.0, mu=3.0, capital=None, nu=1.0, custom_profits=None, custom_risks=None, custom_principals=None):
    all_results = []
    for val in range(32):
        b = f"{val:05b}"
        eval_res = evaluate_portfolio(b, lam=lam, mu=mu, capital=capital, nu=nu, custom_profits=custom_profits, custom_risks=custom_risks, custom_principals=custom_principals)
        all_results.append(eval_res)
    all_results.sort(key=lambda r: (not r["is_valid"], r["objective"]))
    valid_combos = [r for r in all_results if r["is_valid"]]
    return {
        "best": valid_combos[0] if valid_combos else all_results[0],
        "all_valid": valid_combos,
        "all_states": all_results
    }

def solve_portfolio(lam=1.0, mu=3.0, reps=3, capital=None, nu=1.0, custom_profits=None, custom_risks=None, custom_principals=None):
    qp = build_qubo(lam=lam, mu=mu, capital=capital, nu=nu, custom_profits=custom_profits, custom_risks=custom_risks, custom_principals=custom_principals)
    
    sampler = Sampler()
    optimizer = COBYLA(maxiter=120)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=reps)
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    
    bitstring = "".join(str(int(result.x[i])) for i in range(5))
    q_eval = evaluate_portfolio(bitstring, lam=lam, mu=mu, capital=capital, nu=nu, custom_profits=custom_profits, custom_risks=custom_risks, custom_principals=custom_principals)
    
    samples_list = []
    if hasattr(result, "samples") and result.samples:
        for s in result.samples:
            s_bit = "".join(str(int(s.x[i])) for i in range(5))
            eval_s = evaluate_portfolio(s_bit, lam=lam, mu=mu, capital=capital, nu=nu, custom_profits=custom_profits, custom_risks=custom_risks, custom_principals=custom_principals)
            samples_list.append({
                "bitstring": s_bit,
                "probability": float(round(float(s.probability) * 100.0, 2)),
                "shots": int(round(float(s.probability) * 1024)),
                "objective": float(round(float(s.fval), 4)),
                "is_valid": bool(eval_s["is_valid"]),
                "k": int(eval_s["k"]),
                "loans": eval_s["selected_loans"]
            })
        samples_list.sort(key=lambda x: x["probability"], reverse=True)
    
    c_res = solve_classical(lam=lam, mu=mu, capital=capital, nu=nu, custom_profits=custom_profits, custom_risks=custom_risks, custom_principals=custom_principals)
    
    divergence = "0.0%" if q_eval["objective"] == c_res["best"]["objective"] else f"{abs(q_eval['objective'] - c_res['best']['objective']):.2f}"
    
    ret_loans = []
    for i, l in enumerate(LOANS):
        nl = l.copy()
        if custom_principals is not None:
            nl["principal"] = float(custom_principals[i])
            nl["principal_fmt"] = f"₹{nl['principal']:.2f} Cr"
        if custom_profits is not None:
            nl["profit"] = float(custom_profits[i])
            nl["profit_fmt"] = f"₹{nl['profit']*10:.1f} L"
        ret_loans.append(nl)

    return {
        "quantum": q_eval,
        "classical": c_res["best"],
        "verification": {
            "is_optimal": bool(q_eval["objective"] == c_res["best"]["objective"]),
            "ground_truth_match": bool(q_eval["selected_indices"] == c_res["best"]["selected_indices"]),
            "divergence": divergence
        },
        "samples": samples_list,
        "loans": ret_loans,
        "risk_matrix": RISK_MATRIX,
        "params": {"lambda": float(lam), "mu": float(mu), "reps": int(reps)}
    }
