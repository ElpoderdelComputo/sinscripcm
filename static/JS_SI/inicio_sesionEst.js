const btnTogglePassword = document.querySelector('.btn-toggle-password');
const inputPassword = document.querySelector('#password');

btnTogglePassword.addEventListener('click', function() {
    if (inputPassword.type === 'password') {
        inputPassword.type = 'text';
        btnTogglePassword.innerHTML = '<i class="far fa-eye"></i>';
    } else {
        inputPassword.type = 'password';
        btnTogglePassword.innerHTML = '<i class="far fa-eye-slash"></i>';
    }
});