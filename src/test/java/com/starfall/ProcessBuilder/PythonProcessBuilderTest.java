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
                .buildQuantumRequest(asteroid, simulations);

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
}
