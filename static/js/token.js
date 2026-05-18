
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

        /* Animation phase */

        generationView.classList.add("slide-up");

        setTimeout(() => {
            generationView.style.display = "none";

            tokenResultView.classList.remove("hidden");
            tokenResultView.classList.add("fade-in");

            generatedToken.innerText = token;
            tokenCard.classList.add("token-generated");
        }, 500);

        // console.log("Generated token:", token);

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
});

