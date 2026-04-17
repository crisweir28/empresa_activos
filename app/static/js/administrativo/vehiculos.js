/* app/static/js/administrativo/vehiculos.js */

// ── Validadores específicos de vehículos ────────────────────
const REGEX_PLACA = /^[A-Z0-9]{2,4}[-\s]?[A-Z0-9]{2,4}[-\s]?[A-Z0-9]{0,4}$/i;

function vPlaca(input) {
  const v = input.value.trim();
  if (!v) return setMsg(input, 'v-placa', false, 'Campo obligatorio');
  if (!REGEX_PLACA.test(v)) return setMsg(input, 'v-placa', false, 'Formato inválido. Ej: ABC-123');
  return setMsg(input, 'v-placa', true, 'Se ve bien');
}

function vVin(input) {
  const v = input.value.trim();
  if (!v) { limpiar(input, 'v-vin'); return true; }
  if (v.length !== 17) return setMsg(input, 'v-vin', false, 'Debe tener exactamente 17 caracteres');
  return setMsg(input, 'v-vin', true, 'Se ve bien');
}

function vPoliza(input) {
  const v = input.value.trim();
  if (!v) { limpiar(input, 'v-poliza'); return true; }
  if (v.length < 10 || v.length > 15) return setMsg(input, 'v-poliza', false, 'Entre 10 y 15 caracteres');
  return setMsg(input, 'v-poliza', true, 'Se ve bien');
}

function vAnio(input) {
  const v = input.value.trim();
  if (!v) { limpiar(input, 'v-anio'); return true; }
  const n = parseInt(v);
  if (n < 1990 || n > 2030) return setMsg(input, 'v-anio', false, 'Año entre 1990 y 2030');
  return setMsg(input, 'v-anio', true, 'Se ve bien');
}

// ── Submit con validación del form de nuevo vehículo ────────
function submitVehiculo() {
  const form   = document.getElementById('form-vehiculo-nuevo');
  const nombre = form.querySelector('[name="nombre"]');
  const marca  = form.querySelector('[name="marca"]');
  const placa  = form.querySelector('[name="matricula"]');
  const vin    = form.querySelector('[name="vin"]');
  const poliza = form.querySelector('[name="poliza_seguro"]');

  const ok = [
    vCampo(nombre, 'v-nombre'),
    vCampo(marca,  'v-marca'),
    vPlaca(placa),
    vVin(vin),
    vPoliza(poliza),
  ].every(Boolean);

  if (!ok) {
    const primer = form.querySelector('.input-err');
    if (primer) primer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }
  form.submit();
}

// ── Abrir modal editar con datos precargados ────────────────
function editarVehiculo(id, nombre, matricula, marca, modelo, km, tipo, estado, valor, fecha) {
  document.getElementById('form-editar').action = `/administrativo/vehiculos/${id}/editar`;
  document.getElementById('e-nombre').value     = nombre;
  document.getElementById('e-matricula').value  = matricula;
  document.getElementById('e-marca').value      = marca;
  document.getElementById('e-modelo').value     = modelo;
  document.getElementById('e-km').value         = km;
  document.getElementById('e-tipo').value       = tipo;
  document.getElementById('e-estado').value     = estado;
  document.getElementById('e-valor').value      = valor;
  document.getElementById('e-fecha').value      = fecha;
  abrirModal('modal-editar');
}

// ── Toggle de campos de arrendamiento ───────────────────────
function toggleArrendamiento(cb) {
  document.getElementById('campos-arrendamiento').style.display = cb.checked ? 'block' : 'none';
}