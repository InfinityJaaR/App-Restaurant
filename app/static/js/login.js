document.getElementById('signup-link').addEventListener('click', function(e) {
    e.preventDefault();
    document.querySelector('.container').classList.add('active');
});

document.getElementById('login-link').addEventListener('click', function(e) {
    e.preventDefault();
    document.querySelector('.container').classList.remove('active');
});

document.getElementById('next-phase').addEventListener('click', function() {
    document.querySelector('.signup-phase-1').classList.add('inactive');
    document.querySelector('.signup-phase-2').classList.add('active');
});

document.getElementById('prev-phase').addEventListener('click', function() {
    document.querySelector('.signup-phase-1').classList.remove('inactive');
    document.querySelector('.signup-phase-2').classList.remove('active');
});

document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.querySelector('input[name="phone"]');
    const phoneMask = IMask(phoneInput, {
        mask: '0000-0000',
        lazy: true,  // Cambiar a true para que no muestre la máscara inicialmente
    });

    document.getElementById('signup-form').addEventListener('submit', function(e) {
        // Validación del teléfono
        if (!phoneMask.masked.isComplete) {
            e.preventDefault();
            alert('Por favor ingrese un número de teléfono válido de 8 dígitos');
            return;
        }

        // Validación del email
        const email = document.querySelector('input[name="email"]').value;
        if (!email.includes('@') || !email.includes('.com')) {
            e.preventDefault();
            alert('El email debe contener @ y .com');
            return;
        }

        // Validación de contraseñas
        const passwords = document.querySelectorAll('.signup-phase-2 input[type="password"]');
        if (passwords[0].value !== passwords[1].value) {
            e.preventDefault();
            alert('Las contraseñas no coinciden');
            return;
        }
    });
});