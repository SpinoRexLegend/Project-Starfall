package com.starfall.controller;

import com.starfall.coreLogic.AsteroidChecker;
import com.starfall.exception.PythonServiceException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

import java.util.Map;

import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(MockitoExtension.class)
class AsteroidControllerTest {

    @Mock
    private AsteroidChecker asteroidChecker;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
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
        doReturn(ResponseEntity.ok(Map.of("status", "success")))
                .when(asteroidChecker).handleAsteroid("A-1");

        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"A-1\"}"))
                .andExpect(status().isOk());

        verify(asteroidChecker).handleAsteroid("A-1");
    }

    @Test
    void keepsLegacyEndpointCompatible() throws Exception {
        doReturn(ResponseEntity.ok(Map.of("status", "success")))
                .when(asteroidChecker).handleAsteroid("A-1");

        mockMvc.perform(post("/api/asteroid")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"A-1\"}"))
                .andExpect(status().isOk());

        verify(asteroidChecker).handleAsteroid("A-1");
    }

    @Test
    void rejectsBlankAsteroidIdBeforeCallingCoreLogic() throws Exception {
        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"   \"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));

        verifyNoInteractions(asteroidChecker);
    }

    @Test
    void rejectsMalformedJsonBeforeCallingCoreLogic() throws Exception {
        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{not-json}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("MALFORMED_JSON"));

        verifyNoInteractions(asteroidChecker);
    }

    @Test
    void reportsPythonFailureAsBadGateway() throws Exception {
        when(asteroidChecker.handleAsteroid("A-1"))
                .thenThrow(new PythonServiceException("simulations", "offline"));

        mockMvc.perform(post("/api/v1/analyses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"asteroidId\":\"A-1\"}"))
                .andExpect(status().isBadGateway())
                .andExpect(jsonPath("$.code").value("PYTHON_SERVICE_ERROR"))
                .andExpect(jsonPath("$.message").value("Analysis dependency failed during simulations"));
    }
}
