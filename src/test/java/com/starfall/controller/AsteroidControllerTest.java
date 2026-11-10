package com.starfall.controller;

import com.starfall.coreLogic.AsteroidChecker;
import com.starfall.exception.PythonServiceException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class AsteroidControllerTest {

    private StubAsteroidChecker asteroidChecker;
    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        asteroidChecker = new StubAsteroidChecker();
        LocalValidatorFactoryBean validator = new LocalValidatorFactoryBean();
        validator.afterPropertiesSet();
        mockMvc = MockMvcBuilders
                .standaloneSetup(new AsteroidController(asteroidChecker))
                .setControllerAdvice(new ApiExceptionHandler())
                .setValidator(validator)
                .build();
    }

    @Test
    void acceptsVersionedAnalysisEndpoint() throws Exception {
        asteroidChecker.response = ResponseEntity.ok(Map.of("status", "success"));

        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"A-1\"}"))
                .andExpect(status().isOk());

        assertEquals("A-1", asteroidChecker.receivedAsteroidId);
    }

    @Test
    void keepsLegacyEndpointCompatible() throws Exception {
        asteroidChecker.response = ResponseEntity.ok(Map.of("status", "success"));

        mockMvc.perform(post("/api/asteroid")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"A-1\"}"))
                .andExpect(status().isOk());
    }

    @Test
    void rejectsBlankAsteroidId() throws Exception {
        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"   \"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }

    @Test
    void reportsPythonFailureAsBadGateway() throws Exception {
        asteroidChecker.failure = new PythonServiceException("simulations", "offline");

        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"A-1\"}"))
                .andExpect(status().isBadGateway())
                .andExpect(jsonPath("$.code").value("PYTHON_SERVICE_ERROR"));
    }

    private static final class StubAsteroidChecker extends AsteroidChecker {
        private ResponseEntity<?> response;
        private RuntimeException failure;
        private String receivedAsteroidId;

        private StubAsteroidChecker() {
            super(null, null);
        }

        @Override
        public ResponseEntity<?> handleAsteroid(String asteroidId) {
            receivedAsteroidId = asteroidId;
            if (failure != null) {
                throw failure;
            }
            return response;
        }
    }
}
