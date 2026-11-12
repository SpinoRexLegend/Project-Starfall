# JUnit 5 learning guide for Project Starfall

This guide is designed around tests that actually exist in Starfall. The goal is not to memorize annotations; it is to understand what behavior each test protects and why the chosen test boundary is appropriate.

## 1. The mental model

Every useful test follows the same structure:

1. **Arrange** the input, dependency behavior, and expected result.
2. **Act** by calling the production code once.
3. **Assert** the observable result or side effect.

Test behavior, not private implementation. A refactor should not break a test when the public behavior remains unchanged.

## 2. The JUnit 5 pieces used here

| Feature | Starfall example | Why it is used |
| --- | --- | --- |
| `@Test` | `PythonProcessBuilderTest` | Runs one deterministic example. |
| `@BeforeEach` | `AsteroidControllerTest` | Creates a clean controller and `MockMvc` instance for every test. |
| `@BeforeAll` / `@AfterAll` | `AsteroidAnalysisRequestValidationTest` | Creates and closes one expensive validator factory for the class. |
| `@ParameterizedTest` | `AsteroidAnalysisRequestValidationTest` | Runs the same rule against null, empty, and whitespace values. |
| `@ExtendWith(MockitoExtension.class)` | `MLControllerTest` | Creates and validates Mockito mocks for each test. |
| `@Mock` | `AsteroidCheckerTest` | Replaces database and service dependencies with controllable collaborators. |
| `@InjectMocks` | `AsteroidCheckerTest` | Constructs the real unit under test with those mocks. |
| `when(...).thenReturn(...)` | `MLAnalysisServiceTest` | Defines a dependency response for the Arrange phase. |
| `verify(...)` | `DatabaseControllerTest` | Proves an expected dependency interaction occurred. |
| `ArgumentCaptor` | `DatabaseControllerTest` | Inspects the entity passed to Hibernate without using MySQL. |
| `assertEquals` | `PythonProcessBuilderTest` | Verifies exact request mappings. |
| `assertThrows` | `MLAnalysisServiceTest` | Verifies dependency failures are not silently converted into valid data. |
| `MockMvc` | `AsteroidControllerTest` | Tests HTTP status and JSON without opening a real network port. |

JUnit Jupiter is JUnit 5's programming and extension model. Spring Boot's test starter supplies Jupiter, parameterized-test support, assertions, and Spring testing utilities.

## 3. Run the tests

From `E:\Project_Starfall` in PowerShell:

```powershell
$env:JAVA_HOME = (Resolve-Path '.tools\jdk-23.0.2+7').Path
.\.tools\apache-maven-3.10.0\bin\mvn.cmd '-Dmaven.repo.local=.tools\m2-repository' test
```

Run one class:

```powershell
.\.tools\apache-maven-3.10.0\bin\mvn.cmd '-Dmaven.repo.local=.tools\m2-repository' '-Dtest=AsteroidAnalysisRequestValidationTest' test
```

Run one test method:

```powershell
.\.tools\apache-maven-3.10.0\bin\mvn.cmd '-Dmaven.repo.local=.tools\m2-repository' '-Dtest=AsteroidAnalysisRequestValidationTest#acceptsNonBlankAsteroidId' test
```

## 4. Read the new parameterized test

`AsteroidAnalysisRequestValidationTest` protects the `@NotBlank` API invariant.

- Arrange: construct a request with the parameter supplied by JUnit.
- Act: call `validator.validate(request)`.
- Assert: invalid identifiers produce at least one constraint violation.
- Why parameterized: null, empty, and whitespace values are different inputs governed by the same rule.
- Positive control: `acceptsNonBlankAsteroidId` proves the validator is not rejecting every value.

## 5. Understand the existing test boundaries

### Pure unit mapping test

`PythonProcessBuilderTest` constructs normal Java objects and verifies the outgoing maps. It is fast because it needs no Spring context, database, HTTP server, or Python process.

### HTTP controller test

`AsteroidControllerTest` uses standalone `MockMvc`. It verifies routing, Jakarta validation, HTTP status codes, and exception translation while replacing the real `AsteroidChecker` with a Mockito mock.

### Orchestration test

`AsteroidCheckerTest` keeps the real orchestration logic and mocks `DatabaseController` and `MLController`. `when` supplies simulation, quantum, and risk results; `verify` proves each persistence boundary receives the correct object.

### Outbound HTTP test

`MLAnalysisServiceTest` mocks `RestTemplate` and `PythonProcessBuilder`. It covers valid responses, malformed service contracts, agent-to-quantum handoff, and transport failures without opening a socket.

### Persistence-mapping test

`DatabaseControllerTest` mocks Hibernate's `SessionFactory`, `Session`, and `Transaction`. An `ArgumentCaptor` verifies that response maps become correctly populated entities and that transactions commit.

## 6. What to say in an interview

> I use JUnit 5 to test behavior at the smallest useful boundary and Mockito to isolate dependencies. Controllers use standalone MockMvc, orchestration tests mock service and persistence boundaries, outbound HTTP tests mock RestTemplate, and Hibernate mapping tests capture persisted entities without starting MySQL. I use verify for important interactions, assertThrows for failure contracts, and parameterized tests for repeated invariants. Full database and service wiring belongs in a separate integration-test layer.

Be ready to explain these tradeoffs:

- `when` controls what a mock returns; `verify` checks how the unit collaborated with it.
- `@InjectMocks` does not create a Spring context; it only performs constructor/field injection into a normal object.
- Mock dependencies, not the class whose behavior you are testing.
- Unit tests should be deterministic and independent of execution order.
- Test names should state expected behavior, not implementation details.
- Coverage is evidence that code ran, not proof that the right behavior was asserted.
- Mocking everything can make tests mirror implementation and become fragile.

## 7. Practice exercises

1. Add a database failure case and verify the transaction is rolled back.
2. Add a `MLAnalysisServiceTest` for an invalid quantum response envelope.
3. Add a controller test proving unknown JSON fields follow the intended API policy.

For each exercise, first state the behavior in one sentence. Then write Arrange, Act, and Assert comments temporarily. Remove the comments once the structure is obvious.
