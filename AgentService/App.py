import os

from flask import Flask, jsonify, request

from MLSimulator import AgenticPlanner


app = Flask(__name__)


def error_response(code, message, status_code):
    return jsonify({
        "status": "error",
        "code": code,
        "message": message
    }), status_code


def configured_boolean(name, default):
    value = os.getenv(name, str(default)).strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise AgenticPlanner.AgentPlanningError(f"{name} must be a boolean")


@app.get("/health")
@app.get("/internal/v1/health")
def health():
    return jsonify({"status": "UP", "service": "starfall-agent"}), 200


@app.post("/internal/v1/agent-decisions")
def decide():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("MALFORMED_JSON", "Request body must contain a JSON object", 400)

    asteroid = data.get("asteroid")
    simulations = data.get("simulations")
    try:
        try:
            plan = AgenticPlanner.generate_grover_plan(asteroid, simulations)
        except AgenticPlanner.AgentInputError:
            raise
        except AgenticPlanner.AgentPlanningError:
            if not configured_boolean("AI_AGENT_FALLBACK_ENABLED", True):
                raise
            plan = AgenticPlanner.generate_fallback_plan(asteroid, simulations)
    except AgenticPlanner.AgentInputError as exception:
        return error_response("VALIDATION_ERROR", str(exception), 400)
    except AgenticPlanner.AgentPlanningError as exception:
        return error_response("AI_AGENT_ERROR", str(exception), 502)

    return jsonify({"status": "success", "output": plan}), 200


if __name__ == "__main__":
    app.run(
        host=os.getenv("AGENT_HOST", "127.0.0.1"),
        port=int(os.getenv("AGENT_PORT", "5001")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )
