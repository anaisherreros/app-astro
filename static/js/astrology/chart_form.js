const form = document.getElementById("chart-form");
const submitBtn = document.getElementById("submit-btn");
const resultBox = document.getElementById("result");
const resultContent = document.getElementById("result-content");
const birthPlaceInput = document.getElementById("birth_place");
const suggestionsList = document.getElementById("city-suggestions");
let suggestionsData = [];
let activeSuggestionIndex = -1;
let debounceTimer = null;

function setError(id, message) {
    const el = document.getElementById("error_" + id);
    if (el) {
        el.textContent = message || "";
    }
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
                `<li data-index="${index}" role="option">${item.label}</li>`
        )
        .join("");
    suggestionsList.hidden = false;
}

async function fetchCitySuggestions(query) {
    const response = await fetch(
        `/astrology/cities/suggest/?q=${encodeURIComponent(query)}`
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

birthPlaceInput.addEventListener("input", async () => {
    const query = birthPlaceInput.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < 2) {
        renderSuggestions([]);
        return;
    }

    debounceTimer = setTimeout(async () => {
        const items = await fetchCitySuggestions(query);
        renderSuggestions(items);
    }, 180);
});

birthPlaceInput.addEventListener("keydown", (event) => {
    if (suggestionsList.hidden || !suggestionsData.length) {
        return;
    }

    if (event.key === "ArrowDown") {
        event.preventDefault();
        activeSuggestionIndex =
            (activeSuggestionIndex + 1) % suggestionsData.length;
    } else if (event.key === "ArrowUp") {
        event.preventDefault();
        activeSuggestionIndex =
            (activeSuggestionIndex - 1 + suggestionsData.length) %
            suggestionsData.length;
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
    items.forEach((item) => item.classList.remove("active"));
    if (items[activeSuggestionIndex]) {
        items[activeSuggestionIndex].classList.add("active");
    }
});

suggestionsList.addEventListener("mousedown", (event) => {
    const item = event.target.closest("li");
    if (!item) {
        return;
    }

    const index = Number(item.dataset.index);
    if (Number.isNaN(index)) {
        return;
    }
    applySuggestion(index);
});

document.addEventListener("click", (event) => {
    if (
        !suggestionsList.hidden &&
        !suggestionsList.contains(event.target) &&
        event.target !== birthPlaceInput
    ) {
        renderSuggestions([]);
    }
});

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

        resultBox.hidden = false;
        resultContent.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        resultBox.hidden = false;
        resultContent.textContent = "Error al llamar a la API: " + error;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Calcular carta (mock)";
    }
});

