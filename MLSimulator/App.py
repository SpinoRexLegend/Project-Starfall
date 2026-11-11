import os
import random
import uuid
from datetime import datetime

from flask import Flask, jsonify, request

import RiskAssessor
import QuantumOptimizer
import AgenticPlanner

app = Flask(__name__)


def error_response(code, message, status_code=400):
    return jsonify({
        "status": "error",
        "code": code,
        "message": message
    }), status_code


def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def required_number(data, key, minimum=None, maximum=None):
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, f"{key} must be a number"
    value = float(value)
    if minimum is not None and value < minimum:
        return None, f"{key} must be at least {minimum}"
    if maximum is not None and value > maximum:
        return None, f"{key} must be at most {maximum}"
    return value, None


def configured_positive_integer(name, default):
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exception:
        raise RuntimeError(f"{name} must be an integer") from exception
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return value


def configured_boolean(name, default):
    value = os.getenv(name, str(default)).strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be a boolean")


@app.get("/health")
@app.get("/internal/v1/health")
def health():
    return jsonify({"status": "UP", "service": "starfall-analysis"}), 200


@app.route("/predict", methods=["POST"])
@app.route("/internal/v1/simulations", methods=["POST"])
def predict():
    data = json_body()
    if data is None:
        return error_response("MALFORMED_JSON", "Request body must contain a JSON object")

    material = data.get("Material", "Unknown")
    if not isinstance(material, str) or not material.strip():
        return error_response("VALIDATION_ERROR", "Material must be a non-empty string")

    diameter, error = required_number(data, "Diameter", minimum=0.000001)
    if error:
        return error_response("VALIDATION_ERROR", error)
    velocity, error = required_number(data, "Velocity", minimum=0.000001)
    if error:
        return error_response("VALIDATION_ERROR", error)

    simulations = []
    base_fuel = (diameter * velocity) / 10.0
    
    # Calculate a "best" base for successful impacts
    for i in range(8):
        # vary angle and base attributes
        angle_variance = random.uniform(-15.0, 15.0)
        fuel_variance = random.uniform(0.8, 1.5)
        success_chance = random.random() # 0.0 to 1.0

        simulations.append({
            "SimulationID": str(uuid.uuid4()),
            "Angle at which force to be applied": round(90.0 + angle_variance, 2),
            "Execution time for hitting the earth": round(random.uniform(5.0, 30.0), 2),
            "Distance from which it will pass if force is applied at that angle": round(random.uniform(1000.0, 50000.0), 2),
            "Fuel Cost": round(base_fuel * fuel_variance, 2),
            "Chances of success": 1 if success_chance > 0.5 else 0,
            "time and date of simulation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    response = {
        "status": "success",
        "output": simulations
    }

    return jsonify(response), 200


@app.route("/assess", methods=["POST"])
@app.route("/internal/v1/risk-assessments", methods=["POST"])
def assess():
    data = json_body()
    if data is None:
        return error_response("MALFORMED_JSON", "Request body must contain a JSON object")

    asteroid_id = data.get("asteroidID")
    if not isinstance(asteroid_id, str) or not asteroid_id.strip():
        return error_response("VALIDATION_ERROR", "asteroidID is required")

    material = data.get("Material", "Unknown")
    if not isinstance(material, str) or not material.strip():
        return error_response("VALIDATION_ERROR", "Material must be a non-empty string")

    diameter, error = required_number(data, "Diameter", minimum=0.000001)
    if error:
        return error_response("VALIDATION_ERROR", error)
    velocity, error = required_number(data, "Velocity", minimum=0.000001)
    if error:
        return error_response("VALIDATION_ERROR", error)
    best_fuel, error = required_number(data, "BestFuel", minimum=0)
    if error:
        return error_response("VALIDATION_ERROR", error)
    best_distance, error = required_number(data, "BestDistance", minimum=0)
    if error:
        return error_response("VALIDATION_ERROR", error)

    try:
        result = RiskAssessor.perform_assessment(
            asteroid_id,
            diameter,
            velocity,
            material,
            best_fuel,
            best_distance
        )
    except ValueError as exception:
        return error_response("RISK_CALCULATION_ERROR", str(exception), 422)

    return jsonify({
        "status": "success",
        "output": result
    }), 200


@app.route("/quantum", methods=["POST"])
@app.route("/internal/v1/optimizations", methods=["POST"])
def quantum():
    data = json_body()
    if data is None:
        return error_response("MALFORMED_JSON", "Request body must contain a JSON object")

    candidates = data.get("candidates")
    agent_metadata = data.get("agent")

    seed_value = os.getenv("QUANTUM_SEED")
    seed = int(seed_value) if seed_value is not None else None

    try:
        if not isinstance(candidates, list) or not candidates:
            asteroid = data.get("asteroid")
            simulations = data.get("simulations")
            if not isinstance(asteroid, dict) or not asteroid:
                return error_response(
                    "VALIDATION_ERROR",
                    "asteroid must be a non-empty object"
                )
            if not isinstance(simulations, list) or not simulations:
                return error_response(
                    "VALIDATION_ERROR",
                    "simulations must be a non-empty array"
                )

            # Compatibility path for legacy direct callers. Spring's production
            # flow obtains this plan from the dedicated Agent Service on port 5001.
            try:
                agent_plan = AgenticPlanner.generate_grover_plan(asteroid, simulations)
            except AgenticPlanner.AgentInputError:
                raise
            except AgenticPlanner.AgentPlanningError:
                if not configured_boolean("AI_AGENT_FALLBACK_ENABLED", True):
                    raise
                agent_plan = AgenticPlanner.generate_fallback_plan(asteroid, simulations)
            candidates = agent_plan["candidates"]
            agent_metadata = {
                "model": agent_plan["model"],
                "mode": agent_plan.get("mode", "external-agent"),
                "summary": agent_plan["summary"],
                "candidateAssessments": candidates
            }

        result = QuantumOptimizer.perform_quantum_optimization(
            candidates,
            shots=configured_positive_integer("QUANTUM_SHOTS", 4096),
            seed=seed
        )
        if isinstance(agent_metadata, dict):
            result["agent"] = agent_metadata
    except AgenticPlanner.AgentInputError as exception:
        return error_response("VALIDATION_ERROR", str(exception), 400)
    except AgenticPlanner.AgentPlanningError as exception:
        return error_response("AI_AGENT_ERROR", str(exception), 502)
    except (QuantumOptimizer.QuantumOptimizationError, RuntimeError, ValueError) as exception:
        return error_response("QUANTUM_EXECUTION_ERROR", str(exception), 422)

    return jsonify({
        "status": "success",
        "output": result
    }), 200


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )
