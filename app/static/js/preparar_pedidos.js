document.addEventListener('DOMContentLoaded', function () {
    const serverMessages = document.getElementById('server-messages');

    // Mostrar mensajes dinámicos desde el servidor
    function mostrarMensaje(tipo, mensaje) {
        const div = document.createElement('div');
        div.className = `p-4 rounded-lg shadow-md bg-${tipo}-200 border-l-4 border-${tipo}-500 text-${tipo}-800 mb-4`;
        div.textContent = mensaje;
        serverMessages.appendChild(div);

        setTimeout(() => div.remove(), 5000); // Eliminar el mensaje después de 5 segundos
    }

    // Mostrar mensajes precargados en el DOM (desde Django)
    const mensajesPrecargados = document.querySelectorAll('.server-message');
    mensajesPrecargados.forEach(mensaje => {
        const tipo = mensaje.dataset.tipo || 'blue'; // Tipo de mensaje: green, red, blue
        mostrarMensaje(tipo, mensaje.textContent);
    });
});
