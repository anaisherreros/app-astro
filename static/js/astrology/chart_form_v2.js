/** Rutas API (sobrescribir desde plantilla con window.ATLAS_URLS). */
const ATLAS = window.ATLAS_URLS || {
    chart: "/astrology/chart/",
    interpretation: "/astrology/interpretation/",
    citiesSuggest: "/astrology/cities/suggest/",
};

const form = document.getElementById("chart-form");
const submitBtn = document.getElementById("submit-btn");
const submitBtnLabel = document.getElementById("submit-btn-label");
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
/** JSON crudo: solo en la pestaña Planetas (bloque colapsable). */
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

function getCsrfToken() {
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input && input.value) {
        return input.value;
    }
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

let markedOptionsApplied = false;

function configureMarkedParser() {
    if (markedOptionsApplied || typeof marked === "undefined") {
        return;
    }
    const m = marked;
    if (typeof m.setOptions === "function") {
        m.setOptions({
            gfm: true,
            breaks: false,
            mangle: false,
            headerIds: false,
        });
    }
    markedOptionsApplied = true;
}

function stripLeadingInterpretacionHeading(markdown) {
    const lines = String(markdown ?? "").replace(/\r\n/g, "\n").split("\n");
    while (lines.length) {
        const first = lines[0].trim();
        if (!first) {
            lines.shift();
            continue;
        }
        if (/^(#{1,6}\s*)?Interpretación\s*$/i.test(first)) {
            lines.shift();
            continue;
        }
        break;
    }
    return lines.join("\n").trim();
}

function parseMarkdownToHtml(markdown) {
    configureMarkedParser();
    const md = stripLeadingInterpretacionHeading(String(markdown ?? "").trim().replace(/\r\n/g, "\n"));
    if (!md) {
        return "";
    }
    const parse =
        typeof marked !== "undefined" && typeof marked.parse === "function"
            ? (src) => marked.parse(src)
            : typeof marked !== "undefined" && typeof marked === "function"
              ? (src) => marked(src)
              : null;
    if (!parse) {
        return escapeHtml(md).replace(/\n/g, "<br />");
    }
    const sep = "\n---\n";
    const idx = md.lastIndexOf(sep);
    let rawHtml;
    if (idx !== -1) {
        const mainMd = stripLeadingInterpretacionHeading(md.slice(0, idx).trim());
        const synMd = stripLeadingInterpretacionHeading(md.slice(idx + sep.length).trim());
        rawHtml =
            parse(mainMd) +
            (synMd ? `<div class="synthesis">${parse(synMd)}</div>` : "");
    } else {
        rawHtml = parse(md);
    }
    if (typeof DOMPurify !== "undefined" && typeof DOMPurify.sanitize === "function") {
        try {
            return DOMPurify.sanitize(rawHtml, { USE_PROFILES: { html: true } });
        } catch {
            return DOMPurify.sanitize(rawHtml);
        }
    }
    return rawHtml;
}

/** Orden: primera coincidencia gana (títulos tipo "Figura…" antes que "Sol…"). */
const INTERPRETATION_H2_ICON_ENTRIES = [
    ["figura", "✦"],
    ["sol", "☉"],
    ["luna", "☽"],
    ["saturno", "♄"],
    ["ascendente", "↑"],
    ["recorrido de casas", "✺"],
    ["casas", "⌂"],
    ["nodo", "☊"],
    ["sintesis", "◈"],
];

function normalizeInterpretationH2MatchText(s) {
    return String(s ?? "")
        .normalize("NFD")
        .replace(/\p{M}/gu, "")
        .toLowerCase();
}

function interpretationH2IconForPlainText(plain) {
    const hay = normalizeInterpretationH2MatchText(plain);
    for (const [key, symbol] of INTERPRETATION_H2_ICON_ENTRIES) {
        const esc = key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const re = new RegExp(`\\b${esc}\\b`, "i");
        if (re.test(hay)) {
            return symbol;
        }
    }
    return null;
}

/**
 * Tras el markdown: icono dorado delante de cada h2 según el texto (no en `.synthesis`).
 */
function decorateInterpretationH2Icons(root) {
    if (!root || typeof root.querySelectorAll !== "function") {
        return;
    }
    const headings = root.querySelectorAll("h2");
    headings.forEach((h2) => {
        if (h2.closest(".synthesis")) {
            return;
        }
        if (h2.querySelector(":scope > .interpret-h2-icon")) {
            return;
        }
        const plain = h2.textContent || "";
        const icon = interpretationH2IconForPlainText(plain);
        if (!icon) {
            return;
        }
        const span = document.createElement("span");
        span.className = "interpret-h2-icon";
        span.setAttribute("aria-hidden", "true");
        span.textContent = icon;
        h2.insertBefore(span, h2.firstChild);
    });
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
        .map(
            (item, index) =>
                `<li class="city-dropdown-item" data-index="${index}" role="option">${escapeHtml(item.label)}</li>`,
        )
        .join("");
    suggestionsList.hidden = false;
}

async function fetchCitySuggestions(query) {
    const response = await fetch(
        `${ATLAS.citiesSuggest}?q=${encodeURIComponent(query)}`,
    );
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

function initFlatpickrBirthFields() {
    const birthDateEl = document.getElementById("birth_date");
    const birthTimeEl = document.getElementById("birth_time");
    if (!birthDateEl || !birthTimeEl || typeof flatpickr !== "function") {
        console.warn("[Atlas chart_form] flatpickr no disponible; usa texto plano para fecha/hora.");
        return;
    }
    const esLocale =
        typeof flatpickr !== "undefined" && flatpickr.l10ns && flatpickr.l10ns.es ? flatpickr.l10ns.es : undefined;

    const dateOpts = {
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "d/m/Y",
        allowInput: false,
        disableMobile: true,
        monthSelectorType: "static",
        altInputClass: "form-input",
    };
    if (esLocale) {
        dateOpts.locale = esLocale;
    }
    flatpickr(birthDateEl, dateOpts);

    flatpickr(birthTimeEl, {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
        allowInput: false,
        disableMobile: true,
        minuteIncrement: 1,
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
    const known = new Set(
        Array.from(resultTabs).map((btn) => btn.dataset.tab).filter(Boolean),
    );
    const resolved = known.has(tabName) ? tabName : "interpretation";
    resultTabs.forEach((btn) => {
        btn.setAttribute("aria-selected", btn.dataset.tab === resolved ? "true" : "false");
    });
    resultPanels.forEach((panel) => {
        const isActive = panel.dataset.panel === resolved;
        panel.hidden = !isActive;
        panel.classList.toggle("hidden", !isActive);
    });
}

function syncResultsChartCaption() {
    const cap = document.getElementById("results-chart-caption");
    const textEl = document.getElementById("results-chart-caption-text");
    if (!cap || !textEl) {
        return;
    }
    const name = document.getElementById("full_name")?.value?.trim() || "";
    const line = name ? `Carta natal de ${name}` : "Carta natal";
    textEl.textContent = line.toLocaleUpperCase("es");
    cap.hidden = false;
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

function interpretationStep1Html(step1) {
    const positionList = step1.facts.positions
        .map((fact) => `<li>${escapeHtml(fact.text_display)}</li>`)
        .join("");
    const aspectList = step1.facts.aspects
        .map((fact) => `<li>${escapeHtml(fact.text_display)}</li>`)
        .join("");
    const unaspectedList = step1.facts.unaspected
        .map((fact) => `<li>${escapeHtml(fact.text_display)}</li>`)
        .join("");

    return `
        <article class="card-surface interpret-block interpret-facts-card p-1">
            <h3>Hechos estructurados</h3>
            <p class="intro">Resumen automático de la carta en texto, por si la interpretación principal no está disponible.</p>

            <h4>Posiciones</h4>
            <ul class="list-disc space-y-1">${positionList || "<li>Sin datos de posiciones.</li>"}</ul>

            <h4>Aspectos (sin duplicados A-B / B-A)</h4>
            <ul class="list-disc space-y-1">${aspectList || "<li>Sin datos de aspectos.</li>"}</ul>

            <h4>Inaspectados</h4>
            <ul class="list-disc space-y-1">${unaspectedList || "<li>Sin planetas inaspectados.</li>"}</ul>
        </article>
    `;
}

function renderInterpretationStep1(step1) {
    if (!interpretationCards) {
        return;
    }
    interpretationCards.innerHTML = interpretationStep1Html(step1);
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
    if (!resultBox || !resultContent) {
        return;
    }
    if (!DEBUG_SHOW_RAW_JSON) {
        resultBox.hidden = true;
        resultContent.textContent = "";
        return;
    }
    resultBox.hidden = false;
    resultContent.textContent = JSON.stringify(data, null, 2);
}

function renderChartVisuals(data) {
    const result = getResultPayload(data);
    const step1 = buildStep1Payload(result);
    renderPlanetsCards(result);
    renderAspectsTable(result);
    renderRawJson(buildStep1DebugData(data, step1));
    return { result, step1 };
}

function renderInterpretationLoading() {
    if (!interpretationCards) {
        return;
    }
    interpretationCards.innerHTML = `
        <article class="card-surface-gray p-1">
            <p class="body-copy text-primary">Carta calculada. Redactando la interpretación (puede tardar un minuto)…</p>
        </article>
    `;
}

function renderInterpretationFromLLM(text, inputTokens, outputTokens) {
    if (!interpretationCards) {
        return;
    }
    const safe = (text || "").trim();
    if (!safe) {
        interpretationCards.innerHTML = `
            <article class="card-surface-gray p-1">
                <p class="text-error">No se recibió texto de interpretación. Revisa los logs del servidor; si activaste el JSON técnico, estará en la pestaña Planetas.</p>
            </article>
        `;
        return;
    }
    const bodyHtml = parseMarkdownToHtml(safe);
    if (inputTokens != null && outputTokens != null) {
        console.info("[Atlas interpretation] tokens", {
            input_tokens: inputTokens,
            output_tokens: outputTokens,
        });
    }
    interpretationCards.innerHTML = `
        <article class="card-surface interpret-block interpret-llm-card">
            <div id="interpretation" class="interpret-llm-body">${bodyHtml}</div>
        </article>
    `;
    const interpretRoot = document.getElementById("interpretation");
    if (interpretRoot) {
        decorateInterpretationH2Icons(interpretRoot);
    }
}

function renderInterpretationError(message, step1) {
    if (!interpretationCards) {
        return;
    }
    const errBlock = `
        <article class="card-surface-gray p-1">
            <p class="text-error">No se pudo generar la interpretación: ${escapeHtml(message)}</p>
            <p class="body-copy mt-2 text-sm text-muted">Comprueba ANTHROPIC_API_KEY en el servidor y tu conexión. Mientras tanto puedes revisar planetas y aspectos en las otras pestañas.</p>
        </article>
    `;
    const fallback = step1 != null ? interpretationStep1Html(step1) : "";
    interpretationCards.innerHTML = `${errBlock}${fallback}`;
}

async function fetchInterpretation(chartPayload, nombre) {
    const csrf = getCsrfToken();
    if (!csrf) {
        console.warn(
            "[Atlas interpretation] No hay token CSRF (csrftoken). ¿Falta {% csrf_token %} en el formulario?",
        );
    }

    console.info("[Atlas interpretation] Enviando POST %s …", ATLAS.interpretation);

    const response = await fetch(ATLAS.interpretation, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf,
        },
        body: JSON.stringify({
            chart: chartPayload,
            nombre: nombre || null,
        }),
    });

    const rawText = await response.text();
    let payload;
    try {
        payload = JSON.parse(rawText);
    } catch (e) {
        console.error(
            "[Atlas interpretation] Respuesta no JSON (status %s). Primeros 400 caracteres:\n%s",
            response.status,
            rawText.slice(0, 400),
        );
        throw new Error(
            `El servidor no devolvio JSON (HTTP ${response.status}). Revisa la consola del servidor (runserver / Railway logs).`,
        );
    }

    if (!response.ok || payload.error) {
        console.error("[Atlas interpretation] Error API:", response.status, payload);
        const detail = payload.traceback ? `${payload.error}\n(ver traceback en logs servidor)` : payload.error;
        throw new Error(detail || `HTTP ${response.status}`);
    }

    if (typeof payload.interpretation !== "string") {
        console.error("[Atlas interpretation] Respuesta sin campo interpretation:", payload);
        throw new Error("El servidor no devolvió texto de interpretación.");
    }

    console.info(
        "[Atlas interpretation] OK (input_tokens=%s output_tokens=%s)",
        payload.input_tokens,
        payload.output_tokens,
    );
    return payload;
}

function showResults() {
    resultsShell.classList.remove("hidden");
    resultsShell.hidden = false;
    syncResultsChartCaption();
}

function hideResults() {
    const cap = document.getElementById("results-chart-caption");
    if (cap) {
        cap.hidden = true;
    }
    resultsShell.classList.add("hidden");
    resultsShell.hidden = true;
}

setupTabs();
bindCityAutocomplete();
setActiveTab("interpretation");
hideResults();
initFlatpickrBirthFields();

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    setError("birth_date", "");
    setError("birth_time", "");
    setError("birth_place", "");

    const birthDate = document.getElementById("birth_date").value;
    const birthTimeRaw = document.getElementById("birth_time").value;
    const birthTime = birthTimeRaw.length > 5 ? birthTimeRaw.slice(0, 5) : birthTimeRaw;
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
        <article class="card-surface-gray p-1">
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
    if (submitBtnLabel) {
        submitBtnLabel.textContent = "Calculando...";
    } else {
        submitBtn.textContent = "Calculando...";
    }

    try {
        const params = new URLSearchParams({
            birth_date: birthDate,
            birth_time: birthTime,
            birth_place: birthPlace,
        });

        const response = await fetch(`${ATLAS.chart}?${params.toString()}`);
        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.error || "No se pudo calcular la carta.");
        }

        const { result, step1 } = renderChartVisuals(data);
        const fullName = document.getElementById("full_name")?.value?.trim() || "";

        renderInterpretationLoading();
        try {
            const llm = await fetchInterpretation(result, fullName);
            renderInterpretationFromLLM(
                llm.interpretation,
                llm.input_tokens,
                llm.output_tokens,
            );
        } catch (interpretError) {
            renderInterpretationError(interpretError.message, step1);
        }
    } catch (error) {
        interpretationCards.innerHTML = `
            <article class="card-surface-gray p-1">
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
        if (resultBox) {
            resultBox.hidden = true;
        }
        if (resultContent) {
            resultContent.textContent = "";
        }
    } finally {
        submitBtn.disabled = false;
        if (submitBtnLabel) {
            submitBtnLabel.textContent = "Calcular mi carta";
        } else {
            submitBtn.textContent = "Calcular mi carta";
        }
    }
});
