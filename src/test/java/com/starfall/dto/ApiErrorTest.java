package com.starfall.dto;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ApiErrorTest {

    @Test
    void createsStableErrorEnvelope() {
        ApiError error = ApiError.of("VALIDATION_ERROR", "Asteroid ID is required");

        assertEquals("error", error.status());
        assertEquals("VALIDATION_ERROR", error.code());
        assertEquals("Asteroid ID is required", error.message());
    }
}
