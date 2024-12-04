document.addEventListener('DOMContentLoaded', function () {
    const resumenPedidoList = document.getElementById('resumen-pedido-list');
    const pedidoTotalElement = document.getElementById('pedido-total');
    const jsMessages = document.getElementById('js-messages');
    let pedido = [];

    function mostrarMensajeJS(tipo, mensaje) {
        jsMessages.innerHTML = `<div class="bg-${tipo}-500 text-white font-bold p-4 rounded mb-4">${mensaje}</div>`;
        setTimeout(() => (jsMessages.innerHTML = ''), 3000);
    }

    window.agregarPlatillo = function (platilloId) {
        const cantidadInput = document.getElementById(`cantidad-${platilloId}`);
        const disponibleElement = document.getElementById(`disponible-${platilloId}`);
        const cantidadDisponible = parseInt(disponibleElement.innerText);
        const cantidad = parseInt(cantidadInput.value);

        if (cantidad > cantidadDisponible || cantidad <= 0) {
            Swal.fire({
                title: 'Cantidad no válida',
                text: `Por favor, elija un valor entre 1 y ${cantidadDisponible}.`,
                icon: 'warning',
                confirmButtonText: 'Aceptar'
            });
            return;
        }

        const nombrePlatillo = document.querySelector(`#platillo-row-${platilloId} td:nth-child(1)`).innerText;
        const precioPlatillo = parseFloat(document.querySelector(`#platillo-row-${platilloId} td:nth-child(2)`).innerText.replace('$', '').trim());

        disponibleElement.innerText = cantidadDisponible - cantidad;

        const existente = pedido.find(p => p.id === platilloId);
        if (existente) {
            existente.cantidad += cantidad;
        } else {
            pedido.push({ id: platilloId, nombre: nombrePlatillo, precio: precioPlatillo, cantidad });
        }

        actualizarResumenPedido();
    };

    function actualizarResumenPedido() {
        resumenPedidoList.innerHTML = '';
        let total = 0;

        pedido.forEach((item, index) => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;

            const row = document.createElement('tr');
            row.classList.add('border-b');
            row.innerHTML = `
                <td class="border px-4 py-2">${item.nombre}</td>
                <td class="border px-4 py-2">
                    <button class="bg-gray-300 hover:bg-gray-500 text-black font-bold px-2 rounded disminuir" data-index="${index}">-</button>
                    ${item.cantidad}
                    <button class="bg-gray-300 hover:bg-gray-500 text-black font-bold px-2 rounded aumentar" data-index="${index}">+</button>
                </td>
                <td class="border px-4 py-2">$${subtotal.toFixed(2)}</td>
                <td class="border px-4 py-2">
                    <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded eliminar" data-index="${index}">Eliminar</button>
                </td>
            `;
            resumenPedidoList.appendChild(row);
        });

        pedidoTotalElement.textContent = total.toFixed(2);

        document.querySelectorAll('.disminuir').forEach(button => {
            button.addEventListener('click', function () {
                disminuirCantidad(parseInt(this.dataset.index));
            });
        });

        document.querySelectorAll('.aumentar').forEach(button => {
            button.addEventListener('click', function () {
                aumentarCantidad(parseInt(this.dataset.index));
            });
        });

        document.querySelectorAll('.eliminar').forEach(button => {
            button.addEventListener('click', function () {
                eliminarPlatillo(parseInt(this.dataset.index));
            });
        });
    }

    function disminuirCantidad(index) {
        const item = pedido[index];
        if (item.cantidad > 1) {
            item.cantidad--;
            const disponibleElement = document.getElementById(`disponible-${item.id}`);
            disponibleElement.innerText = parseInt(disponibleElement.innerText) + 1;
            actualizarResumenPedido();
        }
    }

    function aumentarCantidad(index) {
        const item = pedido[index];
        const disponibleElement = document.getElementById(`disponible-${item.id}`);
        const cantidadDisponible = parseInt(disponibleElement.innerText);

        if (cantidadDisponible > 0) {
            item.cantidad++;
            disponibleElement.innerText = cantidadDisponible - 1;
            actualizarResumenPedido();
        } else {
            Swal.fire({
                title: 'Cantidad no disponible',
                text: 'No hay más unidades disponibles.',
                icon: 'warning',
                confirmButtonText: 'Aceptar'
            });
        }
    }

    function eliminarPlatillo(index) {
        const item = pedido[index];
        const disponibleElement = document.getElementById(`disponible-${item.id}`);
        disponibleElement.innerText = parseInt(disponibleElement.innerText) + item.cantidad;

        pedido.splice(index, 1);
        actualizarResumenPedido();
    }

    document.getElementById('guardar-pedido').addEventListener('click', function () {
        const nombre = document.getElementById('nombre').value;
        const telefono = document.getElementById('telefono').value;
        const ubicacion = document.getElementById('ubicacion').value;
        const correo = document.getElementById('correo').value;
        const tipo_pago = document.getElementById('tipo_pago').value;

        if (!nombre || !telefono || !ubicacion) {
            mostrarMensajeJS('red', 'Por favor complete todos los campos del cliente.');
            return;
        }

        if (pedido.length === 0) {
            mostrarMensajeJS('red', 'Por favor agregue al menos un platillo al pedido.');
            return;
        }

        fetch('/app/registro_pedidos_no_registrados/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                nombre,
                telefono,
                ubicacion,
                correo,
                tipo_pago,
                platillos: pedido.map(item => ({ id: item.id, cantidad: item.cantidad }))
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                Swal.fire('Éxito', data.message, 'success');
                document.getElementById('cliente-form').reset();
                resumenPedidoList.innerHTML = '';
                pedidoTotalElement.textContent = '0.00';
                pedido = [];
                document.querySelectorAll('[id^="disponible-"]').forEach(element => {
                    const originalCantidad = element.getAttribute('data-original-cantidad');
                    element.innerText = originalCantidad;
                });
            } else {
                Swal.fire('Error', data.error, 'error');
            }
        })
        .catch(error => {
            mostrarMensajeJS('red', 'Error al registrar el pedido. Intente nuevamente.');
            console.error('Error:', error);
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.querySelectorAll('[id^="disponible-"]').forEach(element => {
        element.setAttribute('data-original-cantidad', element.innerText);
    });
});
