// base.js — JS compartido para páginas protegidas (dashboard, activos, departamentos)

// Protección bfcache: al pulsar "atrás" tras logout, verifica sesión
window.addEventListener("pageshow", function(e) {
  if (e.persisted) {
    fetch("/api/check-session", { credentials: "same-origin" })
      .then(function(r) { if (r.status === 401) window.location.replace("/login"); })
      .catch(function()  { window.location.replace("/login"); });
  }
});

// Logout seguro: fetch + replace elimina la página del historial
document.querySelectorAll('a[href*="logout"]').forEach(function(btn) {
  btn.addEventListener("click", function(e) {
    e.preventDefault();
    fetch("/logout", {
      credentials: "same-origin",
      headers: { "X-Requested-With": "fetch" }
    }).finally(function() {
      window.location.replace("/login");
    });
  });
});

function abrirModal(id) {
    document.getElementById(id).classList.add('active');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('active');
}