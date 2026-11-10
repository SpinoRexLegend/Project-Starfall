import math
import uuid
from datetime import datetime, timezone

from qiskit import QuantumCircuit
from qiskit.circuit.library import grover_operator
from qiskit.primitives import StatevectorSampler


class QuantumOptimizationError(RuntimeError):
    pass


def _build_oracle(marked_indices, qubit_count):
    oracle = QuantumCircuit(qubit_count, name="largest-score oracle")

    for marked_index in marked_indices:
        marked_state = format(marked_index, f"0{qubit_count}b")
        zero_qubits = [
            qubit
            for qubit, bit in enumerate(reversed(marked_state))
            if bit == "0"
        ]

        if zero_qubits:
            oracle.x(zero_qubits)

        if qubit_count == 1:
            oracle.z(0)
        else:
            target_qubit = qubit_count - 1
            oracle.h(target_qubit)
            oracle.mcx(list(range(target_qubit)), target_qubit)
            oracle.h(target_qubit)

        if zero_qubits:
            oracle.x(zero_qubits)

    return oracle


def _optimal_iteration_count(state_count, marked_count):
    if marked_count <= 0 or marked_count >= state_count:
        return 0

    theta = math.asin(math.sqrt(marked_count / state_count))
    return math.floor(math.pi / (4 * theta))


def perform_quantum_optimization(candidates, shots, seed=None):
    if not candidates:
        raise QuantumOptimizationError("At least one candidate is required")
    if shots <= 0:
        raise QuantumOptimizationError("shots must be greater than zero")

    eligible_indices = [
        index for index, candidate in enumerate(candidates)
        if candidate["eligible"]
    ]
    if not eligible_indices:
        raise QuantumOptimizationError("No successful simulation is eligible for optimization")

    largest_score = max(candidates[index]["score"] for index in eligible_indices)
    marked_indices = [
        index for index in eligible_indices
        if math.isclose(
            candidates[index]["score"],
            largest_score,
            rel_tol=1e-12,
            abs_tol=1e-12
        )
    ]

    qubit_count = max(1, math.ceil(math.log2(len(candidates))))
    state_count = 2 ** qubit_count
    iterations = _optimal_iteration_count(state_count, len(marked_indices))

    oracle = _build_oracle(marked_indices, qubit_count)
    circuit = QuantumCircuit(qubit_count)
    circuit.h(range(qubit_count))

    if iterations > 0:
        amplification = grover_operator(oracle)
        for _ in range(iterations):
            circuit.compose(amplification, inplace=True)

    circuit.measure_all()

    try:
        sampler = StatevectorSampler(default_shots=shots, seed=seed)
        sampler_result = sampler.run([circuit], shots=shots).result()
        counts = sampler_result[0].data.meas.get_counts()
    except Exception as exception:
        raise QuantumOptimizationError("Qiskit Grover execution failed") from exception

    measured_index = max(
        marked_indices,
        key=lambda index: counts.get(format(index, f"0{qubit_count}b"), 0)
    )
    selected_candidate = candidates[measured_index]
    optimized_at = datetime.now(timezone.utc).isoformat()

    database_entries = []
    bar_chart = []

    for index, candidate in enumerate(candidates):
        state = format(index, f"0{qubit_count}b")
        probability = counts.get(state, 0) / shots
        is_marked = index in marked_indices

        database_entries.append({
            "QuantumID": "QTM-" + str(uuid.uuid4())[:8].upper(),
            "Qubits_used": qubit_count,
            "Iterations": iterations,
            "Optimal_probability": round(probability, 6),
            "Optimised_at": optimized_at,
            "Sim_ID": candidate["simulationId"]
        })
        bar_chart.append({
            "label": candidate["simulationId"][:8].upper(),
            "probabilityHeight": round(probability * 100, 4),
            "isOptimal": is_marked,
            "score": candidate["score"]
        })

    return {
        "algorithm": "Grover amplitude amplification",
        "executionBackend": "Qiskit StatevectorSampler",
        "largestScore": largest_score,
        "selectedSimulationID": selected_candidate["simulationId"],
        "markedSimulationIDs": [
            candidates[index]["simulationId"] for index in marked_indices
        ],
        "qubitsUsed": qubit_count,
        "iterations": iterations,
        "shots": shots,
        "database_entries": database_entries,
        "bar_chart": bar_chart
    }
