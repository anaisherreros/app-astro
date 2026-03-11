const form = document.getElementById("chart-form");
const submitBtn = document.getElementById("submit-btn");
const resultBox = document.getElementById("result");
const resultContent = document.getElementById("result-content");

function setError(id, message) {
    const el = document.getElementById("error_" + id);
    if (el) {
        el.textContent = message || "";
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    setError("birth_date", "");
    setError("birth_time", "");
    setError("birth_place", "");

    const birthDate = document.getElementById("birth_date").value;
    const birthTime = document.getElementById("birth_time").value;
    const birthPlace = document.getElementById("birth_place").value.trim();

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

