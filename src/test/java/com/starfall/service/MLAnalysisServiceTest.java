package com.starfall.service;

import com.starfall.ProcessBuilder.PythonProcessBuilder;
import com.starfall.DatabaseHandling.Asteroid;
import com.starfall.exception.PythonServiceException;
import org.junit.jupiter.api.Test;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HashMap;
import java.util.List;

class MLAnalysisServiceTest {

    @Test
    void doesNotReturnPythonFailureAsSimulationData() {
        MLAnalysisService service = new MLAnalysisService(
                new FailingRestTemplate(),
                new PythonProcessBuilder(),
                "http://python",
                "http://agent");

        assertThrows(
                PythonServiceException.class,
                () -> service.callPython("Iron", 100.0, 20.0));
    }

    @Test
    void doesNotHideAgentServiceFailure() {
        MLAnalysisService service = new MLAnalysisService(
                new FailingRestTemplate(),
                new PythonProcessBuilder(),
                "http://python",
                "http://agent");

        assertThrows(
                PythonServiceException.class,
                () -> service.callQuantumPython(new Asteroid(), List.of(new HashMap<>())));
    }

    private static final class FailingRestTemplate extends RestTemplate {
        @Override
        public <T> ResponseEntity<T> exchange(
                String url,
                HttpMethod method,
                HttpEntity<?> requestEntity,
                ParameterizedTypeReference<T> responseType,
                Object... uriVariables) {
            throw new ResourceAccessException("offline");
        }
    }
}
