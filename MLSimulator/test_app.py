import unittest
from unittest.mock import patch

from App import app


class StarfallApiTest(unittest.TestCase):

    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/internal/v1/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual("UP", response.get_json()["status"])

    def test_versioned_simulation_endpoint(self):
        response = self.client.post("/internal/v1/simulations", json={
            "Material": "Iron",
            "Diameter": 100.0,
            "Velocity": 20.0
        })

        body = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual("success", body["status"])
        self.assertEqual(8, len(body["output"]))

    def test_legacy_simulation_endpoint_remains_compatible(self):
        response = self.client.post("/predict", json={
            "Material": "Iron",
            "Diameter": 100.0,
            "Velocity": 20.0
        })

        self.assertEqual(200, response.status_code)

    def test_simulation_rejects_invalid_values(self):
        response = self.client.post("/internal/v1/simulations", json={
            "Material": "Iron",
            "Diameter": -1,
            "Velocity": 20.0
        })

        self.assertEqual(400, response.status_code)
        self.assertEqual("VALIDATION_ERROR", response.get_json()["code"])

    def test_risk_assessment_rejects_missing_fields(self):
        response = self.client.post("/internal/v1/risk-assessments", json={
            "asteroidID": "A-1"
        })

        self.assertEqual(400, response.status_code)

    def test_optimization_requires_simulations(self):
        response = self.client.post("/internal/v1/optimizations", json={
            "asteroid": {"asteroidID": "A-1"},
            "simulations": []
        })

        self.assertEqual(400, response.status_code)

    @patch("App.AgenticPlanner.generate_grover_plan")
    def test_optimization_sends_agent_candidates_to_grover(self, generate_plan):
        generate_plan.return_value = {
            "model": "test-model",
            "summary": "SIM-B is the safest feasible strategy.",
            "candidates": [
                {"simulationId": "SIM-A", "score": 10.0, "eligible": True, "rationale": "Lower margin"},
                {"simulationId": "SIM-B", "score": 50.0, "eligible": True, "rationale": "Best margin"},
                {"simulationId": "SIM-C", "score": 20.0, "eligible": True, "rationale": "Moderate margin"}
            ]
        }
        asteroid = {"asteroidID": "A-1", "diameterKm": 100.0, "velocityKmps": 20.0}
        simulations = [
            {"SimulationID": "SIM-A", "Chances of success": 1, "Fuel Cost": 30.0},
            {"SimulationID": "SIM-B", "Chances of success": 1, "Fuel Cost": 20.0},
            {"SimulationID": "SIM-C", "Chances of success": 1, "Fuel Cost": 25.0}
        ]
        response = self.client.post("/internal/v1/optimizations", json={
            "asteroid": asteroid,
            "simulations": simulations
        })

        body = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(50.0, body["output"]["largestScore"])
        self.assertEqual("SIM-B", body["output"]["selectedSimulationID"])
        self.assertEqual("test-model", body["output"]["agent"]["model"])
        generate_plan.assert_called_once_with(asteroid, simulations)

    @patch("App.AgenticPlanner.generate_grover_plan")
    def test_optimization_accepts_candidates_from_separate_agent_service(self, generate_plan):
        candidates = [
            {"simulationId": "SIM-A", "score": 10.0, "eligible": True, "rationale": "Lower"},
            {"simulationId": "SIM-B", "score": 80.0, "eligible": True, "rationale": "Best"}
        ]
        agent = {
            "model": "starfall-local-safety-agent",
            "mode": "fallback",
            "summary": "Validated separately.",
            "candidateAssessments": candidates
        }

        response = self.client.post("/internal/v1/optimizations", json={
            "candidates": candidates,
            "agent": agent
        })

        body = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual("SIM-B", body["output"]["selectedSimulationID"])
        self.assertEqual(agent, body["output"]["agent"])
        generate_plan.assert_not_called()

    @patch("App.QuantumOptimizer.perform_quantum_optimization")
    @patch("App.AgenticPlanner.generate_fallback_plan")
    @patch("App.AgenticPlanner.generate_grover_plan")
    def test_optimization_uses_fallback_when_agent_is_unavailable(
            self, generate_plan, generate_fallback, optimize):
        asteroid = {"asteroidID": "A-1"}
        simulations = [{"SimulationID": "SIM-A", "Chances of success": 1}]

        generate_plan.side_effect = __import__("AgenticPlanner").AgentPlanningError(
            "provider unavailable"
        )
        generate_fallback.return_value = {
            "model": "starfall-local-safety-agent",
            "mode": "fallback",
            "summary": "Local safety policy used.",
            "candidates": [{
                "simulationId": "SIM-A",
                "score": 50.0,
                "eligible": True,
                "rationale": "Eligible"
            }]
        }
        optimize.return_value = {
            "largestScore": 50.0,
            "selectedSimulationID": "SIM-A"
        }

        with patch.dict("os.environ", {}, clear=True):
            response = self.client.post("/internal/v1/optimizations", json={
                "asteroid": asteroid,
                "simulations": simulations
            })

        body = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual("fallback", body["output"]["agent"]["mode"])
        generate_fallback.assert_called_once_with(asteroid, simulations)


if __name__ == "__main__":
    unittest.main()
