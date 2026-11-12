package com.starfall.ProcessBuilder;

import com.starfall.DatabaseHandling.Asteroid;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PythonProcessBuilderTest {

    @Test
    void buildsAgentRequestWithEveryAsteroidFieldAndUnmodifiedSimulations() {
        Asteroid asteroid = new Asteroid();
        asteroid.setAsteroid_Id("AST-1");
        asteroid.setName("Test asteroid");
        asteroid.setDiameter(100.0);
        asteroid.setVelocity(20.0);
        asteroid.setComposition("Iron");
        asteroid.setDSource("Test source");
        asteroid.setDDate("2026-11-10");

        HashMap<String, Object> simulation = new HashMap<>();
        simulation.put("SimulationID", "SIM-1");
        simulation.put("Fuel Cost", 25.0);
        List<HashMap<String, Object>> simulations = List.of(simulation);

        HashMap<String, Object> request = new PythonProcessBuilder()
                .buildAgentRequest(asteroid, simulations);

        Map<?, ?> asteroidDetails = (Map<?, ?>) request.get("asteroid");
        assertEquals("AST-1", asteroidDetails.get("asteroidID"));
        assertEquals("Test asteroid", asteroidDetails.get("name"));
        assertEquals(100.0, asteroidDetails.get("diameterKm"));
        assertEquals(20.0, asteroidDetails.get("velocityKmps"));
        assertEquals("Iron", asteroidDetails.get("composition"));
        assertEquals("Test source", asteroidDetails.get("detectionSource"));
        assertEquals("2026-11-10", asteroidDetails.get("detectionDate"));
        assertEquals(simulations, request.get("simulations"));
    }

    @Test
    void buildsQuantumRequestFromAgentPlanWithoutCaseContext() {
        List<HashMap<String, Object>> candidates = List.of(new HashMap<>(Map.of(
                "simulationId", "SIM-1",
                "score", 80.0,
                "eligible", true,
                "rationale", "Best")));
        HashMap<String, Object> plan = new HashMap<>();
        plan.put("model", "starfall-local-safety-agent");
        plan.put("mode", "fallback");
        plan.put("summary", "Validated separately.");
        plan.put("recommendation", "Proceed with SIM-1.");
        plan.put("candidates", candidates);

        HashMap<String, Object> request = new PythonProcessBuilder()
                .buildQuantumOptimizationRequest(plan);

        assertEquals(candidates, request.get("candidates"));
        Map<?, ?> agent = (Map<?, ?>) request.get("agent");
        assertEquals("starfall-local-safety-agent", agent.get("model"));
        assertEquals("Proceed with SIM-1.", agent.get("recommendation"));
        assertEquals(candidates, agent.get("candidateAssessments"));
    }
}
