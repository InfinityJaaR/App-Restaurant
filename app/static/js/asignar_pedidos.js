document.addEventListener('DOMContentLoaded', function () {
    const botonesAsignar = document.querySelectorAll('.boton-asignar');

    // Asignar pedido a repartidor
    botonesAsignar.forEach(boton => {
        boton.addEventListener('click', function () {
            const pedidoId = this.dataset.pedidoId;
            fetch('/asignar_pedido/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ pedido_id: pedidoId })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`Pedido ${pedidoId} asignado correctamente.`);
                        location.reload(); // Refrescar la página
                    } else if (data.error === 'no_repartidores') {
                        mostrarMensaje('red', 'No hay repartidores disponibles. El pedido permanecerá pendiente.');
                    } else {
                        mostrarMensaje('red', 'Error al asignar el pedido.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    mostrarMensaje('red', 'Error en la solicitud. Intenta nuevamente.');
                });
        });
    });

    // Función para mostrar mensajes dinámicos
    function mostrarMensaje(tipo, texto) {
        const messagesContainer = document.querySelector('.messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `p-4 rounded-lg shadow-md bg-${tipo}-200 border-l-4 border-${tipo}-500 transition duration-300 ease-in-out transform hover:scale-105`;
        messageDiv.innerHTML = `<p class="font-semibold text-${tipo}-800">${texto}</p>`;
        messagesContainer.appendChild(messageDiv);

        // Eliminar el mensaje automáticamente después de 3 segundos
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }

    // Ocultar mensajes precargados después de 3 segundos
    setTimeout(() => {
        const precargados = document.querySelectorAll('.messages .p-4');
        precargados.forEach(message => {
            message.remove();
        });
    }, 3000);
});
