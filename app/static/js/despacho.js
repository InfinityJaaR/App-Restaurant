document.addEventListener('DOMContentLoaded', function () {
    const pedidosList = document.getElementById('pedidos-list');
    const pedidosProcesoList = document.getElementById('pedidos-proceso-list');
    const repartidoresList = document.getElementById('repartidores-list');

    // Asignar pedido automáticamente
    window.marcarEnProceso = function (pedidoId) {
        fetch('/gestion_pedidos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                pedido_id: pedidoId,
                accion: 'en_proceso'
            })
        }).then(response => {
            if (response.ok) {
                Swal.fire({
                    title: 'Pedido en Proceso',
                    text: `Pedido ${pedidoId} está ahora en proceso.`,
                    icon: 'info',
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    location.reload();
                });
            }
        });
    };

    // Marcar pedido como listo para despacho
    window.marcarListoParaDespacho = function (pedidoId) {
        fetch('/gestion_pedidos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                pedido_id: pedidoId,
                accion: 'listo_para_despacho'
            })
        }).then(response => {
            if (response.ok) {
                Swal.fire({
                    title: 'Pedido Listo para Despacho',
                    text: `Pedido ${pedidoId} se encuentra listo para despacho.`,
                    icon: 'success',
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    location.reload();
                });
            }
        });
    };
});