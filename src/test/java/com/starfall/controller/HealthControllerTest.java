package com.starfall.controller;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

class HealthControllerTest {

    @Test
    void reportsApiIdentityAndUpStatus() {
        Map<String, String> health = new HealthController().health();

        assertEquals("UP", health.get("status"));
        assertEquals("starfall-api", health.get("service"));
    }
}
