from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "Project-Starfall-Interview-Playbook.pdf"

NAVY = colors.HexColor("#07152A")
NAVY_2 = colors.HexColor("#0D2340")
GOLD = colors.HexColor("#C9A84C")
GOLD_LIGHT = colors.HexColor("#E7D395")
CREAM = colors.HexColor("#F5EEDC")
INK = colors.HexColor("#182536")
MUTED = colors.HexColor("#5F6D7A")
PALE = colors.HexColor("#F3F5F7")
LINE = colors.HexColor("#D7DEE5")
WHITE = colors.white


styles = getSampleStyleSheet()
cover_kicker = ParagraphStyle(
    "CoverKicker", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=9, leading=12, textColor=GOLD_LIGHT, tracking=2.0,
    alignment=TA_LEFT, spaceAfter=10,
)
cover_title = ParagraphStyle(
    "CoverTitle", parent=styles["Title"], fontName="Times-Bold",
    fontSize=34, leading=39, textColor=CREAM, alignment=TA_LEFT,
    spaceAfter=14,
)
cover_subtitle = ParagraphStyle(
    "CoverSubtitle", parent=styles["Normal"], fontName="Helvetica",
    fontSize=12, leading=18, textColor=colors.HexColor("#C7D1DD"),
    alignment=TA_LEFT, spaceAfter=16,
)
h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Times-Bold",
    fontSize=23, leading=27, textColor=NAVY, spaceBefore=4, spaceAfter=12,
)
h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=13, leading=17, textColor=GOLD, spaceBefore=12, spaceAfter=6,
)
body = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9.2, leading=13.6, textColor=INK, spaceAfter=7,
)
small = ParagraphStyle(
    "Small", parent=body, fontSize=8, leading=11.5, textColor=MUTED,
)
question_style = ParagraphStyle(
    "Question", parent=body, fontName="Helvetica-Bold", fontSize=10.1,
    leading=14, textColor=NAVY, spaceBefore=7, spaceAfter=3, keepWithNext=True,
)
answer_style = ParagraphStyle(
    "Answer", parent=body, fontSize=9, leading=13.2, leftIndent=8,
    borderColor=LINE, borderWidth=0, spaceAfter=7,
)
follow_style = ParagraphStyle(
    "Follow", parent=small, fontName="Helvetica-Oblique", leftIndent=8,
    textColor=colors.HexColor("#6C5B2B"), spaceAfter=8,
)
table_head = ParagraphStyle(
    "TableHead", parent=small, fontName="Helvetica-Bold", textColor=CREAM,
)
table_text = ParagraphStyle(
    "TableText", parent=small, textColor=INK,
)
quote_style = ParagraphStyle(
    "Quote", parent=body, fontName="Times-Italic", fontSize=11,
    leading=16, textColor=NAVY, leftIndent=8, rightIndent=8,
)


def para(text, style=body):
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def draw_cover(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.line(22 * mm, height - 24 * mm, width - 22 * mm, height - 24 * mm)
    canvas.setStrokeColor(colors.HexColor("#31445C"))
    canvas.circle(width - 34 * mm, 38 * mm, 26 * mm, fill=0, stroke=1)
    canvas.circle(width - 34 * mm, 38 * mm, 15 * mm, fill=0, stroke=1)
    canvas.setFillColor(GOLD)
    canvas.circle(width - 34 * mm, 38 * mm, 1.7 * mm, fill=1, stroke=0)
    canvas.restoreState()


def draw_page(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, height - 17 * mm, width - 18 * mm, height - 17 * mm)
    canvas.setFont("Helvetica-Bold", 7.2)
    canvas.setFillColor(NAVY)
    canvas.drawString(18 * mm, height - 13 * mm, "PROJECT STARFALL")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 18 * mm, height - 13 * mm, "INTERVIEW PLAYBOOK")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9.5 * mm, "Architecture - Java - AI - Quantum - Testing - Production")
    canvas.drawRightString(width - 18 * mm, 9.5 * mm, str(doc.page))
    canvas.restoreState()


def section_header(story, number, title, intro):
    story.append(para(f"SECTION {number:02d}", h2))
    story.append(para(title, h1))
    story.append(para(intro, body))
    story.append(Spacer(1, 2 * mm))


question_number = 0


def add_qa(story, question, answer, follow=None):
    global question_number
    question_number += 1
    story.append(para(f"Q{question_number}. {question}", question_style))
    story.append(para(answer, answer_style))
    if follow:
        story.append(para(f"Likely follow-up: {follow}", follow_style))


def callout(story, title, text):
    box = Table(
        [[para(title, table_head)], [para(text, table_text)]],
        colWidths=[165 * mm],
    )
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY_2),
        ("BACKGROUND", (0, 1), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(box)
    story.append(Spacer(1, 4 * mm))


def add_section(story, number, title, intro, questions):
    section_header(story, number, title, intro)
    for item in questions:
        add_qa(story, *item)
    story.append(PageBreak())


story = []
story.extend([
    Spacer(1, 42 * mm),
    para("CELESTIAL DEFENCE OBSERVATORY / CANDIDATE EDITION", cover_kicker),
    para("Project Starfall\nInterview Playbook", cover_title),
    para(
        "A project-specific preparation guide for software engineering, Java, Spring Boot, "
        "Python, AI agents, Qiskit, databases, frontend performance, testing, system design, "
        "behavioral interviews, and honest discussion of production gaps.",
        cover_subtitle,
    ),
    Spacer(1, 16 * mm),
    para("Includes 100+ interview prompts and five complete mock interviews", cover_kicker),
    Spacer(1, 52 * mm),
    para("Prepared from the current Starfall codebase - November 2026", cover_subtitle),
    PageBreak(),
])


section_header(story, 0, "How to use this playbook", "Do not memorize sentences. Learn the architecture, the reasons behind each decision, and the limits you can discuss honestly.")
callout(story, "THE 30-SECOND RULE", "Start with the outcome, name the technologies, explain your contribution, and finish with one measurable proof. Only go deeper when the interviewer asks.")
story.append(para("Recommended study order", h2))
study_rows = [
    [para("Pass", table_head), para("Focus", table_head), para("Goal", table_head)],
    [para("1", table_text), para("Pitch and architecture", table_text), para("Explain the complete request flow without notes.", table_text)],
    [para("2", table_text), para("Your strongest two areas", table_text), para("Give implementation details and tradeoffs.", table_text)],
    [para("3", table_text), para("Testing and failures", table_text), para("Explain how 41 JUnit tests isolate dependencies.", table_text)],
    [para("4", table_text), para("Known gaps", table_text), para("Be honest about Random Forest, migrations, and production operations.", table_text)],
    [para("5", table_text), para("Mock interviews", table_text), para("Answer aloud, then compare with the model answer.", table_text)],
]
study_table = Table(study_rows, colWidths=[18 * mm, 52 * mm, 95 * mm], repeatRows=1)
study_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.4, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(study_table)
story.append(Spacer(1, 5 * mm))
story.append(para("Answer structure", h2))
story.append(para("Technical question: definition -> Starfall implementation -> tradeoff -> verification. Behavioral question: situation -> task -> action -> result -> lesson. Design question: requirements -> data flow -> failure modes -> scale -> security -> observability.", body))
story.append(PageBreak())


add_section(story, 1, "Project pitch and ownership", "These questions test whether you understand the product and can separate your contribution from the team's work.", [
    ("Tell me about Project Starfall.", "Starfall is an asteroid-threat analysis platform. A browser submits an archived asteroid ID to Spring Boot, which loads physical data from MySQL, calls Python for trajectory simulation and physics-based risk assessment, asks a structured AI decision agent to score every candidate, and uses a Qiskit Grover circuit to amplify the strongest eligible intervention. The result is persisted and rendered as an auditable dashboard.", "What part did you personally implement?"),
    ("What problem does the project solve?", "It demonstrates how heterogeneous systems can coordinate a defensible decision: physical data retrieval, simulation, risk calculation, AI-assisted scoring, quantum search, persistence, and presentation. It is a research and portfolio system, not a certified planetary-defence product."),
    ("Give me a 30-second version.", "Starfall is a multi-service decision pipeline built with Spring Boot, Python, MySQL, an OpenAI-compatible agent, and Qiskit. It turns one asteroid identifier into simulated deflection options, validates and scores those options, amplifies the best candidate with Grover search, stores the analysis, and presents it in a responsive frontend. I focused on making the interfaces explicit, testable, and configurable rather than hardcoding credentials or service URLs."),
    ("What was the original state of the codebase?", "The original version was a small prototype with placeholder service calls, incomplete database methods, no complete frontend, and no meaningful automated tests. The current version has versioned APIs, separated Python services, actual Qiskit execution, a structured agent contract, physics calculations, a launcher, and 41 passing JUnit tests plus Python tests."),
    ("What was your most important engineering contribution?", "The most important contribution was converting an informal prototype into an explicit end-to-end contract. Each boundary now has validation, known payload shapes, timeouts, error translation, tests, and a clear fallback path. That makes failures explainable instead of silently producing plausible-looking results."),
    ("What would you demo first?", "I would submit a known asteroid ID, then trace the dashboard backward: recommended simulation, Grover histogram, agent rationale, risk and kinetic energy, simulation table, API response, and stored rows. That proves the whole pipeline rather than only showing the UI."),
    ("What are you most proud of?", "The structured agent boundary. The model may write natural-language explanations, but simulation IDs, scores, eligibility, and rationales must satisfy a strict schema. The application rejects unknown IDs, duplicates, missing candidates, invalid scores, and attempts to mark a failed simulation eligible."),
])


add_section(story, 2, "Architecture and system design", "Expect to draw the request path and explain why the system is split across Java, Python, and the browser.", [
    ("Walk me through one request end to end.", "The frontend posts asteroidId to POST /api/v1/analyses. Spring validates it and loads the Asteroid entity. It calls the Python simulation endpoint, persists candidates, sends asteroid plus simulations to the agent service, forwards validated candidates to the quantum endpoint, identifies the selected simulation, calculates risk, persists risk and quantum rows, and returns one response for the dashboard."),
    ("Why use Spring Boot as the orchestrator?", "Spring owns the public API, validation, database lifecycle, timeouts, CORS, and error translation. Java is a good fit for strongly typed service orchestration and mature persistence tooling, while Python remains focused on scientific and AI libraries."),
    ("Why separate the agent service from the analysis service?", "They fail differently and have different credentials. The agent service owns external model calls and structured validation; the analysis service owns simulations, physics, and Qiskit. Separation reduces credential exposure and allows either service to evolve independently."),
    ("Is this a microservice architecture?", "It is a small service-oriented architecture: one Spring API, one agent service, one analysis service, a static frontend, and MySQL. I would not claim mature microservices because deployment, discovery, distributed tracing, independent scaling, and service authentication are not yet complete."),
    ("What are the synchronous failure points?", "MySQL lookup, simulation HTTP call, agent HTTP call, quantum execution, risk calculation, and persistence can each fail. Spring applies connect/read timeouts and translates Python failures to a 502, but production still needs retries, circuit breakers, idempotency, and a durable analysis state machine."),
    ("How would you make the workflow asynchronous?", "Create an analysis job record, return 202 with a job ID, publish work to a queue, let workers execute simulation, agent, quantum, and risk stages, persist stage status, and expose a polling or server-sent-events endpoint. Each stage must be idempotent and retryable."),
    ("What data should identify a complete analysis?", "A dedicated analysis_run UUID should link the asteroid, simulation batch, agent plan, risk result, quantum job, model version, prompt version, timestamps, and status. The current schema links individual rows but lacks a first-class aggregate run identifier."),
    ("How would this scale?", "Keep Spring stateless, pool database connections, run multiple Python workers, cache immutable asteroid records, queue long quantum or model operations, and partition analysis records by run ID. Scale only after measuring latency by stage."),
])


add_section(story, 3, "Java and Spring Boot", "These questions target dependency injection, REST contracts, validation, exceptions, and orchestration code.", [
    ("Why constructor injection?", "It makes required dependencies explicit, supports immutable fields, prevents partially initialized objects, and lets Mockito inject mocks without starting Spring. Starfall controllers and services receive collaborators through constructors."),
    ("How is request validation implemented?", "AsteroidAnalysisRequest is a record with Jakarta validation constraints. The controller uses @Valid. Invalid input becomes MethodArgumentNotValidException and ApiExceptionHandler returns a stable ApiError with HTTP 400."),
    ("Why use a DTO instead of accepting a Map?", "A DTO documents the contract, enables compile-time access and validation, and prevents arbitrary JSON from leaking into business logic. Starfall still uses maps at some Python boundaries; replacing those with typed DTOs is a planned improvement."),
    ("What does the exception handler achieve?", "It centralizes HTTP error semantics. Validation and malformed JSON become 400 responses; Python dependency failures become 502 responses without exposing internal provider details."),
    ("Why is a Python outage a 502?", "Spring is acting as a gateway/orchestrator. The client request may be valid, but an upstream dependency failed, so Bad Gateway describes the boundary accurately."),
    ("What is RestTemplate doing here?", "MLAnalysisService builds JSON requests, applies configured connect/read timeouts through a RestTemplate bean, posts to internal endpoints, validates response envelopes, and wraps failures with operation context. For newer code, WebClient or RestClient could be considered, but the important part is a tested contract."),
    ("Why does the project use ResponseEntity?", "It allows the controller/core layer to return explicit status codes and bodies for not-found, invalid, downstream-failure, and success cases. A more mature design would return domain results and keep all HTTP construction in controllers."),
    ("What Java improvements remain?", "Replace HashMap payloads with records, add an analysis aggregate and explicit state enum, remove unchecked casts, add structured logging, and separate orchestration from response construction. Integration tests should verify Spring wiring with a real test database."),
])


add_section(story, 4, "REST APIs and distributed-service contracts", "Interviewers often probe versioning, idempotency, errors, and compatibility.", [
    ("What are the main public and internal endpoints?", "The public API exposes POST /api/v1/analyses and GET /api/v1/health. A legacy POST /api/asteroid remains for compatibility. Internal Python endpoints cover simulations, risk assessments, optimizations, agent decisions, and health."),
    ("Why version the public endpoint?", "Versioning makes breaking changes explicit and allows clients to migrate deliberately. Internal services are also versioned because independently deployed components need stable contracts."),
    ("How do you validate a service response?", "The Java service requires a success envelope and the expected output type. The agent layer performs deeper semantic validation: known IDs, exactly one assessment per simulation, finite scores from 0 to 100, and eligibility consistent with source success."),
    ("Is POST /api/v1/analyses idempotent?", "Not currently. Repeating a request generates new simulations and persistence rows. Production should accept an idempotency key or create a run ID so retries do not duplicate work."),
    ("How do you handle backward compatibility?", "The legacy public and Python routes remain temporarily while new versioned routes are the preferred contract. Compatibility routes should have telemetry and a removal date rather than remaining forever."),
    ("How would you document the API?", "Add OpenAPI schemas for requests, success responses, errors, and examples; generate client contracts; and run contract tests in CI. The current README lists endpoints but is not a machine-verifiable specification."),
    ("What timeout policy is used?", "Connect and read timeouts are externalized through application properties. Timeouts prevent threads from waiting forever, but production also needs retry budgets, circuit breakers, and total request deadlines."),
])


add_section(story, 5, "Hibernate and MySQL", "Be ready to discuss entities, sessions, transactions, migrations, and data integrity.", [
    ("How does Starfall connect to MySQL?", "DatabaseController builds a Hibernate SessionFactory using environment-backed URL, username, password, schema action, SQL logging, and Hikari pool settings. Credentials are not committed, and the launcher requests the password securely."),
    ("Why use try-with-resources for sessions?", "It guarantees each Hibernate Session closes even when mapping or persistence throws. This is safer than the original long-lived shared session and transaction."),
    ("What does hbm2ddl validate do?", "It checks entity mappings against the existing schema without creating or mutating tables. That is safer for production than update or create-drop, but it requires reliable migrations before startup."),
    ("What is wrong with the current migration approach?", "The SQL migration is manual, hardcodes the schema, assumes constraint names, deletes quantum rows, copies legacy tables without idempotency guards, and drops old tables. It should be replaced with tested Flyway or Liquibase migrations plus backup and rollback procedures."),
    ("How are database units tested?", "DatabaseControllerTest mocks SessionFactory, Session, and Transaction. ArgumentCaptor inspects the exact entity passed to persist, and verify confirms commit and resource closure. A separate integration test should still use MySQL or Testcontainers."),
    ("What transaction risk exists in the full workflow?", "Simulations are persisted before agent, quantum, and risk stages complete. A later failure can leave a partial run. A production design needs an analysis run state, explicit transaction boundaries, and possibly an outbox or saga-style workflow."),
    ("Why is a random five-digit risk ID risky?", "The key space is small, so collisions become likely over time and inserts can fail. Use a database-generated key or UUID."),
    ("What indexes would you add?", "Index asteroid_id and created_at on risk records, simulation batch/run IDs, selected simulation foreign keys, analysis status, and any lookup used by dashboards. Index choices should follow measured queries rather than guesses."),
])


add_section(story, 6, "Python, simulation, and machine learning", "This section is important because the current simulation module is not yet a trained ML model.", [
    ("Which regression model does the project currently use?", "None. The current simulation endpoint uses deterministic formulas plus random ranges to generate candidates. I would state this clearly rather than call it machine learning."),
    ("Where are values still hardcoded?", "The simulation count, angle range, execution-time range, miss-distance range, success threshold, and base fuel formula are still embedded in the Python simulation function. Risk thresholds are also heuristic, although material densities are configurable."),
    ("How would you add Random Forest correctly?", "Define a labeled dataset and target variables, document units, split train/validation/test data, build preprocessing in a Pipeline, tune a RandomForestRegressor or classifier with cross-validation, compare against simple baselines, persist the full pipeline with metadata, and load a versioned model for inference."),
    ("Why start with a baseline model?", "A Random Forest is not automatically better. A mean predictor, linear model, or simple rule baseline reveals whether the model adds measurable value. Metrics and error analysis should drive selection."),
    ("Which metrics would you use?", "For continuous outputs: MAE, RMSE, R-squared, calibration by range, and domain-specific constraint violations. For success classification: precision, recall, F1, ROC-AUC, calibration, and especially false-negative cost."),
    ("How would you prevent data leakage?", "Split by event or asteroid before fitting preprocessing, never derive features from future outcomes, keep test data untouched, and version both raw data and feature code. Similar trajectories from one asteroid should not be scattered across train and test sets."),
    ("How do the Flask services validate input?", "They require JSON objects, check required strings and finite positive numbers, use stable error codes, and return explicit status envelopes. More mature schemas could use Pydantic or JSON Schema at every boundary."),
    ("How would you make simulation reproducible?", "Accept or derive a run seed, record it with the analysis, remove uncontrolled global randomness, version all model/config inputs, and store the model and dataset identifiers used for each result."),
])


add_section(story, 7, "Agentic AI and OpenAI integration", "Discuss the agent as a constrained decision component, not an unquestioned authority.", [
    ("What makes the AI part agentic?", "The agent receives full case context, evaluates every candidate, produces comparable scores and eligibility decisions, and writes rationales that drive the next tool-like stage, Grover optimization. It is still a bounded single-agent decision step, not an autonomous multi-agent organization."),
    ("How is ChatGPT called?", "The agent service posts to an OpenAI Responses-compatible /v1/responses endpoint using a runtime API key and model name. It requests strict JSON-schema output and sets store to false."),
    ("How do you prevent hallucinated simulation IDs?", "After generation, validation builds the set of source simulation IDs, rejects unknown or duplicate IDs, requires every source simulation exactly once, and rejects successful eligibility claims for simulations whose source result failed."),
    ("Why not send unstructured text directly into Grover?", "Grover needs deterministic candidate states and numeric scores. Natural-language summary and rationale are for humans; a validated candidate schema is the machine contract."),
    ("What happens if the provider is unavailable?", "If fallback is enabled, the agent service uses a deterministic local policy based on normalized miss distance, fuel, execution time, and mission success. The UI labels this as the Starfall local safety agent so it is not misrepresented as external AI."),
    ("How is prompt injection addressed?", "The instructions state that supplied JSON fields are data, not instructions, and structured output limits the response surface. Production should also sanitize untrusted text, isolate tools, use least privilege, log prompt/model versions, and run adversarial evaluations."),
    ("How would you evaluate the agent?", "Create a curated case set with expert rankings, measure candidate completeness, schema validity, unsafe eligibility rate, rank agreement, rationale faithfulness, latency, cost, and fallback frequency. Run the same set on prompt/model changes before deployment."),
    ("What is the most honest limitation?", "The agent produces a recommendation but is not a certified decision authority. Scores reflect prompt and model behavior, and the current fallback weights are configurable heuristics. Human review remains required."),
])


add_section(story, 8, "Qiskit and Grover's algorithm", "Interviewers may test both implementation knowledge and whether you overclaim quantum advantage.", [
    ("Explain Grover's algorithm simply.", "Grover starts with equal amplitude across states, uses an oracle to phase-mark target states, and applies a diffusion operator to amplify their amplitudes. Repeating the process approximately square-root of N times increases the probability of measuring a marked state."),
    ("How does Starfall build the oracle?", "It classically finds the largest score among eligible candidates, identifies every tied index, converts each index to a binary state, applies X gates to zero positions, uses a multi-controlled phase operation, and uncomputes the X gates."),
    ("How are qubits calculated?", "The implementation uses max(1, ceil(log2(candidate count))). That creates enough computational states for every candidate. Unused padded states have no candidate mapping."),
    ("How are Grover iterations calculated?", "It derives theta from arcsin(sqrt(marked/state count)) and uses floor(pi divided by 4 theta), with zero iterations when every state is marked or no meaningful amplification is possible."),
    ("Which backend is used?", "Qiskit's local StatevectorSampler with configurable shots and optional seed. It is actual circuit execution in Qiskit, but not IBM quantum hardware."),
    ("Does this provide quantum speedup?", "No practical speedup is claimed. The maximum score is identified classically before constructing the oracle, and the candidate set is tiny. The circuit demonstrates amplitude amplification and an auditable quantum workflow."),
    ("Why select the measured marked state by counts?", "For tied maximum candidates, the implementation compares counts for marked states and selects the most frequently measured one. Every marked state is valid; a deterministic tie-break policy could be added if reproducibility is more important."),
    ("How would you use IBM hardware?", "Add IBM credentials through secrets, select a backend, transpile for its basis gates and topology, submit an asynchronous job, persist job IDs and calibration metadata, handle queue time and noise, and keep a simulator fallback."),
    ("What quantum tests exist?", "Python tests verify largest eligible score selection, dynamic qubit count, rejection when no candidate is eligible, and prevention of failed-candidate selection."),
])


add_section(story, 9, "Physics and risk calculation", "Know what is physically grounded and what is still a heuristic.", [
    ("How is kinetic energy calculated?", "The asteroid is approximated as a sphere. Diameter is converted from kilometers to meters, volume is 4/3 pi r cubed, mass is density times volume, velocity is converted to meters per second, and energy is 1/2 m v squared. Joules are converted to megatons of TNT."),
    ("Where does density come from?", "Composition aliases map to configurable metallic, carbonaceous, icy, stony, or default bulk densities. Environment variables can override each default."),
    ("What assumptions should you disclose?", "Spherical shape, uniform bulk density, input unit correctness, no atmospheric entry model, no fragmentation, and no uncertainty propagation. These assumptions make the value an estimate, not an authoritative impact model."),
    ("Is impact probability scientifically modeled?", "No. It is currently a bounded heuristic based on miss distance and velocity. It needs calibration against orbital uncertainty data or replacement by a domain model."),
    ("Why can kinetic energy become huge?", "Energy grows with volume, which scales with diameter cubed, and with velocity squared. A small unit error therefore creates an enormous difference, so explicit schemas and unit tests are essential."),
    ("How is the physics tested?", "A Python unit test uses known diameter, velocity, and density values and checks estimated mass, joules, megatons, formula metadata, and configurable density behavior."),
])


add_section(story, 10, "Frontend, UX, and performance", "The frontend is intentionally cinematic, but interview answers should connect design choices to usability and performance.", [
    ("What frontend framework is used?", "Vanilla HTML, CSS, and JavaScript, not React. That keeps deployment simple, but larger state and component requirements may justify a framework later."),
    ("How does the frontend call the API?", "It posts JSON to /api/v1/analyses, uses same-origin by default, supports an injected apiBaseUrl for separate hosting, validates response shape, and renders with textContent rather than unsafe HTML insertion."),
    ("How was landing-page lag reduced?", "Large videos were transcoded to optimized web MP4 files, loading is deferred, hero video starts during idle time, protocol video hydrates near the viewport, offscreen videos pause, and document visibility pauses/resumes playback. The combined key media size fell by roughly 82.7 percent."),
    ("How is mobile handled?", "Responsive grids collapse to one column, contributor cards use fixed square crops, the heavy hero video is disabled on small screens, and the protocol video remains available with Data Saver protection."),
    ("How does the planet rotate?", "The circular planet is a masked element whose pseudo-element contains a repeating texture translated horizontally by a CSS keyframe. A specific reduced-motion override preserves this requested effect while other animations remain minimized."),
    ("How are agent narratives rendered safely?", "The browser reads validated summary, recommendation, and selected-candidate rationale fields and assigns them with textContent. It does not interpret model output as HTML."),
    ("What frontend tests remain?", "Add Playwright tests for submission, success/failure rendering, external versus fallback labels, videos, responsive breakpoints, accessibility, keyboard navigation, and visual regression."),
])


add_section(story, 11, "JUnit 5, Mockito, and testing strategy", "Use concrete examples from the 41-test Java suite and explain why each test boundary exists.", [
    ("How many Java tests are currently passing?", "Forty-one JUnit 5 tests across thirteen suites, with zero failures and zero errors in the latest full Maven run."),
    ("Why use Mockito?", "Mockito isolates the unit from databases, HTTP clients, and other services. Tests control collaborator behavior with when and verify important interactions without launching external infrastructure."),
    ("What is the role of MockitoExtension?", "@ExtendWith(MockitoExtension.class) initializes @Mock fields, performs strict stubbing checks, and supports @InjectMocks before each JUnit test."),
    ("What does @InjectMocks do?", "It constructs the real unit and supplies available mocks through constructors or fields. It is not a Spring context and does not replace integration testing."),
    ("How is AsteroidChecker tested?", "DatabaseController and MLController are mocked. Tests cover blank IDs, missing asteroids, the successful orchestration path, unknown quantum selections, empty simulations, and persistence interactions."),
    ("How is outbound HTTP tested?", "MLAnalysisServiceTest mocks RestTemplate and PythonProcessBuilder, returning success envelopes or throwing ResourceAccessException. Tests cover simulations, risk, agent-to-quantum handoff, invalid agent responses, and operation-aware exceptions."),
    ("How is Hibernate mapping tested without MySQL?", "A test-only SessionFactory constructor allows mocks for SessionFactory, Session, and Transaction. ArgumentCaptor inspects SimulationRun, RiskAssessment, and QuantumOptimise entities passed to persist."),
    ("Why use MockMvc?", "Standalone MockMvc exercises routing, JSON conversion, Jakarta validation, controller advice, statuses, and response JSON without opening a port or booting the whole application."),
    ("What should not be mocked?", "The unit under test, simple value objects, deterministic pure functions, and behavior that can be tested cheaply with real objects. CorsConfig uses a real CorsRegistry because mocking its fluent concrete registration added no value."),
    ("Unit test versus integration test?", "A unit test isolates one class and runs quickly. An integration test verifies wiring or infrastructure such as Spring plus MySQL. Starfall now has strong unit coverage but still needs Testcontainers and end-to-end tests."),
    ("How did Java 23 affect Mockito?", "Dynamic Byte Buddy attachment was slow and emits future-compatibility warnings. Surefire now starts Byte Buddy as a static javaagent, making Mockito startup reliable and future-facing."),
    ("What does 100 percent coverage fail to prove?", "It does not prove correct assertions, realistic data, absence of race conditions, integration correctness, performance, or security. Coverage is one signal, not the objective."),
])


add_section(story, 12, "Security, reliability, and production readiness", "These questions reveal whether you can distinguish a polished demo from a production system.", [
    ("How are secrets handled?", "Database passwords and OpenAI API keys come from environment variables. The launcher securely prompts for the MySQL password and does not commit it. Production should use a secrets manager and short-lived credentials."),
    ("What security is still missing?", "Authentication, authorization, internal service identity, TLS policy, rate limiting, request-size limits, secret rotation, audit logging, dependency scanning, and a threat model."),
    ("How would you protect internal Python endpoints?", "Place services on a private network, use mutual TLS or signed service tokens, restrict ingress, rotate credentials, validate audience and expiry, and log authenticated caller identity."),
    ("What observability would you add?", "Structured JSON logs, a correlation ID propagated across services, stage timing, agent model and prompt version, quantum job metadata, database metrics, traces, error-rate dashboards, and alerts on fallback usage."),
    ("How would you retry safely?", "Retry only transient failures with exponential backoff and jitter, enforce a total deadline, use idempotency keys, avoid retrying validation errors, and record attempts. Circuit breakers should stop cascades when a dependency remains unhealthy."),
    ("What is the difference between liveness and readiness?", "Liveness says the process is running; readiness says it can serve traffic. Starfall health endpoints are mostly liveness checks. Readiness should test required dependencies with bounded calls."),
    ("How would you deploy it?", "Containerize Spring and Python services, use managed MySQL, inject secrets and configuration, run migrations as a controlled job, place services behind a gateway, add health/readiness probes, and use CI/CD with staged rollout and rollback."),
    ("What is the current production-readiness estimate?", "The project is a strong integrated prototype. Functionally it is around three-quarters complete, but production readiness is lower because ML training, migrations, security, observability, and end-to-end deployment are unfinished."),
])


add_section(story, 13, "Behavioral and ownership questions", "Use the STAR structure, but keep the technical result measurable and honest.", [
    ("Describe a difficult bug you solved.", "Situation: the frontend appeared broken and video/planet effects did not run. Task: identify whether the cause was media, CSS, browser policy, or API failure. Action: traced media hydration, mobile breakpoints, reduced-motion behavior, and playback state; optimized assets and added viewport-aware loading. Result: video playback was verified by readyState and advancing currentTime, rotation was proven with timed captures, and media payload fell about 82.7 percent."),
    ("Tell me about a design disagreement.", "Explain the competing goals, the evidence you gathered, the decision criteria, the selected tradeoff, and what would trigger revisiting it. A good Starfall example is separating agent and analysis services versus keeping one Python process."),
    ("How did you handle incomplete requirements?", "I converted broad goals such as 'agentic AI' and 'actual Grover' into contracts: full context in, strict candidates out, validation rules, fallback behavior, circuit metadata, and tests. I documented what was demonstrational versus production-ready."),
    ("Tell me about a mistake.", "Choose a real engineering mistake, such as initially treating visually loaded media as proof of playback or relying on a Maven wrapper process that hid output. Explain the evidence that corrected your assumption and the durable verification you added."),
    ("How do you prioritize technical debt?", "Rank by safety and failure cost: incorrect decision logic and data loss first, then security and observability, then maintainability and polish. For Starfall, trained ML and safe migrations precede additional animation."),
    ("How do you learn unfamiliar technology?", "Start with the smallest executable example, read primary documentation, identify invariants, build a focused test, integrate behind a narrow interface, and explain the limits. The Qiskit and Mockito work both followed this pattern."),
    ("What would you do differently?", "Define the analysis aggregate and schemas first, use versioned migrations from day one, add a reproducible model pipeline before naming the module ML, and establish CI with unit and integration tests earlier."),
])


add_section(story, 14, "Trap questions and honest answers", "These are designed to catch exaggeration. A precise limitation usually sounds stronger than an inflated claim.", [
    ("Is the AI recommendation always correct?", "No. It is constrained and validated, but model judgment can still be wrong. The project preserves rationales, labels fallback mode, rejects structural violations, and should require expert review."),
    ("Is this a real quantum advantage?", "No. It is a real Qiskit Grover circuit used as an educational optimization stage, but maximum identification occurs classically and the search space is small."),
    ("Is Random Forest implemented?", "Not yet. The current simulation logic is formula- and random-range based. I have a clear plan for dataset construction, baselines, model evaluation, serialization, and inference."),
    ("Is the frontend React?", "No. It is vanilla HTML, CSS, and JavaScript. I would only migrate if component complexity, state management, or team needs justify the added build system."),
    ("Are migrations production safe?", "No. The current normalization SQL helped clean a local schema but is not sufficiently idempotent or reversible. Flyway/Testcontainers and backup-verified migrations are required."),
    ("Do unit tests prove the database works?", "No. Mockito tests prove mapping and interactions. A real MySQL integration test is still required for DDL, constraints, dialect behavior, and transaction semantics."),
    ("Why keep a fallback if you want ChatGPT output?", "Availability and safety. The fallback is deterministic, data-relative, and clearly labeled. It prevents an external provider outage from becoming an opaque system failure, while test mode can disable fallback to verify the real provider."),
    ("What is the biggest remaining risk?", "Decision correctness. The UI and orchestration are ahead of the underlying simulation and probability models. Production work should prioritize validated data and scientific calibration."),
])


section_header(story, 15, "Rapid-fire revision", "Practice answering each in one or two sentences.")
rapid = [
    ("What is dependency injection?", "Supplying a class's collaborators from outside so construction, configuration, and testing remain explicit."),
    ("What is CORS?", "A browser policy controlled by server headers that permits selected origins to call an API."),
    ("400 versus 404 versus 502?", "Invalid request, resource not found, and valid gateway request whose upstream dependency failed."),
    ("What is HikariCP?", "A JDBC connection pool used to reuse bounded database connections efficiently."),
    ("What is an ORM?", "A mapping layer between objects and relational tables; it reduces boilerplate but does not remove the need to understand SQL."),
    ("What is idempotency?", "Repeating the same operation produces no additional side effects beyond the first successful execution."),
    ("What is a circuit breaker?", "A resilience pattern that stops repeated calls to an unhealthy dependency and probes recovery later."),
    ("What is structured output?", "Model output constrained to a machine-validated schema rather than arbitrary prose."),
    ("What is amplitude amplification?", "A quantum process that increases measurement probability of oracle-marked states."),
    ("What is a qubit?", "A quantum state represented by amplitudes over zero and one, with multi-qubit systems representing combined basis states."),
    ("What is RMSE?", "The square root of mean squared error; it penalizes larger regression errors more strongly than MAE."),
    ("What is overfitting?", "Learning training-specific patterns that do not generalize to unseen data."),
    ("What is a mock?", "A controllable test double that can return configured values and verify interactions."),
    ("What is ArgumentCaptor?", "A Mockito utility for inspecting the actual object passed to a mocked method."),
    ("What is MockMvc?", "A Spring test utility that exercises MVC routing and serialization without a live network server."),
    ("What is @ParameterizedTest?", "A JUnit 5 test executed repeatedly with different supplied arguments."),
    ("What is a health check?", "A bounded endpoint or probe describing process liveness or service readiness."),
    ("What is prompt injection?", "Untrusted input attempting to override model instructions or trigger unauthorized behavior."),
    ("What is graceful degradation?", "Continuing with reduced, explicit functionality when a nonessential dependency fails."),
    ("What is observability?", "The ability to understand internal state through logs, metrics, and traces."),
]
for q, a in rapid:
    add_qa(story, q, a)
story.append(PageBreak())


section_header(story, 16, "Mock interview 1 - Recruiter and project overview", "Target time: 20 minutes. Answer first, then read the model response.")
mock1 = [
    ("Interviewer: Tell me about yourself and this project.", "Candidate: I am a software engineer focused on Java backend systems and practical AI integration. Project Starfall is my end-to-end demonstration: Spring Boot orchestrates MySQL, Python simulations, a structured decision agent, Qiskit Grover optimization, and a responsive dashboard. My work centered on converting an incomplete prototype into explicit, tested service contracts."),
    ("Interviewer: Why did you choose this project?", "Candidate: It forced me to connect several disciplines instead of building another CRUD application. The challenge was not merely calling AI or Qiskit; it was validating their outputs, handling failures, persisting an auditable result, and communicating limitations honestly."),
    ("Interviewer: What measurable improvements did you make?", "Candidate: The codebase gained versioned APIs, separate agent and analysis services, actual Qiskit execution, physics calculations, one-command startup, optimized media with about 82.7 percent lower key payload, and 41 passing JUnit tests across 13 suites."),
    ("Interviewer: What was the hardest part?", "Candidate: Keeping the decision chain trustworthy across weakly typed boundaries. I introduced strict agent schemas, ID validation, score bounds, eligibility checks, explicit error envelopes, and Mockito tests at each Java boundary."),
    ("Interviewer: What remains incomplete?", "Candidate: The simulation module is not yet a trained Random Forest model, probability scoring is heuristic, migrations need Flyway and rollback testing, and production security and observability are not complete."),
    ("Interviewer: Why should we hire you?", "Candidate: I can move from ambiguous requirements to a working system while preserving honesty about risk. I do not stop at a visual demo; I trace failures, add tests, measure performance, and explain tradeoffs clearly."),
]
for q, a in mock1:
    story.append(para(q, question_style)); story.append(para(a, answer_style))
story.append(PageBreak())


section_header(story, 17, "Mock interview 2 - Java, Spring, and database", "Target time: 35 minutes. Expect code-level follow-ups.")
mock2 = [
    ("Interviewer: Trace the Spring request.", "Candidate: AsteroidController validates AsteroidAnalysisRequest and delegates to AsteroidChecker. The checker loads the entity, calls MLController for simulation, agent/quantum, and risk work, persists each result through DatabaseController, and returns the aggregate response. ApiExceptionHandler translates validation and dependency failures."),
    ("Interviewer: Why not put everything in the controller?", "Candidate: Controllers should own HTTP concerns, not orchestration, persistence, or service-client logic. Separation lets MockMvc test the HTTP contract and Mockito test the orchestration independently."),
    ("Interviewer: Show how Mockito helps.", "Candidate: AsteroidCheckerTest uses @Mock for DatabaseController and MLController and @InjectMocks for the real checker. when supplies candidate and quantum results; verify proves simulations, risk, and quantum entries were persisted."),
    ("Interviewer: How do you test Hibernate without MySQL?", "Candidate: DatabaseController receives a test-only SessionFactory seam. The test mocks Session and Transaction, captures the entity passed to persist, checks mapped fields, and verifies commit and closure. I would add Testcontainers for integration behavior."),
    ("Interviewer: Identify a transaction problem.", "Candidate: Simulations commit before the later agent, quantum, and risk stages. If one fails, the run is partial. I would add analysis_run status and design idempotent stage transactions rather than pretending one database transaction can cover remote calls."),
    ("Interviewer: Why a static Byte Buddy agent?", "Candidate: Java 23 made Mockito's dynamic self-attachment slow and future-hostile. Surefire now launches Byte Buddy as a javaagent so the tests start reliably and avoid dynamic-attachment behavior."),
    ("Interviewer: What would you refactor next?", "Candidate: Replace HashMap service payloads with records, add an analysis aggregate, remove unchecked casts, introduce structured logging, and isolate response mapping from orchestration."),
]
for q, a in mock2:
    story.append(para(q, question_style)); story.append(para(a, answer_style))
story.append(PageBreak())


section_header(story, 18, "Mock interview 3 - AI, ML, and quantum", "Target time: 40 minutes. The goal is precise claims, not buzzwords.")
mock3 = [
    ("Interviewer: Describe the AI request and response.", "Candidate: The agent receives the complete asteroid object and every simulation. The Responses API must return summary, final recommendation, and one candidate object per simulation with ID, score, eligibility, and rationale. The application validates all fields before Grover sees them."),
    ("Interviewer: What if the model invents an ID?", "Candidate: Validation rejects it. The returned ID set must exactly match the source set, duplicates are forbidden, and failed simulations cannot be eligible."),
    ("Interviewer: Is your simulation machine learning?", "Candidate: Not yet. It is formula- and random-range based. My Random Forest plan starts with data and baselines, not with importing sklearn and calling fit."),
    ("Interviewer: Explain your Random Forest evaluation plan.", "Candidate: Split by asteroid to prevent leakage, use preprocessing pipelines, compare MAE and RMSE against simple baselines, evaluate constraint violations and classification calibration, tune with cross-validation, and version the complete model pipeline."),
    ("Interviewer: Explain the Grover circuit.", "Candidate: Eligible maximum-score indices are phase-marked by an oracle. The circuit starts in uniform superposition, composes the Grover operator for a calculated iteration count, measures all qubits, and reports probabilities and the selected marked state."),
    ("Interviewer: Is that quantum optimization?", "Candidate: It is a real implementation of amplitude amplification, but not a practical quantum speedup because the maximum is found classically and the state space is small. I describe it as a demonstrational quantum search stage."),
    ("Interviewer: What changes on IBM hardware?", "Candidate: Transpilation, backend topology, queueing, noise, calibration metadata, asynchronous jobs, credentials, and cost become operational concerns. The API must expose job state rather than block a browser request."),
]
for q, a in mock3:
    story.append(para(q, question_style)); story.append(para(a, answer_style))
story.append(PageBreak())


section_header(story, 19, "Mock interview 4 - System design and production", "Target time: 45 minutes. Draw the design while answering.")
mock4 = [
    ("Interviewer: Redesign Starfall for production.", "Candidate: I would create asynchronous analysis jobs, add a queue, independent workers, managed MySQL, Flyway migrations, service authentication, a gateway, secrets management, traces, metrics, and an immutable audit record containing model and prompt versions."),
    ("Interviewer: How does the client receive progress?", "Candidate: POST returns 202 and a run ID. GET /analyses/{id} returns stage status, while server-sent events can stream transitions. Every worker update is idempotent and version-checked."),
    ("Interviewer: How do you avoid duplicate runs?", "Candidate: Accept an idempotency key scoped to the caller, store the request hash and result reference, and return the existing run for retries. Stage consumers also deduplicate message IDs."),
    ("Interviewer: What if OpenAI is down?", "Candidate: A circuit breaker opens after transient failures. The run either uses the explicitly labeled deterministic fallback or waits for manual retry based on policy. Metrics track fallback rate so degradation is visible."),
    ("Interviewer: How do you secure it?", "Candidate: User authentication and roles at the gateway, private service networking, mTLS or signed service tokens, least-privilege database accounts, encrypted secrets, rate limits, schema validation, audit logs, and regular dependency scanning."),
    ("Interviewer: What do you monitor?", "Candidate: Request and stage latency, error and timeout rates, queue depth, database pool use, model cost and token count, schema rejection rate, fallback rate, quantum job duration, and incomplete-run age."),
    ("Interviewer: What is your rollout plan?", "Candidate: Run migrations against a restored backup, deploy compatible readers first, canary the new worker, compare shadow results, enforce automated rollback thresholds, and preserve old contracts until clients migrate."),
]
for q, a in mock4:
    story.append(para(q, question_style)); story.append(para(a, answer_style))
story.append(PageBreak())


section_header(story, 20, "Mock interview 5 - Testing and debugging", "Target time: 35 minutes. Think aloud and separate evidence from assumptions.")
mock5 = [
    ("Interviewer: The frontend says dependency failed. What do you do?", "Candidate: Capture the API status and response first, check Spring logs with the correlation ID, identify which operation the PythonServiceException names, call that service's bounded health endpoint, then inspect its logs and configuration. I do not start by changing UI code."),
    ("Interviewer: A unit test passes but production fails against MySQL.", "Candidate: That indicates the mocked contract differs from infrastructure behavior. Add a Testcontainers integration test covering schema migration, constraints, dialect, and transactions; reproduce with production-like data; keep the unit test for fast mapping feedback."),
    ("Interviewer: Why verify interactions?", "Candidate: When a unit's contract includes a side effect, such as persisting risk, verify proves the collaborator was called with the expected object. I avoid verifying incidental getter calls because that couples tests to implementation."),
    ("Interviewer: A Mockito test has unnecessary stubbing. What does that mean?", "Candidate: The test configured behavior it did not use, often indicating shared setup or unclear scope. I move the stub into only the tests that need it rather than disabling strictness globally."),
    ("Interviewer: How did you test video playback?", "Candidate: I distinguished source hydration from actual playback. A browser probe checked readyState, paused state, currentSrc, and currentTime advancement; timed screenshots verified planet texture movement."),
    ("Interviewer: What test should be added next?", "Candidate: A full Testcontainers and HTTP end-to-end test that starts Spring, agent, and analysis services, applies migrations, submits a fixed seeded case, and asserts persisted and returned results. That closes the largest confidence gap."),
    ("Interviewer: Summarize your testing philosophy.", "Candidate: Test behavior at the smallest useful boundary, mock only external collaborators, keep pure logic real, verify important outputs and side effects, use integration tests for wiring, and treat coverage as evidence rather than a target."),
]
for q, a in mock5:
    story.append(para(q, question_style)); story.append(para(a, answer_style))
story.append(PageBreak())


section_header(story, 21, "Final revision checklist", "Use this page the night before and again one hour before the interview.")
checklist = [
    "Deliver the 30-second and two-minute project pitches without notes.",
    "Draw the complete request flow and name every failure boundary.",
    "Explain one Mockito test using Arrange, Act, Assert, when, and verify.",
    "Explain why the current simulation is not yet Random Forest.",
    "Explain Grover without claiming a practical quantum speedup.",
    "State the kinetic-energy equation and unit conversions.",
    "Name three production gaps: migrations, security, and observability.",
    "Prepare one bug story, one disagreement story, and one mistake story.",
    "Know the numbers: 41 JUnit tests, 13 suites, zero failures, and about 82.7 percent media reduction.",
    "End answers with evidence: a test, metric, log, schema rule, or measured result.",
]
rows = [[para("READY", table_head), para("CHECK", table_head)]]
for item in checklist:
    rows.append([para("[ ]", table_text), para(item, table_text)])
table = Table(rows, colWidths=[20 * mm, 145 * mm], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.4, LINE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story.append(table)
story.append(Spacer(1, 8 * mm))
callout(story, "FINAL REMINDER", "A strong interview answer is not the longest answer. It is the clearest claim, backed by implementation detail, honest tradeoffs, and proof.")


doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=23 * mm,
    bottomMargin=19 * mm,
    title="Project Starfall Interview Playbook",
    author="Project Starfall",
    subject="Project-specific interview questions and mock interviews",
)
doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_page)
print(OUTPUT)
