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
    {"id": "L1", "code": "LN-101", "sector": "Textiles", "profit": 1.8, "principal": 2.8},
    {"id": "L2", "code": "LN-102", "sector": "Agri", "profit": 1.5, "principal": 4.2},
    {"id": "L3", "code": "LN-103", "sector": "Retail", "profit": 2.0, "principal": 3.5},
    {"id": "L4", "code": "LN-104", "sector": "Transport", "profit": 1.2, "principal": 1.8},
    {"id": "L5", "code": "LN-105", "sector": "Construction", "profit": 2.4, "principal": 2.5}
]

RISK_MATRIX = [
    [0.0, 0.3, 0.5, 0.2, 0.4],
    [0.3, 0.0, 0.3, 0.6, 0.2],
    [0.5, 0.3, 0.0, 0.3, 0.5],
    [0.2, 0.6, 0.3, 0.0, 0.3],
    [0.4, 0.2, 0.5, 0.3, 0.0]
]

def build_qubo(lam=1.0, mu=3.0, capital=None):
    profits = [l["profit"] for l in LOANS]
    risks = RISK_MATRIX
    
    qp = QuadraticProgram("Loan_Portfolio_Optimization")
    for i in range(5):
        qp.binary_var(name=f"x_{i}")
        
    linear = {f"x_{i}": -profits[i] for i in range(5)}
    quadratic = {}
    for i in range(5):
        for j in range(i + 1, 5):
            coupling = lam * (risks[i][j] + risks[j][i])
            quadratic[(f"x_{i}", f"x_{j}")] = coupling
            
    qp.minimize(linear=linear, quadratic=quadratic)
    
    qp.linear_constraint(linear={f"x_{i}": 1 for i in range(5)}, sense="==", rhs=3, name="k_limit")
    
    if capital is not None:
        qp.linear_constraint(linear={f"x_{i}": LOANS[i]["principal"] for i in range(5)}, sense="<=", rhs=capital, name="cap_limit")
        
    from qiskit_optimization.converters import QuadraticProgramToQubo
    conv = QuadraticProgramToQubo(penalty=mu)
    qubo = conv.convert(qp)
    return qubo

qubo = build_qubo(capital=8.0)
print(qubo.export_as_lp_string())

sampler = Sampler()
optimizer = COBYLA(maxiter=10)
qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)
meo = MinimumEigenOptimizer(qaoa)
res = meo.solve(qubo)
print(res)
