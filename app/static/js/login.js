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

document.getElementById('signup-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const passwords = document.querySelectorAll('.signup-phase-2 input[type="password"]');
    if (passwords[0].value !== passwords[1].value) {
        alert('Las contraseñas no coinciden');
        return;
    }
    // Aquí puedes agregar el código para enviar el formulario
});