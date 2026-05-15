const tokenInput = document.getElementById('token');
const toggleBtn = document.getElementById('toggleToken');
const eyeIcon = document.getElementById('eyeIcon');

toggleBtn.addEventListener('click', () => {
    if (tokenInput.type === 'password') {
        tokenInput.type = 'text';
        eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><line x1="2" y1="2" x2="23" y2="23"></line>';
    } 
    else { // back to normal eye
        tokenInput.type = 'password';
        eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
    }
});