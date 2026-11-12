package com.starfall.controller;

import com.starfall.dto.ApiError;
import com.starfall.exception.PythonServiceException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.core.MethodParameter;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ApiExceptionHandlerTest {

    @Mock
    private MethodParameter methodParameter;

    @Mock
    private BindingResult bindingResult;

    private final ApiExceptionHandler handler = new ApiExceptionHandler();

    @Test
    void usesFirstValidationMessage() {
        when(bindingResult.getFieldErrors()).thenReturn(List.of(
                new FieldError("request", "asteroidId", "Asteroid ID is required")));
        MethodArgumentNotValidException validationException =
                new MethodArgumentNotValidException(methodParameter, bindingResult);

        ResponseEntity<ApiError> response = handler.handleValidation(validationException);

        assertEquals(400, response.getStatusCode().value());
        assertEquals("VALIDATION_ERROR", response.getBody().code());
        assertEquals("Asteroid ID is required", response.getBody().message());
    }

    @Test
    void mapsMalformedJsonToBadRequest() {
        ResponseEntity<ApiError> response = handler.handleMalformedJson();

        assertEquals(400, response.getStatusCode().value());
        assertEquals("MALFORMED_JSON", response.getBody().code());
    }

    @Test
    void mapsPythonFailureToBadGatewayWithoutLeakingInternalMessage() {
        ResponseEntity<ApiError> response = handler.handlePythonService(
                new PythonServiceException("optimizations", "secret provider detail"));

        assertEquals(502, response.getStatusCode().value());
        assertEquals("PYTHON_SERVICE_ERROR", response.getBody().code());
        assertEquals("Analysis dependency failed during optimizations", response.getBody().message());
    }
}
