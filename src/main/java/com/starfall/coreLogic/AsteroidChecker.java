package com.starfall.coreLogic;

import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.DatabaseHandling.DatabaseController;
import com.starfall.controller.MLController;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.ArrayList;
import java.util.List;

@Service
public class AsteroidChecker {

    private final DatabaseController databaseController;
    private final MLController mlController;

    public AsteroidChecker(DatabaseController databaseController, MLController mlController) {
        this.databaseController = databaseController;
        this.mlController = mlController;
    }

    public ResponseEntity<?> handleAsteroid(String asteroidId) {

        if (asteroidId == null || asteroidId.trim().isEmpty()) {
            HashMap<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", "Asteroid ID cannot be empty.");
            return ResponseEntity.badRequest().body(error);
        }

        Asteroid asteroid = databaseController.getAsteroid(asteroidId);

        if (asteroid == null) {
            HashMap<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", "Asteroid not found.");
            return ResponseEntity.status(404).body(error);
        }

        // ✅ Get JSON from ML layer
        List<HashMap<String, Object>> results = mlController.processAsteroid(asteroid);

        if (results == null || results.isEmpty()) {
            HashMap<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", "No simulations returned.");
            return ResponseEntity.status(500).body(error);
        }

        // ✅ Save ML JSON results into Simulation database table mapping
        databaseController.saveSimulationFromResult(results);

        List<HashMap<String, Object>> allResults = new ArrayList<>(results);
        HashMap<String, Object> quantumOptimization =
                mlController.processQuantumOptimization(asteroid, allResults);

        String selectedSimulationId = String.valueOf(
                quantumOptimization.get("selectedSimulationID"));
        HashMap<String, Object> bestResult = allResults.stream()
                .filter(result -> selectedSimulationId.equals(simulationId(result)))
                .findFirst()
                .orElse(null);

        if (bestResult == null) {
            HashMap<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", "Quantum search did not return a known simulation.");
            return ResponseEntity.status(502).body(error);
        }

        List<HashMap<String, Object>> displayResults = new ArrayList<>(allResults);
        if (displayResults.size() > 1) {
            displayResults.remove(bestResult);
        }

        HashMap<String, Object> riskAssessment = mlController.processRisk(asteroid, bestResult);
        if (riskAssessment != null && !riskAssessment.isEmpty() && !riskAssessment.containsKey("error")) {
            databaseController.saveRiskAssessmentFromResult(riskAssessment);
        }
        
        if (quantumOptimization != null && quantumOptimization.containsKey("database_entries")) {
            Object dbEntriesObj = quantumOptimization.get("database_entries");
            if (dbEntriesObj instanceof java.util.List) {
                try {
                    java.util.List<HashMap<String, Object>> dbEntries = (java.util.List<HashMap<String, Object>>) dbEntriesObj;
                    databaseController.saveQuantumOptimiseFromResult(dbEntries);
                } catch (Exception ignored) {}
            }
        }

        HashMap<String, Object> finalResponse = new HashMap<>();
        finalResponse.put("simulations", displayResults);
        finalResponse.put("quantum", quantumOptimization != null ? quantumOptimization : new HashMap<>());
        finalResponse.put("riskAssessment", riskAssessment != null ? riskAssessment : new HashMap<>());
        finalResponse.put("optimalStrategy", bestResult != null ? bestResult : new HashMap<>());

        return ResponseEntity.ok(finalResponse);
    }

    private String simulationId(HashMap<String, Object> simulation) {
        return String.valueOf(
                simulation.getOrDefault("SimulationID", simulation.get("s_ID")));
    }
}
