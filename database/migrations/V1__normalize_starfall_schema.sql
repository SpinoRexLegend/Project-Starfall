USE aegis;

DROP VIEW IF EXISTS asteroid_risk_assessment;
DROP VIEW IF EXISTS high_risk_asteroids;
DROP VIEW IF EXISTS successful_simulations;

ALTER TABLE simulation_run
    MODIFY COLUMN Simulation_ID VARCHAR(36) NOT NULL,
    MODIFY COLUMN Impact_angle_deg DOUBLE NOT NULL,
    MODIFY COLUMN Execution_time DOUBLE NOT NULL,
    MODIFY COLUMN Missed_distance_km DOUBLE NOT NULL,
    MODIFY COLUMN Fuel_Cost DOUBLE NOT NULL,
    MODIFY COLUMN Success BIT(1) NOT NULL,
    MODIFY COLUMN Simulated_at VARCHAR(255) NOT NULL;

INSERT INTO simulation_run (
    Simulation_ID,
    Impact_angle_deg,
    Execution_time,
    Missed_distance_km,
    Fuel_Cost,
    Success,
    Simulated_at
)
SELECT
    Simulation_Id,
    Impact_angle_deg,
    Execution_time,
    Missed_distance_km,
    Fuel_Cost,
    Success,
    Simulated_at
FROM simulationrun;

ALTER TABLE risk_assessment
    DROP FOREIGN KEY fk_asteroid,
    DROP FOREIGN KEY risk_assessment_ibfk_1;

ALTER TABLE risk_assessment
    MODIFY COLUMN asteroid_id VARCHAR(20) NOT NULL,
    MODIFY COLUMN impact_probability DOUBLE NOT NULL,
    MODIFY COLUMN kinetic_energy_mt DOUBLE NOT NULL,
    MODIFY COLUMN estimated_damage VARCHAR(50) NOT NULL,
    MODIFY COLUMN risk_score DOUBLE NOT NULL,
    MODIFY COLUMN requires_deflection BIT(1) NOT NULL,
    MODIFY COLUMN raw_response TEXT NULL,
    MODIFY COLUMN created_at VARCHAR(255) NULL;

INSERT INTO risk_assessment (
    assessment_id,
    asteroid_id,
    impact_probability,
    kinetic_energy_mt,
    estimated_damage,
    risk_score,
    requires_deflection,
    raw_response,
    created_at
)
SELECT
    assessment_id,
    asteroid_id,
    impact_probability,
    kinetic_energy_mt,
    estimated_damage,
    risk_score,
    requires_deflection,
    raw_response,
    created_at
FROM riskassessment;

ALTER TABLE risk_assessment
    ADD CONSTRAINT fk_risk_assessment_asteroid
        FOREIGN KEY (asteroid_id) REFERENCES asteroid (Asteroid_ID);

DELETE FROM quantum_optimisation_result;

ALTER TABLE quantum_optimisation_result
    MODIFY COLUMN Qubits_used INT NOT NULL,
    MODIFY COLUMN Iterations INT NOT NULL,
    MODIFY COLUMN Optimal_probability DOUBLE NOT NULL,
    MODIFY COLUMN Optimised_at VARCHAR(255) NOT NULL,
    ADD COLUMN Simulation_ID VARCHAR(36) NOT NULL,
    ADD CONSTRAINT fk_quantum_simulation
        FOREIGN KEY (Simulation_ID) REFERENCES simulation_run (Simulation_ID);

DROP TABLE IF EXISTS final_decision;
DROP TABLE IF EXISTS deflection_strategy;
DROP TABLE IF EXISTS safety_evaluation;
DROP TABLE IF EXISTS agent_log;
DROP TABLE IF EXISTS finaldecision;
DROP TABLE IF EXISTS defstrat;
DROP TABLE IF EXISTS simulationrun;
DROP TABLE IF EXISTS riskassessment;
