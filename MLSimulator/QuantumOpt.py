from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import math

def create_oracle(target_binary, num_qubits):
    oracle = QuantumCircuit(num_qubits, name="Oracle")

    for i, bit in enumerate(reversed(target_binary)):
        if bit == '0':
            oracle.x(i)

    oracle.h(num_qubits - 1)
    oracle.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    oracle.h(num_qubits - 1)

    for i, bit in enumerate(reversed(target_binary)):
        if bit == '0':
            oracle.x(i)

    return oracle

def create_diffuser(num_qubits):
    diffuser = QuantumCircuit(num_qubits, name="Diffuser")

    diffuser.h(range(num_qubits))
    diffuser.x(range(num_qubits))

    diffuser.h(num_qubits - 1)
    diffuser.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    diffuser.h(num_qubits - 1)

    diffuser.x(range(num_qubits))
    diffuser.h(range(num_qubits))

    return diffuser

def find_high_risk_asteroid(target_binary):
    num_qubits = len(target_binary)
    num_iterations = math.floor((math.pi / 4) * math.sqrt(2**num_qubits))

    grover_circuit = QuantumCircuit(num_qubits, num_qubits)
    grover_circuit.h(range(num_qubits))
    grover_circuit.barrier()

    oracle = create_oracle(target_binary, num_qubits)
    diffuser = create_diffuser(num_qubits)

    for _ in range(num_iterations):
        grover_circuit.append(oracle, range(num_qubits))
        grover_circuit.append(diffuser, range(num_qubits))

    grover_circuit.barrier()
    grover_circuit.measure(range(num_qubits), range(num_qubits))

    simulator = AerSimulator()
    compiled_circuit = transpile(grover_circuit, simulator)
    result = simulator.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts(compiled_circuit)

    highest_prob_state = max(counts, key=counts.get)
    return highest_prob_state, counts, num_iterations

# =====================================================================
# Dynamic Execution
# =====================================================================
if __name__ == "__main__":
    # You can pass any binary string length dynamically here
    target_risk_id = input("Enter the binary ID of the high-risk asteroid to isolate (e.g., '101', '11010'): ")

    if target_risk_id.strip():
        found_id, results, iterations = find_high_risk_asteroid(target_risk_id)
        print(f"\nExecuted for {iterations} iterations.")
        print(f"=> The algorithm successfully isolated Asteroid ID: {found_id}")
        print(f"Full probability distribution: {results}")