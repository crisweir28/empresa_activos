// app/static/js/ti/dataTable.js

(() => {

  // Variables globales seguras
  window.tablaEquipos = null;
  window.filtroActual = 'todos';

  $(document).ready(function () {

    // Verificar que exista la tabla
    if (!$('#tabla-equipos').length) {
      console.error('❌ No existe #tabla-equipos');
      return;
    }

    // Evitar doble inicialización
    if ($.fn.DataTable.isDataTable('#tabla-equipos')) {
      $('#tabla-equipos').DataTable().destroy();
    }

    // Inicializar DataTables
    window.tablaEquipos = $('#tabla-equipos').DataTable({
      language: {
        url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-MX.json'
      },

      pageLength: 25,

      lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, "Todos"]
      ],

      order: [[0, 'asc']],

      dom: 'lfrtip',

      buttons: [
        {
          extend: 'pdfHtml5',
          title: 'Equipos TI',
          exportOptions: {
            columns: [0, 1, 2, 3, 4, 5],
            modifier: {
              search: 'applied',
              order: 'applied',
              page: 'all'
            }
          }
        },

        {
          extend: 'excelHtml5',
          title: 'Equipos TI',
          exportOptions: {
            columns: [0, 1, 2, 3, 4, 5],
            modifier: {
              search: 'applied',
              order: 'applied',
              page: 'all'
            }
          }
        },

        {
          extend: 'csvHtml5',
          title: 'Equipos TI',
          exportOptions: {
            columns: [0, 1, 2, 3, 4, 5],
            modifier: {
              search: 'applied',
              order: 'applied',
              page: 'all'
            }
          }
        },

        {
          extend: 'print',
          title: 'Equipos TI',
          exportOptions: {
            columns: [0, 1, 2, 3, 4, 5],
            modifier: {
              search: 'applied',
              order: 'applied',
              page: 'all'
            }
          }
        }
      ],

      scrollX: true,

      columnDefs: [
        {
          orderable: false,
          targets: [6]
        }
      ]
    });

    // Filtro inicial
    window.filtrarEquipos('todos');

    // Hover cards
    configurarHoverCards();

    console.log('✅ DataTables inicializado correctamente');

  });

  // ════════════════════════════════════════
  // FILTRAR EQUIPOS
  // ════════════════════════════════════════

  window.filtrarEquipos = function (filtro) {

    window.filtroActual = filtro;

    document.querySelectorAll('.stat-card').forEach(card => {
      card.style.transform = '';
      card.style.boxShadow = '';
      card.style.border = '1px solid var(--border)';
    });

    const activeCard = document.getElementById('filtro-' + filtro);

    if (activeCard) {
      activeCard.style.transform = 'scale(1.02)';
      activeCard.style.boxShadow = '0 8px 24px rgba(37, 99, 235, 0.15)';
      activeCard.style.border = '2px solid #2563eb';
    }

    if (!window.tablaEquipos) return;

    if (filtro === 'todos') {

      window.tablaEquipos
        .columns([3, 4])
        .search('')
        .draw();

    } else if (filtro === 'bueno') {

      window.tablaEquipos
        .column(4)
        .search('bueno', false, false)
        .draw();

    } else if (filtro === 'malo') {

      window.tablaEquipos
        .column(4)
        .search('malo|dañado|regular', true, false)
        .draw();

    } else {

      window.tablaEquipos
        .column(3)
        .search(filtro, false, false)
        .draw();
    }

    actualizarContador();

    const titulos = {
      todos: '💻 Equipos registrados',
      almacen: '📦 Equipos en almacén',
      asignado: '👤 Equipos asignados',
      bueno: '✅ Equipos en buen estado',
      malo: '⚠️ Equipos en mal estado',
      mantenimiento: '🔧 Equipos en mantenimiento',
      baja: '🗑️ Equipos dados de baja'
    };

    const titulo = document.getElementById('titulo-equipos');

    if (titulo) {
      titulo.textContent = titulos[filtro] || '💻 Equipos';
    }
  };

  // ════════════════════════════════════════
  // CONTADOR
  // ════════════════════════════════════════

  function actualizarContador() {

    if (!window.tablaEquipos) return;

    let total = window.tablaEquipos
      .rows({ search: 'applied' })
      .count();

    const contador = document.getElementById('contador-equipos');

    if (contador) {
      contador.textContent = total;
    }
  }

  // ════════════════════════════════════════
  // REPORTES
  // ════════════════════════════════════════

  window.toggleReportMenu = function (event) {

    event.stopPropagation();

    const menu = document.getElementById('report-menu');

    if (!menu) return;

    menu.style.display =
      menu.style.display === 'none'
        ? 'block'
        : 'none';
  };

  window.generarReporte = function (formato) {

    const menu = document.getElementById('report-menu');

    if (menu) {
      menu.style.display = 'none';
    }

    if (!window.tablaEquipos) return;

    if (formato === 'pdf') {
      window.tablaEquipos.button(0).trigger();
    }

    else if (formato === 'excel') {
      window.tablaEquipos.button(1).trigger();
    }

    else if (formato === 'csv') {
      window.tablaEquipos.button(2).trigger();
    }

    else if (formato === 'print') {
      window.tablaEquipos.button(3).trigger();
    }

    if (typeof Swal !== 'undefined') {

      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: `📊 Generando ${formato.toUpperCase()}...`,
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true,
      });
    }
  };

  // ════════════════════════════════════════
  // CERRAR MENÚ
  // ════════════════════════════════════════

  document.addEventListener('click', function (event) {

    const menu = document.getElementById('report-menu');

    if (
      menu &&
      !event.target.closest('.report-dropdown') &&
      !event.target.closest('button')
    ) {
      menu.style.display = 'none';
    }
  });

  // ════════════════════════════════════════
  // HOVER CARDS
  // ════════════════════════════════════════

  function configurarHoverCards() {

    document.querySelectorAll('.stat-card').forEach(card => {

      card.addEventListener('mouseenter', function () {

        if (
          !this.style.transform ||
          this.style.transform === 'translateY(-2px)'
        ) {
          this.style.transform = 'translateY(-2px)';
        }
      });

      card.addEventListener('mouseleave', function () {

        if (this.style.transform === 'translateY(-2px)') {
          this.style.transform = '';
        }
      });
    });
  }

})();