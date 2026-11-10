package com.starfall.controller;

import com.starfall.dto.ApiError;
import com.starfall.exception.PythonServiceException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiError> handleValidation(MethodArgumentNotValidException exception) {
        String message = exception.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(error -> error.getDefaultMessage())
                .orElse("Request validation failed");
        return ResponseEntity.badRequest().body(ApiError.of("VALIDATION_ERROR", message));
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiError> handleMalformedJson() {
        return ResponseEntity.badRequest()
                .body(ApiError.of("MALFORMED_JSON", "Request body must contain valid JSON"));
    }

    @ExceptionHandler(PythonServiceException.class)
    public ResponseEntity<ApiError> handlePythonService(PythonServiceException exception) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(ApiError.of(
                        "PYTHON_SERVICE_ERROR",
                        "Analysis dependency failed during " + exception.getOperation()));
    }
}
