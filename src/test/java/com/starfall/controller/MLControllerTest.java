package com.starfall.controller;

import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.service.MLAnalysisService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.HashMap;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class MLControllerTest {

    @Mock
    private MLAnalysisService service;

    @InjectMocks
    private MLController controller;

    @Test
    void mapsAsteroidFieldsIntoSimulationRequest() {
        Asteroid asteroid = asteroid();
        List<HashMap<String, Object>> expected = List.of(simulation("SIM-A", 42.0, 1));
        when(service.callPython("Iron", 100.0, 20.0)).thenReturn(expected);

        assertSame(expected, controller.processAsteroid(asteroid));
        verify(service).callPython("Iron", 100.0, 20.0);
    }

    @Test
    void mapsSelectedSimulationIntoRiskRequest() {
        Asteroid asteroid = asteroid();
        HashMap<String, Object> selected = simulation("SIM-A", 4200.0, 1);
        selected.put("Fuel Cost", 17.5);
        HashMap<String, Object> expected = new HashMap<>();
        expected.put("riskScore", 72.0);
        when(service.callRiskAssessmentPython("AST-1", "Iron", 100.0, 20.0, 17.5, 4200.0))
                .thenReturn(expected);

        assertSame(expected, controller.processRisk(asteroid, selected));
        verify(service).callRiskAssessmentPython("AST-1", "Iron", 100.0, 20.0, 17.5, 4200.0);
    }

    @Test
    void usesZeroRiskDefaultsWhenSelectedSimulationHasNoMetrics() {
        Asteroid asteroid = asteroid();
        when(service.callRiskAssessmentPython("AST-1", "Iron", 100.0, 20.0, 0.0, 0.0))
                .thenReturn(new HashMap<>());

        controller.processRisk(asteroid, new HashMap<>());

        verify(service).callRiskAssessmentPython("AST-1", "Iron", 100.0, 20.0, 0.0, 0.0);
    }

    @Test
    void sendsCompleteCaseToAgentAndQuantumService() {
        Asteroid asteroid = asteroid();
        List<HashMap<String, Object>> simulations = List.of(
                simulation("SIM-A", 42.0, 1),
                simulation("SIM-B", 99.0, 0));
        HashMap<String, Object> expected = new HashMap<>();
        expected.put("selectedSimulationID", "SIM-A");
        when(service.callQuantumPython(asteroid, simulations)).thenReturn(expected);

        assertSame(expected, controller.processQuantumOptimization(asteroid, simulations));
        verify(service).callQuantumPython(asteroid, simulations);
    }

    @Test
    void rejectsEmptySimulationSetBeforeCallingService() {
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> controller.processQuantumOptimization(asteroid(), List.of()));

        assertEquals("No simulations are available for agent analysis", exception.getMessage());
        verifyNoInteractions(service);
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
        simulation.put("Distance from which it will pass if force is applied at that angle", distance);
        simulation.put("Chances of success", success);
        return simulation;
    }
}
