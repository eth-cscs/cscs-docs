document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".v-badge").forEach(function (el) {
        el.title = "available in " + el.textContent.trim();
    });
});
