import itertools
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning)
from scipy.sparse import SparseEfficiencyWarning
warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA

try:
    from qiskit.primitives import StatevectorSampler as Sampler
except ImportError:
    try:
        from qiskit.primitives import Sampler
    except ImportError:
        from qiskit_algorithms.utils import algorithm_globals
        Sampler = None

DEFAULT_LOANS = [
    {"id": "LN-101", "code": "LN-101", "sector": "Agri-Tech & Spice Processing", "sector_short": "Agri", "profit": 4.2, "principal": 2.8, "rating": "A+", "collateral": "140%"},
    {"id": "LN-102", "code": "LN-102", "sector": "Renewable Solar Micro-Grid", "sector_short": "CleanTech", "profit": 6.7, "principal": 4.2, "rating": "AA", "collateral": "155%"},
    {"id": "LN-103", "code": "LN-103", "sector": "Marine Exports & Cold Chain", "sector_short": "ColdChain", "profit": 5.2, "principal": 3.5, "rating": "A", "collateral": "110%"},
    {"id": "LN-104", "code": "LN-104", "sector": "Healthcare Diagnostics Hub", "sector_short": "MedTech", "profit": 4.8, "principal": 1.8, "rating": "A+", "collateral": "135%"},
    {"id": "LN-105", "code": "LN-105", "sector": "Commercial Retail & Textile", "sector_short": "Retail", "profit": 3.0, "principal": 2.5, "rating": "BBB+", "collateral": "105%"}
]

DEFAULT_RISK_MATRIX = [
    [0.00, 0.12, 0.28, 0.18, 0.45],
    [0.12, 0.00, 0.15, 0.22, 0.31],
    [0.28, 0.15, 0.00, 0.33, 0.78],
    [0.18, 0.22, 0.33, 0.00, 0.26],
    [0.45, 0.31, 0.78, 0.26, 0.00]
]

def validate_inputs(loans, risk_matrix):
    """
    Validates loan and risk matrix inputs:
    - 5 loans, each with numeric profit
    - 5x5 symmetric risk matrix with zero diagonal
    """
    if not isinstance(loans, (list, tuple)) or len(loans) != 5:
        raise ValueError(f"Expected exactly 5 loan applications, received {len(loans) if isinstance(loans, list) else type(loans)}")
    
    for idx, loan in enumerate(loans):
        if not isinstance(loan, dict):
            raise ValueError(f"Loan at index {idx} must be an object/dict")
        profit = loan.get("profit")
        if profit is None or not isinstance(profit, (int, float, np.number)):
            try:
                float(profit)
            except (ValueError, TypeError):
                raise ValueError(f"Loan {idx + 1} ({loan.get('sector', 'Unknown')}): profit must be a numeric value, got '{profit}'")

    if not isinstance(risk_matrix, (list, tuple)) or len(risk_matrix) != 5:
        raise ValueError("Risk matrix must be a 5x5 matrix (list of 5 rows)")
    
    for r_idx, row in enumerate(risk_matrix):
        if not isinstance(row, (list, tuple)) or len(row) != 5:
            raise ValueError(f"Risk matrix row {r_idx} must contain exactly 5 numeric values")
        for c_idx, val in enumerate(row):
            try:
                float(val)
            except (ValueError, TypeError):
                raise ValueError(f"Risk matrix cell [{r_idx}, {c_idx}] must be numeric, got '{val}'")
    
    # Zero diagonal check
    for i in range(5):
        diag_val = float(risk_matrix[i][i])
        if abs(diag_val) > 1e-4:
            raise ValueError(f"Risk matrix diagonal cell [{i},{i}] must be 0.0 (received {diag_val})")
            
    # Symmetry check
    for i in range(5):
        for j in range(i + 1, 5):
            val_ij = float(risk_matrix[i][j])
            val_ji = float(risk_matrix[j][i])
            if abs(val_ij - val_ji) > 1e-4:
                raise ValueError(f"Risk matrix must be symmetric: cell [{i},{j}] ({val_ij}) != cell [{j},{i}] ({val_ji})")

def compute_auto_scaled_mu(profits, risks, lam=1.0, base_mu=3.0):
    """
    Calculates auto-scaled mu constraint weight so that the cardinality constraint
    (sum(x_i) - 3)^2 ALWAYS dominates the objective function regardless of the scale
    of profits or risks entered by the user.
    """
    total_abs_profit = sum(abs(float(p)) for p in profits)
    total_abs_risk = sum(abs(float(risks[i][j])) for i in range(5) for j in range(5))
    
    # Penalty of missing cardinality by 1 is mu * ((k - 3)^2 - 0) >= mu.
    # The max unconstrained profit swing is total_abs_profit + lam * total_abs_risk.
    safe_mu = 2.0 * (total_abs_profit + lam * total_abs_risk) + 10.0
    return max(float(base_mu), float(safe_mu))

def build_qubo(profits, risks, lam=1.0, mu=3.0, capital=None, nu=1.0, principals=None):
    """
    Constructs QuadraticProgram for H = -sum(profit_i * x_i) + lambda * sum(risk_ij * x_i * x_j) + mu * (sum(x_i) - 3)^2
    Optionally incorporates capital budget penalty if specified.
    """
    qp = QuadraticProgram("Thrissur_Bank_Loan_Optimization")
    for i in range(5):
        qp.binary_var(name=f"x_{i}")
        
    linear = {}
    for i in range(5):
        # Penalty expansion: mu*(sum(x) - 3)^2 = -5*mu*x_i + 2*mu*x_i*x_j + 9*mu
        linear[f"x_{i}"] = -float(profits[i]) - 5.0 * float(mu)
        
    quadratic = {}
    for i in range(5):
        for j in range(i + 1, 5):
            coupling = float(lam) * (float(risks[i][j]) + float(risks[j][i])) + 2.0 * float(mu)
            quadratic[(f"x_{i}", f"x_{j}")] = coupling
            
    constant = 9.0 * float(mu)
    
    if capital is not None and principals is not None:
        C = float(capital)
        for i in range(5):
            pi = float(principals[i])
            linear[f"x_{i}"] += nu * (pi**2 - 2 * C * pi)
        for i in range(5):
            for j in range(i + 1, 5):
                pi = float(principals[i])
                pj = float(principals[j])
                quadratic[(f"x_{i}", f"x_{j}")] += 2.0 * nu * pi * pj
        constant += nu * (C**2)

    qp.minimize(constant=constant, linear=linear, quadratic=quadratic)
    return qp

def evaluate_combination(x, profits, risks, lam=1.0, mu=3.0, capital=None, nu=1.0, principals=None):
    """
    Evaluates a 5-bit combination for profit, risk, penalty, and overall Hamiltonian objective.
    """
    bitstring = "".join(str(int(b)) for b in x)
    selected_indices = [i for i, b in enumerate(x) if b == 1]
    k = sum(x)
    
    profit = sum(float(profits[i]) for i in selected_indices)
    risk = sum(float(risks[i][j]) for i in selected_indices for j in selected_indices)
    cardinality_penalty = float(mu) * ((k - 3) ** 2)
    
    cap_penalty = 0.0
    total_principal = 0.0
    is_valid = bool(k == 3)
    
    if principals is not None:
        total_principal = sum(float(principals[i]) for i in selected_indices)
        if capital is not None and total_principal > float(capital):
            is_valid = False
            cap_penalty = float(nu) * ((total_principal - float(capital)) ** 2)
            
    # Unpenalized objective (what bank wants to minimize: -profit + lam*risk)
    unpenalized_obj = -profit + float(lam) * risk
    # Total Hamiltonian objective including constraint penalties
    total_obj = unpenalized_obj + cardinality_penalty + cap_penalty
    
    return {
        "bitstring": bitstring,
        "selected_indices": selected_indices,
        "k": int(k),
        "is_valid": is_valid,
        "total_profit": float(round(profit, 4)),
        "total_risk": float(round(risk, 4)),
        "total_principal": float(round(total_principal, 4)),
        "cardinality_penalty": float(round(cardinality_penalty, 4)),
        "objective": float(round(unpenalized_obj, 4)),
        "hamiltonian_energy": float(round(total_obj, 4))
    }

def solve_brute_force(profits, risks, lam=1.0, mu=3.0, capital=None, nu=1.0, principals=None):
    """
    Brute-force exact solver: enumerates all C(5,3) = 10 combinations of exactly 3 loans.
    Provides the mathematically certified ground truth optimum.
    """
    all_combos = []
    for combo in itertools.combinations(range(5), 3):
        x = [1 if i in combo else 0 for i in range(5)]
        eval_res = evaluate_combination(x, profits, risks, lam=lam, mu=mu, capital=capital, nu=nu, principals=principals)
        all_combos.append(eval_res)
        
    # Sort by valid first, then by lowest unpenalized objective (-profit + lambda*risk)
    all_combos.sort(key=lambda item: (not item["is_valid"], item["objective"]))
    best_exact = all_combos[0]
    return {
        "best": best_exact,
        "all_combinations": all_combos
    }

def solve_portfolio(loans=None, risk_matrix=None, lam=1.0, mu=3.0, auto_scale_mu=True, reps=2, capital=None, nu=1.0):
    """
    Full solver pipeline:
    1. Validates inputs
    2. Auto-scales mu if requested
    3. Builds QUBO
    4. Solves with QAOA (COBYLA, reps=2, StatevectorSampler)
    5. Solves with Brute-Force enumeration C(5,3)=10
    6. Verifies whether QAOA matches ground truth
    """
    # 1. Fallback to default if not provided
    if loans is None:
        loans = DEFAULT_LOANS
    if risk_matrix is None:
        risk_matrix = DEFAULT_RISK_MATRIX
        
    validate_inputs(loans, risk_matrix)
    
    profits = [float(l["profit"]) for l in loans]
    principals = [float(l.get("principal", 2.0)) for l in loans]
    
    # 2. Determine effective mu
    if auto_scale_mu:
        eff_mu = compute_auto_scaled_mu(profits, risk_matrix, lam=lam, base_mu=mu)
    else:
        eff_mu = float(mu)
        
    # 3. Brute Force Ground Truth
    bf_result = solve_brute_force(
        profits, risk_matrix, lam=lam, mu=eff_mu, 
        capital=capital, nu=nu, principals=principals
    )
    best_bf = bf_result["best"]
    
    # 4. QAOA Solver
    qp = build_qubo(
        profits, risk_matrix, lam=lam, mu=eff_mu, 
        capital=capital, nu=nu, principals=principals
    )
    
    sampler = Sampler()
    optimizer = COBYLA(maxiter=100)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=int(reps))
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    
    q_x = [int(result.x[i]) for i in range(5)]
    q_eval = evaluate_combination(
        q_x, profits, risk_matrix, lam=lam, mu=eff_mu, 
        capital=capital, nu=nu, principals=principals
    )
    
    # Format samples distribution
    samples_list = []
    if hasattr(result, "samples") and result.samples:
        for s in result.samples:
            s_x = [int(s.x[i]) for i in range(5)]
            s_eval = evaluate_combination(
                s_x, profits, risk_matrix, lam=lam, mu=eff_mu, 
                capital=capital, nu=nu, principals=principals
            )
            prob_pct = float(round(float(s.probability) * 100.0, 2))
            samples_list.append({
                "bitstring": s_eval["bitstring"],
                "probability": prob_pct,
                "shots": int(round(float(s.probability) * 1024)),
                "objective": s_eval["objective"],
                "energy": float(round(float(s.fval), 4)),
                "is_valid": s_eval["is_valid"],
                "k": s_eval["k"],
                "selected_indices": s_eval["selected_indices"]
            })
        samples_list.sort(key=lambda item: item["probability"], reverse=True)
        
    # Check if QAOA matched brute force
    matched = (set(q_eval["selected_indices"]) == set(best_bf["selected_indices"]))
    divergence_str = "0.0%" if matched else f"Δ = {abs(q_eval['objective'] - best_bf['objective']):.2f}"

    # Annotate loans with selected flags
    enriched_loans = []
    for idx, l in enumerate(loans):
        l_copy = dict(l)
        l_copy["index"] = idx
        l_copy["qaoa_selected"] = (idx in q_eval["selected_indices"])
        l_copy["bf_selected"] = (idx in best_bf["selected_indices"])
        l_copy["profit"] = float(profits[idx])
        l_copy["principal"] = float(principals[idx])
        enriched_loans.append(l_copy)

    # Attach sector names to selected outputs
    q_eval["selected_loans"] = [enriched_loans[i]["id"] for i in q_eval["selected_indices"]]
    q_eval["selected_sectors"] = [enriched_loans[i]["sector"] for i in q_eval["selected_indices"]]
    best_bf["selected_loans"] = [enriched_loans[i]["id"] for i in best_bf["selected_indices"]]
    best_bf["selected_sectors"] = [enriched_loans[i]["sector"] for i in best_bf["selected_indices"]]

    return {
        "status": "success",
        "matched": matched,
        "selected_loans_qaoa": q_eval["selected_loans"],
        "selected_loans_brute_force": best_bf["selected_loans"],
        "selected_sectors_qaoa": q_eval["selected_sectors"],
        "selected_sectors_brute_force": best_bf["selected_sectors"],
        "total_profit_qaoa": q_eval["total_profit"],
        "total_profit_brute_force": best_bf["total_profit"],
        "total_risk_qaoa": q_eval["total_risk"],
        "total_risk_brute_force": best_bf["total_risk"],
        "objective_qaoa": q_eval["objective"],
        "objective_brute_force": best_bf["objective"],
        "divergence": divergence_str,
        "quantum": q_eval,
        "classical": best_bf,
        "brute_force_all": bf_result["all_combinations"],
        "samples": samples_list,
        "loans": enriched_loans,
        "risk_matrix": risk_matrix,
        "qubo_params": {
            "lambda": float(lam),
            "mu_effective": float(round(eff_mu, 2)),
            "mu_base": float(mu),
            "auto_scaled": bool(auto_scale_mu),
            "reps": int(reps)
        },
        "verification": {
            "is_optimal": matched,
            "ground_truth_match": matched,
            "divergence": divergence_str
        }
    }
