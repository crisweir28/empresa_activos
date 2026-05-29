/* app/static/js/ti/equipos.js
 * JS específico del template ti/equipos.html
 * Depende de: shared.js + ti.js (deben cargarse antes)
 */

// ── Validador específico: IMEI (15 dígitos) ────────────────
function vImei(input) {
  const v = input.value.trim();
  if (!v) { limpiar(input, 'ti-imei'); return true; }
  if (!/^\d{15}$/.test(v)) return setMsg(input, 'ti-imei', false, 'IMEI debe tener 15 dígitos');
  return setMsg(input, 'ti-imei', true, 'Se ve bien');
}

// ── Submit con validación del form de nuevo equipo ─────────
function submitEquipo() {
  const form   = document.getElementById('form-nuevo-equipo');
  const nombre = form.querySelector('[name="nombre"]');
  const marca  = form.querySelector('[name="marca"]');

  const ok = [
    vCampo(nombre, 'ti-nombre'),
    vCampo(marca,  'ti-marca'),
  ].every(Boolean);

  if (!ok) {
    const primer = form.querySelector('.input-err');
    if (primer) primer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }
  form.submit();
}

// ── Abrir modal editar con datos precargados ───────────────
function editarEquipo(id, nombre, tipo, marca, modelo, serie, condicion, costo, fecha) {
  document.getElementById('form-editar').action = `/ti/equipos/${id}/editar`;
  document.getElementById('e-nombre').value     = nombre;
  document.getElementById('e-tipo').value       = tipo;
  document.getElementById('e-marca').value      = marca;
  document.getElementById('e-modelo').value     = modelo;
  document.getElementById('e-serie').value      = serie;
  document.getElementById('e-condicion').value  = condicion;
  document.getElementById('e-costo').value      = costo;
  document.getElementById('e-fecha').value      = fecha;
  abrirModal('modal-editar');
}

// ── Mostrar/ocultar campos según tipo de equipo ────────────
// Celular → muestra IMEI; Monitor → oculta specs (procesador, ram, etc.)
/* ═══════════════════════════════════════════════════════
   ACTUALIZAR actualizarCampos() en app/static/js/ti/equipos.js
═══════════════════════════════════════════════════════ */

// Esta es la versión actualizada. Reemplaza tu actualizarCampos() actual.
// Maneja: IMEI (solo celular), Cargador (solo laptop), y campos de specs.

function actualizarCampos() {
  const tipo = document.getElementById('n-tipo').value;

  // ── Campo IMEI: solo para celulares ──────────────────────
  const campoImei = document.getElementById('campo-imei');
  if (campoImei) {
    if (tipo === 'celular') {
      campoImei.style.display = '';
    } else {
      campoImei.style.display = 'none';
      // Limpiar valor para que no se envíe basura
      const inputImei = campoImei.querySelector('input[name="imei"]');
      if (inputImei) inputImei.value = '';
    }
  }

  // ── Campo Cargador: solo para laptops ────────────────────
  const campoCargador = document.getElementById('campo-cargador');
  if (campoCargador) {
    const inputCargador = campoCargador.querySelector('input[name="serie_cargador"]');

    if (tipo === 'laptop') {
      campoCargador.style.display = '';
      // ✅ Activar required dinámicamente
      if (inputCargador) inputCargador.setAttribute('required', 'required');
    } else {
      campoCargador.style.display = 'none';
      // ✅ Quitar required y limpiar para no bloquear el submit
      if (inputCargador) {
        inputCargador.removeAttribute('required');
        inputCargador.value = '';
        inputCargador.classList.remove('is-invalid');
      }
    }
  }

  // ── Campos de specs: ocultar para tipos sin sentido ──────
  // (ajusta según tu lógica actual, esto es solo ejemplo)
  const camposSpecs = document.getElementById('campos-specs');
  if (camposSpecs) {
    const tiposConSpecs = ['laptop', 'desktop'];
    camposSpecs.style.display = tiposConSpecs.includes(tipo) ? '' : 'none';
  }
}

// Ejecutar una vez al cargar para que el estado inicial sea correcto
document.addEventListener('DOMContentLoaded', function() {
  if (typeof actualizarCampos === 'function') {
    actualizarCampos();
  }
});

// ── Toggle de campos de arrendamiento ──────────────────────
function toggleArrendamiento(cb) {
  document.getElementById('campos-arrendamiento').style.display = cb.checked ? 'block' : 'none';
}

// ── Preview de la evidencia fotográfica ────────────────────
function previewEv(input) {
  const wrap = document.getElementById('ev-preview');
  const img  = document.getElementById('ev-img');
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => { img.src = e.target.result; wrap.style.display = 'block'; };
    reader.readAsDataURL(input.files[0]);
  } else {
    wrap.style.display = 'none';
  }
}

// ── Socket.IO: actualización de lista en tiempo real ───────
if (typeof io !== 'undefined') {
  const socket = io();
  socket.on('ti_equipos_update', function() {
    fetch(window.location.href)
      .then(r => r.text())
      .then(html => {
        const parser      = new DOMParser();
        const doc         = parser.parseFromString(html, 'text/html');
        const nuevaTbody  = doc.querySelector('.panel table tbody');
        const actualTbody = document.querySelector('.panel table tbody');
        if (nuevaTbody && actualTbody) {
          actualTbody.innerHTML = nuevaTbody.innerHTML;
          Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'info',
            title: 'Lista actualizada',
            text: 'Un equipo fue modificado.',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
          });
        }
      });
  });
}