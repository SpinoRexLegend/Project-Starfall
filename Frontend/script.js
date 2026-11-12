document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysis-form');
    const input = document.getElementById('userInput');
    const submitButton = document.getElementById('startBtn');
    const buttonLabel = submitButton.querySelector('.button-label');
    const requestStatus = document.getElementById('request-status');
    const resultsSection = document.getElementById('results');

    initDeferredVideos();

    const configuredApiBaseUrl = window.STARFALL_CONFIG?.apiBaseUrl;
    const isLocalStaticPreview = ['127.0.0.1', 'localhost'].includes(window.location.hostname)
        && window.location.port !== '8080';
    const fallbackApiBaseUrl = isLocalStaticPreview
        ? `${window.location.protocol}//${window.location.hostname}:8080`
        : '';
    const apiBaseUrl = (configuredApiBaseUrl || fallbackApiBaseUrl).replace(/\/$/, '');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const asteroidId = input.value.trim();

        if (!asteroidId) {
            setRequestState('error', 'Enter an asteroid identifier to continue');
            input.focus();
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${apiBaseUrl}/api/v1/analyses`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ asteroidId })
            });
            const data = await response.json().catch(() => null);
            if (!response.ok) {
                throw new Error(data?.message || `Analysis failed with status ${response.status}`);
            }
            if (!data || typeof data !== 'object') {
                throw new Error('The observatory returned an unreadable case file');
            }

            renderCaseFile(asteroidId, data);
            setRequestState('success', 'Case file complete · recommendation prepared');
            resultsSection.hidden = false;
            window.setTimeout(() => resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
        } catch (error) {
            console.error('Starfall analysis failed:', error);
            setRequestState('error', error.message || 'Unable to reach the Starfall observatory');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        submitButton.disabled = isLoading;
        buttonLabel.textContent = isLoading ? 'Consulting the observatory' : 'Commence analysis';
        if (isLoading) setRequestState('loading', 'Simulation · agent review · quantum search');
    }

    function setRequestState(state, message) {
        requestStatus.className = `request-status ${state}`;
        requestStatus.querySelector('span:last-child').textContent = message;
    }

    function renderCaseFile(asteroidId, data) {
        const risk = objectOrEmpty(data.riskAssessment);
        const quantum = objectOrEmpty(data.quantum);
        const optimal = objectOrEmpty(data.optimalStrategy);
        const agent = objectOrEmpty(quantum.agent);
        const simulations = mergeSimulations(data.simulations, optimal);
        const selectedId = stringValue(quantum.selectedSimulationID);

        setText('case-id', asteroidId.toUpperCase());
        const impactProbability = numericValue(risk.impactProbability);
        setText('metric-risk', impactProbability === null ? '—' : `${(impactProbability * 100).toFixed(1)}%`);
        setText('metric-risk-label', stringValue(risk.estimatedDamage) || 'Damage class unavailable');

        const kineticEnergy = numericValue(risk.kineticEnergyMT);
        const materialDensity = numericValue(risk.materialDensityKgM3);
        setText('metric-energy', formatEnergyMt(kineticEnergy));
        setText('metric-energy-label', materialDensity === null
            ? '½mv² · Megatons TNT'
            : `½mv² · ${formatNumber(materialDensity, 0)} kg/m³`);
        setText('metric-selection', selectedId ? compactId(selectedId, 13) : '—');

        const qubits = numericValue(quantum.qubitsUsed);
        const iterations = numericValue(quantum.iterations);
        setText('metric-qubits', qubits === null ? '—' : `${formatNumber(qubits, 0)} q`);
        setText('metric-iterations', `${iterations === null ? '—' : formatNumber(iterations, 0)} Grover iterations`);

        const agentMode = stringValue(agent.mode);
        const agentModel = agentMode === 'fallback'
            ? 'Starfall local safety agent'
            : (stringValue(agent.model) || 'Validated scoring layer');
        setText('agent-model', agentModel);
        setText('agent-summary', stringValue(agent.summary) || 'Candidate simulations were validated and submitted to Grover amplitude amplification.');

        const selectedAssessment = Array.isArray(agent.candidateAssessments)
            ? agent.candidateAssessments.find((candidate) => stringValue(candidate?.simulationId) === selectedId)
            : null;
        setText('agent-rationale', stringValue(selectedAssessment?.rationale) || 'The selected state carried the strongest eligible score supplied to the Grover oracle.');

        renderRecommendation(optimal, stringValue(agent.recommendation));
        renderChart(quantum.bar_chart, selectedId);
        renderSimulationTable(simulations, selectedId);
    }

    function renderRecommendation(optimal, agentRecommendation) {
        const distance = numericValue(optimal['Distance from which it will pass if force is applied at that angle']);
        const fuel = numericValue(optimal['Fuel Cost']);
        const execution = numericValue(optimal['Execution time for hitting the earth']);
        const angle = numericValue(optimal['Angle at which force to be applied']);

        setText('output-text', agentRecommendation || 'The decision agent did not provide a final recommendation.');
        setText('strategy-angle', angle === null ? '—' : `${formatNumber(angle, 2)}°`);
        setText('strategy-distance', distance === null ? '—' : `${formatNumber(distance, 2)} km`);
        setText('strategy-fuel', fuel === null ? '—' : formatNumber(fuel, 2));
        setText('strategy-time', execution === null ? '—' : `${formatNumber(execution, 2)} s`);
    }

    function renderChart(points, selectedId) {
        const chart = document.getElementById('quantum-chart');
        chart.replaceChildren();
        const validPoints = Array.isArray(points) ? points : [];
        validPoints.forEach((point) => {
            const probability = clamp(numericValue(point?.probabilityHeight) ?? 0, 0, 100);
            const group = document.createElement('div');
            group.className = 'bar-group';
            group.title = `${stringValue(point?.label) || 'State'}: ${probability.toFixed(2)}%`;

            const bar = document.createElement('div');
            bar.className = `bar${point?.isOptimal ? ' highlight' : ''}`;
            bar.style.height = `${Math.max(probability, .7)}%`;

            const label = document.createElement('span');
            label.className = 'bar-label';
            label.textContent = stringValue(point?.label) || 'STATE';
            group.append(bar, label);
            chart.appendChild(group);
        });

        setText('probability-note', selectedId ? `Amplified state · ${compactId(selectedId, 13)}` : 'Highest amplified state');
        chart.setAttribute('aria-label', validPoints.length ? `Grover probability chart with ${validPoints.length} measured states` : 'No Grover probability data available');
    }

    function renderSimulationTable(simulations, selectedId) {
        const body = document.getElementById('log-body');
        body.replaceChildren();
        simulations.forEach((simulation) => {
            const simulationId = simulationIdentifier(simulation);
            const row = document.createElement('tr');
            if (simulationId === selectedId) row.classList.add('recommended');

            appendCell(row, compactId(simulationId, 12) || 'Unknown');
            appendCell(row, formattedMeasurement(simulation['Angle at which force to be applied'], '°'));
            appendCell(row, formattedMeasurement(simulation['Execution time for hitting the earth'], ' s'));
            appendCell(row, formattedMeasurement(simulation['Distance from which it will pass if force is applied at that angle'], ' km'));
            appendCell(row, formattedMeasurement(simulation['Fuel Cost'], ''));

            const statusCell = document.createElement('td');
            const status = document.createElement('span');
            const succeeded = simulationSucceeded(simulation);
            status.className = `status-chip ${succeeded ? 'success' : 'failure'}`;
            status.textContent = succeeded ? 'Successful' : 'Failed';
            statusCell.appendChild(status);
            row.appendChild(statusCell);
            body.appendChild(row);
        });
        setText('simulation-count', simulations.length);
    }

    function mergeSimulations(value, optimal) {
        const simulations = Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') : [];
        const optimalId = simulationIdentifier(optimal);
        if (optimalId && !simulations.some((simulation) => simulationIdentifier(simulation) === optimalId)) return [optimal, ...simulations];
        return simulations;
    }

    function simulationIdentifier(simulation) {
        if (!simulation || typeof simulation !== 'object') return '';
        return stringValue(simulation.SimulationID ?? simulation.s_ID);
    }

    function simulationSucceeded(simulation) {
        if (!simulation || typeof simulation !== 'object') return false;
        const value = simulation['Chances of success'] ?? simulation.Success ?? simulation.success;
        if (typeof value === 'boolean') return value;
        if (typeof value === 'number') return value > .5;
        return ['true', '1'].includes(String(value).toLowerCase());
    }

    function appendCell(row, value) { const cell = document.createElement('td'); cell.textContent = value; row.appendChild(cell); }
    function formattedMeasurement(value, suffix) { const numeric = numericValue(value); return numeric === null ? '—' : `${formatNumber(numeric, 2)}${suffix}`; }
    function numericValue(value) { if (value === null || value === undefined || value === '') return null; const numeric = Number(value); return Number.isFinite(numeric) ? numeric : null; }
    function stringValue(value) { return typeof value === 'string' ? value.trim() : ''; }
    function objectOrEmpty(value) { return value && typeof value === 'object' && !Array.isArray(value) ? value : {}; }
    function compactId(value, length) { const text = stringValue(value); if (!text || text.length <= length) return text; return `${text.slice(0, length - 1)}…`; }
    function formatNumber(value, fractionDigits) { return new Intl.NumberFormat('en-US', { minimumFractionDigits: fractionDigits, maximumFractionDigits: fractionDigits }).format(value); }
    function formatEnergyMt(value) {
        if (value === null) return '—';
        if (value === 0) return '0';
        return Math.abs(value) < .01 ? value.toExponential(2) : formatNumber(value, 2);
    }
    function clamp(value, minimum, maximum) { return Math.min(maximum, Math.max(minimum, value)); }
    function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = String(value); }

    function initDeferredVideos() {
        const saveData = Boolean(navigator.connection?.saveData);
        const canAnimateHero = window.matchMedia('(min-width: 900px)').matches && !saveData;
        const canAnimateProtocol = !saveData;
        const heroVideo = document.querySelector('[data-deferred-video="hero"]');
        const viewportVideos = [...document.querySelectorAll('[data-deferred-video="viewport"]')];

        const hydrateVideo = (video) => {
            if (!video || video.dataset.hydrated === 'true') return;
            const source = video.querySelector('source[data-src]');
            if (!source) return;
            video.muted = true;
            video.defaultMuted = true;
            video.loop = true;
            source.src = source.dataset.src;
            source.removeAttribute('data-src');
            video.dataset.hydrated = 'true';
            video.addEventListener('canplay', () => video.classList.add('is-ready'), { once: true });
            video.load();
        };

        const playVideo = (video) => {
            hydrateVideo(video);
            video.dataset.inView = 'true';
            if (!document.hidden) video.play().catch(() => {});
        };

        if (heroVideo && canAnimateHero) {
            const startHero = () => playVideo(heroVideo);
            if ('requestIdleCallback' in window) window.requestIdleCallback(startHero, { timeout: 2500 });
            else window.setTimeout(startHero, 1200);
        }

        if (canAnimateProtocol && viewportVideos.length && 'IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    const video = entry.target;
                    if (entry.isIntersecting) playVideo(video);
                    else {
                        video.dataset.inView = 'false';
                        video.pause();
                    }
                });
            }, { rootMargin: '240px 0px', threshold: 0.01 });
            viewportVideos.forEach((video) => observer.observe(video));
        }

        document.addEventListener('visibilitychange', () => {
            document.querySelectorAll('video[data-hydrated="true"]').forEach((video) => {
                if (document.hidden) video.pause();
                else if (video.dataset.inView === 'true') video.play().catch(() => {});
            });
        });
    }
});
