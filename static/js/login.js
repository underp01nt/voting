const credential = document.getElementById('credential');
const toggleBtn = document.getElementById('toggleToken');
const eyeIcon = document.getElementById('eyeIcon');
const submitBtn = document.getElementById('submitBtn');

// QR options 
const uploadQrBtn = document.getElementById("uploadQrBtn");
const scanQrBtn = document.getElementById("scanQrBtn");
const qrFileInput = document.getElementById("qrFileInput");

const sleep = ms => new Promise(r => setTimeout(r, ms));
WAIT_TIME_MS = 1000;

async function authenticateCredential(credentialString) {
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
        submitBtn.disabled = false;
    }
}

/* LISTENERS */

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

uploadQrBtn.addEventListener("click", () => {
    qrFileInput.click();
});

scanQrBtn.addEventListener("click", () => {
    alert("not yet implemented");
    // implement this maybe?
});

submitBtn.addEventListener('click', async () => {
    submitBtn.disabled = true;
    await new Promise(r => setTimeout(r, WAIT_TIME_MS));
    await authenticateCredential(credential.value.trim());
})

qrFileInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    const image = new Image();

    image.onload = async () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        canvas.width = image.width;
        canvas.height = image.height;

        ctx.drawImage(image, 0, 0);

        // get the image data and decode into string
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const qr = jsQR(imageData.data, imageData.width, imageData.height);

        if (!qr) { alert("No QR code detected."); return; }

        const credentialString = qr.data.trim();
        credential.value = credentialString;

        submitBtn.disabled = true;
        await new Promise(r => setTimeout(r, WAIT_TIME_MS));
        
        await authenticateCredential(credentialString);
    };

    image.src = URL.createObjectURL(file);
});
