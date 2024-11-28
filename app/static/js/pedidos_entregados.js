document.addEventListener('DOMContentLoaded', function () {
    const filasPorPagina = 5;
    const cuerpoTabla = document.getElementById('pedidos-entregados-body');
    const contenedorPaginacion = document.getElementById('pagination-container');
    const filas = Array.from(cuerpoTabla.getElementsByTagName('tr'));
    const totalPaginas = Math.ceil(filas.length / filasPorPagina);

    function mostrarPagina(pagina) {
        cuerpoTabla.innerHTML = '';
        const inicio = (pagina - 1) * filasPorPagina;
        const fin = inicio + filasPorPagina;
        const filasPagina = filas.slice(inicio, fin);
        filasPagina.forEach(fila => cuerpoTabla.appendChild(fila));
    }

    function crearControlesPaginacion() {
        contenedorPaginacion.innerHTML = '';

        // Botón de página anterior
        const enlaceAnterior = document.createElement('a');
        enlaceAnterior.href = '#';
        enlaceAnterior.innerHTML = '&laquo;';
        enlaceAnterior.classList.add('page-link', 'page-arrow');
        enlaceAnterior.addEventListener('click', function (e) {
            e.preventDefault();
            const paginaActiva = document.querySelector('.page-link.active');
            const paginaActual = parseInt(paginaActiva.textContent);
            if (paginaActual > 1) {
                mostrarPagina(paginaActual - 1);
                actualizarPaginaActiva(paginaActual - 1);
            }
        });
        contenedorPaginacion.appendChild(enlaceAnterior);

        // Botones de número de página
        for (let i = 1; i <= totalPaginas; i++) {
            const enlacePagina = document.createElement('a');
            enlacePagina.href = '#';
            enlacePagina.textContent = i;
            enlacePagina.classList.add('page-link');
            enlacePagina.addEventListener('click', function (e) {
                e.preventDefault();
                mostrarPagina(i);
                actualizarPaginaActiva(i);
            });
            contenedorPaginacion.appendChild(enlacePagina);
        }

        // Botón de página siguiente
        const enlaceSiguiente = document.createElement('a');
        enlaceSiguiente.href = '#';
        enlaceSiguiente.innerHTML = '&raquo;';
        enlaceSiguiente.classList.add('page-link', 'page-arrow');
        enlaceSiguiente.addEventListener('click', function (e) {
            e.preventDefault();
            const paginaActiva = document.querySelector('.page-link.active');
            const paginaActual = parseInt(paginaActiva.textContent);
            if (paginaActual < totalPaginas) {
                mostrarPagina(paginaActual + 1);
                actualizarPaginaActiva(paginaActual + 1);
            }
        });
        contenedorPaginacion.appendChild(enlaceSiguiente);

        if (totalPaginas === 0) {
            const enlacePagina = document.createElement('a');
            enlacePagina.href = '#';
            enlacePagina.textContent = 1;
            enlacePagina.classList.add('page-link', 'active');
            contenedorPaginacion.appendChild(enlacePagina);
        }
    }

    function actualizarPaginaActiva(paginaActiva) {
        const enlacesPagina = contenedorPaginacion.getElementsByClassName('page-link');
        Array.from(enlacesPagina).forEach(enlace => {
            enlace.classList.remove('active', 'btn-primary');
            enlace.classList.add('btn-secondary');
            if (parseInt(enlace.textContent) === paginaActiva) {
                enlace.classList.add('active', 'btn-primary');
                enlace.classList.remove('btn-secondary');
            }
        });
    }

    if (filas.length > 0) {
        mostrarPagina(1);
        crearControlesPaginacion();
        actualizarPaginaActiva(1);
    } else {
        crearControlesPaginacion();
    }
});
