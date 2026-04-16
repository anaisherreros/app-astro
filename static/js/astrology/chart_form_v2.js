const form = document.getElementById("chart-form");
const submitBtn = document.getElementById("submit-btn");
const birthPlaceInput = document.getElementById("birth_place");
const suggestionsList = document.getElementById("city-suggestions");

const resultsShell = document.getElementById("results-shell");
const resultTabs = document.querySelectorAll(".result-tab-btn");
const resultPanels = document.querySelectorAll(".result-panel");

const interpretationCards = document.getElementById("interpretation-cards");
const planetsCards = document.getElementById("planets-cards");
const aspectsTableBody = document.getElementById("aspects-table-body");

const resultBox = document.getElementById("result");
const resultContent = document.getElementById("result-content");
const DEBUG_SHOW_RAW_JSON = true;

let suggestionsData = [];
let activeSuggestionIndex = -1;
let debounceTimer = null;

const PLANET_LABELS = {
    ascendant: "Ascendente",
    sun: "Sol",
    moon: "Luna",
    mercury: "Mercurio",
    venus: "Venus",
    mars: "Marte",
    jupiter: "Jupiter",
    saturn: "Saturno",
    uranus: "Urano",
    neptune: "Neptuno",
    pluto: "Pluton",
    north_node: "Nodo Norte",
};

const PLANET_ORDER = [
    "ascendant",
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "north_node",
];

const PLANET_SYMBOLS = {
    ascendant: "↑",
    sun: "☉",
    moon: "☽",
    mercury: "☿",
    venus: "♀",
    mars: "♂",
    jupiter: "♃",
    saturn: "♄",
    uranus: "♅",
    neptune: "♆",
    pluto: "♇",
    north_node: "☊",
};

const ASPECT_LABELS = {
    conjunction: "Conjuncion",
    sextile: "Sextil",
    trine: "Trigono",
    semi_sextile: "Semi sextil",
    quincunx: "Quincuncio",
    square: "Cuadratura",
    opposition: "Oposicion",
};

const ASPECT_SYMBOLS = {
    conjunction: "☌",
    sextile: "✶",
    trine: "△",
    semi_sextile: "⚺",
    quincunx: "⚻",
    square: "□",
    opposition: "☍",
};

const SIGN_DISPLAY_BY_CANONICAL = {
    aries: "Aries",
    tauro: "Tauro",
    geminis: "Géminis",
    cancer: "Cáncer",
    leo: "Leo",
    virgo: "Virgo",
    libra: "Libra",
    escorpio: "Escorpio",
    sagitario: "Sagitario",
    capricornio: "Capricornio",
    acuario: "Acuario",
    piscis: "Piscis",
};

const SIGN_CANONICAL_BY_INPUT = {
    aries: "aries",
    tauro: "tauro",
    geminis: "geminis",
    cancer: "cancer",
    leo: "leo",
    virgo: "virgo",
    libra: "libra",
    escorpio: "escorpio",
    sagitario: "sagitario",
    capricornio: "capricornio",
    acuario: "acuario",
    piscis: "piscis",
};

const ASPECT_DISPLAY_LABELS = {
    conjunction: "conjunción",
    sextile: "sextil",
    trine: "trígono",
    semi_sextile: "semi sextil",
    quincunx: "quincuncio",
    square: "cuadratura",
    opposition: "oposición",
};

function setError(id, message) {
    const el = document.getElementById("error_" + id);
    if (el) {
        el.textContent = message || "";
    }
}

function formatDegree(value) {
    if (typeof value !== "number") {
        return "--";
    }
    return `${value.toFixed(2)}°`;
}

function normalizeTextValue(value) {
    if (typeof value !== "string") {
        return "";
    }
    return value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

function normalizeSign(sign) {
    const normalizedInput = normalizeTextValue(sign);
    const canonical = SIGN_CANONICAL_BY_INPUT[normalizedInput] || normalizedInput || "desconocido";
    return {
        canonical,
        display: SIGN_DISPLAY_BY_CANONICAL[canonical] || sign || "--",
    };
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getResultPayload(data) {
    // Accept payloads like:
    // {result:{...}} or {result:{result:{...}}} or {...}
    let current = data;
    for (let i = 0; i < 3; i += 1) {
        if (current?.result && typeof current.result === "object") {
            current = current.result;
            continue;
        }
        break;
    }
    if (current && typeof current === "object") {
        return current;
    }
    return {};
}

function renderSuggestions(items) {
    suggestionsData = items;
    activeSuggestionIndex = -1;

    if (!items.length) {
        suggestionsList.hidden = true;
        suggestionsList.innerHTML = "";
        return;
    }

    suggestionsList.innerHTML = items
        .map((item, index) => `<li data-index="${index}" role="option">${escapeHtml(item.label)}</li>`)
        .join("");
    suggestionsList.hidden = false;
}

async function fetchCitySuggestions(query) {
    const response = await fetch(`/astrology/cities/suggest/?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
        return [];
    }
    const data = await response.json();
    return data.results || [];
}

function applySuggestion(index) {
    const item = suggestionsData[index];
    if (!item) {
        return;
    }
    birthPlaceInput.value = item.value;
    renderSuggestions([]);
}

function bindCityAutocomplete() {
    birthPlaceInput.addEventListener("input", () => {
        const query = birthPlaceInput.value.trim();
        clearTimeout(debounceTimer);

        if (query.length < 2) {
            renderSuggestions([]);
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                renderSuggestions(await fetchCitySuggestions(query));
            } catch {
                renderSuggestions([]);
            }
        }, 180);
    });

    birthPlaceInput.addEventListener("keydown", (event) => {
        if (suggestionsList.hidden || !suggestionsData.length) {
            return;
        }

        if (event.key === "ArrowDown") {
            event.preventDefault();
            activeSuggestionIndex = (activeSuggestionIndex + 1) % suggestionsData.length;
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            activeSuggestionIndex = (activeSuggestionIndex - 1 + suggestionsData.length) % suggestionsData.length;
        } else if (event.key === "Enter") {
            if (activeSuggestionIndex >= 0) {
                event.preventDefault();
                applySuggestion(activeSuggestionIndex);
            }
            return;
        } else if (event.key === "Escape") {
            renderSuggestions([]);
            return;
        } else {
            return;
        }

        const items = suggestionsList.querySelectorAll("li");
        items.forEach((item) => item.classList.remove("is-active"));
        if (items[activeSuggestionIndex]) {
            items[activeSuggestionIndex].classList.add("is-active");
        }
    });

    suggestionsList.addEventListener("mousedown", (event) => {
        const li = event.target.closest("li");
        if (!li) {
            return;
        }
        const index = Number(li.dataset.index);
        if (!Number.isNaN(index)) {
            applySuggestion(index);
        }
    });

    document.addEventListener("click", (event) => {
        if (!suggestionsList.hidden && !suggestionsList.contains(event.target) && event.target !== birthPlaceInput) {
            renderSuggestions([]);
        }
    });
}

function setupTabs() {
    resultTabs.forEach((btn) => {
        btn.addEventListener("click", () => {
            setActiveTab(btn.dataset.tab);
        });
    });
}

function setActiveTab(tabName) {
    resultTabs.forEach((btn) => {
        btn.setAttribute("aria-selected", btn.dataset.tab === tabName ? "true" : "false");
    });
    resultPanels.forEach((panel) => {
        const isActive = panel.dataset.panel === tabName;
        panel.hidden = !isActive;
        panel.classList.toggle("hidden", !isActive);
    });
}

function getPlanetRows(result) {
    const planets = result?.planets || {};
    const ascendant = result?.angles?.ascendant || null;
    const northNode = result?.nodes?.north_node || null;

    return PLANET_ORDER.map((key) => {
        if (key === "ascendant") {
            return { key, data: ascendant };
        }
        if (key === "north_node") {
            return { key, data: northNode };
        }
        return { key, data: planets[key] || null };
    }).filter((item) => item.data);
}

function buildStep1Payload(result) {
    const rows = getPlanetRows(result);
    const rawAspects = Array.isArray(result?.aspects) ? result.aspects : [];
    const rawUnaspected = Array.isArray(result?.unaspected_planets) ? result.unaspected_planets : [];

    const normalizedPlanets = rows.map(({ key, data }) => {
        const signInfo = normalizeSign(data?.sign);
        return {
            key,
            label: PLANET_LABELS[key] || key,
            sign_canonical: signInfo.canonical,
            sign_display: signInfo.display,
            house: data?.house ?? null,
            degree: data?.degree ?? null,
        };
    });

    const seenAspectIds = new Set();
    const normalizedAspects = [];

    rawAspects.forEach((item) => {
        const pointA = item?.point_a;
        const pointB = item?.point_b;
        const aspectName = item?.aspect;

        if (!pointA || !pointB || !aspectName) {
            return;
        }

        const [left, right] = [pointA, pointB].sort();
        const aspectId = `${left}_${aspectName}_${right}`;
        if (seenAspectIds.has(aspectId)) {
            return;
        }
        seenAspectIds.add(aspectId);

        normalizedAspects.push({
            fact_id: aspectId,
            point_a: pointA,
            point_b: pointB,
            point_a_label: PLANET_LABELS[pointA] || pointA,
            point_b_label: PLANET_LABELS[pointB] || pointB,
            aspect_canonical: aspectName,
            aspect_display: ASPECT_DISPLAY_LABELS[aspectName] || aspectName,
            orb: typeof item?.orb === "number" ? item.orb : null,
        });
    });

    const normalizedUnaspected = rawUnaspected.map((planetKey) => {
        const planetData = result?.planets?.[planetKey];
        const signInfo = normalizeSign(planetData?.sign);
        return {
            key: planetKey,
            label: PLANET_LABELS[planetKey] || planetKey,
            sign_canonical: signInfo.canonical,
            sign_display: signInfo.display,
            house: planetData?.house ?? null,
        };
    });

    const positionFacts = normalizedPlanets.map((item) => ({
        fact_id: `${item.key}_in_${item.sign_canonical}_house_${item.house ?? "na"}`,
        type: "position",
        text_display: `${item.label} en ${item.sign_display} en casa ${item.house ?? "--"}.`,
    }));

    const aspectFacts = normalizedAspects.map((item) => ({
        fact_id: item.fact_id,
        type: "aspect",
        text_display: `${item.point_a_label} en ${item.aspect_display} con ${item.point_b_label}${item.orb !== null ? ` (orbe ${formatDegree(item.orb)})` : ""}.`,
    }));

    const unaspectedFacts = normalizedUnaspected.map((item) => ({
        fact_id: `${item.key}_unaspected`,
        type: "unaspected",
        text_display: `${item.label} inaspectado en ${item.sign_display} en casa ${item.house ?? "--"}.`,
    }));

    return {
        normalized: {
            planets: normalizedPlanets,
            aspects: normalizedAspects,
            unaspected_planets: normalizedUnaspected,
        },
        facts: {
            positions: positionFacts,
            aspects: aspectFacts,
            unaspected: unaspectedFacts,
            all: [...positionFacts, ...aspectFacts, ...unaspectedFacts],
        },
    };
}

function buildStep1DebugData(originalData, step1) {
    return {
        source_payload: originalData,
        pipeline_status: {
            current_step: 1,
            completed_steps: [1],
            next_step: 2,
            step_name: "json_to_structured_text",
        },
        debug: {
            step1_normalized: step1.normalized,
            step1_text_facts: step1.facts,
        },
    };
}

function renderInterpretationStep1(step1) {
    if (!interpretationCards) {
        return;
    }

    const positionList = step1.facts.positions
        .map((fact) => `<li>${escapeHtml(fact.text_display)}</li>`)
        .join("");
    const aspectList = step1.facts.aspects
        .map((fact) => `<li>${escapeHtml(fact.text_display)}</li>`)
        .join("");
    const unaspectedList = step1.facts.unaspected
        .map((fact) => `<li>${escapeHtml(fact.text_display)}</li>`)
        .join("");

    interpretationCards.innerHTML = `
        <article class="card-surface-navy interpret-block p-5">
            <h3>Paso 1: JSON a texto estructurado</h3>
            <p class="intro">Este bloque muestra la conversión inicial de la carta a hechos en español, listos para deduplicación y búsqueda RAG.</p>

            <h4>Posiciones</h4>
            <ul class="list-disc space-y-1">${positionList || "<li>Sin datos de posiciones.</li>"}</ul>

            <h4>Aspectos (sin duplicados A-B / B-A)</h4>
            <ul class="list-disc space-y-1">${aspectList || "<li>Sin datos de aspectos.</li>"}</ul>

            <h4>Inaspectados</h4>
            <ul class="list-disc space-y-1">${unaspectedList || "<li>Sin planetas inaspectados.</li>"}</ul>
        </article>
    `;
}

function renderPlanetsCards(result) {
    if (!planetsCards) {
        return;
    }

    const rows = getPlanetRows(result);
    if (!rows.length) {
        planetsCards.innerHTML = `
            <article class="planet-card sm:col-span-2">
                <p class="body-copy">No hay datos de planetas para esta carta.</p>
            </article>
        `;
        return;
    }

    planetsCards.innerHTML = rows
        .map(({ key, data }) => {
            const sym = escapeHtml(PLANET_SYMBOLS[key]);
            const label = escapeHtml(PLANET_LABELS[key]);
            return `
                <article class="planet-card">
                    <div class="planet-card-head">
                        <span class="planet-symbol-circle" aria-hidden="true">${sym}</span>
                        <h3 class="planet-card-title">${label}</h3>
                        <span class="planet-house-pill">Casa ${data.house ?? "--"}</span>
                    </div>
                    <p class="planet-card-meta">${escapeHtml(data.sign ?? "--")} · ${formatDegree(data.degree)}</p>
                </article>
            `;
        })
        .join("");
}

function getAspectRowClass(aspectName) {
    if (aspectName === "opposition" || aspectName === "square") {
        return "aspect-row-red";
    }
    if (aspectName === "quincunx" || aspectName === "semi_sextile") {
        return "aspect-row-green";
    }
    if (aspectName === "trine" || aspectName === "sextile") {
        return "aspect-row-blue";
    }
    return "aspect-row-neutral";
}

function renderAspectsTable(result) {
    if (!aspectsTableBody) {
        return;
    }

    const aspects = result?.aspects || [];
    if (!aspects.length) {
        aspectsTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="py-3 text-muted">No se detectaron aspectos para esta carta.</td>
            </tr>
        `;
        return;
    }

    aspectsTableBody.innerHTML = aspects
        .map((item) => {
            const a = escapeHtml(PLANET_LABELS[item.point_a] || item.point_a);
            const b = escapeHtml(PLANET_LABELS[item.point_b] || item.point_b);
            const aspectLabel = escapeHtml(ASPECT_LABELS[item.aspect] || item.aspect);
            const symbol = ASPECT_SYMBOLS[item.aspect] || "•";
            const rowClass = getAspectRowClass(item.aspect);
            return `
                <tr class="${rowClass}">
                    <td>${a}</td>
                    <td class="aspect-cell-aspect">${symbol} ${aspectLabel}</td>
                    <td>${b}</td>
                    <td>${formatDegree(item.orb)}</td>
                </tr>
            `;
        })
        .join("");
}

function renderRawJson(data) {
    if (!DEBUG_SHOW_RAW_JSON) {
        resultBox.hidden = true;
        resultContent.textContent = "";
        return;
    }
    resultBox.hidden = false;
    resultContent.textContent = JSON.stringify(data, null, 2);
}

function renderAll(data) {
    const result = getResultPayload(data);
    const step1 = buildStep1Payload(result);
    renderInterpretationStep1(step1);
    renderPlanetsCards(result);
    renderAspectsTable(result);
    renderRawJson(buildStep1DebugData(data, step1));
}

function showResults() {
    resultsShell.classList.remove("hidden");
    resultsShell.hidden = false;
}

function hideResults() {
    resultsShell.classList.add("hidden");
    resultsShell.hidden = true;
}

setupTabs();
bindCityAutocomplete();
setActiveTab("interpretation");
hideResults();

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    setError("birth_date", "");
    setError("birth_time", "");
    setError("birth_place", "");

    const birthDate = document.getElementById("birth_date").value;
    const birthTime = document.getElementById("birth_time").value;
    const birthPlace = birthPlaceInput.value.trim();

    let valid = true;
    if (!birthDate) {
        setError("birth_date", "La fecha es obligatoria.");
        valid = false;
    }
    if (!birthTime) {
        setError("birth_time", "La hora es obligatoria.");
        valid = false;
    }
    if (!birthPlace) {
        setError("birth_place", "El lugar es obligatorio.");
        valid = false;
    }
    if (!valid) {
        return;
    }

    // Show the result shell immediately so user sees progress state.
    showResults();
    setActiveTab("interpretation");
    interpretationCards.innerHTML = `
        <article class="card-surface-gray p-4">
            <p class="body-copy text-primary">Calculando carta...</p>
        </article>
    `;
    if (planetsCards) {
        planetsCards.innerHTML = `
            <article class="planet-card sm:col-span-2">
                <p class="body-copy">Calculando...</p>
            </article>
        `;
    }
    aspectsTableBody.innerHTML = `
        <tr><td colspan="4" class="py-3 text-muted">Calculando...</td></tr>
    `;

    submitBtn.disabled = true;
    submitBtn.textContent = "Calculando...";

    try {
        const params = new URLSearchParams({
            birth_date: birthDate,
            birth_time: birthTime,
            birth_place: birthPlace,
        });

        const response = await fetch(`/astrology/chart/?${params.toString()}`);
        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.error || "No se pudo calcular la carta.");
        }

        renderAll(data);
    } catch (error) {
        interpretationCards.innerHTML = `
            <article class="card-surface-gray p-4">
                <p class="text-error">Error al calcular la carta: ${escapeHtml(error.message)}</p>
            </article>
        `;
        if (planetsCards) {
            planetsCards.innerHTML = `
                <article class="planet-card sm:col-span-2">
                    <p class="text-error">Sin datos de planetas por error de calculo.</p>
                </article>
            `;
        }
        aspectsTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="py-3 text-error">Sin datos de aspectos por error de calculo.</td>
            </tr>
        `;
        resultBox.hidden = false;
        resultContent.textContent = "Error al calcular la carta: " + error.message;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Calcular carta";
    }
});
