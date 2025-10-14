const totalSteps = 5;
let currentStep = 1;

function updateProgress() {
    const percent = (currentStep / totalSteps) * 100;
    document.getElementById('progress-bar').style.width = percent + '%';
}

function showStep(stepId) {
    document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
    document.getElementById('step' + stepId).style.display = 'block';

    // Si es el paso 5, se llama a la función de geolocalización (debe estar definida en el otro archivo)
    if (stepId === 5) {
        actualizarConfirmacion(); // Esta función la definiremos en el archivo de geolocalización
    }
}

function nextStep(from, to) {
    // Si vamos del paso 4 al 5, guardamos la unidad destino
    if (from === 4 && to === 5) {
        const unidadSelect = document.querySelector('select[name="unidad_destino_form"]');
        const unidadValue = unidadSelect.value;
        const unidadText = unidadSelect.options[unidadSelect.selectedIndex]?.text || 'No seleccionada';
        document.getElementById('confirm-destino').textContent = unidadText;
        document.getElementById('unidad_destino').value = unidadValue;
    }

    showStep(to);
    currentStep = to;
    updateProgress();
}

function prevStep(from, to) {
    showStep(to);
    currentStep = to;
    updateProgress();
}

// Iniciar en el paso 1 al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    showStep(1);
});