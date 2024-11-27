function filterTable() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const selectedGroup = document.getElementById('groupFilter').value.toLowerCase();
    const rows = document.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const groupCell = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
        
        const matchesSearch = text.includes(searchText);
        const matchesGroup = selectedGroup === '' || groupCell === selectedGroup;
        
        row.style.display = matchesSearch && matchesGroup ? '' : 'none';
    });
}

document.getElementById('searchInput').addEventListener('keyup', filterTable);
document.getElementById('groupFilter').addEventListener('change', filterTable);

const rowsPerPage = 7;
let currentPage = 1;

function showPage(page) {
    const rows = document.querySelectorAll('tbody tr:not([style*="display: none"])');
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    rows.forEach((row, index) => {
        row.classList.toggle('hidden', index < start || index >= end);
    });

    updatePagination(rows.length);
}

function updatePagination(totalRows) {
    const totalPages = Math.max(1, Math.ceil(totalRows / rowsPerPage)); // Asegura mínimo 1 página
    const paginationContainer = document.querySelector('.pagination');
    paginationContainer.innerHTML = '';

    // Botón anterior
    const prevButton = createPaginationButton('&laquo;', currentPage > 1);
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    });
    paginationContainer.appendChild(prevButton);

    // Números de página
    for (let i = 1; i <= totalPages; i++) {
        const pageButton = createPaginationButton(i, true);
        if (i === currentPage) pageButton.classList.add('active');
        pageButton.addEventListener('click', () => {
            currentPage = i;
            showPage(currentPage);
        });
        paginationContainer.appendChild(pageButton);
    }

    // Botón siguiente
    const nextButton = createPaginationButton('&raquo;', currentPage < totalPages);
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    });
    paginationContainer.appendChild(nextButton);
}

function createPaginationButton(text, enabled) {
    const button = document.createElement('button');
    button.className = `pagination-btn ${!enabled ? 'disabled' : ''}`;
    button.innerHTML = text;
    if (!enabled) button.disabled = true;
    return button;
}

const originalFilterTable = filterTable;
filterTable = function() {
    originalFilterTable();
    currentPage = 1;
    showPage(currentPage);
};

// Inicializar paginación
document.addEventListener('DOMContentLoaded', () => {
    showPage(currentPage);
});