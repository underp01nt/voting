function validateAlgorithms() {
    const checkboxes = document.getElementsByName("algorithms");
    const firstCheckbox = checkboxes[0];

    for (let cb of checkboxes) {
        cb.addEventListener("change", () => {
            firstCheckbox.setCustomValidity("");
        });
    }

    let checked = Array.from(checkboxes).some(cb => cb.checked);

    if (!checked) {
        firstCheckbox.setCustomValidity("Please choose an algorithm.");
        firstCheckbox.reportValidity();
        return false;
    }

    firstCheckbox.setCustomValidity("");
    return true;
}