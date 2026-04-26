const form = document.getElementById("analyzeForm");
const submitBtn = document.getElementById("submitBtn");

if (form && submitBtn) {
    form.addEventListener("submit", () => {
        const textNode = submitBtn.querySelector(".btn-text");
        const spinner = submitBtn.querySelector(".spinner");
        if (textNode) textNode.textContent = "Analyzing...";
        if (spinner) spinner.classList.remove("hidden");
        submitBtn.disabled = true;
    });
}
