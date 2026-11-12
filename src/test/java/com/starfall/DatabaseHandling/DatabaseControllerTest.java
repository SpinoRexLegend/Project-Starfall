package com.starfall.DatabaseHandling;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class DatabaseControllerTest {

    @Mock
    private SessionFactory sessionFactory;

    @Mock
    private Session session;

    @Mock
    private Transaction transaction;

    private DatabaseController controller;

    @BeforeEach
    void setUp() {
        controller = new DatabaseController(sessionFactory);
    }

    @Test
    void retrievesAsteroidAndClosesSession() {
        openSession();
        Asteroid asteroid = new Asteroid();
        when(session.find(Asteroid.class, "AST-1")).thenReturn(asteroid);

        assertSame(asteroid, controller.getAsteroid("AST-1"));
        verify(session).close();
    }

    @Test
    void mapsAndPersistsSimulationResult() {
        openSession();
        when(session.beginTransaction()).thenReturn(transaction);
        HashMap<String, Object> source = new HashMap<>();
        source.put("SimulationID", "SIM-A");
        source.put("Angle at which force to be applied", 97.2);
        source.put("Execution time for hitting the earth", 12.5);
        source.put("Distance from which it will pass if force is applied at that angle", 4200.0);
        source.put("Fuel Cost", 17.0);
        source.put("Chances of success", 1);
        source.put("time and date of simulation", "2026-11-11 10:00:00");

        controller.saveSimulationFromResult(List.of(source));

        ArgumentCaptor<SimulationRun> captor = ArgumentCaptor.forClass(SimulationRun.class);
        verify(session).persist(captor.capture());
        SimulationRun saved = captor.getValue();
        assertEquals("SIM-A", saved.getS_ID());
        assertEquals(97.2, saved.getAngleOI());
        assertEquals(12.5, saved.getToe());
        assertEquals(4200.0, saved.getDistanceMissed());
        assertEquals(17.0, saved.getFuel());
        assertTrue(saved.isSuccess());
        verify(transaction).commit();
        verify(session).close();
    }

    @Test
    void mapsAndPersistsRiskAssessment() {
        openSession();
        when(session.beginTransaction()).thenReturn(transaction);
        HashMap<String, Object> source = new HashMap<>(Map.of(
                "assessmentID", 12345,
                "asteroidID", "AST-1",
                "impactProbability", 0.72,
                "kineticEnergyMT", 18.5,
                "estimatedDamage", "High",
                "riskScore", 88.0,
                "requiresDeflection", true,
                "rawResponse", "{}",
                "createdAt", "2026-11-11 10:00:00"));

        controller.saveRiskAssessmentFromResult(source);

        ArgumentCaptor<RiskAssessment> captor = ArgumentCaptor.forClass(RiskAssessment.class);
        verify(session).persist(captor.capture());
        RiskAssessment saved = captor.getValue();
        assertEquals(12345, saved.getAss_ID());
        assertEquals("AST-1", saved.getAID());
        assertEquals(0.72, saved.getIp());
        assertEquals(18.5, saved.getKineticEnergy());
        assertEquals("High", saved.getDamage());
        assertEquals(88.0, saved.getRiskScore());
        assertTrue(saved.isDefReq());
        verify(transaction).commit();
    }

    @Test
    void mapsAndPersistsQuantumResults() {
        openSession();
        when(session.beginTransaction()).thenReturn(transaction);
        HashMap<String, Object> source = new HashMap<>(Map.of(
                "QuantumID", "QTM-1",
                "Qubits_used", 3,
                "Iterations", 2,
                "Optimal_probability", 0.91,
                "Optimised_at", "2026-11-11T10:00:00Z",
                "Sim_ID", "SIM-A"));

        controller.saveQuantumOptimiseFromResult(List.of(source));

        ArgumentCaptor<QuantumOptimise> captor = ArgumentCaptor.forClass(QuantumOptimise.class);
        verify(session).persist(captor.capture());
        QuantumOptimise saved = captor.getValue();
        assertEquals("QTM-1", saved.getAss_ID());
        assertEquals(3, saved.getQubits());
        assertEquals(2, saved.getIteration());
        assertEquals(0.91, saved.getOpProb());
        assertEquals("SIM-A", saved.getSimID());
        verify(transaction).commit();
    }

    @Test
    void closesSessionFactoryDuringShutdown() {
        when(sessionFactory.isClosed()).thenReturn(false);

        controller.closeSession();

        verify(sessionFactory).close();
    }

    private void openSession() {
        when(sessionFactory.openSession()).thenReturn(session);
    }
}
