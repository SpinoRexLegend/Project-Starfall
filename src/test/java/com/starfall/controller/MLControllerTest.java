package com.starfall.controller;

import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.service.MLAnalysisService;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class MLControllerTest {

    @Test
    void sendsCompleteAsteroidAndSimulationDetailsToAgentService() {
        StubMLAnalysisService service = new StubMLAnalysisService();
        MLController controller = new MLController(service);
        Asteroid asteroid = asteroid();
        List<HashMap<String, Object>> simulations = List.of(
                simulation("SIM-A", 42.0, 1),
                simulation("SIM-B", 99.0, 0));

        controller.processQuantumOptimization(asteroid, simulations);

        assertEquals(asteroid, service.asteroid);
        assertEquals(simulations, service.simulations);
    }

    private Asteroid asteroid() {
        Asteroid asteroid = new Asteroid();
        asteroid.setAsteroid_Id("AST-1");
        asteroid.setName("Test asteroid");
        asteroid.setDiameter(100.0);
        asteroid.setVelocity(20.0);
        asteroid.setComposition("Iron");
        asteroid.setDSource("Test source");
        asteroid.setDDate("2026-11-10");
        return asteroid;
    }

    private HashMap<String, Object> simulation(String id, double distance, int success) {
        HashMap<String, Object> simulation = new HashMap<>();
        simulation.put("SimulationID", id);
        simulation.put(
                "Distance from which it will pass if force is applied at that angle",
                distance);
        simulation.put("Chances of success", success);
        return simulation;
    }

    private static final class StubMLAnalysisService extends MLAnalysisService {
        private Asteroid asteroid;
        private List<HashMap<String, Object>> simulations;

        private StubMLAnalysisService() {
            super(null, null, "http://python");
        }

        @Override
        public HashMap<String, Object> callQuantumPython(
                Asteroid asteroid,
                List<HashMap<String, Object>> simulations) {
            this.asteroid = asteroid;
            this.simulations = simulations;
            return new HashMap<>();
        }
    }
}
