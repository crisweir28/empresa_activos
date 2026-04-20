/* app/static/js/shared.js
 * JS compartido por múltiples módulos.
 * Incluir SIEMPRE antes de los JS específicos del módulo.
 *
 * Contiene:
 *   - abrirModal / cerrarModal  (helpers de modales)
 *   - showTab                    (tabs con .tab-content + style.display)
 *   - abrirLightbox / cerrarLightbox
 *   - listener de Escape para cerrar el lightbox
 */

// ══ Modales ═════════════════════════════════════════════════
function abrirModal(id)  { document.getElementById(id).classList.add('open'); }
function cerrarModal(id) { document.getElementById(id).classList.remove('open'); }

// ══ Tabs ════════════════════════════════════════════════════
// Variante para templates que usan .tab-content con display:none/block
function showTab(name, btn) {
  document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).style.display = 'block';
  btn.classList.add('active');
}

// ══ Lightbox ════════════════════════════════════════════════
// Requiere en el HTML: #lightbox, #lb-img, #lb-tipo, #lb-fecha, #lb-nombre, #lb-download
function abrirLightbox(url, tipo, fecha, nombre) {
  document.getElementById('lb-img').src            = url;
  document.getElementById('lb-tipo').textContent   = tipo;
  document.getElementById('lb-fecha').textContent  = fecha;
  document.getElementById('lb-nombre').textContent = nombre;
  document.getElementById('lb-download').href      = url;
  document.getElementById('lb-download').download  = nombre;
  document.getElementById('lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function cerrarLightbox() {
  const lb = document.getElementById('lightbox');
  if (!lb) return;
  lb.classList.remove('open');
  document.body.style.overflow = '';
}

// Escape cierra el lightbox (si está abierto)
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') cerrarLightbox();
});