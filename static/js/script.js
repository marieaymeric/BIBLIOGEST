// script.js — BiblioGest
// Ferme automatiquement les messages flash après quelques secondes.

document.addEventListener("DOMContentLoaded", function () {
    const alertes = document.querySelectorAll(".alert");
    alertes.forEach(function (alerte) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alerte);
            bsAlert.close();
        }, 6000);
    });
});
