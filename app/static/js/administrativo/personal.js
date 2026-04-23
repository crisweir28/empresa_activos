/* app/static/js/administrativo/personal.js */
function editarPersonalData(btn) {
  const d = btn.dataset;
  document.getElementById('form-editar-p').action = `/administrativo/personal/${d.id}/editar`;
  document.getElementById('ep-nombre').value    = d.nombre;
  document.getElementById('ep-apellido').value  = d.apellido;
  document.getElementById('ep-telefono').value  = d.telefono;
  document.getElementById('ep-area').value      = d.area;
  document.getElementById('ep-correo').value    = d.correo;
  document.getElementById('ep-jefe').value      = d.jefe;
  document.getElementById('ep-licencia').value  = d.licencia;
  document.getElementById('ep-lic-vig').value   = d.licVig;
  document.getElementById('ep-seguro').value    = d.seguro;
  document.getElementById('ep-seg-vig').value   = d.segVig;
  document.getElementById('modal-editar').classList.add('open');
}