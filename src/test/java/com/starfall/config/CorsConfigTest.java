package com.starfall.config;

import org.junit.jupiter.api.Test;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CorsConfigTest {

    @Test
    void registersTrimmedOriginsAndExpectedHttpContract() {
        ExposedCorsRegistry registry = new ExposedCorsRegistry();

        new CorsConfig(" http://localhost:5500, ,https://starfall.example ")
                .addCorsMappings(registry);

        CorsConfiguration configuration = registry.configurations().get("/api/**");
        assertEquals(
                java.util.List.of("http://localhost:5500", "https://starfall.example"),
                configuration.getAllowedOrigins());
        assertEquals(java.util.List.of("GET", "POST", "OPTIONS"), configuration.getAllowedMethods());
        assertEquals(java.util.List.of("Content-Type", "Accept"), configuration.getAllowedHeaders());
    }

    private static final class ExposedCorsRegistry extends CorsRegistry {
        private Map<String, CorsConfiguration> configurations() {
            return getCorsConfigurations();
        }
    }
}
