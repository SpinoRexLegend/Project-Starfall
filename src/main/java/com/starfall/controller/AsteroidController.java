package com.starfall.controller;

import com.starfall.coreLogic.AsteroidChecker;
import com.starfall.dto.AsteroidAnalysisRequest;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class AsteroidController {

    private final AsteroidChecker asteroidChecker;

    public AsteroidController(AsteroidChecker asteroidChecker) {
        this.asteroidChecker = asteroidChecker;
    }

    @PostMapping({"/v1/analyses", "/asteroid"})
    public ResponseEntity<?> receiveAsteroid(@Valid @RequestBody AsteroidAnalysisRequest request) {
        return asteroidChecker.handleAsteroid(request.asteroidId());
    }
}
