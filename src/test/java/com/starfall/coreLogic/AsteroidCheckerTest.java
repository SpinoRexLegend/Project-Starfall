package com.starfall.coreLogic;

import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.DatabaseHandling.DatabaseController;
import com.starfall.controller.MLController;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AsteroidCheckerTest {

    @Mock
    private DatabaseController databaseController;

    @Mock
    private MLController mlController;

    @InjectMocks
    private AsteroidChecker checker;

    @Test
    void rejectsBlankIdentifierWithoutDatabaseLookup() {
        ResponseEntity<?> response = checker.handleAsteroid("   ");

        assertEquals(400, response.getStatusCode().value());
        verifyNoInteractions(databaseController, mlController);
    }

    @Test
    void returnsNotFoundWhenArchiveHasNoAsteroid() {
        when(databaseController.getAsteroid("AST-404")).thenReturn(null);

        ResponseEntity<?> response = checker.handleAsteroid("AST-404");

        assertEquals(404, response.getStatusCode().value());
        verify(databaseController).getAsteroid("AST-404");
        verifyNoInteractions(mlController);
    }

    @Test
    @SuppressWarnings("unchecked")
    void orchestratesSimulationAgentQuantumRiskAndPersistence() {
        Asteroid asteroid = asteroid();
        HashMap<String, Object> first = simulation("SIM-A", 1000.0);
        HashMap<String, Object> selected = simulation("SIM-B", 9000.0);
        List<HashMap<String, Object>> simulations = List.of(first, selected);
        HashMap<String, Object> quantumEntry = new HashMap<>(Map.of("Sim_ID", "SIM-B"));
        HashMap<String, Object> quantum = new HashMap<>();
        quantum.put("selectedSimulationID", "SIM-B");
        quantum.put("database_entries", List.of(quantumEntry));
        HashMap<String, Object> risk = new HashMap<>(Map.of("riskScore", 88.0));
        when(databaseController.getAsteroid("AST-1")).thenReturn(asteroid);
        when(mlController.processAsteroid(asteroid)).thenReturn(simulations);
        when(mlController.processQuantumOptimization(asteroid, simulations)).thenReturn(quantum);
        when(mlController.processRisk(asteroid, selected)).thenReturn(risk);

        ResponseEntity<?> response = checker.handleAsteroid("AST-1");

        assertEquals(200, response.getStatusCode().value());
        Map<String, Object> body = (Map<String, Object>) response.getBody();
        assertSame(selected, body.get("optimalStrategy"));
        assertEquals(List.of(first), body.get("simulations"));
        assertSame(quantum, body.get("quantum"));
        assertSame(risk, body.get("riskAssessment"));
        verify(databaseController).saveSimulationFromResult(simulations);
        verify(databaseController).saveRiskAssessmentFromResult(risk);
        verify(databaseController).saveQuantumOptimiseFromResult(List.of(quantumEntry));
    }

    @Test
    void rejectsQuantumSelectionThatIsNotInSimulationSet() {
        Asteroid asteroid = asteroid();
        List<HashMap<String, Object>> simulations = List.of(simulation("SIM-A", 1000.0));
        when(databaseController.getAsteroid("AST-1")).thenReturn(asteroid);
        when(mlController.processAsteroid(asteroid)).thenReturn(simulations);
        when(mlController.processQuantumOptimization(asteroid, simulations))
                .thenReturn(new HashMap<>(Map.of("selectedSimulationID", "UNKNOWN")));

        ResponseEntity<?> response = checker.handleAsteroid("AST-1");

        assertEquals(502, response.getStatusCode().value());
        verify(mlController, never()).processRisk(any(), any());
        verify(databaseController, never()).saveRiskAssessmentFromResult(any());
    }

    @Test
    void returnsServerErrorWhenSimulationServiceReturnsNoCandidates() {
        Asteroid asteroid = asteroid();
        when(databaseController.getAsteroid("AST-1")).thenReturn(asteroid);
        when(mlController.processAsteroid(asteroid)).thenReturn(List.of());

        ResponseEntity<?> response = checker.handleAsteroid("AST-1");

        assertEquals(500, response.getStatusCode().value());
        verify(databaseController, never()).saveSimulationFromResult(any());
    }

    private Asteroid asteroid() {
        Asteroid asteroid = new Asteroid();
        asteroid.setAsteroid_Id("AST-1");
        asteroid.setComposition("Iron");
        asteroid.setDiameter(1.0);
        asteroid.setVelocity(20.0);
        return asteroid;
    }

    private HashMap<String, Object> simulation(String id, double distance) {
        HashMap<String, Object> simulation = new HashMap<>();
        simulation.put("SimulationID", id);
        simulation.put("Distance from which it will pass if force is applied at that angle", distance);
        simulation.put("Fuel Cost", 10.0);
        simulation.put("Chances of success", 1);
        return simulation;
    }
}
