// pagina/static/pagina/js/form_steps.js

const totalSteps = 5;
let currentStep = 1;

function updateProgress() {
    const percent = (currentStep / totalSteps) * 100;
    document.getElementById('progress-bar').style.width = percent + '%';
}

function showStep(stepId) {
    document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
    document.getElementById('step' + stepId).style.display = 'block';

    if (stepId === 5) {
        // Llama a la función para mostrar resumen (incluye GPS, unidad y hora)
        mostrarResumen();
    }
}

function nextStep(from, to) {
    // Selecciona el contenedor del paso actual (por ejemplo, #step1)
    const currentStepElement = document.getElementById(`step${from}`);

    // Busca dentro de ese contenedor todos los elementos con el atributo 'required'
    const requiredFields = currentStepElement.querySelectorAll('[required]');

    // Verifica si hay campos requeridos vacíos
    let allFilled = true;
    for (let field of requiredFields) {
        // El campo select también se valida correctamente con .value
        if (!field.value.trim()) { // .trim() elimina espacios en blanco al inicio y final
            allFilled = false;
            break; // Si encontramos uno vacío, ya no es necesario seguir comprobando
        }
    }

    // Si hay campos vacíos, no avanzamos
    if (!allFilled) {
        // Reemplazamos alert por SweetAlert2
        Swal.fire({
            icon: 'warning',
            title: 'Campos incompletos',
            text: 'Por favor, complete todos los campos obligatorios antes de continuar.',
            confirmButtonText: 'Aceptar',
        });
        return; // Salimos de la función sin avanzar
    }

    // Si vamos del paso 4 al 5, guardamos la unidad destino en el hidden input
    // La obtención del texto de la unidad destino se hará en mostrarResumen
    if (from === 4 && to === 5) {
        const unidadSelect = document.querySelector('select[name="unidad_destino_form"]');
        const unidadValue = unidadSelect.value;
        // const unidadText = unidadSelect.options[unidadSelect.selectedIndex]?.text || 'No seleccionada';
        document.getElementById('unidad_destino').value = unidadValue;
        // window.unidadDestinoSeleccionada = unidadText; // Ya no es necesario
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

// Nueva función para mostrar el resumen
function mostrarResumen() {
    // Obtener valores de los campos del formulario
    const motivo = document.querySelector('textarea[name="motivo"]')?.value || '-';
    const sintomas = document.querySelector('textarea[name="sintomas"]')?.value || '-';
    const antecedentes = document.querySelector('textarea[name="antecedentes"]')?.value || '-';
    // Obtener unidad destino *directamente* del select
    const unidadSelect = document.querySelector('select[name="unidad_destino_form"]');
    const unidadDestino = unidadSelect ? unidadSelect.options[unidadSelect.selectedIndex]?.text || '-' : '-';
    // Obtener hora actual
    const ahora = new Date();
    const horaEnvio = ahora.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });

    // Actualizar los elementos del resumen
    document.getElementById('resumen-motivo').textContent = motivo;
    document.getElementById('resumen-sintomas').textContent = sintomas;
    document.getElementById('resumen-antecedentes').textContent = antecedentes;
    document.getElementById('resumen-destino').textContent = unidadDestino; // Ahora debería funcionar
    document.getElementById('resumen-hora').textContent = horaEnvio;

    // Manejar la ubicación GPS
    const ubicacionSpan = document.getElementById('resumen-ubicacion');
    if (typeof latitudActual !== 'undefined' && typeof longitudActual !== 'undefined' && latitudActual !== null && longitudActual !== null) {
        // Si las variables ya existen y tienen valor, mostrarlas
        ubicacionSpan.textContent = `${latitudActual.toFixed(4)}, ${longitudActual.toFixed(4)} (autodetectada)`;
    } else {
        // Si no, mostrar "Detectando..." y llamar a la función de geolocalización
        ubicacionSpan.textContent = 'Detectando...';
        if (typeof obtenerUbicacionGPS === 'function') {
            obtenerUbicacionGPS();
        } else {
            console.error("La función obtenerUbicacionGPS no está definida o geolocation.js no se ha cargado correctamente.");
            ubicacionSpan.textContent = 'Error al obtener ubicación.';
        }
    }
}

// Iniciar en el paso 1 al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    showStep(1);
});