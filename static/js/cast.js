const allCandidates = [
    "Candidate Alpha", "Candidate Beta", "Candidate Gamma", "Candidate Delta",
    "Senator Epsilon", "Representative Zeta", "Governor Eta", "Mayor Theta"
];

let cart = [];

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
        c.toUpperCase().includes(filter) && !cart.includes(c)
    );

    dropdown.innerHTML = '';
    if (filtered.length === 0) {
        dropdown.innerHTML = '<div style="padding: 10px; color: #666;">No candidates found</div>';
    } else {
        filtered.forEach(candidate => {
            const div = document.createElement('div');
            div.style.padding = '10px';
            div.style.cursor = 'pointer';
            div.style.borderBottom = '1px solid #eee';
            div.textContent = candidate;
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
    if (cart.includes(candidate)) return;
    cart.push(candidate);
    renderCart();
    filterCandidates();
}

function removeFromCart(candidate) {
    cart = cart.filter(c => c !== candidate);
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
            <span>${candidate}</span>
            <button class="remove-btn" onclick="removeFromCart('${candidate}')">✕</button>
        `;
        cartDiv.appendChild(item);
    });
}
