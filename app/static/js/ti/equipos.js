/* app/static/js/ti/equipos.js
 * JS específico del módulo de equipos TI
 * Depende de: shared.js + ti.js (deben cargarse antes)
 * Requiere: validacion_tooltip.js (validarFormulario)
 */

// ══════════════════════════════════════════════════════════════
// GESTOR DE ARCHIVOS — acumulado global
// Debe declararse primero porque cerrarModal lo usa
// ══════════════════════════════════════════════════════════════
const _archivosAcumulados = {};

// ══════════════════════════════════════════════════════════════
// VALIDADORES ESPECÍFICOS
// ══════════════════════════════════════════════════════════════
function vImei(input) {
  const v = input.value.trim();
  if (!v) { limpiar(input, 'ti-imei'); return true; }
  if (!/^\d{15}$/.test(v)) return setMsg(input, 'ti-imei', false, 'IMEI debe tener 15 dígitos');
  return setMsg(input, 'ti-imei', true, 'Se ve bien');
}

async function validarSerieUnica(input) {
  const serie = input.value.trim();

  if (!serie) {
    input.classList.remove('is-invalid', 'is-valid');
    limpiar(input, 'ti-serie');
    return true;
  }

  try {
    const resp = await fetch(`/ti/equipos/validar-serie?serie=${encodeURIComponent(serie)}`);

    if (!resp.ok) throw new Error('Error del servidor');

    const data = await resp.json();

    if (data.existe) {
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
      setMsg(input, 'ti-serie', false, 'Este número de serie ya existe');
      return false;
    }

    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    setMsg(input, 'ti-serie', true, 'Número de serie disponible');
    return true;

  } catch (error) {
    console.error(error);
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    setMsg(input, 'ti-serie', false, 'Error validando serie');
    return false;
  }
}

// ══════════════════════════════════════════════════════════════
// SUBMIT — NUEVO EQUIPO
// ══════════════════════════════════════════════════════════════
async function submitEquipo() {
  const form = document.getElementById('form-nuevo-equipo');

  if (!validarFormulario('form-nuevo-equipo')) return;

  const inputSerie = form.querySelector('[name="numero_serie"]');
  const serie = inputSerie.value.trim();

  if (!serie) {
    form.submit();
    return;
  }

  try {
    const response = await fetch(`/ti/equipos/validar-serie?serie=${encodeURIComponent(serie)}`);

    if (!response.ok) throw new Error('Error del servidor');

    const data = await response.json();

    if (data.existe) {
      inputSerie.classList.add('is-invalid');
      inputSerie.classList.remove('is-valid');
      setMsg(inputSerie, 'ti-serie', false, 'Este número de serie ya está registrado.');

      Swal.fire({
        icon: 'warning',
        title: 'Serie duplicada',
        text: 'Debes capturar un número de serie único.',
        target: document.getElementById('modal-nuevo'),
        customClass: { container: 'swal-sobre-modal' }
      });

      return;
    }

    form.submit();

  } catch (error) {
    console.error(error);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No fue posible validar el número de serie.'
    });
  }
}

// ══════════════════════════════════════════════════════════════
// ABRIR MODAL EDITAR — Precarga TODOS los campos
// ══════════════════════════════════════════════════════════════
function editarEquipo(data) {
  document.getElementById('form-editar').action = `/ti/equipos/${data.id}/editar`;

  setVal('e-nombre',         data.nombre);
  setVal('e-tipo',           data.tipo);
  setVal('e-gama',           data.gama);
  setVal('e-estado',         data.estado);
  setVal('e-condicion',      data.condicion);
  setVal('e-marca',          data.marca);
  setVal('e-modelo',         data.modelo);
  setVal('e-serie',          data.numero_serie);
  setVal('e-imei',           data.imei);
  setVal('e-serie-cargador', data.serie_cargador);
  setVal('e-procesador',     data.procesador);
  setVal('e-ram',            data.memoria_ram);
  setVal('e-almacenamiento', data.almacenamiento);
  setVal('e-so',             data.sistema_operativo);
  setVal('e-costo',          data.costo);
  setVal('e-garantia',       data.garantia);
  setVal('e-fecha',          data.fecha_adquisicion);
  setVal('e-ubicacion',      data.ubicacion_id);
  setVal('e-accesorios',     data.accesorios);
  setVal('e-comentarios',    data.comentarios);

  const cbArr = document.getElementById('e-arrendamiento');
  cbArr.checked = !!data.arrendamiento;
  document.getElementById('e-campos-arrendamiento').style.display =
    cbArr.checked ? 'block' : 'none';

  setVal('e-fecha-renovacion', data.fecha_renovacion);
  setVal('e-proveedor',        data.proveedor_arrendamiento);

  actualizarCamposEdit();
  abrirModal('modal-editar');
}

function setVal(id, valor) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = (valor === null || valor === undefined) ? '' : valor;
}

// ══════════════════════════════════════════════════════════════
// CAMPOS DINÁMICOS — MODAL NUEVO
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
// CAMPOS DINÁMICOS — MODAL EDITAR
// ══════════════════════════════════════════════════════════════
function actualizarCamposEdit() {
  const tipo = document.getElementById('e-tipo').value;

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

  const camposSpecs = document.getElementById('e-campos-specs');
  if (camposSpecs) {
    const tiposConSpecs = ['laptop', 'desktop'];
    camposSpecs.style.display = tiposConSpecs.includes(tipo) ? '' : 'none';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  if (typeof actualizarCampos === 'function' && document.getElementById('n-tipo')) {
    actualizarCampos();
  }
});

// ══════════════════════════════════════════════════════════════
// TOGGLE ARRENDAMIENTO
// ══════════════════════════════════════════════════════════════
function toggleArrendamiento(cb) {
  document.getElementById('campos-arrendamiento').style.display = cb.checked ? 'block' : 'none';
}

function toggleArrendamientoEdit(cb) {
  document.getElementById('e-campos-arrendamiento').style.display = cb.checked ? 'block' : 'none';
}

// ══════════════════════════════════════════════════════════════
// CERRAR MODAL + LIMPIEZA TOTAL
// ══════════════════════════════════════════════════════════════
function cerrarModal(idModal) {
  const modal = document.getElementById(idModal);
  if (!modal) return;

  modal.classList.remove('open');

  // Limpiar listas de archivos y acumulados
  modal.querySelectorAll('.lista-archivos').forEach(l => l.innerHTML = '');
  modal.querySelectorAll('input[type="file"]').forEach(inp => {
    const key = inp.id || inp.name;
    if (_archivosAcumulados[key]) delete _archivosAcumulados[key];
  });

  const form = modal.querySelector('form');
  if (!form) return;

  form.reset();
  form.classList.remove('was-validated');

  form.querySelectorAll('input, select, textarea').forEach(el => {
    el.classList.remove('is-valid', 'is-invalid', 'input-ok', 'input-err');
    if (el.setCustomValidity) el.setCustomValidity('');
    el.style.borderColor = '';
    el.style.boxShadow = '';
    el.style.background = '';
    el.style.backgroundColor = '';
    el.blur();
  });

  form.querySelectorAll('.field-msg').forEach(msg => {
    msg.textContent = '';
    msg.className = 'field-msg';
  });

  ['campos-arrendamiento', 'e-campos-arrendamiento'].forEach(id => {
    const sec = document.getElementById(id);
    if (sec) sec.style.display = 'none';
  });

  if (document.activeElement) document.activeElement.blur();
}

// ══════════════════════════════════════════════════════════════
// GESTOR DE ARCHIVOS MÚLTIPLES CON PREVIEW Y ELIMINAR
// ══════════════════════════════════════════════════════════════
function agregarArchivos(input, idLista, modo) {
  const key = input.id || input.name;

  if (!_archivosAcumulados[key]) {
    _archivosAcumulados[key] = new DataTransfer();
  }

  const nombresExistentes = new Set(
    Array.from(_archivosAcumulados[key].files).map(f => f.name)
  );

  Array.from(input.files).forEach(file => {
    if (!nombresExistentes.has(file.name)) {
      _archivosAcumulados[key].items.add(file);
    }
  });

  input.files = _archivosAcumulados[key].files;
  _renderLista(input, idLista, modo, key);
}

function _renderLista(input, idLista, modo, key) {
  const lista = document.getElementById(idLista);
  if (!lista) return;

  lista.innerHTML = '';

  const archivos = Array.from(_archivosAcumulados[key]?.files || []);
  if (archivos.length === 0) return;

  archivos.forEach((file, idx) => {
    const item = document.createElement('div');
    item.className = 'archivo-item';

    if (modo === 'imagenes' && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = e => {
        item.innerHTML = `
          <div class="archivo-preview-img">
            <img src="${e.target.result}" alt="${file.name}" style="display:block;width:100%;height:100%;object-fit:cover;">
            <button type="button" class="archivo-eliminar"
                    onclick="_eliminarArchivo('${key}', '${idLista}', '${modo}', ${idx})"
                    title="Eliminar">
              <i class="bi bi-trash3-fill"></i>
            </button>
          </div>
          <div class="archivo-nombre">${file.name}</div>
        `;
      };
      reader.readAsDataURL(file);

    } else if (file.type === 'application/pdf') {
      const url = URL.createObjectURL(file);
      item.innerHTML = `
        <div class="archivo-preview-doc">
          <embed src="${url}" type="application/pdf">
          <button type="button" class="archivo-eliminar"
                  onclick="_eliminarArchivo('${key}', '${idLista}', '${modo}', ${idx})"
                  title="Eliminar">
            <i class="bi bi-trash3-fill"></i>
          </button>
        </div>
        <div class="archivo-nombre">${file.name} · ${(file.size / 1024).toFixed(1)} KB</div>
      `;

    } else {
      item.innerHTML = `
        <div class="archivo-preview-doc archivo-generico">
          <i class="bi bi-file-earmark-text"></i>
          <button type="button" class="archivo-eliminar"
                  onclick="_eliminarArchivo('${key}', '${idLista}', '${modo}', ${idx})"
                  title="Eliminar">
            <i class="bi bi-trash3-fill"></i>
          </button>
        </div>
        <div class="archivo-nombre">${file.name} · ${(file.size / 1024).toFixed(1)} KB</div>
      `;
    }

    lista.appendChild(item);
  });

  // ── Botón "Agregar más" ──────────────────────────────────
  const btnMas = document.createElement('div');
  btnMas.className = 'archivo-item';
  btnMas.innerHTML = `
    <button type="button" class="archivo-agregar-mas"
            onclick="document.getElementById('${input.id}').click()"
            title="Agregar más archivos">
      <i class="bi bi-plus-lg"></i>
    </button>
    <div class="archivo-nombre">Agregar</div>
  `;
  lista.appendChild(btnMas);
}

function _eliminarArchivo(key, idLista, modo, idx) {
  if (!_archivosAcumulados[key]) return;

  const dt = new DataTransfer();
  Array.from(_archivosAcumulados[key].files).forEach((f, i) => {
    if (i !== idx) dt.items.add(f);
  });
  _archivosAcumulados[key] = dt;

  const input = document.querySelector(`#${key}, [name="${key}"]`);
  if (input) {
    input.files = dt.files;
    _renderLista(input, idLista, modo, key);
  }
}

// ══════════════════════════════════════════════════════════════
// SOCKET.IO — actualización de lista en tiempo real
// ══════════════════════════════════════════════════════════════
if (typeof io !== 'undefined') {
  const socket = io();
  socket.on('ti_equipos_update', function () {
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