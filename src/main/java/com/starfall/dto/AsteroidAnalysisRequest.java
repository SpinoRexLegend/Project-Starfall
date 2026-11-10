package com.starfall.dto;

import jakarta.validation.constraints.NotBlank;

public record AsteroidAnalysisRequest(
        @NotBlank(message = "asteroidId is required") String asteroidId) {
}
