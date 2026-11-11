package com.starfall.ProcessBuilder;

import com.starfall.DatabaseHandling.Asteroid;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;

@Component
public class PythonProcessBuilder {

    public HashMap<String, Object> buildRequest(String material, double diameter, double velocity) {

        HashMap<String, Object> map = new HashMap<>();
        map.put("Material", material);
        map.put("Diameter", diameter);
        map.put("Velocity", velocity);

        return map;
    }

    public HashMap<String, Object> buildRiskRequest(String asteroidId, String material, double diameter, double velocity, double bestFuel, double bestDistance) {
        HashMap<String, Object> map = new HashMap<>();
        map.put("asteroidID", asteroidId);
        map.put("Material", material);
        map.put("Diameter", diameter);
        map.put("Velocity", velocity);
        map.put("BestFuel", bestFuel);
        map.put("BestDistance", bestDistance);
        return map;
    }

    public HashMap<String, Object> buildAgentRequest(
            Asteroid asteroid,
            List<HashMap<String, Object>> simulations) {
        HashMap<String, Object> asteroidDetails = new HashMap<>();
        asteroidDetails.put("asteroidID", asteroid.getAsteroid_Id());
        asteroidDetails.put("name", asteroid.getName());
        asteroidDetails.put("diameterKm", asteroid.getDiameter());
        asteroidDetails.put("velocityKmps", asteroid.getVelocity());
        asteroidDetails.put("composition", asteroid.getComposition());
        asteroidDetails.put("detectionSource", asteroid.getDSource());
        asteroidDetails.put("detectionDate", asteroid.getDDate());

        HashMap<String, Object> map = new HashMap<>();
        map.put("asteroid", asteroidDetails);
        map.put("simulations", simulations);
        return map;
    }

    public HashMap<String, Object> buildQuantumRequest(
            Asteroid asteroid,
            List<HashMap<String, Object>> simulations) {
        return buildAgentRequest(asteroid, simulations);
    }

    public HashMap<String, Object> buildQuantumOptimizationRequest(
            HashMap<String, Object> agentPlan) {
        Object candidates = agentPlan.get("candidates");

        HashMap<String, Object> agentMetadata = new HashMap<>();
        agentMetadata.put("model", agentPlan.get("model"));
        agentMetadata.put("mode", agentPlan.get("mode"));
        agentMetadata.put("summary", agentPlan.get("summary"));
        agentMetadata.put("candidateAssessments", candidates);

        HashMap<String, Object> map = new HashMap<>();
        map.put("candidates", candidates);
        map.put("agent", agentMetadata);
        return map;
    }
}
