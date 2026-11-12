package com.starfall.dto;

import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AsteroidAnalysisRequestValidationTest {

    private static ValidatorFactory validatorFactory;
    private static Validator validator;

    @BeforeAll
    static void createValidator() {
        validatorFactory = Validation.buildDefaultValidatorFactory();
        validator = validatorFactory.getValidator();
    }

    @AfterAll
    static void closeValidator() {
        validatorFactory.close();
    }

    @ParameterizedTest(name = "rejects missing or blank asteroid ID: [{0}]")
    @NullAndEmptySource
    @ValueSource(strings = {" ", "   ", "\t"})
    void rejectsMissingOrBlankAsteroidId(String asteroidId) {
        AsteroidAnalysisRequest request = new AsteroidAnalysisRequest(asteroidId);

        assertFalse(validator.validate(request).isEmpty());
    }

    @Test
    void acceptsNonBlankAsteroidId() {
        AsteroidAnalysisRequest request = new AsteroidAnalysisRequest("2024 MW3");

        assertTrue(validator.validate(request).isEmpty());
    }
}
