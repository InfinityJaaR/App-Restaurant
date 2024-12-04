document.addEventListener('DOMContentLoaded', function () {
    const botonesDetalles = document.querySelectorAll('.boton-detalles');
    const botonesMarcarPendiente = document.querySelectorAll('.boton-marcar-pendiente');

    // Mostrar detalles del pedido
    botonesDetalles.forEach(boton => {
        boton.addEventListener('click', function () {
            const pedidoId = this.dataset.pedidoId;
            fetch(`/lineas_pedido/${pedidoId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const detallesDiv = document.getElementById(`detalles-${pedidoId}`);
                        detallesDiv.innerHTML = data.lineas.map(linea => `
                            <div class="flex justify-between border p-2 mb-2">
                                <span>${linea.platillo}</span>
                                <span>Cantidad: ${linea.cantidad}</span>
                            </div>
                        `).join('');
                        detallesDiv.classList.remove('hidden');
                    } else {
                        alert('Error al cargar detalles del pedido.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });

    // Marcar pedido como pendiente
    botonesMarcarPendiente.forEach(boton => {
        boton.addEventListener('click', function () {
            const pedidoId = this.dataset.pedidoId;
            fetch('/cambiar_estado/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ pedido_id: pedidoId, nuevo_estado: 'Pendiente' })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Pedido marcado como pendiente.');
                        location.reload();
                    } else {
                        alert('Error al marcar como pendiente.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});
