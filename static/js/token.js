// placeholder public key, to be fetched from backend
const RSA_N = BigInt("9516311845790656153499716760847001433441357"); 
const RSA_E = 65537n;


function bytesToBigInt(bytes) {
    return BigInt(
        "0x" +
        Array.from(bytes)
            .map(b => b.toString(16).padStart(2, "0"))
            .join("")
    );
}

function modPow(base, exponent, modulus) {  // returns base^exponent % modulus
    let result = 1n;
    base %= modulus;

    while (exponent > 0n) {
        if (exponent % 2n === 1n) {
            result = (result * base) % modulus;
        }

        exponent >>= 1n;
        base = (base * base) % modulus;
    }

    return result;
}

function gcd(a, b) {  
    while (b !== 0n) {
        const temp = b;
        b = a % b;
        a = temp;
    }

    return a;
}

function generateBlindingFactor(n) {
    let r;

    do {
        const bytes = new Uint8Array(32);
        crypto.getRandomValues(bytes);
        r = bytesToBigInt(bytes);
    } while (gcd(r, n) !== 1n);

    return r;
}

function modInverse(a, m) {   // considering a * x ≡ 1 (mod m), this computes x
    let m0 = m;
    let y = 0n;
    let x = 1n;

    if (m === 1n) return 0n;

    while (a > 1n) {
        const q = a / m;

        let t = m;
        m = a % m;
        a = t;

        t = y;
        y = x - q * y;
        x = t;
    }

    if (x < 0n) x += m0;

    return x;
}

async function getUnblindedCredential(token) {
    /* begin token blinding */
    const encoder = new TextEncoder();
    const tokenBytes = encoder.encode(token);
    const tokenInt = bytesToBigInt(tokenBytes);

    const r = generateBlindingFactor(RSA_N);

    // blind the token
    const blindedToken = (tokenInt * modPow(r, RSA_E, RSA_N)) % RSA_N;

    // send blinded token for signing, should receive signed, blinded signature
    const response = await fetch("/blind-sign", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            blinded_token: blindedToken.toString()
        })
    }); const data = await response.json();

    const blindedSignature = BigInt(data.blinded_signature);

    // unblind the signature
    const rInverse = modInverse(r, RSA_N);
    const unblindedSignature = (blindedSignature * rInverse) % RSA_N;

    // combine token and signature
    const credential = `${token}.${unblindedSignature.toString()}`;

    return credential
}


document.addEventListener("DOMContentLoaded", () => {
    const tokenCard = document.getElementById("tokenCard");
    const tokenResultView = document.getElementById("tokenResultView");

    const generateBtn = document.getElementById("generateTokenBtn");
    const generationView = document.getElementById("generationView");
    const generatedToken = document.getElementById("generatedToken");

    const copyBtn = document.getElementById("copyTokenBtn");
    const copyStatus = document.getElementById("copyStatus");

    generateBtn.addEventListener("click", async () => {
        generateBtn.disabled = true;
        generateBtn.innerText = "Generating...";

        const randomBytes = new Uint8Array(32);  // define 32 bit size

        crypto.getRandomValues(randomBytes);

        const token = btoa(String.fromCharCode(...randomBytes))  // need regex for non-fatal transmission
            .replace(/\+/g, "-")   // replace + 
            .replace(/\//g, "_")   // replace /
            .replace(/=+$/, "");   // replace trailing ='s at end

        // use raw token to get unblinded, signed credential
        const credential = await getUnblindedCredential(token); console.log(credential);

        /* Animation phase */
        generationView.classList.add("slide-up");

        setTimeout(() => {
            generationView.style.display = "none";

            tokenResultView.classList.remove("hidden");
            tokenResultView.classList.add("fade-in");

            generatedToken.innerText = credential;
            tokenCard.classList.add("token-generated");
        }, 500);

        // console.log("Generated token:", token);
    });

    copyBtn.addEventListener("click", async () => {
        const token = generatedToken.innerText;

        await navigator.clipboard.writeText(token);
        copyBtn.innerText = "Copied to clipboard!";
        copyBtn.classList.add("copy-success-btn");

        setTimeout(() => {
            copyBtn.innerText = "Copy token";
            copyBtn.classList.remove("copy-success-btn");
        }, 2200);
    });

    continueBtn.addEventListener("click", () => {
        const confirmed = confirm(
            "WARNING:\n\nYou may only register for one anonymous token per election.\n\n" +
            "Ensure that you have securely stored your token before continuing."
        );
        if (confirmed) window.location.href = "/";

    });
});

