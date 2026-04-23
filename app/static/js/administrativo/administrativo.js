/* app/static/js/administrativo/administrativo.js */

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

// Número >= 0 (reutilizable para costo/valor/km)
function vNumero(input, key, msg = 'No puede ser negativo') {
  const v = input.value.trim();
  if (!v) { limpiar(input, key); return true; }
  const n = parseFloat(v);
  if (isNaN(n) || n < 0) return setMsg(input, key, false, msg);
  return setMsg(input, key, true, 'Se ve bien');
}

// ══ Helpers de modales ═══════════════════════════════════════
function abrirModal(id)  { document.getElementById(id).classList.add('open'); }
function cerrarModal(id) { document.getElementById(id).classList.remove('open'); }

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

// ══ Tabs ═════════════════════════════════════════════════════
function showTab(name, btn) {
  document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).style.display = 'block';
  btn.classList.add('active');
}

// ══ Preview de foto genérico ═════════════════════════════════
// Uso: <input onchange="previewFoto(this,'id-del-wrap')">
// El wrap debe contener un <img> hijo.
function previewFoto(input, wrapId) {
  const wrap = document.getElementById(wrapId);
  if (!wrap) return;
  const img = wrap.querySelector('img');
  if (input.files && input.files[0] && img) {
    const reader = new FileReader();
    reader.onload = e => { img.src = e.target.result; wrap.style.display = 'block'; };
    reader.readAsDataURL(input.files[0]);
  } else {
    wrap.style.display = 'none';
  }
}

// ══ Completar mantenimiento ══════════════════════════════════
// Usado por mantenimiento.html y vehiculo_detalle.html
function completarMant(id) {
  document.getElementById('form-completar').action = `/administrativo/mantenimiento/${id}/completar`;
  abrirModal('modal-completar');
}

// ══ Filtrado de vehículos en dashboard ═══════════════════════
let filtroActual = 'todos';

const titulos = {
  'todos': 'Todos los vehículos',
  'activo': 'Vehículos activos',
  'mantenimiento': 'Vehículos en mantenimiento',
  'baja': 'Vehículos dados de baja'
};

function filtrarVehiculos(filtro) {
  filtroActual = filtro;
  
  // Actualizar cards activas
  document.querySelectorAll('.filtro-card').forEach(card => {
    card.classList.remove('active');
    if (card.dataset.filtro === filtro) {
      card.classList.add('active');
    }
  });
  
  // Filtrar filas
  const filas = document.querySelectorAll('.vehiculo-row');
  let visibles = 0;
  
  filas.forEach(fila => {
    const estado = fila.dataset.estado;
    if (filtro === 'todos' || estado === filtro) {
      fila.style.display = '';
      visibles++;
    } else {
      fila.style.display = 'none';
    }
  });
  
  // Actualizar título y contador
  document.getElementById('titulo-tabla').textContent = titulos[filtro];
  document.getElementById('contador-vehiculos').textContent = `(${visibles})`;
  
  // Mostrar mensaje si no hay resultados
  const tabla = document.getElementById('tabla-vehiculos');
  const sinResultados = document.getElementById('sin-resultados');
  if (visibles === 0) {
    tabla.style.display = 'none';
    sinResultados.style.display = 'block';
  } else {
    tabla.style.display = '';
    sinResultados.style.display = 'none';
  }
}

// ══ Estilos dinámicos para dashboard ═════════════════════════
(function initDashboardStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .filtro-card {
      transition: all 0.2s ease;
    }
    .filtro-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .filtro-card.active {
      border: 2px solid var(--accent);
      box-shadow: 0 4px 16px rgba(124,92,252,0.15);
    }
  `;
  document.head.appendChild(style);
})();