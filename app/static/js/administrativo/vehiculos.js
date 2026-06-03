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

// ═══════════════════════════════════════════════════════════
// Helper: marcar campo duplicado en rojo
// Acepta selectores dentro del modal por name="..."
// ═══════════════════════════════════════════════════════════
function marcarCampoDuplicado(modal, nameCampo) {
  const el = modal.querySelector(`[name="${nameCampo}"]`);
  if (el) {
    el.classList.add('is-invalid');
    el.focus();
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// ═══════════════════════════════════════════════════════════
// SUBMIT NUEVO VEHÍCULO (AJAX con validación de duplicados)
// ═══════════════════════════════════════════════════════════
async function submitVehiculo() {
  const form = document.getElementById('form-vehiculo-nuevo');
  const modal = document.getElementById('modal-nuevo');

  // ── Validar campos required con tooltips Bootstrap ──
  if (!validarFormulario('form-vehiculo-nuevo')) {
    return;
  }

  // ── Validar formato de campos opcionales ──
  const placa  = form.querySelector('[name="matricula"]');
  const vin    = form.querySelector('[name="vin"]');
  const poliza = form.querySelector('[name="poliza_seguro"]');

  const erroresFormato = [];

  if (placa.value.trim() && !REGEX_PLACA.test(placa.value.trim())) {
    erroresFormato.push('La placa no tiene un formato válido (Ej: ABC-1234)');
    placa.classList.add('is-invalid');
  }
  if (vin.value.trim() && vin.value.trim().length !== 17) {
    erroresFormato.push(`El VIN debe tener exactamente 17 caracteres (tiene ${vin.value.trim().length})`);
    vin.classList.add('is-invalid');
  }
  if (poliza.value.trim()) {
    const len = poliza.value.trim().length;
    if (len < 10 || len > 15) {
      erroresFormato.push(`La póliza debe tener entre 10 y 15 caracteres (tiene ${len})`);
      poliza.classList.add('is-invalid');
    }
  }

  if (erroresFormato.length > 0) {
    Swal.fire({
      icon: 'warning',
      title: 'Revisa los datos',
      html: '<ul style="text-align:left;margin:0;padding-left:20px;font-size:14px">' +
        erroresFormato.map(e => `<li>${e}</li>`).join('') +
        '</ul>',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc2626'
    });
    return;
  }

  // ── Enviar vía AJAX para recibir respuesta JSON ──
  try {
    const formData = new FormData(form);
    const response = await fetch(form.action, {
      method: 'POST',
      body: formData
    });
    const data = await response.json();

    if (data.ok) {
      // Éxito → recargar para mostrar el flash y la lista actualizada
      Swal.fire({
        icon: 'success',
        title: '✅ Registrado',
        text: 'Vehículo registrado correctamente.',
        timer: 1500,
        showConfirmButton: false
      });
      setTimeout(() => location.reload(), 1500);
    } else if (data.campo) {
      // Duplicado → marcar campo en rojo y mostrar alerta SIN cerrar modal
      marcarCampoDuplicado(modal, data.campo);
      Swal.fire({
        icon: 'warning',
        title: 'Dato duplicado',
        html: data.mensaje,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc2626'
      });
    } else {
      // Otro error
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: data.mensaje || 'No se pudo guardar el vehículo'
      });
    }
  } catch (err) {
    console.error(err);
    Swal.fire({
      icon: 'error',
      title: 'Error de red',
      text: 'No se pudo conectar con el servidor'
    });
  }
}

// ═══════════════════════════════════════════════════════════
// SUBMIT EDITAR VEHÍCULO (AJAX con validación de duplicados)
// ═══════════════════════════════════════════════════════════

async function editarVehiculo(id) {
  try {
    const response = await fetch(`/administrativo/api/vehiculo/${id}`);
    const data = await response.json();

    document.getElementById('form-editar').action = `/administrativo/vehiculos/${id}/editar`;

    // ── Campos de texto ─────────────────────────────────────
    document.getElementById('e-nombre').value         = data.nombre || '';
    document.getElementById('e-tipo-vehiculo').value  = data.tipo_vehiculo || '';
    document.getElementById('e-marca').value          = data.marca || '';
    document.getElementById('e-modelo').value         = data.modelo || '';
    document.getElementById('e-anio').value           = data.anio || '';
    document.getElementById('e-color').value          = data.color || '';
    document.getElementById('e-matricula').value      = data.matricula || '';
    document.getElementById('e-vin').value            = data.vin || '';
    document.getElementById('e-km').value             = data.kilometraje || '';
    document.getElementById('e-tipo').value           = data.tipo_adquisicion || '';
    document.getElementById('e-estado').value         = data.estado || '';
    document.getElementById('e-valor').value          = data.valor || '';
    document.getElementById('e-fecha').value          = data.fecha_adquisicion || '';
    document.getElementById('e-ubicacion').value      = data.ubicacion_id || '';
    document.getElementById('e-poliza').value         = data.poliza_seguro || '';
    document.getElementById('e-aseguradora').value    = data.aseguradora || '';
    document.getElementById('e-vigencia').value       = data.vigencia_seguro || '';
    document.getElementById('e-verificacion').value   = data.ultima_verificacion || '';
    document.getElementById('e-accesorios').value     = data.accesorios || '';
    document.getElementById('e-comentarios').value    = data.comentarios || '';
    document.getElementById('e-renovacion').value     = data.fecha_renovacion || '';
    document.getElementById('e-proveedor').value      = data.proveedor_arrendamiento || '';

    // ── DOCUMENTOS: tarjeta de circulación ──────────────────
    const tarjetaPreview = document.getElementById('e-tarjeta-preview');
    const tarjetaLink    = document.getElementById('e-tarjeta-link');
    if (data.tarjeta_circulacion_url) {
      tarjetaLink.href = data.tarjeta_circulacion_url;
      tarjetaLink.textContent = '📄 Ver documento actual';
      tarjetaPreview.style.display = 'block';
    } else {
      tarjetaPreview.style.display = 'none';
    }

    // ── DOCUMENTOS: certificado de verificación ─────────────
    const certPreview = document.getElementById('e-certificado-preview');
    const certLink    = document.getElementById('e-certificado-link');
    if (data.certificado_verificacion_url) {
      certLink.href = data.certificado_verificacion_url;
      certLink.textContent = '📄 Ver documento actual';
      certPreview.style.display = 'block';
    } else {
      certPreview.style.display = 'none';
    }

    // ── EVIDENCIAS fotográficas ─────────────────────────────
    function precargarEvidencia(idImg, url) {
      const img = document.getElementById(idImg);
      if (!img) return;
      if (url) {
        img.src = url;
        img.style.display = 'block';
      } else {
        img.src = '';
        img.style.display = 'none';
      }
    }
    precargarEvidencia('e-frente-img',   data.evidencia_frente_url);
    precargarEvidencia('e-lateral-img',  data.evidencia_lateral_url);
    precargarEvidencia('e-interior-img', data.evidencia_interior_url);

    abrirModal('modal-editar');
  } catch (error) {
    console.error(error);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la información del vehículo'
    });
  }
}

// ── Abrir modal editar con datos precargados ────────────────
// ── Abrir modal editar con datos precargados ────────────────
async function editarVehiculo(id) {
  try {
    const response = await fetch(`/administrativo/api/vehiculo/${id}`);
    const data = await response.json();

    document.getElementById('form-editar').action = `/administrativo/vehiculos/${id}/editar`;

    // ── Campos de texto ─────────────────────────────────────
    document.getElementById('e-nombre').value         = data.nombre || '';
    document.getElementById('e-tipo-vehiculo').value  = data.tipo_vehiculo || '';
    document.getElementById('e-marca').value          = data.marca || '';
    document.getElementById('e-modelo').value         = data.modelo || '';
    document.getElementById('e-anio').value           = data.anio || '';
    document.getElementById('e-color').value          = data.color || '';
    document.getElementById('e-matricula').value      = data.matricula || '';
    document.getElementById('e-vin').value            = data.vin || '';
    document.getElementById('e-km').value             = data.kilometraje || '';
    document.getElementById('e-tipo').value           = data.tipo_adquisicion || '';
    document.getElementById('e-estado').value         = data.estado || '';
    document.getElementById('e-valor').value          = data.valor || '';
    document.getElementById('e-fecha').value          = data.fecha_adquisicion || '';
    document.getElementById('e-ubicacion').value      = data.ubicacion_id || '';
    document.getElementById('e-poliza').value         = data.poliza_seguro || '';
    document.getElementById('e-aseguradora').value    = data.aseguradora || '';
    document.getElementById('e-vigencia').value       = data.vigencia_seguro || '';
    document.getElementById('e-verificacion').value   = data.ultima_verificacion || '';
    document.getElementById('e-accesorios').value     = data.accesorios || '';
    document.getElementById('e-comentarios').value    = data.comentarios || '';
    document.getElementById('e-renovacion').value     = data.fecha_renovacion || '';
    document.getElementById('e-proveedor').value      = data.proveedor_arrendamiento || '';

    // ── DOCUMENTOS: tarjeta de circulación ──────────────────
    const tarjetaPreview = document.getElementById('e-tarjeta-preview');
    const tarjetaLink    = document.getElementById('e-tarjeta-link');
    if (data.tarjeta_circulacion_url) {
      tarjetaLink.href = data.tarjeta_circulacion_url;
      tarjetaLink.textContent = '📄 Ver documento actual';
      tarjetaPreview.style.display = 'block';
    } else {
      tarjetaPreview.style.display = 'none';
    }

    // ── DOCUMENTOS: certificado de verificación ─────────────
    const certPreview = document.getElementById('e-certificado-preview');
    const certLink    = document.getElementById('e-certificado-link');
    if (data.certificado_verificacion_url) {
      certLink.href = data.certificado_verificacion_url;
      certLink.textContent = '📄 Ver documento actual';
      certPreview.style.display = 'block';
    } else {
      certPreview.style.display = 'none';
    }

    // ── EVIDENCIAS fotográficas ─────────────────────────────
    function precargarEvidencia(idImg, url) {
      const img = document.getElementById(idImg);
      if (!img) return;
      if (url) {
        img.src = url;
        img.style.display = 'block';
      } else {
        img.src = '';
        img.style.display = 'none';
      }
    }
    precargarEvidencia('e-frente-img',   data.evidencia_frente_url);
    precargarEvidencia('e-lateral-img',  data.evidencia_lateral_url);
    precargarEvidencia('e-interior-img', data.evidencia_interior_url);

    abrirModal('modal-editar');
  } catch (error) {
    console.error(error);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la información del vehículo'
    });
  }
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

function cerrarModal(idModal) {
  const modal = document.getElementById(idModal);
  if (!modal) return;
 
  // Cerrar modal
  modal.classList.remove('open');
 
  // Buscar formulario dentro del modal
  const form = modal.querySelector('form');
  if (!form) return;
 
  // Resetear valores del formulario
  form.reset();
  form.classList.remove('was-validated');
 
  // ── Limpiar TODAS las clases de validación de los campos ──
  form.querySelectorAll('input, select, textarea').forEach(el => {
    // Bootstrap-style
    el.classList.remove('is-valid', 'is-invalid');
    // Sistema legacy (setMsg de administrativo.js)
    el.classList.remove('input-ok', 'input-err');
 
    // Limpiar validez personalizada y estilos inline
    if (el.setCustomValidity) el.setCustomValidity('');
    el.style.borderColor = '';
    el.style.boxShadow = '';
    el.style.background = '';
    el.style.backgroundColor = '';
 
    el.blur();
  });
 
  // ── Limpiar mensajes de validación ──
  form.querySelectorAll('.field-msg').forEach(msg => {
    msg.textContent = '';
    msg.className = 'field-msg';  // ← Quitar clases 'ok' / 'err'
  });
 
  // Limpiar previews de imágenes
  form.querySelectorAll('[id^="prev-"]').forEach(prev => {
    prev.style.display = 'none';
    const img = prev.querySelector('img');
    if (img) img.src = '';
  });
 
  // Ocultar sección de arrendamiento
  const arr = document.getElementById('campos-arrendamiento');
  if (arr) arr.style.display = 'none';
 
  // Quitar focus
  if (document.activeElement) document.activeElement.blur();
}

async function submitEditarVehiculo() {

    const form = document.getElementById('form-editar');

    const formData = new FormData(form);

    try {

        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.ok)  {

            Swal.fire({
                icon: 'success',
                title: 'Vehículo actualizado',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                location.reload();
            });

            return;
        }

        // Limpiar errores previos
        ['e-matricula', 'e-vin', 'e-poliza'].forEach(id => {
            const campo = document.getElementById(id);
            if (campo) campo.classList.remove('input-err');
        });

        // Marcar campos duplicados
        if (data.campo === 'matricula') {
            document.getElementById('e-matricula')?.classList.add('input-err');
        }

        if (data.campo === 'vin') {
            document.getElementById('e-vin')?.classList.add('input-err');
        }

        if (data.campo === 'poliza') {
            document.getElementById('e-poliza')?.classList.add('input-err');
        }

        Swal.fire({
            icon: 'warning',
            title: 'Dato duplicado',
            text: data.mensaje
        });

    } catch (error) {

        console.error(error);

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No fue posible actualizar el vehículo'
        });

    }
}