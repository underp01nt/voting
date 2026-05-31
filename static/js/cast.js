// allCandidates + cart are handled by template context
// console.log(electionId)

async function submitBallot(payload) {
    const response = await fetch(`/elections/${electionId}/ballot`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    }); const data = await response.json();

    return data;
}

const submitListBtn = document.getElementById("submitListBtn");
submitListBtn.addEventListener("click", () => {
    const payload = {candidate_ids: cart.map(c => c.candidate_id), round_number: 1};
    
    // reminder: event listener is not async, so need to wrap in own invoked function
    (async () => { 
        const data = await submitBallot(payload); 
        //console.log(data);
    })();

});

function showDropdown() {
    document.getElementById('search-dropdown').style.display = 'block';
    filterCandidates();
}

function hideDropdown() {
    // Delay hide to allow click to register
    document.getElementById('search-dropdown').style.display = 'none';
}

function filterCandidates() {
    const input = document.getElementById('candidate-search');
    const filter = input.value.toUpperCase();
    const dropdown = document.getElementById('search-dropdown');
    
    const filtered = allCandidates.filter(c => 
        c.name.toUpperCase().includes(filter) && 
        cart.every(item => item.candidate_id !== c.candidate_id) // exclude candidates already in list
    );

    dropdown.innerHTML = '';
    if (filtered.length === 0) {
        dropdown.innerHTML = '<div style="padding: 10px; color: #666;">No candidates found</div>';
    } else {
        filtered.forEach(candidate => {
            const div = document.createElement('div');

            div.style.padding = '8px';
            div.style.cursor = 'pointer';
            div.style.borderBottom = '1px solid #eee';
            div.textContent = candidate.name;

            div.onmousedown = () => { // Use onmousedown to fire before onblur
                addToCart(candidate);
                input.value = '';
            };
            div.onmouseover = () => { div.style.background = '#f0f6fa'; };
            div.onmouseout = () => { div.style.background = 'white'; };
            dropdown.appendChild(div);
        });
    }
}

function addToCart(candidate) {
    if (cart.some(c => c.candidate_id === candidate.candidate_id)) return;

    cart.push(candidate);
    renderCart();
    filterCandidates();
}

function removeFromCart(candidateId) {
    cart = cart.filter(c => c.candidate_id !== candidateId);
    renderCart();
    filterCandidates();
}

function renderCart() {
    const cartDiv = document.getElementById('cart');
    const actionContainer = document.getElementById('action-container');

    if (cart.length === 0) {
        cartDiv.innerHTML = '<p id="empty-msg">No candidates selected. Your ranking will appear here.</p>';
        actionContainer.style.display = 'none';
        return;
    }

    actionContainer.style.display = 'block';
    cartDiv.innerHTML = '';
    
    cart.forEach((candidate, index) => {
        const item = document.createElement('div');
        item.className = 'ballot-item';
        item.innerHTML = `
            <span>${candidate.name}</span>
            <button class="remove-btn" onclick="removeFromCart('${candidate.candidate_id}')">✕</button>
        `;
        cartDiv.appendChild(item);
    });
}