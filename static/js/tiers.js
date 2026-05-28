let candidates = [
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
    { id: 3, name: "Charlie" },
    { id: 4, name: "Dana" }
];

let tiers = [];
let openSearchTier = null; // allow one search box open at a time

addTier();

function addTier() {
    tiers.push({
        id: crypto.randomUUID(),
        candidates: []
    });
    render();
}

function clearAllTiers() {
    tiers = [];
    render();
}

function openSearch(tierId) {
    openSearchTier = tierId;
    render();
}

function closeSearch() {
    openSearchTier = null;
    render();
}

function addCandidateToTier(tierId, candidateId) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return;

    // prevent duplicates across all tiers
    if (isAssigned(candidateId)) return;

    tier.candidates.push(candidateId);
    closeSearch();
    render();
}

function removeCandidate(tierId, candidateId) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return;

    tier.candidates = tier.candidates.filter(id => id !== candidateId);
    render();
}

function isAssigned(candidateId) {
    return tiers.some(t => t.candidates.includes(candidateId));
}


function render() {
    const container = document.getElementById("tiers-container");

    container.innerHTML = tiers.map((tier, index) => {
        const isOpen = openSearchTier === tier.id;
        const availableCandidates = candidates.filter(c =>
            !isAssigned(c.id) || tier.candidates.includes(c.id)
        );

        return `
        <div class="cart-section" style="margin-bottom:16px;">

            <!-- Tier Header -->
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong>Tier ${index + 1}</strong>

                <button  onclick="removeTier('${tier.id}')">
                    Remove
                </button>
            </div>

            <!-- Search Bar -->
            <div style="margin-top:12px; position:relative;">
                <input
                    class="gov-input"
                    placeholder="Search candidates..."
                    onclick="openSearch('${tier.id}')"
                    oninput="filterCandidates('${tier.id}', this.value)"
                >

                ${isOpen ? `
                    <div class="gov-dropdown" style="position:relative; margin-top:5px;">
                        ${availableCandidates.map(c => `
                            <div class="dropdown-item"
                                onclick="addCandidateToTier('${tier.id}', ${c.id})">
                                ${c.name}
                            </div>
                        `).join("")}
                    </div>
                ` : ""}
            </div>


            <div style="margin-top:12px;">
                ${tier.candidates.map(id => {
                    const c = candidates.find(x => x.id === id);
                    return `
                        <div class="ballot-item">
                            <span>${c.name}</span>
                            <button class="remove-btn"
                                    onclick="removeCandidate('${tier.id}', ${id})">
                                ×
                            </button>
                        </div>
                    `;
                }).join("")}
            </div>

        </div>
        `;
    }).join("");
}

function removeTier(tierId) {
    tiers = tiers.filter(t => t.id !== tierId);
    render();
}
function filterCandidates(tierId, query) {
    render();
}

function submitBallot() {
    const payload = {
        tiers: tiers.map((t, i) => ({
            tier: i + 1,
            candidates: t.candidates
        }))
    };

// TODO: make POST request to backend, update user ballot
}