// activos.js — Lógica para el modal de editar activo

function editarActivo(a) {
  document.getElementById('form-editar').action = `/activos/${a.id}/editar`;
  document.getElementById('e-nombre').value = a.nombre          || '';
  document.getElementById('e-serie').value  = a.numero_serie    || '';
  document.getElementById('e-desc').value   = a.descripcion     || '';
  document.getElementById('e-cat').value    = a.categoria       || '';
  document.getElementById('e-estado').value = a.estado          || 'activo';
  document.getElementById('e-valor').value  = a.valor           || 0;
  document.getElementById('e-fecha').value  = a.fecha_adquisicion || '';
  document.getElementById('e-depto').value  = a.departamento_id || '';
  document.getElementById('modal-editar').classList.add('open');
}