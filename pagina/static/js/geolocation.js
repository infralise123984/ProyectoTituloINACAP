// pagina/static/js/geolocation.js

// Variable para almacenar las coordenadas obtenidas
let latitudActual = null;
let longitudActual = null;

// Esta función es llamada desde form_steps.js cuando se entra al paso 5
// function actualizarConfirmacion() {
//     const gpsElement = document.getElementById('ubicacion-gps'); // Este elemento ya no existe en el HTML
//     const horaElement = document.getElementById('hora-envio'); // Este elemento ya no existe en el HTML
//
//     // Actualiza la hora
//     const ahora = new Date();
//     horaElement.textContent = ahora.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
//
//     // Intenta obtener la ubicación si no se ha obtenido aún
//     if (latitudActual === null || longitudActual === null) {
//         gpsElement.textContent = 'Detectando...';
//         obtenerUbicacionGPS();
//     } else {
//         // Si ya la tiene, actualiza el span
//         gpsElement.textContent = `${latitudActual.toFixed(4)}, ${longitudActual.toFixed(4)} (autodetectada)`;
//     }
// }

function obtenerUbicacionGPS() {
    const gpsElement = document.getElementById('resumen-ubicacion'); // Actualizamos el span correcto

    if (!navigator.geolocation) {
        gpsElement.textContent = 'No soportada en este dispositivo.';
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            // Guarda las coordenadas
            latitudActual = position.coords.latitude;
            longitudActual = position.coords.longitude;

            // Actualiza el span de la UI (ahora en el resumen)
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

// Nota: La función actualizarConfirmacion ya no se llama desde form_steps.js
// La lógica de obtener ubicación y hora se maneja ahora en mostrarResumen y geolocation.js