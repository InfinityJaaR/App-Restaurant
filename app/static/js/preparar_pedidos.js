document.addEventListener('DOMContentLoaded', function () {
    const serverMessages = document.getElementById('server-messages');

    // Función para mostrar mensajes dinámicos
    function mostrarMensaje(tipo, mensaje) {
        const div = document.createElement('div');
        div.className = `p-4 rounded-lg shadow-md bg-${tipo}-200 border-l-4 border-${tipo}-500 text-${tipo}-800 mb-4`;
        div.textContent = mensaje;
        serverMessages.appendChild(div);

        setTimeout(() => div.remove(), 5000); // Eliminar el mensaje después de 5 segundos
    }

    // Manejar el envío del formulario "Marcar como Pendiente"
    const forms = document.querySelectorAll('.form-marcar-pendiente');

    forms.forEach(form => {
        form.addEventListener('submit', async function (event) {
            event.preventDefault(); // Prevenir el envío estándar del formulario

            const formData = new FormData(form);
            const csrfToken = formData.get('csrfmiddlewaretoken');
            const pedidoId = formData.get('pedido_id');

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                    },
                    body: formData,
                });

                if (response.ok) {
                    const data = await response.json();

                    // Mostrar el mensaje dinámico basado en la respuesta
                    const tipoMensaje = data.success ? 'green' : 'red';
                    mostrarMensaje(tipoMensaje, data.message);

                    // Eliminar la fila de la tabla si el pedido se ha actualizado correctamente
                    if (data.success) {
                        const row = document.querySelector(`tr[data-pedido-id="${pedidoId}"]`);
                        if (row) {
                            row.remove();
                        }
                    }
                } else {
                    mostrarMensaje('red', 'Error al procesar la solicitud.');
                }
            } catch (error) {
                // Mostrar mensaje de error en caso de fallo
                mostrarMensaje('red', 'Error al procesar la solicitud. Intenta nuevamente.');
                console.error('Error:', error);
            }
        });
    });
});
