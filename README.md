# Project Starfall

**Project Starfall** is an advanced asteroid threat simulation and quantum analysis platform. It provides a robust end-to-end pipeline to evaluate potential asteroid impacts, simulate deflection strategies using machine learning, and optimize the final decision-making process using a quantum-inspired algorithm.

## Overview

The application combines a visually rich frontend for user interaction with a powerful Java Spring Boot backend that delegates complex analytical tasks to an external Python-based machine learning service. 

It handles:
1. **Simulation of Deflection Strategies**: Evaluates various angles, fuel costs, and required execute times to successfully dodge an asteroid.
2. **Risk Assessment**: Computes a risk score taking into account the probability of impact, kinetic energy, estimating potential damage and evaluating if deflection is required based on the optimal simulation result.
3. **Agentic Strategy Assessment**: Sends the complete asteroid and simulation context to a configured AI decision agent, which returns a validated score and eligibility decision for every simulation.
4. **Quantum Optimization**: Uses those validated candidate scores to build the Grover oracle and select the strongest eligible strategy.

## Architecture & Technology Stack

* **Frontend**: HTML5, Vanilla JavaScript, and an extensive custom CSS implementation resulting in a cinematic, highly interactive interface. Includes grid layers, animated histograms, and dynamic tabular data rendering.
* **Backend**: Java 23, powered by the **Spring Boot** framework (v3.2.4).
    * `AsteroidController`: Exposes the initial REST API to receive the Asteroid ID from the frontend.
    * `AsteroidChecker` (Core Logic): Interacts with the database to gather details, pushes the data to the ML layer, computes bounds, updates databases and manages the risk/quantum pipelines.
    * `MLController` & `MLAnalysisService`: Serves as the bridge to a separate Python ML service using Spring's `RestTemplate` for JSON payload exchange.
    * `DatabaseController`: Manages interactions natively with the relational database.
* **Persistence Layer**: **Hibernate ORM** with **MySQL** handles the storage of entities representing the asteroid, multiple simulation runs, risk assessments, and the final quantum optimized choices.
* **Agent Service**: A standalone Python HTTP service on port 5001 owns external-agent calls, structured validation, and the local safety-agent fallback.
* **Analysis/Quantum Service**: A separate Python HTTP service on port 5000 owns simulations, physical risk calculations, and Qiskit Grover execution.

## Key Features

* **Real-time API Delegation**: Spring Boot effortlessly handles the frontend's REST calls and delegates the heavy lifting to Python processes.
* **Simulation Result Processing**: Automatically sorts through dozens of potential impact simulations to determine the "Best Strategy" (e.g. lowest fuel cost, highest distance missed) while deliberately discarding/hiding the optimal one from the user until the quantum check.
* **Quantum Histogram Visuals**: Displays the exact likelihood optimization graph from the algorithm dynamically rendering HTML CSS bars based on probabilities fetched post-operation.
* **Aesthetic Dashboard**: Custom cinematic design complete with background videos (Earth, Black Hole phases), dynamic CSS transitions, and futuristic terminal-like logging overlays.

## Setup Requirements

* Java 23 JDK
* Maven
* MySQL 9+
* Node/Live Server (For quick Frontend hosting)
* The Python analysis service configured through `PYTHON_SERVICE_URL`

Install the shared Python service dependencies with:

```bash
python -m pip install -r MLSimulator/requirements.txt
```

## API Endpoints

The public Spring API exposes:

* `POST /api/v1/analyses` with `{ "asteroidId": "..." }`
* `GET /api/v1/health`
* `POST /api/asteroid` remains available as a compatibility endpoint

The internal Python API exposes:

* `POST /internal/v1/simulations`
* `POST /internal/v1/risk-assessments`
* `POST /internal/v1/optimizations` accepts validated candidates from the Agent Service
* `GET /internal/v1/health`

The dedicated Agent Service exposes:

* `POST /internal/v1/agent-decisions`
* `GET /internal/v1/health`

Run the services from the repository root with:

```bash
python -m AgentService.App
python MLSimulator/App.py
```

Legacy Python endpoints (`/predict`, `/assess`, `/quantum`) remain available during migration.

## Runtime Configuration

Configure production deployments with environment variables rather than committed credentials:

* `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `DB_SCHEMA_ACTION`
* `PYTHON_SERVICE_URL`, `AGENT_SERVICE_URL`, `PYTHON_CONNECT_TIMEOUT`, `PYTHON_READ_TIMEOUT`
* `QUANTUM_SHOTS` and optional `QUANTUM_SEED` for reproducible local sampling
* `OPENAI_API_KEY` and `AI_AGENT_MODEL` for the external decision agent
* Optional `AI_AGENT_BASE_URL` (an OpenAI Responses-compatible `/v1` base URL), `AI_AGENT_TIMEOUT_SECONDS`, and `AI_AGENT_MAX_OUTPUT_TOKENS`
* `AI_AGENT_FALLBACK_ENABLED` defaults to `true`, keeping optimization available through the Starfall local safety agent when the external agent is not configured or temporarily unreachable
* `AI_FALLBACK_DISTANCE_WEIGHT`, `AI_FALLBACK_FUEL_WEIGHT`, and `AI_FALLBACK_TIME_WEIGHT` tune the local data-relative safety policy; supplied values are normalized at runtime
* Kinetic energy uses `E = ½mv²`, with spherical volume, kilometer-to-meter conversion, and composition-based bulk density. Density assumptions can be overridden with `ASTEROID_DENSITY_METALLIC_KG_M3`, `ASTEROID_DENSITY_CARBONACEOUS_KG_M3`, `ASTEROID_DENSITY_ICY_KG_M3`, `ASTEROID_DENSITY_STONY_KG_M3`, or `ASTEROID_DENSITY_DEFAULT_KG_M3`
* `APP_CORS_ALLOWED_ORIGINS`, `SERVER_PORT`
* `HOST`, `PORT`, `AGENT_HOST`, `AGENT_PORT`, `FLASK_DEBUG` for the Python services

The browser client uses same-origin `/api/v1/analyses` by default. A separately hosted frontend can inject `window.STARFALL_CONFIG.apiBaseUrl` at deployment time.

Spring sends the full asteroid record and every generated simulation to the dedicated Agent Service. Natural-language summaries and rationales are retained for display, while a strict candidate schema is validated before the candidate plan crosses into the analysis/quantum service. Unknown or duplicate simulation IDs, missing candidates, invalid scores, and attempts to make failed simulations eligible are rejected. Grover then marks the largest eligible agent score and executes amplitude amplification with Qiskit's local `StatevectorSampler`. The number of qubits and Grover iterations are derived from the candidate and marked-state counts.
