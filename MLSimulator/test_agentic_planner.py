import json
import unittest
from unittest.mock import patch

import AgenticPlanner
from AgenticPlanner import AgentPlanningError


class AgenticPlannerTest(unittest.TestCase):

    def setUp(self):
        self.asteroid = {
            "asteroidID": "AST-1",
            "diameterKm": 100.0,
            "velocityKmps": 20.0,
            "composition": "Iron"
        }
        self.simulations = [
            {
                "SimulationID": "SIM-A",
                "Chances of success": 1,
                "Fuel Cost": 40.0,
                "Distance from which it will pass if force is applied at that angle": 1000.0
            },
            {
                "SimulationID": "SIM-B",
                "Chances of success": 0,
                "Fuel Cost": 20.0,
                "Distance from which it will pass if force is applied at that angle": 5000.0
            }
        ]

    def test_sends_all_details_and_returns_validated_plan(self):
        response = self._provider_response({
            "summary": "SIM-A is the only successful option.",
            "recommendation": "Proceed with SIM-A because it is the only successful option.",
            "candidates": [
                {"simulationId": "SIM-A", "score": 82, "eligible": True, "rationale": "Successful"},
                {"simulationId": "SIM-B", "score": 30, "eligible": False, "rationale": "Failed"}
            ]
        })

        with patch.dict("os.environ", {
            "OPENAI_API_KEY": "test-key",
            "AI_AGENT_MODEL": "test-model"
        }, clear=True), patch.object(
            AgenticPlanner,
            "_call_responses_api",
            return_value=response
        ) as api_call:
            plan = AgenticPlanner.generate_grover_plan(self.asteroid, self.simulations)

        payload = api_call.call_args.args[1]
        sent_context = json.loads(payload["input"])
        self.assertEqual(self.asteroid, sent_context["asteroid"])
        self.assertEqual(self.simulations, sent_context["simulations"])
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual("test-model", plan["model"])
        self.assertEqual("external-agent", plan["mode"])
        self.assertEqual(
            "Proceed with SIM-A because it is the only successful option.",
            plan["recommendation"]
        )
        self.assertEqual(82.0, plan["candidates"][0]["score"])

    def test_fallback_plan_scores_request_data_and_excludes_failed_runs(self):
        self.simulations[0]["Execution time for hitting the earth"] = 8.0
        self.simulations.append({
            "SimulationID": "SIM-C",
            "Chances of success": 1,
            "Fuel Cost": 10.0,
            "Distance from which it will pass if force is applied at that angle": 9000.0,
            "Execution time for hitting the earth": 4.0
        })

        with patch.dict("os.environ", {}, clear=True):
            plan = AgenticPlanner.generate_fallback_plan(self.asteroid, self.simulations)

        candidates = {item["simulationId"]: item for item in plan["candidates"]}
        self.assertEqual("fallback", plan["mode"])
        self.assertEqual("starfall-local-safety-agent", plan["model"])
        self.assertNotIn("unavailable", plan["summary"].lower())
        self.assertGreater(candidates["SIM-C"]["score"], candidates["SIM-A"]["score"])
        self.assertFalse(candidates["SIM-B"]["eligible"])
        self.assertEqual(0.0, candidates["SIM-B"]["score"])

    def test_rejects_hallucinated_simulation_id(self):
        response = self._provider_response({
            "summary": "Invalid plan",
            "recommendation": "Proceed with MADE-UP.",
            "candidates": [
                {"simulationId": "MADE-UP", "score": 99, "eligible": True, "rationale": "Invented"},
                {"simulationId": "SIM-B", "score": 1, "eligible": False, "rationale": "Failed"}
            ]
        })

        with self._configured_provider(response):
            with self.assertRaisesRegex(AgentPlanningError, "unknown simulation ID"):
                AgenticPlanner.generate_grover_plan(self.asteroid, self.simulations)

    def test_rejects_failed_simulation_marked_eligible(self):
        response = self._provider_response({
            "summary": "Invalid plan",
            "recommendation": "Proceed with SIM-B.",
            "candidates": [
                {"simulationId": "SIM-A", "score": 50, "eligible": True, "rationale": "Successful"},
                {"simulationId": "SIM-B", "score": 90, "eligible": True, "rationale": "Unsafe"}
            ]
        })

        with self._configured_provider(response):
            with self.assertRaisesRegex(AgentPlanningError, "unsuccessful simulation"):
                AgenticPlanner.generate_grover_plan(self.asteroid, self.simulations)

    def test_requires_runtime_credentials_and_model(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(AgentPlanningError, "OPENAI_API_KEY"):
                AgenticPlanner.generate_grover_plan(self.asteroid, self.simulations)

    def test_rejects_plan_without_final_recommendation(self):
        response = self._provider_response({
            "summary": "SIM-A is the only successful option.",
            "candidates": [
                {"simulationId": "SIM-A", "score": 82, "eligible": True, "rationale": "Successful"},
                {"simulationId": "SIM-B", "score": 0, "eligible": False, "rationale": "Failed"}
            ]
        })

        with self._configured_provider(response):
            with self.assertRaisesRegex(AgentPlanningError, "final recommendation"):
                AgenticPlanner.generate_grover_plan(self.asteroid, self.simulations)

    def _configured_provider(self, response):
        environment = patch.dict("os.environ", {
            "OPENAI_API_KEY": "test-key",
            "AI_AGENT_MODEL": "test-model"
        }, clear=True)
        provider = patch.object(AgenticPlanner, "_call_responses_api", return_value=response)

        class CombinedContext:
            def __enter__(self_inner):
                environment.start()
                provider.start()

            def __exit__(self_inner, exception_type, exception, traceback):
                provider.stop()
                environment.stop()

        return CombinedContext()

    def _provider_response(self, plan):
        return {
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": json.dumps(plan)
                }]
            }]
        }


if __name__ == "__main__":
    unittest.main()
