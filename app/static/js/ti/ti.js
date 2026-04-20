/* app/static/js/ti.js
 * JS compartido del módulo TI.
 * Depende de: shared.js (debe cargarse antes)
 *
 * NOTA: algunos validadores duplican código de administrativo.js.
 * Cuando se consoliden patrones transversales, estos pueden moverse
 * a shared.js junto con sus equivalentes.
 */

// ══ Validación visual de formularios ═════════════════════════
function setMsg(input, msgId, ok, msg) {
  const el = document.getElementById('msg-' + msgId);
  input.classList.toggle('input-ok',  ok);
  input.classList.toggle('input-err', !ok);
  if (el) {
    el.className = 'field-msg ' + (ok ? 'ok' : 'err');
    el.textContent = (ok ? '✓ ' : '✗ ') + msg;
  }
  return ok;
}

function limpiar(input, msgId) {
  const el = document.getElementById('msg-' + msgId);
  input.classList.remove('input-ok', 'input-err');
  if (el) { el.className = 'field-msg'; el.textContent = ''; }
}

// ── Validadores genéricos ────────────────────────────────────
function vCampo(input, key) {
  const v = input.value.trim();
  if (!v)           return setMsg(input, key, false, 'Campo obligatorio');
  if (v.length < 2) return setMsg(input, key, false, 'Mínimo 2 caracteres');
  return setMsg(input, key, true, 'Se ve bien');
}

function vOpcional(input, key) {
  const v = input.value.trim();
  if (!v) { limpiar(input, key); return true; }
  if (v.length < 2) return setMsg(input, key, false, 'Mínimo 2 caracteres');
  return setMsg(input, key, true, 'Se ve bien');
}

function vFecha(input, key) {
  const v = input.value;
  if (!v) { limpiar(input, key); return true; }
  const fecha = new Date(v), hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  if (fecha > hoy) return setMsg(input, key, false, 'No puede ser fecha futura');
  return setMsg(input, key, true, 'Se ve bien');
}

function vFechaFutura(input, key) {
  const v = input.value;
  if (!v) { limpiar(input, key); return true; }
  const fecha = new Date(v), hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  if (fecha < hoy) return setMsg(input, key, false, 'La fecha ya venció');
  return setMsg(input, key, true, 'Se ve bien');
}

// Número >= 0 (para costo, valor, etc.)
function vNumero(input, key, msg = 'No puede ser negativo') {
  const v = input.value.trim();
  if (!v) { limpiar(input, key); return true; }
  const n = parseFloat(v);
  if (isNaN(n) || n < 0) return setMsg(input, key, false, msg);
  return setMsg(input, key, true, 'Se ve bien');
}

// ══ Confirmación de baja (SweetAlert) ════════════════════════
function confirmarBaja(nombre, formId) {
  Swal.fire({
    title: '¿Dar de baja?',
    html: `<strong>${nombre}</strong> se marcará como baja.<br>Podrás verlo en el filtro "Baja".`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#6b7280',
    confirmButtonText: '🗑️ Dar de baja',
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
    focusCancel: true,
  }).then(result => {
    if (result.isConfirmed) document.getElementById(formId).submit();
  });
}

// ══ Completar mantenimiento (del módulo TI) ═════════════════
// Usa URL /ti/... (distinta a la del módulo administrativo)
function completarMant(id) {
  document.getElementById('form-completar').action = `/ti/mantenimiento/${id}/completar`;
  abrirModal('modal-completar');
}