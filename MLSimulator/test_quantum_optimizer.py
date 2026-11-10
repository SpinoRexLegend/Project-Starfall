import unittest

from QuantumOptimizer import QuantumOptimizationError, perform_quantum_optimization


class QuantumOptimizerTest(unittest.TestCase):

    def test_grover_selects_largest_eligible_score(self):
        result = perform_quantum_optimization(
            [
                {"simulationId": "SIM-A", "score": 12.0, "eligible": True},
                {"simulationId": "SIM-B", "score": 91.0, "eligible": True},
                {"simulationId": "SIM-C", "score": 55.0, "eligible": True}
            ],
            shots=2048,
            seed=7
        )

        self.assertEqual(91.0, result["largestScore"])
        self.assertEqual("SIM-B", result["selectedSimulationID"])
        self.assertEqual(["SIM-B"], result["markedSimulationIDs"])
        self.assertEqual(2, result["qubitsUsed"])
        self.assertEqual("Qiskit StatevectorSampler", result["executionBackend"])

        probabilities = {
            item["label"]: item["probabilityHeight"]
            for item in result["bar_chart"]
        }
        self.assertGreater(probabilities["SIM-B"], probabilities["SIM-A"])
        self.assertGreater(probabilities["SIM-B"], probabilities["SIM-C"])

    def test_failed_candidate_cannot_be_selected(self):
        result = perform_quantum_optimization(
            [
                {"simulationId": "FAILED", "score": 999.0, "eligible": False},
                {"simulationId": "SUCCESS", "score": 10.0, "eligible": True}
            ],
            shots=1024,
            seed=11
        )

        self.assertEqual(10.0, result["largestScore"])
        self.assertEqual("SUCCESS", result["selectedSimulationID"])

    def test_qubit_count_scales_with_candidate_count(self):
        candidates = [
            {"simulationId": f"SIM-{index}", "score": float(index), "eligible": True}
            for index in range(5)
        ]

        result = perform_quantum_optimization(candidates, shots=1024, seed=13)

        self.assertEqual(3, result["qubitsUsed"])
        self.assertEqual("SIM-4", result["selectedSimulationID"])

    def test_requires_an_eligible_candidate(self):
        with self.assertRaises(QuantumOptimizationError):
            perform_quantum_optimization(
                [{"simulationId": "SIM-A", "score": 1.0, "eligible": False}],
                shots=128,
                seed=1
            )


if __name__ == "__main__":
    unittest.main()
