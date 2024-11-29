document.addEventListener('DOMContentLoaded', function () {
    const platillosList = document.getElementById('platillos-list');
    const resumenPedidoList = document.getElementById('resumen-pedido-list');
    const pedidoTotalElement = document.getElementById('pedido-total');
    let pedido = [];

    // Mock data para platillos (reemplazar con una llamada AJAX al servidor para obtener los platillos reales)
    const platillos = [
        { id: 1, nombre: 'Platillo 1', precio: 5.0 },
        { id: 2, nombre: 'Platillo 2', precio: 7.5 },
        { id: 3, nombre: 'Platillo 3', precio: 10.0 },
    ];

    // Renderizar lista de platillos
    platillos.forEach(platillo => {
        const row = document.createElement('tr');
        row.classList.add('border-b');
        row.innerHTML = `
            <td class="border px-4 py-2">${platillo.nombre}</td>
            <td class="border px-4 py-2">$${platillo.precio.toFixed(2)}</td>
            <td class="border px-4 py-2">
                <input type="number" id="cantidad-${platillo.id}" class="w-full border rounded p-2" min="1" value="1">
            </td>
            <td class="border px-4 py-2">
                <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onclick="agregarPlatillo(${platillo.id})">Agregar</button>
            </td>
        `;
        platillosList.appendChild(row);
    });

    // Función para agregar un platillo al pedido
    window.agregarPlatillo = function (platilloId) {
        const platillo = platillos.find(p => p.id === platilloId);
        const cantidadInput = document.getElementById(`cantidad-${platilloId}`);
        const cantidad = parseInt(cantidadInput.value);

        if (cantidad > 0) {
            const existente = pedido.find(p => p.id === platilloId);
            if (existente) {
                existente.cantidad += cantidad;
            } else {
                pedido.push({ ...platillo, cantidad });
            }
            actualizarResumenPedido();
        }
    };

    // Función para actualizar el resumen del pedido
    function actualizarResumenPedido() {
        resumenPedidoList.innerHTML = '';
        let total = 0;

        pedido.forEach(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;

            const row = document.createElement('tr');
            row.classList.add('border-b');
            row.innerHTML = `
                <td class="border px-4 py-2">${item.nombre}</td>
                <td class="border px-4 py-2">${item.cantidad}</td>
                <td class="border px-4 py-2">$${subtotal.toFixed(2)}</td>
            `;
            resumenPedidoList.appendChild(row);
        });

        pedidoTotalElement.textContent = total.toFixed(2);
    }

    // Evento para guardar el pedido
    document.getElementById('guardar-pedido').addEventListener('click', function () {
        const clienteForm = document.getElementById('cliente-form');
        const formData = new FormData(clienteForm);
        const cliente = {
            nombre: formData.get('nombre'),
            telefono: formData.get('telefono'),
            ubicacion: formData.get('ubicacion'),
            correo: formData.get('correo')
        };

        if (cliente.nombre && cliente.telefono && cliente.ubicacion) {
            // Mock guardar pedido (reemplazar con una llamada AJAX para guardar en la base de datos)
            console.log('Cliente:', cliente);
            console.log('Pedido:', pedido);
            Swal.fire({
                title: 'Pedido Guardado',
                text: 'Pedido guardado exitosamente.',
                icon: 'success',
                confirmButtonText: 'Aceptar'
            });
        } else {
            Swal.fire({
                title: 'Campos Incompletos',
                text: 'Por favor complete todos los campos del cliente.',
                icon: 'warning',
                confirmButtonText: 'Aceptar'
            });
        }
    });
});
