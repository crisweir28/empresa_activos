/* app/static/js/ti/equipos.js
 * JS específico del módulo de equipos TI
 * Depende de: shared.js + ti.js (deben cargarse antes)
 * Requiere: validacion_tooltip.js (validarFormulario)
 */

// ══════════════════════════════════════════════════════════════
// VALIDADORES ESPECÍFICOS
// ══════════════════════════════════════════════════════════════
function vImei(input) {
  const v = input.value.trim();
  if (!v) { limpiar(input, 'ti-imei'); return true; }
  if (!/^\d{15}$/.test(v)) return setMsg(input, 'ti-imei', false, 'IMEI debe tener 15 dígitos');
  return setMsg(input, 'ti-imei', true, 'Se ve bien');
}

// ══════════════════════════════════════════════════════════════
// SUBMIT — NUEVO EQUIPO
// ══════════════════════════════════════════════════════════════
function submitEquipo() {
  const form = document.getElementById('form-nuevo-equipo');

  // Validar campos required con tooltips Bootstrap
  if (!validarFormulario('form-nuevo-equipo')) {
    return;
  }

  form.submit();
}

// ══════════════════════════════════════════════════════════════
// ABRIR MODAL EDITAR — Precarga TODOS los campos
// ══════════════════════════════════════════════════════════════
function editarEquipo(data) {
  // `data` es un objeto con todos los campos del equipo
  // (más limpio que pasar 20 parámetros sueltos)

  console.log('DATOS EQUIPO:', data);
  console.log('NOMBRE:', data.nombre);

  document.getElementById('form-editar').action =
    `/ti/equipos/${data.id}/editar`;

  document.getElementById('form-editar').action = `/ti/equipos/${data.id}/editar`;

  // ── Campos básicos ────────────────────────────────────────
  setVal('e-nombre',         data.nombre);
  setVal('e-tipo',           data.tipo);
  setVal('e-gama',           data.gama);
  setVal('e-estado',         data.estado);
  setVal('e-condicion',      data.condicion);
  setVal('e-marca',          data.marca);
  setVal('e-modelo',         data.modelo);
  setVal('e-serie',          data.numero_serie);

  // ── Campos dinámicos (IMEI / Cargador) ────────────────────
  setVal('e-imei',           data.imei);
  setVal('e-serie-cargador', data.serie_cargador);

  // ── Specs ─────────────────────────────────────────────────
  setVal('e-procesador',     data.procesador);
  setVal('e-ram',            data.memoria_ram);
  setVal('e-almacenamiento', data.almacenamiento);
  setVal('e-so',             data.sistema_operativo);

  // ── Costo + fechas ────────────────────────────────────────
  setVal('e-costo',          data.costo);
  setVal('e-garantia',       data.garantia);
  setVal('e-fecha',          data.fecha_adquisicion);
  setVal('e-ubicacion',      data.ubicacion_id);

  // ── Otros ─────────────────────────────────────────────────
  setVal('e-accesorios',     data.accesorios);
  setVal('e-comentarios',    data.comentarios);

  // ── Arrendamiento (checkbox + sección dinámica) ───────────
  const cbArr = document.getElementById('e-arrendamiento');
  cbArr.checked = !!data.arrendamiento;
  document.getElementById('e-campos-arrendamiento').style.display =
    cbArr.checked ? 'block' : 'none';

  setVal('e-fecha-renovacion', data.fecha_renovacion);
  setVal('e-proveedor',        data.proveedor_arrendamiento);

  // ── Mostrar/ocultar IMEI o Cargador según tipo ────────────
  actualizarCamposEdit();

  abrirModal('modal-editar');
}

// Helper interno: setear valor sin romper si el campo no existe
function setVal(id, valor) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = (valor === null || valor === undefined) ? '' : valor;
}

// ══════════════════════════════════════════════════════════════
// CAMPOS DINÁMICOS — MODAL NUEVO
// IMEI solo en celular, Cargador solo en laptop
// ══════════════════════════════════════════════════════════════
function actualizarCampos() {
  const tipo = document.getElementById('n-tipo').value;

  const campoImei = document.getElementById('campo-imei');
  if (campoImei) {
    if (tipo === 'celular') {
      campoImei.style.display = '';
    } else {
      campoImei.style.display = 'none';
      const inputImei = campoImei.querySelector('input[name="imei"]');
      if (inputImei) inputImei.value = '';
    }
  }

  const campoCargador = document.getElementById('campo-cargador');
  if (campoCargador) {
    const inputCargador = campoCargador.querySelector('input[name="serie_cargador"]');
    if (tipo === 'laptop') {
      campoCargador.style.display = '';
      if (inputCargador) inputCargador.setAttribute('required', 'required');
    } else {
      campoCargador.style.display = 'none';
      if (inputCargador) {
        inputCargador.removeAttribute('required');
        inputCargador.value = '';
        inputCargador.classList.remove('is-invalid');
      }
    }
  }

  const camposSpecs = document.getElementById('campos-specs');
  if (camposSpecs) {
    const tiposConSpecs = ['laptop', 'desktop'];
    camposSpecs.style.display = tiposConSpecs.includes(tipo) ? '' : 'none';
  }
}

// ══════════════════════════════════════════════════════════════
// CAMPOS DINÁMICOS — MODAL EDITAR (versión espejo)
// ══════════════════════════════════════════════════════════════
function actualizarCamposEdit() {
  const tipo = document.getElementById('e-tipo').value;

  // IMEI
  const campoImei = document.getElementById('e-campo-imei');
  if (campoImei) {
    if (tipo === 'celular') {
      campoImei.style.display = '';
    } else {
      campoImei.style.display = 'none';
      const inputImei = document.getElementById('e-imei');
      if (inputImei) inputImei.value = '';
    }
  }

  // Cargador
  const campoCargador = document.getElementById('e-campo-cargador');
  if (campoCargador) {
    const inputCargador = document.getElementById('e-serie-cargador');
    if (tipo === 'laptop') {
      campoCargador.style.display = '';
      if (inputCargador) inputCargador.setAttribute('required', 'required');
    } else {
      campoCargador.style.display = 'none';
      if (inputCargador) {
        inputCargador.removeAttribute('required');
        inputCargador.value = '';
        inputCargador.classList.remove('is-invalid');
      }
    }
  }

  // Specs
  const camposSpecs = document.getElementById('e-campos-specs');
  if (camposSpecs) {
    const tiposConSpecs = ['laptop', 'desktop'];
    camposSpecs.style.display = tiposConSpecs.includes(tipo) ? '' : 'none';
  }
}

// Estado inicial del modal nuevo al cargar la página
document.addEventListener('DOMContentLoaded', function() {
  if (typeof actualizarCampos === 'function' && document.getElementById('n-tipo')) {
    actualizarCampos();
  }
});

// ══════════════════════════════════════════════════════════════
// TOGGLE ARRENDAMIENTO (nuevo + editar)
// ══════════════════════════════════════════════════════════════
function toggleArrendamiento(cb) {
  document.getElementById('campos-arrendamiento').style.display = cb.checked ? 'block' : 'none';
}

function toggleArrendamientoEdit(cb) {
  document.getElementById('e-campos-arrendamiento').style.display = cb.checked ? 'block' : 'none';
}

// ══════════════════════════════════════════════════════════════
// PREVIEW EVIDENCIA FOTOGRÁFICA (modal nuevo)
// ══════════════════════════════════════════════════════════════
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

// ══════════════════════════════════════════════════════════════
// CERRAR MODAL + LIMPIEZA TOTAL
// Limpia todos los sistemas de validación:
//   - is-valid / is-invalid  (Bootstrap-style)
//   - input-ok / input-err   (sistema legacy de setMsg)
//   - .field-msg.ok / .field-msg.err (mensajes "Se ve bien")
// ══════════════════════════════════════════════════════════════
function cerrarModal(idModal) {
  const modal = document.getElementById(idModal);
  if (!modal) return;

  modal.classList.remove('open');

  const form = modal.querySelector('form');
  if (!form) return;

  // Reset valores
  form.reset();
  form.classList.remove('was-validated');

  // Limpiar TODAS las clases de validación
  form.querySelectorAll('input, select, textarea').forEach(el => {
    el.classList.remove('is-valid', 'is-invalid');
    el.classList.remove('input-ok', 'input-err');
    if (el.setCustomValidity) el.setCustomValidity('');
    el.style.borderColor = '';
    el.style.boxShadow = '';
    el.style.background = '';
    el.style.backgroundColor = '';
    el.blur();
  });

  // Limpiar mensajes "✓ Se ve bien"
  form.querySelectorAll('.field-msg').forEach(msg => {
    msg.textContent = '';
    msg.className = 'field-msg';
  });

  // Limpiar previews de imágenes
  form.querySelectorAll('[id^="prev-"], #ev-preview').forEach(prev => {
    prev.style.display = 'none';
    const img = prev.querySelector('img');
    if (img) img.src = '';
  });

  // Ocultar sección de arrendamiento (nuevo Y editar)
  ['campos-arrendamiento', 'e-campos-arrendamiento'].forEach(id => {
    const sec = document.getElementById(id);
    if (sec) sec.style.display = 'none';
  });

  // Quitar focus
  if (document.activeElement) document.activeElement.blur();
}

// ══════════════════════════════════════════════════════════════
// SOCKET.IO — actualización de lista en tiempo real
// ══════════════════════════════════════════════════════════════
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