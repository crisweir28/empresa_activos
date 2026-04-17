/* app/static/js/administrativo/personal.js */
function editarPersonal(p) {
  document.getElementById('form-editar-p').action = `/administrativo/personal/${p.id}/editar`;
  document.getElementById('ep-nombre').value    = p.nombre    || '';
  document.getElementById('ep-apellido').value  = p.apellido  || '';
  document.getElementById('ep-telefono').value  = p.telefono  || '';
  document.getElementById('ep-area').value      = p.area      || '';
  document.getElementById('ep-correo').value    = p.correo    || '';
  document.getElementById('ep-jefe').value      = p.jefe_inmediato || '';
  document.getElementById('ep-licencia').value  = p.licencia_numero  || '';
  document.getElementById('ep-lic-vig').value   = p.licencia_vigencia || '';
  document.getElementById('ep-seguro').value    = p.seguro_medico || '';
  document.getElementById('ep-seg-vig').value   = p.seguro_vigencia  || '';
  document.getElementById('modal-editar').classList.add('open');
}