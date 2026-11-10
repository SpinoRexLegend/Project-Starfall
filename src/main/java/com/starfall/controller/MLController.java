package com.starfall.controller;

import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.service.MLAnalysisService;

import org.springframework.stereotype.Controller;

import java.util.HashMap;

import java.util.List;

@Controller
public class MLController {

    private final MLAnalysisService mlAnalysisService;

    public MLController(MLAnalysisService mlAnalysisService) {
        this.mlAnalysisService = mlAnalysisService;
    }

    public List<HashMap<String, Object>> processAsteroid(Asteroid asteroid) {

        String material = asteroid.getComposition();
        double dia = asteroid.getDiameter();
        double vel = asteroid.getVelocity();

        return mlAnalysisService.callPython(material, dia, vel);
    }

    public HashMap<String, Object> processRisk(Asteroid asteroid, HashMap<String, Object> bestSimulation) {
        String material = asteroid.getComposition();
        double dia = asteroid.getDiameter();
        double vel = asteroid.getVelocity();

        double bestFuel = bestSimulation != null && bestSimulation.containsKey("Fuel Cost")
                ? Double.parseDouble(String.valueOf(bestSimulation.get("Fuel Cost")))
                : 0;
        double bestDist = bestSimulation != null
                && bestSimulation.containsKey("Distance from which it will pass if force is applied at that angle")
                        ? Double.parseDouble(String.valueOf(bestSimulation
                                .get("Distance from which it will pass if force is applied at that angle")))
                        : 0;

        return mlAnalysisService.callRiskAssessmentPython(asteroid.getAsteroid_Id(), material, dia, vel, bestFuel,
                bestDist);
    }

    public HashMap<String, Object> processQuantumOptimization(
            Asteroid asteroid,
            List<HashMap<String, Object>> simulations) {
        if (simulations == null || simulations.isEmpty()) {
            throw new IllegalArgumentException("No simulations are available for agent analysis");
        }
        return mlAnalysisService.callQuantumPython(asteroid, simulations);
    }
}
