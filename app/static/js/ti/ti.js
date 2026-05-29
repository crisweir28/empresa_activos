//app/static/js/ti.js
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

if (typeof io !== 'undefined') {
  const socket = io();
  
  socket.on('ti_equipos_update', function() {
    // ← RECARGAR LA PÁGINA AUTOMÁTICAMENTE
    console.log('Evento SocketIO recibido: ti_equipos_update');
    location.reload();
  });
}

// Variable global para almacenar el filtro actual
let filtroActual = 'todos';

// Actualizar la función filtrarEquipos para guardar el filtro
function filtrarEquipos(filtro) {
  filtroActual = filtro; // ← AGREGAR ESTA LÍNEA
  
  const filas = document.querySelectorAll('#tabla-equipos tbody tr');
  const mensajeVacio = document.getElementById('mensaje-vacio');
  const titulo = document.getElementById('titulo-equipos');
  const contador = document.getElementById('contador-equipos');
  const cards = document.querySelectorAll('.stat-card');
  
  let visibles = 0;
  
  // ... resto del código existente ...
}

// Toggle del menú de reportes
function toggleReportMenu(event) {
  event.stopPropagation();
  const menu = document.getElementById('report-menu');
  menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

// Cerrar el menú al hacer clic fuera
document.addEventListener('click', function(event) {
  const menu = document.getElementById('report-menu');
  if (menu && !event.target.closest('.report-dropdown') && !event.target.closest('button')) {
    menu.style.display = 'none';
  }
});

// Generar reporte según el filtro activo
function generarReporte(formato) {
  const menu = document.getElementById('report-menu');
  menu.style.display = 'none';
  
  // Construir URL con parámetros del filtro actual
  let url = `/ti/reporte/${formato}?filtro=${filtroActual}`;
  
  // Mostrar toast de generación
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'info',
    title: `📊 Generando reporte ${formato.toUpperCase()}...`,
    showConfirmButton: false,
    timer: 2000,
    timerProgressBar: true,
  });
  
  // Descargar el archivo
  setTimeout(() => {
    window.location.href = url;
  }, 500);
}

/* ═══════════════════════════════════════════════════════
   VALIDACIÓN AL ENVIAR (con tooltips estilo Bootstrap)
   Función global para usar desde submitEquipo()
═══════════════════════════════════════════════════════ */

/**
 * Valida todos los campos required de un formulario.
 * Marca los inválidos con clase 'is-invalid' (muestra el tooltip).
 *
 * @param {string} idForm - ID del formulario a validar
 * @returns {boolean} true si todos los campos requeridos están llenos
 */
function validarFormulario(idForm) {
  const form = document.getElementById(idForm);
  if (!form) {
    console.warn('validarFormulario: no se encontró el form #' + idForm);
    return true;
  }

  const campos = form.querySelectorAll('[required]');
  let primerInvalido = null;
  let hayErrores = false;

  campos.forEach(function(campo) {
    // Limpiar estado previo
    campo.classList.remove('is-invalid');

    const valor = (campo.value || '').trim();

    if (!valor) {
      campo.classList.add('is-invalid');
      hayErrores = true;
      if (!primerInvalido) primerInvalido = campo;
    }
  });

  // Si hay errores, enfocar el primer campo inválido
  if (hayErrores && primerInvalido) {
    primerInvalido.focus();
    primerInvalido.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return !hayErrores;
}

/* Limpiar el error cuando el usuario empieza a escribir */
document.addEventListener('DOMContentLoaded', function() {
  document.addEventListener('input', function(e) {
    if (e.target.matches('.necesita-validacion [required]') &&
        e.target.classList.contains('is-invalid') &&
        e.target.value.trim()) {
      e.target.classList.remove('is-invalid');
    }
  });

  document.addEventListener('change', function(e) {
    if (e.target.matches('.necesita-validacion [required]') &&
        e.target.classList.contains('is-invalid') &&
        e.target.value.trim()) {
      e.target.classList.remove('is-invalid');
    }
  });
});