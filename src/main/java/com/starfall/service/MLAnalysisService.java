package com.starfall.service;

import com.starfall.ProcessBuilder.PythonProcessBuilder;
import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.exception.PythonServiceException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;

@Service
public class MLAnalysisService {

    private final RestTemplate restTemplate;
    private final PythonProcessBuilder processBuilder;

    private final String pythonBaseUrl;

    public MLAnalysisService(
            RestTemplate restTemplate,
            PythonProcessBuilder processBuilder,
            @Value("${python.service.url}") String pythonBaseUrl) {
        this.restTemplate = restTemplate;
        this.processBuilder = processBuilder;
        this.pythonBaseUrl = pythonBaseUrl.replaceAll("/+$", "");
    }

    public List<HashMap<String, Object>> callPython(String material, double dia, double vel) {

        HashMap<String, Object> requestBody = processBuilder.buildRequest(material, dia, vel);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<HashMap<String, Object>> requestEntity =
                new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<HashMap<String, Object>> response =
                    restTemplate.exchange(
                            pythonBaseUrl + "/internal/v1/simulations",
                            HttpMethod.POST,
                            requestEntity,
                            new ParameterizedTypeReference<HashMap<String, Object>>() {}
                    );

            HashMap<String, Object> body = response.getBody();
            if (body != null && "success".equals(body.get("status")) && body.get("output") instanceof List<?> output) {
                return output.stream()
                        .filter(HashMap.class::isInstance)
                        .map(item -> (HashMap<String, Object>) item)
                        .toList();
            }
            throw new PythonServiceException("simulations", "Python simulation service returned an invalid response");
        } catch (Exception e) {
            throw wrap("simulations", e);
        }
    }

    public HashMap<String, Object> callRiskAssessmentPython(String asteroidId, String material, double dia, double vel, double bestFuel, double bestDistance) {
        HashMap<String, Object> requestBody = processBuilder.buildRiskRequest(asteroidId, material, dia, vel, bestFuel, bestDistance);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<HashMap<String, Object>> requestEntity =
                new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<HashMap<String, Object>> response =
                    restTemplate.exchange(
                            pythonBaseUrl + "/internal/v1/risk-assessments",
                            HttpMethod.POST,
                            requestEntity,
                            new ParameterizedTypeReference<HashMap<String, Object>>() {}
                    );

            HashMap<String, Object> body = response.getBody();
            if (body != null && "success".equals(body.get("status")) && body.get("output") instanceof HashMap) {
                return (HashMap<String, Object>) body.get("output");
            }
            throw new PythonServiceException("risk-assessments", "Python risk service returned an invalid response");
        } catch (Exception e) {
            throw wrap("risk-assessments", e);
        }
    }

    public HashMap<String, Object> callQuantumPython(
            Asteroid asteroid,
            List<HashMap<String, Object>> simulations) {
        HashMap<String, Object> requestBody = processBuilder.buildQuantumRequest(asteroid, simulations);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<HashMap<String, Object>> requestEntity =
                new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<HashMap<String, Object>> response =
                    restTemplate.exchange(
                            pythonBaseUrl + "/internal/v1/optimizations",
                            HttpMethod.POST,
                            requestEntity,
                            new ParameterizedTypeReference<HashMap<String, Object>>() {}
                    );

            HashMap<String, Object> body = response.getBody();
            if (body != null && "success".equals(body.get("status")) && body.get("output") instanceof HashMap) {
                return (HashMap<String, Object>) body.get("output");
            }
            throw new PythonServiceException("optimizations", "Python optimization service returned an invalid response");
        } catch (Exception e) {
            throw wrap("optimizations", e);
        }
    }

    private PythonServiceException wrap(String operation, Exception exception) {
        if (exception instanceof PythonServiceException pythonServiceException) {
            return pythonServiceException;
        }
        return new PythonServiceException(operation, "Python service request failed", exception);
    }
}
