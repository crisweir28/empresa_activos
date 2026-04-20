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
function actualizarCampos() {
  const tipo        = document.getElementById('n-tipo').value;
  const campoIMEI   = document.getElementById('campo-imei');
  const camposSpecs = document.getElementById('campos-specs');
  campoIMEI.style.display   = tipo === 'celular' ? 'block' : 'none';
  camposSpecs.style.display = tipo === 'monitor' ? 'none'  : 'block';
}

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