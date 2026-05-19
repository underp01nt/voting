const credential = document.getElementById('credential');
const toggleBtn = document.getElementById('toggleToken');
const eyeIcon = document.getElementById('eyeIcon');
const submitBtn = document.getElementById('submitBtn');

toggleBtn.addEventListener('click', () => {
    if (credential.type === 'password') {
        credential.type = 'text';
        eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><line x1="2" y1="2" x2="23" y2="23"></line>';
    } 
    else { // back to normal eye
        credential.type = 'password';
        eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
    }
});

submitBtn.addEventListener('click', async () => {
    const [token, signature] = credential.value.split(".");

    // console.log(token)
    // console.log(signature)

    const res = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            token,
            signature
        })
    });

    const data = await res.json();
    // console.log(data);

    if (res.ok && data.status === "authenticated") {
        window.location.href = data.redirect;  
    } else {
        alert("Invalid credential")
    }
})
