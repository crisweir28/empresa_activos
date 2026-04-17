/* app/static/js/proyectos/detalle.js
 * JS específico del template proyectos/detalle.html
 * Depende de: proyectos.js (debe cargarse antes)
 *
 * Nota: la variable `activos` (con datos de Jinja) se define inline
 *       en el template, antes de cargar este archivo.
 */

// ── Abrir modal de editar ──────────────────────────────────
function abrirEditar() {
  abrirModal('modal-editar');
}

// ── Eliminar proyecto con confirmación ─────────────────────
function eliminarProyecto(nombre, url) {
  confirmarAccion({
    titulo: '¿Eliminar proyecto?',
    mensaje: `El proyecto <strong>${nombre}</strong> y todos sus datos serán eliminados permanentemente.`,
    confirmText: '🗑️ Sí, eliminar',
    icon: 'warning',
    onConfirm: () => {
      const form = document.getElementById('form-eliminar');
      form.action = url;
      form.submit();
    }
  });
}

// ── Quitar persona del proyecto ────────────────────────────
function quitarPersonal(nombre, asignacionId) {
  confirmarAccion({
    titulo: '¿Quitar del proyecto?',
    mensaje: `<strong>${nombre}</strong> será removido de este proyecto.`,
    confirmText: 'Sí, quitar',
    icon: 'question',
    onConfirm: () => {
      document.getElementById(`form-quitar-${asignacionId}`).submit();
    }
  });
}

// ── Filtrar activos por tipo en el modal ───────────────────
// Depende de la variable global `activos` (definida inline en el template)
function filtrarActivos(tipo) {
  const sel = document.getElementById('select-activo');
  sel.innerHTML = '<option value="">— Seleccionar activo —</option>';
  if (!tipo || !activos[tipo]) { sel.disabled = true; return; }
  activos[tipo].forEach(a => {
    const opt = document.createElement('option');
    opt.value = a.id;
    opt.textContent = a.nombre;
    sel.appendChild(opt);
  });
  sel.disabled = false;
}