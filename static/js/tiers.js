// console.log(JSON.stringify(candidates, null, 2))

let tiers = [];
let activeTierId = null;

addTier();

async function submitBallot(payload) {
    const response = await fetch(`/elections/${electionId}/ballot`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    return data;
}

// close search boxes if outside click is detected
document.addEventListener("click", (event) => {
    const searchContainer = event.target.closest(".tier-search-container");

    if (!searchContainer) { activeTierId = null; render(); }
});

const submitBtn = document.getElementById("submitListBtn");
submitBtn.addEventListener("click", () => {
     if (tiers.length === 0) {
        alert("You must create at least one tier before submitting.");
        return;
    }

    const emptyTiers = tiers
        .map((t, i) => ({index: i + 1, empty: t.candidates.length === 0}))
        .filter(t => t.empty);

    if (emptyTiers.length > 0) {
        alert("At least one tier has no candidates.");
        return;
    }

    const confirmed = confirm(
        "WARNING: You cannot return to this ballot once it is submitted.\n\n" +
        "Do you want to continue?"
    );

    if (!confirmed) return;

    const payload = {
        round_number: 1,
        tiers: tiers.map(t => t.candidates)
    };

    (async () => {
        try {
            const data = await submitBallot(payload);
            window.location.href = "/";
        }
        catch (err) {
            alert("Failed to submit ballot.");
            console.error(err);
        }
    })();
});

function addTier() {
    tiers.push({
        id: crypto.randomUUID(),
        candidates: [],
        search: ""
    });

    render();
}

function removeTier(tierId) {
    const confirmed = confirm(
        "Remove this tier?\n\nAll candidates in this tier will be removed."
    ); if (!confirmed) return;

    tiers = tiers.filter(t => t.id !== tierId);
    if (activeTierId === tierId) activeTierId = null;
    render();
}

function clearAllTiers() {
    const confirmed = confirm(
        "Clear all tiers?\n\nThis will remove every tier and candidate assignment."
    ); if (!confirmed) return;

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

            <div class="tier-header">
                <div class="tier-label">
                    <span class="tier-badge">${index + 1}</span>
                    <span class="tier-title">Tier ${index + 1}</span>
                </div>

                <button
                    class="tier-remove-btn"
                    onclick="removeTier('${tier.id}')"
                >
                    Remove
                </button>
            </div>

            <div
                class="tier-search-container"
                style="margin-top:12px; position:relative;"
            >

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
                        const c = candidates.find(x => x.candidate_id === id);
                        return `
                            <div class="ballot-item">
                                <span>${c.name}</span>
                                <button class="remove-btn"
                                        onclick="removeCandidate('${tier.id}', '${id}')">
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
             onclick="addCandidateToTier('${tier.id}', '${c.candidate_id}')"
             style="padding:8px; cursor:pointer;">
            ${c.name}
        </div>
    `).join("");
}

function getAvailableCandidates(tierId, query) {
    const tier = tiers.find(t => t.id === tierId);
    if (!tier) return [];

    const q = query.toLowerCase();

    return candidates.filter(c => {
        const matchesSearch = c.name.toLowerCase().includes(q);

        const notInThisTier = !tier.candidates.includes(c.candidate_id);

        const notUsedElsewhere = !tiers.some(t =>
            t.id !== tierId && t.candidates.includes(c.candidate_id)
        );

        return matchesSearch && notInThisTier && notUsedElsewhere;
    });
}

