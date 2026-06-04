let candidates = [  // define this
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
    { id: 3, name: "Charlie" },
    { id: 4, name: "Dana" }
];

let tiers = [];
let activeTierId = null;

addTier();

function addTier() {
    tiers.push({
        id: crypto.randomUUID(),
        candidates: [],
        search: ""
    });

    render();
}

function removeTier(tierId) {
    tiers = tiers.filter(t => t.id !== tierId);
    if (activeTierId === tierId) activeTierId = null;
    render();
}

function clearAllTiers() {
    tiers = [];
    activeTierId = null;
    render();
}

function addCandidateToTier(tierId, candidateId) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return;

    tier.candidates.push(candidateId);
    tier.search = "";
    activeTierId = null;

    render();
}

function removeCandidate(tierId, candidateId) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return;

    tier.candidates = tier.candidates.filter(id => id !== candidateId);
    render();
}

function setSearch(tierId, value) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return;

    tier.search = value;
    activeTierId = tierId;

    updateDropdown(tierId);
}

function openSearch(tierId) {
    activeTierId = tierId;
    updateDropdown(tierId);
}

function closeSearch() {
    activeTierId = null;
    render();
}

function render() {
    const container = document.getElementById("tiers-container");

    container.innerHTML = tiers.map((tier, index) => `
        <div class="cart-section" style="margin-bottom:16px;">

            <div style="display:flex; justify-content:space-between;">
                <strong>Tier ${index + 1}</strong>

                <button class="btn btn-secondary"
                        onclick="removeTier('${tier.id}')">
                    Remove
                </button>
            </div>

            <div style="margin-top:12px; position:relative;">

                <input
                    id="search-${tier.id}"
                    class="gov-input"
                    placeholder="Search candidates..."
                    value="${tier.search}"
                    onfocus="openSearch('${tier.id}')"
                    oninput="setSearch('${tier.id}', this.value)"
                    autocomplete="off"
                />

                <div
                    id="dropdown-${tier.id}"
                    class="gov-dropdown"
                    style="display:none; margin-top:5px;"
                ></div>

            </div>

            <div style="margin-top:12px;">
                ${tier.candidates.length === 0
                    ? `<div style="color:#666;">No candidates in this tier</div>`
                    : tier.candidates.map(id => {
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
                    }).join("")
                }
            </div>

        </div>
    `).join("");
}

function updateDropdown(tierId) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return;

    const dropdown = document.getElementById(`dropdown-${tierId}`);
    if (!dropdown) return;

    const query = tier.search.toLowerCase();

    const results = getAvailableCandidates(tier.id, tier.search);

    dropdown.style.display = activeTierId === tierId ? "block" : "none";

    if (results.length === 0) {
        dropdown.innerHTML = `<div style="padding:10px;color:#666;">No candidates found</div>`;
        return;
    }

    dropdown.innerHTML = results.map(c => `
        <div class="dropdown-item"
             onclick="addCandidateToTier('${tier.id}', ${c.id})"
             style="padding:8px; cursor:pointer;">
            ${c.name}
        </div>
    `).join("");
}

function submitBallot() {
    const emptyTiers = tiers
        .map((t, i) => ({ index: i + 1, empty: t.candidates.length === 0 }))
        .filter(t => t.empty);

    if (emptyTiers.length > 0) {
        const tierList = emptyTiers.map(t => `Tier ${t.index}`).join(", ");
        alert("At least one tier is missing")
        return;
    }

    const payload = {
        round_number: 1,
        tiers: tiers.map(t => t.candidates)
    };

    console.log(JSON.stringify(payload, null, 2));
}

function getAvailableCandidates(tierId, query) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return [];

    const q = query.toLowerCase();

    return candidates.filter(c => {
        const matchesSearch = c.name.toLowerCase().includes(q);

        const notInThisTier = !tier.candidates.includes(c.id);

        const notUsedElsewhere = !tiers.some(t =>
            t.id !== tierId && t.candidates.includes(c.id)
        );

        return matchesSearch && notInThisTier && notUsedElsewhere;
    });
}

