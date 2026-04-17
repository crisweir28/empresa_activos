function setMsg(input, msgId, ok, msg) {
  const el = document.getElementById('msg-' + msgId);
  input.classList.toggle('input-ok',  ok);
  input.classList.toggle('input-err', !ok);
  if (el) {
    el.className = 'field-msg ' + (ok ? 'ok' : 'err');
    el.textContent = ok ? '✓ ' + msg : '✗ ' + msg;
  }
  return ok;
}

function limpiarMsg(input, msgId) {
  const el = document.getElementById('msg-' + msgId);
  input.classList.remove('input-ok', 'input-err');
  if (el) { el.className = 'field-msg'; el.textContent = ''; }
}

// Campo obligatorio — mínimo 2 caracteres
function vCampo(input, key) {
  const v = input.value.trim();
  if (!v)       return setMsg(input, key, false, 'Campo obligatorio');
  if (v.length < 2) return setMsg(input, key, false, 'Mínimo 2 caracteres');
  return setMsg(input, key, true, 'Se ve bien');
}

// Campo opcional — solo valida si tiene contenido
function vOpcional(input, key) {
  const v = input.value.trim();
  if (!v) { limpiarMsg(input, key); return true; }
  if (v.length < 2) return setMsg(input, key, false, 'Mínimo 2 caracteres');
  return setMsg(input, key, true, 'Se ve bien');
}

// Costo — número >= 0
function vCosto(input) {
  const v = input.value.trim();
  if (!v) { limpiarMsg(input, 'h-costo'); return true; }
  const n = parseFloat(v);
  if (isNaN(n) || n < 0) return setMsg(input, 'h-costo', false, 'Valor inválido');
  return setMsg(input, 'h-costo', true, 'Se ve bien');
}

// Fecha — no puede ser futura
function vFecha(input) {
  const v = input.value;
  if (!v) { limpiarMsg(input, 'h-fecha'); return true; }
  const fecha = new Date(v);
  const hoy   = new Date();
  hoy.setHours(0,0,0,0);
  if (fecha > hoy) return setMsg(input, 'h-fecha', false, 'No puede ser fecha futura');
  return setMsg(input, 'h-fecha', true, 'Se ve bien');
}

// Submit con validación de obligatorios
function submitHerramienta() {
  const form   = document.getElementById('form-alta-herramienta');
  const nombre = form.querySelector('[name="nombre"]');
  const marca  = form.querySelector('[name="marca"]');

  const okNombre = vCampo(nombre, 'h-nombre');
  const okMarca  = vCampo(marca,  'h-marca');

  if (!okNombre || !okMarca) {
    const primer = form.querySelector('.input-err');
    if (primer) primer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }
  form.submit();
}

// ── Otras funciones ───────────────────────────────────────────
function asignarHerr(id, nombre) {
  document.getElementById('asignar-titulo').textContent = `👤 Asignar: ${nombre}`;
  document.getElementById('form-asignar').action = `/almacen/herramientas/${id}/asignar`;
  document.getElementById('modal-asignar').classList.add('open');
}

function previewEvidencia(input) {
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
    if (result.isConfirmed) {
      document.getElementById(formId).submit();
    }
  });
}