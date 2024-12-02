document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profileForm');
    const inputs = form.querySelectorAll('input');
    const btnEdit = document.getElementById('btnEdit');
    const updateActions = document.querySelector('.update-actions');
    const btnCancel = document.querySelector('.btn-cancel');
    
    // Almacenar valores originales
    let originalValues = {};
    inputs.forEach(input => {
        originalValues[input.name] = input.value;
    });

    // Función para cambiar a modo edición
    btnEdit.addEventListener('click', function() {
        inputs.forEach(input => input.removeAttribute('readonly'));
        btnEdit.style.display = 'none';
        updateActions.style.display = 'flex';
    });

    // Función para cancelar edición
    btnCancel.addEventListener('click', function() {
        // Restaurar valores originales
        inputs.forEach(input => {
            input.value = originalValues[input.name];
            input.setAttribute('readonly', true);
        });
        
        // Restaurar estado de los botones
        updateActions.style.display = 'none';
        btnEdit.style.display = 'inline-block'; // Cambiado de 'block' a 'inline-block'
    });

    // Manejar el envío del formulario
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        this.submit();
    });
});
