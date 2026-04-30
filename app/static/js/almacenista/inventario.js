// ── Validaciones de formulario ────────────────────────────────
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

// ── Filtrado de herramientas en dashboard ─────────────────────
function filtrarHerramientas(filtro) {
  const filas = document.querySelectorAll('#tabla-herramientas tbody tr');
  const mensajeVacio = document.getElementById('mensaje-vacio');
  const titulo = document.getElementById('titulo-inventario');
  const contador = document.getElementById('contador-herramientas');
  const cards = document.querySelectorAll('.stat-card');
  
  let visibles = 0;
  
  // ← NUEVO: Resetear todas las cards (incluyendo borde)
  cards.forEach((card) => {
    card.style.transform = '';
    card.style.boxShadow = '';
    card.style.border = '1px solid var(--border)'; // ← RESETEAR BORDE
  });
  
  const cardMap = {
    'todos': 0,
    'disponible': 1,
    'asignado': 2,
    'daniado': 3,
    'baja': 4
  };
  
  // ← MEJORADO: Marcar card activa con borde de color
  if (cardMap[filtro] !== undefined) {
    const activeCard = cards[cardMap[filtro]];
    activeCard.style.transform = 'translateY(-2px) scale(1.02)';
    activeCard.style.boxShadow = '0 8px 24px rgba(34, 211, 165, 0.25)';
    activeCard.style.border = '2px solid var(--accent)'; // ← BORDE DE COLOR
  }
  
  // Filtrar filas
  filas.forEach(fila => {
    const estado = fila.dataset.estado;
    let mostrar = false;
    
    if (filtro === 'todos') {
      mostrar = true;
    } else if (filtro === 'daniado') {
      mostrar = (estado === 'dañado' || estado === 'perdido');
    } else {
      mostrar = (estado === filtro);
    }
    
    if (mostrar) {
      fila.style.display = '';
      visibles++;
    } else {
      fila.style.display = 'none';
    }
  });
  
  // Actualizar título y contador
  const titulos = {
    'todos': '📋 Inventario completo',
    'disponible': '✅ Herramientas disponibles',
    'asignado': '👤 Herramientas asignadas',
    'daniado': '⚠️ Herramientas dañadas / perdidas',
    'baja': '🗑️ Herramientas dadas de baja'
  };
  
  titulo.textContent = titulos[filtro] || '📋 Inventario';
  contador.textContent = visibles;
  
  // Mostrar/ocultar mensaje de vacío
  if (visibles === 0) {
    document.querySelector('#tabla-herramientas').style.display = 'none';
    mensajeVacio.style.display = 'block';
  } else {
    document.querySelector('#tabla-herramientas').style.display = 'table';
    mensajeVacio.style.display = 'none';
  }
}

// Estilo hover para las cards (solo en dashboard)
if (document.querySelector('.stat-card')) {
  document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
      if (!this.style.transform) {
        this.style.transform = 'translateY(-2px)';
      }
    });
    
    card.addEventListener('mouseleave', function() {
      if (this.style.transform === 'translateY(-2px)') {
        this.style.transform = '';
      }
    });
  });
}