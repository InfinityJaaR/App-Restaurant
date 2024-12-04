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
                        location.reload();
                    } else if (data.error === 'no_repartidores') {
                        alert('No hay repartidores disponibles. El pedido permanecerá pendiente.');
                    } else {
                        alert('Error al asignar el pedido.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});
