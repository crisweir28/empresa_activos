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

async function validarYAsignarConductor(idVehiculo) {
  const select = document.querySelector('#form-asignar-conductor select[name="personal_id"]');
  const idPersonal = select.value;
  
  if (!idPersonal) {
    Swal.fire({
      icon: 'warning',
      title: 'Selecciona un conductor',
      text: 'Debes seleccionar un conductor para continuar'
    });
    return;
  }
  
  // Mostrar loading
  Swal.fire({
    title: 'Verificando documentos...',
    html: 'Consultando el estado de los documentos del conductor',
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });
  
  try {
    // Verificar documentos del conductor
    const response = await fetch(`/administrativo/api/verificar-documentos-conductor/${idPersonal}`);
    const data = await response.json();
    
    if (!data.ok) {
      throw new Error(data.error || 'Error al verificar documentos');
    }
    
    // Cerrar loading
    Swal.close();
    
    // Si todo está OK, asignar directo sin preguntar
    if (data.estado === 'ok') {
      asignarConductorDirecto(idVehiculo);
      return;
    }
    
    // Si hay advertencias o está bloqueado, SIEMPRE mostrar confirmación
    mostrarConfirmacionAsignacion(data, idVehiculo);
    
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo verificar los documentos: ' + error.message
    });
  }
}

// app/static/js/administrativo/vehiculos.js

async function validarYAsignarConductor(idVehiculo) {
  const select = document.querySelector('#form-asignar-conductor select[name="personal_id"]');
  const idPersonal = select.value;
  
  if (!idPersonal) {
    Swal.fire({
      icon: 'warning',
      title: 'Selecciona un conductor',
      text: 'Debes seleccionar un conductor para continuar'
    });
    return;
  }
  
  // Mostrar loading
  Swal.fire({
    title: 'Verificando documentos...',
    html: 'Consultando el estado de los documentos del conductor',
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });
  
  try {
    // Verificar documentos del conductor
    const response = await fetch(`/administrativo/api/verificar-documentos-conductor/${idPersonal}`);
    const data = await response.json();
    
    if (!data.ok) {
      throw new Error(data.error || 'Error al verificar documentos');
    }
    
    // Cerrar loading
    Swal.close();
    
    // Si todo está OK, asignar directo sin preguntar
    if (data.estado === 'ok') {
      asignarConductorDirecto(idVehiculo);
      return;
    }
    
    // Si hay advertencias o está bloqueado, SIEMPRE mostrar confirmación
    mostrarConfirmacionAsignacion(data, idVehiculo);
    
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo verificar los documentos: ' + error.message
    });
  }
}

// Mostrar confirmación con advertencias (SIEMPRE se puede asignar con confirmación)
function mostrarConfirmacionAsignacion(data, idVehiculo) {
  const { detalles, riesgos, resumen } = data;
  
  let htmlContent = '<div style="text-align:left;max-height:400px;overflow-y:auto">';
  
  // Documentos vencidos
  if (detalles.vencidos && detalles.vencidos.length > 0) {
    htmlContent += '<div style="margin-bottom:16px"><strong style="color:#dc2626">📋 Documentos vencidos:</strong><ul style="margin:8px 0;padding-left:20px;font-size:13px">';
    detalles.vencidos.forEach(doc => {
      const nombre = doc.tipo.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      htmlContent += `<li>${nombre} (Venció: ${doc.vencimiento})</li>`;
    });
    htmlContent += '</ul></div>';
  }
  
  // Documentos faltantes críticos
  if (detalles.faltantes_criticos && detalles.faltantes_criticos.length > 0) {
    htmlContent += '<div style="margin-bottom:16px"><strong style="color:#dc2626">⚠️ Documentos críticos faltantes:</strong><ul style="margin:8px 0;padding-left:20px;font-size:13px">';
    detalles.faltantes_criticos.forEach(tipo => {
      const nombre = tipo.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      htmlContent += `<li>${nombre}</li>`;
    });
    htmlContent += '</ul></div>';
  }
  
  // Documentos por vencer
  if (detalles.por_vencer && detalles.por_vencer.length > 0) {
    htmlContent += '<div style="margin-bottom:16px"><strong style="color:#d97706">📅 Documentos por vencer:</strong><ul style="margin:8px 0;padding-left:20px;font-size:13px">';
    detalles.por_vencer.forEach(doc => {
      const nombre = doc.tipo.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      htmlContent += `<li>${nombre} (Vence en ${doc.dias} días)</li>`;
    });
    htmlContent += '</ul></div>';
  }
  
  // Documentos recomendados faltantes
  if (detalles.faltantes_recomendados && detalles.faltantes_recomendados.length > 0) {
    htmlContent += '<div style="margin-bottom:16px"><strong style="color:#d97706">📄 Documentos recomendados faltantes:</strong><ul style="margin:8px 0;padding-left:20px;font-size:13px">';
    detalles.faltantes_recomendados.forEach(tipo => {
      const nombre = tipo.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      htmlContent += `<li>${nombre}</li>`;
    });
    htmlContent += '</ul></div>';
  }
  
  // Riesgos
  if (riesgos.conductor && riesgos.conductor.length > 0) {
    htmlContent += '<div style="margin-bottom:12px"><strong style="color:#dc2626">🚫 Riesgos para el conductor:</strong><ul style="margin:8px 0;padding-left:20px;font-size:12px">';
    riesgos.conductor.forEach(riesgo => {
      htmlContent += `<li>${riesgo}</li>`;
    });
    htmlContent += '</ul></div>';
  }
  
  if (riesgos.empresa && riesgos.empresa.length > 0) {
    htmlContent += '<div><strong style="color:#dc2626">🏢 Riesgos para la empresa:</strong><ul style="margin:8px 0;padding-left:20px;font-size:12px">';
    riesgos.empresa.forEach(riesgo => {
      htmlContent += `<li>${riesgo}</li>`;
    });
    htmlContent += '</ul></div>';
  }
  
  htmlContent += '</div>';
  
  Swal.fire({
    title: "⚠️ Advertencias de documentación",
    html: htmlContent,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#6b7280",
    confirmButtonText: "Sí, asignar bajo mi responsabilidad",
    cancelButtonText: "No, elegir otro conductor",
    reverseButtons: true,
    width: '600px',
    footer: '<strong style="color:#856404">⚠️ Al confirmar, acepto la responsabilidad de asignar este vehículo</strong>'
  }).then((result) => {
    if (result.isConfirmed) {
      // Confirmar asignación
      Swal.fire({
        title: "Asignado correctamente",
        text: "El conductor ha sido asignado al vehículo",
        icon: "success",
        timer: 2000,
        showConfirmButton: false
      });
      
      // Cerrar modal y enviar formulario
      cerrarModal('modal-conductor');
      setTimeout(() => {
        asignarConductorDirecto(idVehiculo);
      }, 500);
    }
    // Si cancela, el modal principal queda abierto para elegir otro conductor
  });
}

// Asignar conductor directamente (sin validación adicional)
function asignarConductorDirecto(idVehiculo) {
  document.getElementById('form-asignar-conductor').submit();
}