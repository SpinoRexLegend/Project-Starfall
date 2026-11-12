import unittest
from unittest.mock import patch

from AgentService.App import app
from MLSimulator import AgenticPlanner


class AgentServiceApiTest(unittest.TestCase):

    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.payload = {
            "asteroid": {"asteroidID": "AST-1", "diameterKm": 0.05},
            "simulations": [{
                "SimulationID": "SIM-A",
                "Chances of success": 1,
                "Fuel Cost": 10.0
            }]
        }

    def test_health_identifies_agent_service(self):
        response = self.client.get("/internal/v1/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual("starfall-agent", response.get_json()["service"])

    @patch("AgentService.App.AgenticPlanner.generate_fallback_plan")
    @patch("AgentService.App.AgenticPlanner.generate_grover_plan")
    def test_returns_fallback_plan_when_external_agent_is_unavailable(
            self, generate_plan, generate_fallback):
        generate_plan.side_effect = AgenticPlanner.AgentPlanningError("offline")
        generate_fallback.return_value = {
            "model": "starfall-local-safety-agent",
            "mode": "fallback",
            "summary": "Validated locally.",
            "recommendation": "Proceed with SIM-A.",
            "candidates": [{
                "simulationId": "SIM-A",
                "score": 50.0,
                "eligible": True,
                "rationale": "Eligible"
            }]
        }

        with patch.dict("os.environ", {}, clear=True):
            response = self.client.post(
                "/internal/v1/agent-decisions",
                json=self.payload
            )

        body = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual("fallback", body["output"]["mode"])
        generate_fallback.assert_called_once_with(
            self.payload["asteroid"],
            self.payload["simulations"]
        )

    def test_rejects_missing_case_context(self):
        response = self.client.post(
            "/internal/v1/agent-decisions",
            json={"asteroid": {}, "simulations": []}
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual("VALIDATION_ERROR", response.get_json()["code"])


if __name__ == "__main__":
    unittest.main()
