package com.starfall.service;

import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.ProcessBuilder.PythonProcessBuilder;
import com.starfall.exception.PythonServiceException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class MLAnalysisServiceTest {

    @Mock
    private RestTemplate restTemplate;

    @Mock
    private PythonProcessBuilder processBuilder;

    private MLAnalysisService service;

    @BeforeEach
    void setUp() {
        service = new MLAnalysisService(restTemplate, processBuilder, "http://python/", "http://agent/");
    }

    @Test
    void returnsSimulationOutputFromValidServiceResponse() {
        HashMap<String, Object> request = new HashMap<>(Map.of("Material", "Iron"));
        HashMap<String, Object> simulation = new HashMap<>(Map.of("SimulationID", "SIM-A"));
        HashMap<String, Object> response = success(List.of(simulation));
        when(processBuilder.buildRequest("Iron", 100.0, 20.0)).thenReturn(request);
        when(exchange("http://python/internal/v1/simulations")).thenReturn(ResponseEntity.ok(response));

        List<HashMap<String, Object>> result = service.callPython("Iron", 100.0, 20.0);

        assertEquals(List.of(simulation), result);
        verify(processBuilder).buildRequest("Iron", 100.0, 20.0);
    }

    @Test
    void wrapsSimulationTransportFailureWithOperationContext() {
        when(processBuilder.buildRequest("Iron", 100.0, 20.0)).thenReturn(new HashMap<>());
        when(exchange("http://python/internal/v1/simulations"))
                .thenThrow(new ResourceAccessException("offline"));

        PythonServiceException exception = assertThrows(
                PythonServiceException.class,
                () -> service.callPython("Iron", 100.0, 20.0));

        assertEquals("simulations", exception.getOperation());
    }

    @Test
    void returnsRiskAssessmentFromValidServiceResponse() {
        HashMap<String, Object> request = new HashMap<>();
        HashMap<String, Object> risk = new HashMap<>(Map.of("riskScore", 72.0));
        when(processBuilder.buildRiskRequest("AST-1", "Iron", 100.0, 20.0, 4.0, 5000.0))
                .thenReturn(request);
        when(exchange("http://python/internal/v1/risk-assessments"))
                .thenReturn(ResponseEntity.ok(success(risk)));

        assertSame(risk, service.callRiskAssessmentPython(
                "AST-1", "Iron", 100.0, 20.0, 4.0, 5000.0));
    }

    @Test
    void sendsAgentPlanToQuantumService() {
        Asteroid asteroid = new Asteroid();
        List<HashMap<String, Object>> simulations = List.of(new HashMap<>(Map.of("SimulationID", "SIM-A")));
        HashMap<String, Object> agentRequest = new HashMap<>();
        HashMap<String, Object> agentPlan = new HashMap<>(Map.of(
                "model", "gpt-test",
                "recommendation", "Proceed with SIM-A.",
                "candidates", List.of()));
        HashMap<String, Object> quantumRequest = new HashMap<>();
        HashMap<String, Object> quantumResult = new HashMap<>(Map.of("selectedSimulationID", "SIM-A"));
        when(processBuilder.buildAgentRequest(asteroid, simulations)).thenReturn(agentRequest);
        when(processBuilder.buildQuantumOptimizationRequest(agentPlan)).thenReturn(quantumRequest);
        when(exchange("http://agent/internal/v1/agent-decisions"))
                .thenReturn(ResponseEntity.ok(success(agentPlan)));
        when(exchange("http://python/internal/v1/optimizations"))
                .thenReturn(ResponseEntity.ok(success(quantumResult)));

        assertSame(quantumResult, service.callQuantumPython(asteroid, simulations));
        verify(processBuilder).buildQuantumOptimizationRequest(agentPlan);
    }

    @Test
    void rejectsAgentResponseWithoutCandidates() {
        Asteroid asteroid = new Asteroid();
        List<HashMap<String, Object>> simulations = List.of(new HashMap<>());
        when(processBuilder.buildAgentRequest(asteroid, simulations)).thenReturn(new HashMap<>());
        when(exchange("http://agent/internal/v1/agent-decisions"))
                .thenReturn(ResponseEntity.ok(success(new HashMap<>(Map.of("summary", "invalid")))));

        PythonServiceException exception = assertThrows(
                PythonServiceException.class,
                () -> service.callQuantumPython(asteroid, simulations));

        assertEquals("agent-decisions", exception.getOperation());
    }

    @SuppressWarnings("unchecked")
    private ResponseEntity<HashMap<String, Object>> exchange(String url) {
        return restTemplate.exchange(
                eq(url),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                any(ParameterizedTypeReference.class));
    }

    private HashMap<String, Object> success(Object output) {
        HashMap<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("output", output);
        return response;
    }
}
