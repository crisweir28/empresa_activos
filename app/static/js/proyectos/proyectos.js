/* app/static/js/proyectos.js
 * JS compartido del módulo proyectos.
 */

// ══ Helpers de modales ═══════════════════════════════════════
function abrirModal(id)  { document.getElementById(id).classList.add('open'); }
function cerrarModal(id) { document.getElementById(id).classList.remove('open'); }

// ══ Tabs (variante con .tab-panel + classList) ══════════════
function showTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}

// ══ Confirmación genérica con SweetAlert ═════════════════════
// Uso: confirmarAccion({
//   titulo, mensaje, confirmText, icon, onConfirm
// })
function confirmarAccion({ titulo, mensaje, confirmText = 'Sí', icon = 'warning', onConfirm }) {
  Swal.fire({
    title: titulo,
    html: mensaje,
    icon,
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#6b7280',
    confirmButtonText: confirmText,
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
    focusCancel: true,
  }).then(result => {
    if (result.isConfirmed && typeof onConfirm === 'function') onConfirm();
  });
}