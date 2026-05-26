// ── Tabs ─────────────────────────────────────────────────────
function showTab(name, btn) {
  document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).style.display = 'block';
  btn.classList.add('active');
}

// ── Lightbox ──────────────────────────────────────────────────
function abrirLightbox(url, tipo, fecha, nombre) {
  document.getElementById('lb-img').src = url;
  document.getElementById('lb-tipo').textContent = tipo;
  document.getElementById('lb-fecha').textContent = fecha;
  document.getElementById('lb-nombre').textContent = nombre;
  document.getElementById('lb-download').href = url;
  document.getElementById('lb-download').download = nombre;
  document.getElementById('lightbox').style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function cerrarLightbox() {
  document.getElementById('lightbox').style.display = 'none';
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') cerrarLightbox();
});