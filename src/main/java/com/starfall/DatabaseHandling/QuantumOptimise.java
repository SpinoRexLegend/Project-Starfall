package com.starfall.DatabaseHandling;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "quantum_optimisation_result")
@Data
public class QuantumOptimise {

    @Id
    @Column(name = "Quantum_ID")
    public String ass_ID;

    @Column(name = "Qubits_used")
    public int qubits;

    @Column(name = "Iterations")
    public int iteration;

    @Column(name = "Optimal_probability")
    public double opProb;

    @Column(name = "Optimised_at", length = 255)
    public String oDate;

    @Column(name = "Simulation_ID", length = 36, nullable = false)
    public String simID;
}
