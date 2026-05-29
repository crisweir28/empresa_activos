// ── Inicializar DataTable ─────────────────────────────────────
let tablaAuditoria;

$(document).ready(function() {

  tablaAuditoria = $('#tabla-auditoria').DataTable({
    language: {
      lengthMenu: "Mostrar _MENU_ registros",
      search: "Buscar:",
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      infoEmpty: "Sin registros",
      infoFiltered: "(filtrado de _MAX_ registros)",
      zeroRecords: "No se encontraron resultados",
      emptyTable: "Sin datos disponibles",
      paginate: {
        first: "«",
        previous: "‹",
        next: "›",
        last: "»"
      }
    },

    pageLength: 10,
    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
    order: [[1, 'asc']],
    responsive: true
  });

  // Cargar columnas guardadas
  cargarConfiguracionColumnas();
});


// ═══════════════════════════════════════════════════════════
// CONFIGURACIÓN DE COLUMNAS
// ═══════════════════════════════════════════════════════════

const STORAGE_KEY_COLUMNAS = 'auditoria_columnas_visibles';

function abrirModalColumnas() {
  document.getElementById('modal-columnas').style.display = 'flex';
}

function cerrarModalColumnas() {
  document.getElementById('modal-columnas').style.display = 'none';
}

function guardarConfiguracionColumnas() {

  const checks = document.querySelectorAll('.check-columna input');
  const columnasVisibles = [];

  checks.forEach(check => {

    const index = parseInt(check.value);
    const visible = check.checked;

    tablaAuditoria.column(index).visible(visible);

    if (visible) {
      columnasVisibles.push(index);
    }
  });

  localStorage.setItem(
    STORAGE_KEY_COLUMNAS,
    JSON.stringify(columnasVisibles)
  );

  cerrarModalColumnas();
}

function cargarConfiguracionColumnas() {

  const guardadas = localStorage.getItem(STORAGE_KEY_COLUMNAS);

  if (!guardadas) {
    return;
  }

  const columnasVisibles = JSON.parse(guardadas);

  const checks = document.querySelectorAll('.check-columna input');

  checks.forEach(check => {

    const index = parseInt(check.value);
    const visible = columnasVisibles.includes(index);

    check.checked = visible;

    tablaAuditoria.column(index).visible(visible);
  });
}

function restablecerColumnas() {

  const checks = document.querySelectorAll('.check-columna input');

  checks.forEach(check => {
    check.checked = true;
  });

  guardarConfiguracionColumnas();
}


// ═══════════════════════════════════════════════════════════
// OBTENER COLUMNAS VISIBLES
// ═══════════════════════════════════════════════════════════

function obtenerColumnasVisibles() {

  const columnas = [];

  tablaAuditoria.columns().every(function(index) {

    if (this.visible()) {

      const nombre = $(this.header()).text().trim();

      if (nombre) {
        columnas.push(nombre);
      }
    }
  });

  return columnas;
}


// ═══════════════════════════════════════════════════════════
// EVENTOS GENERALES
// ═══════════════════════════════════════════════════════════

// Cerrar modal al hacer click fuera
window.addEventListener('click', function(e) {

  const modal = document.getElementById('modal-columnas');

  if (e.target === modal) {
    cerrarModalColumnas();
  }
});


// ── Toggle del menú de reportes ───────────────────────────────
function toggleReportMenu(event) {

  event.stopPropagation();

  const menu = document.getElementById('report-menu');

  menu.style.display =
    menu.style.display === 'none'
      ? 'block'
      : 'none';
}


// Cerrar el menú al hacer clic fuera
document.addEventListener('click', function(event) {

  const menu = document.getElementById('report-menu');

  if (
    menu &&
    !event.target.closest('.report-dropdown') &&
    !event.target.closest('button[onclick*="toggleReportMenu"]')
  ) {
    menu.style.display = 'none';
  }
});


// ═══════════════════════════════════════════════════════════
// GENERAR REPORTES
// ═══════════════════════════════════════════════════════════

function generarReporte(formato) {

  const params = new URLSearchParams(window.location.search);

  const tipo = params.get('tipo') || '';
  const condicion = params.get('condicion') || '';

  // Obtener columnas visibles
  const columnas = obtenerColumnasVisibles();

  let url = '';

  if (formato === 'print') {
    window.print();
    return;
  }

  if (formato === 'pdf') {

    url = "{{ url_for('rh.auditoria_reporte_pdf') }}";

  } else if (formato === 'excel') {

    url = "{{ url_for('rh.auditoria_reporte_excel') }}";

  } else if (formato === 'csv') {

    url = "{{ url_for('rh.auditoria_reporte_csv') }}";
  }

  const queryParams = new URLSearchParams();

  if (tipo) {
    queryParams.append('tipo', tipo);
  }

  if (condicion) {
    queryParams.append('condicion', condicion);
  }

  // ENVIAR COLUMNAS VISIBLES AL BACKEND
  queryParams.append(
    'columnas',
    JSON.stringify(columnas)
  );

  if (queryParams.toString()) {
    url += '?' + queryParams.toString();
  }

  window.location.href = url;

  document.getElementById('report-menu').style.display = 'none';
}