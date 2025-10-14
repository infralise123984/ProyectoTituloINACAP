// pagina/static/pagina/js/geolocation.js

// Variable para almacenar las coordenadas obtenidas
let latitudActual = null;
let longitudActual = null;

// Esta función es llamada desde form_steps.js cuando se entra al paso 5
function actualizarConfirmacion() {
    const gpsElement = document.getElementById('ubicacion-gps');
    const horaElement = document.getElementById('hora-envio');

    // Actualiza la hora
    const ahora = new Date();
    horaElement.textContent = ahora.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });

    // Intenta obtener la ubicación si no se ha obtenido aún
    if (latitudActual === null || longitudActual === null) {
        gpsElement.textContent = 'Detectando...';
        obtenerUbicacionGPS();
    } else {
        // Si ya la tiene, actualiza el span
        gpsElement.textContent = `${latitudActual.toFixed(4)}, ${longitudActual.toFixed(4)} (autodetectada)`;
    }
}

function obtenerUbicacionGPS() {
    const gpsElement = document.getElementById('ubicacion-gps');

    if (!navigator.geolocation) {
        gpsElement.textContent = 'No soportada en este dispositivo.';
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            // Guarda las coordenadas
            latitudActual = position.coords.latitude;
            longitudActual = position.coords.longitude;

            // Actualiza el span de la UI
            gpsElement.textContent = `${latitudActual.toFixed(4)}, ${longitudActual.toFixed(4)} (autodetectada)`;

            // Actualiza los campos ocultos del formulario
            document.getElementById('latitud').value = latitudActual.toFixed(6);
            document.getElementById('longitud').value = longitudActual.toFixed(6);
        },
        (error) => {
            let msg = "No disponible";
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    msg = "Permiso denegado";
                    break;
                case error.POSITION_UNAVAILABLE:
                    msg = "No disponible";
                    break;
                case error.TIMEOUT:
                    msg = "Tiempo agotado";
                    break;
            }
            gpsElement.textContent = msg;
            // IMPORTANTE: Si falla, los campos ocultos estarán vacíos o con valores anteriores
            // Debes manejar esto en la vista de Django si es crítico
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000 // 1 minuto
        }
    );
}

// Nota: Esta función DEBE ser global para que form_steps.js la pueda llamar.
// Por eso no está dentro de un bloque como document.addEventListener('DOMContentLoaded', ...).
// Asegúrate de que form_steps.js se cargue antes que geolocation.js en tu HTML.