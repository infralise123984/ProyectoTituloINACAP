// pagina/static/pagina/js/form_steps.js

const totalSteps = 6;                    // ← 6 pasos ahora
let currentStep = 1;

function updateProgress() {
    const percent = (currentStep / totalSteps) * 100;
    document.getElementById('progress-bar').style.width = percent + '%';
}

function showStep(stepId) {
    document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
    document.getElementById('step' + stepId).style.display = 'block';

    if (stepId === 6) {                 // ← Resumen en el paso 6
        mostrarResumen();
    }
}

/* --------------------------------------------------------------
   Validación de campos required en el paso actual
   -------------------------------------------------------------- */
function nextStep(from, to) {
    const currentStepEl = document.getElementById(`step${from}`);
    const required = currentStepEl.querySelectorAll('[required]');

    let allFilled = true;
    for (let field of required) {
        if (!field.value.trim()) {
            allFilled = false;
            break;
        }
    }

    if (!allFilled) {
        Swal.fire({
            icon: 'warning',
            title: 'Campos incompletos',
            text: 'Por favor, complete todos los campos obligatorios antes de continuar.',
            confirmButtonText: 'Aceptar',
        });
        return;
    }

    // Paso 5 → 6: copiar el ID de la unidad destino al hidden
    if (from === 5 && to === 6) {
        const selectUnidad = document.querySelector('select[name="unidad_destino"]');
        if (selectUnidad) {
            document.getElementById('unidad_destino').value = selectUnidad.value;
        }
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

/* --------------------------------------------------------------
   RESUMEN (solo muestra lo que el usuario ingresó)
   -------------------------------------------------------------- */
function mostrarResumen() {
    // --- Paciente ------------------------------------------------
    const nombre = document.querySelector('[name="nombre_paciente"]').value.trim();
    const apellido = document.querySelector('[name="apellido_paciente"]').value.trim();
    const paciente = apellido ? `${nombre} ${apellido}` : nombre;
    document.getElementById('resumen-paciente').textContent = paciente || 'No identificado';

    // --- RUT -----------------------------------------------------
    const rut = document.querySelector('[name="rut_paciente"]').value.trim() || 'No informado';
    document.getElementById('resumen-rut').textContent = rut;

    // --- Clínica -------------------------------------------------
    document.getElementById('resumen-motivo').textContent =
        document.querySelector('[name="motivo"]').value.trim() || '-';
    document.getElementById('resumen-sintomas').textContent =
        document.querySelector('[name="sintomas"]').value.trim() || '-';
    document.getElementById('resumen-antecedentes').textContent =
        document.querySelector('[name="antecedentes"]').value.trim() || '-';

    // --- Destino -------------------------------------------------
    const selUnidad = document.querySelector('select[name="unidad_destino"]');
    const destino = selUnidad ? selUnidad.options[selUnidad.selectedIndex]?.text || '-' : '-';
    document.getElementById('resumen-destino').textContent = destino;

    // --- Hora ----------------------------------------------------
    const ahora = new Date();
    document.getElementById('resumen-hora').textContent =
        ahora.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });

    // --- GPS -----------------------------------------------------
    const ubicSpan = document.getElementById('resumen-ubicacion');
    if (latitudActual !== null && longitudActual !== null) {
        ubicSpan.textContent = `${latitudActual.toFixed(4)}, ${longitudActual.toFixed(4)} (autodetectada)`;
    } else {
        ubicSpan.textContent = 'Detectando...';
        if (typeof obtenerUbicacionGPS === 'function') {
            obtenerUbicacionGPS();
        } else {
            console.error('obtenerUbicacionGPS no está definida');
            ubicSpan.textContent = 'Error al obtener ubicación.';
        }
    }
}

/* --------------------------------------------------------------
   Inicialización
   -------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    showStep(1);
    updateProgress();
});