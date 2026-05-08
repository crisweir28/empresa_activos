/* app/static/js/ticketing/dashboard_ti.js */
let tecnicos = [];
let currentFilter = 'all';
let graficasCargadas = false;

// Cargar técnicos al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Cargando técnicos...');
    fetch('/ticketing/api/tecnicos')
        .then(response => response.json())
        .then(data => {
            console.log('Técnicos cargados:', data);
            tecnicos = data;
        })
        .catch(error => console.error('Error cargando técnicos:', error));
    
    // Event listeners para tarjetas de filtro
    document.querySelectorAll('.metric-card').forEach(card => {
        card.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            if (filter) {  // Solo aplicar filtro si tiene data-filter
                applyFilter(filter);
            }
        });
    });
    
    // Event listeners para botones de filtro adicionales
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            if (filter) {
                applyFilter(filter);
            }
        });
    });
    
    // Activar visualmente el filtro "todos" sin aplicarlo
    const allCard = document.querySelector('[data-filter="all"]');
    if (allCard) {
        allCard.classList.add('active');
    }
});

// Mapa de estados
const estadosMap = {
    'all': 'Todos',
    'abierto': 'Abiertos',
    'proceso': 'En Proceso',
    'cerrado': 'Cerrados',
    'urgente': 'Urgentes',
    'sin_asignar': 'Sin Asignar'
};

// Colores del tag de filtro
const filterColors = {
    'all': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    'abierto': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    'proceso': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    'cerrado': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    'urgente': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
    'sin_asignar': 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)'
};

function applyFilter(filter) {
    currentFilter = filter;
    
    // ═══════════════════════════════════════════════════════
    // QUITAR .ACTIVE DE TODAS LAS TARJETAS (incluida Estadísticas)
    // ═══════════════════════════════════════════════════════
    document.querySelectorAll('.metric-card').forEach(card => {
        card.classList.remove('active');
    });
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Activar SOLO la tarjeta seleccionada
    const activeCard = document.querySelector(`.metric-card[data-filter="${filter}"]`);
    const activeBtn = document.querySelector(`.filter-btn[data-filter="${filter}"]`);
    
    if (activeCard) {
        activeCard.classList.add('active');
    }
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // ═══════════════════════════════════════════════════════
    // OCULTAR GRÁFICAS Y MOSTRAR TABLA AL APLICAR FILTRO
    // ═══════════════════════════════════════════════════════
    const estadisticasSection = document.getElementById('estadisticasSection');
    const activosSection = document.querySelector('.tickets-section');
    
    if (estadisticasSection && activosSection) {
        estadisticasSection.style.display = 'none';
        activosSection.style.display = 'block';
    }
    
    // Mostrar/ocultar info de filtro con color correspondiente
    const filterInfo = document.getElementById('filterInfo');
    const filterName = document.getElementById('filterName');
    const filterTag = document.getElementById('filterTagElement');
    
    if (filter === 'all') {
        filterInfo.style.display = 'none';
    } else {
        filterInfo.style.display = 'block';
        filterName.textContent = estadosMap[filter];
        filterTag.style.background = filterColors[filter];
    }
    
    // Filtrar tickets
    const rows = document.querySelectorAll('.ticket-row');
    
    rows.forEach(row => {
        const estado = row.getAttribute('data-estado').toLowerCase();
        const prioridad = row.getAttribute('data-prioridad');
        const asignado = row.getAttribute('data-asignado');
        
        let showRow = false;
        
        if (filter === 'all') {
            showRow = true;
        } else if (filter === 'abierto') {
            showRow = estado === 'abierto';
        } else if (filter === 'proceso') {
            showRow = estado === 'en proceso' || estado === 'escalado' || estado === 'pendiente';
        } else if (filter === 'cerrado') {
            showRow = estado === 'resuelto' || estado === 'cerrado' || estado === 'sin solución';
        } else if (filter === 'urgente') {
            showRow = prioridad === 'Urgente';
        } else if (filter === 'sin_asignar') {
            showRow = asignado === 'no';
        }
        
        row.style.display = showRow ? '' : 'none';
    });
}

function clearFilter() {
    applyFilter('all');
}

function abrirModalAsignar(idTicket, numeroTicket) {
    console.log('Abriendo modal. Técnicos disponibles:', tecnicos);
    
    document.getElementById('ticketInfo').textContent = 'Ticket: ' + numeroTicket;
    document.getElementById('formAsignar').action = '/ticketing/ticket/' + idTicket + '/asignar';
    
    // Llenar select de técnicos
    const selectTecnico = document.querySelector('select[name="id_tecnico"]');
    selectTecnico.innerHTML = '<option value="">-- Selecciona un técnico --</option>';
    
    tecnicos.forEach(tecnico => {
        const option = document.createElement('option');
        option.value = tecnico.id;
        option.textContent = `${tecnico.nombre} (${tecnico.email})`;
        selectTecnico.appendChild(option);
    });
    
    // Abrir modal
    const modal = document.getElementById('modalAsignar');
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function cerrarModalAsignar() {
    const modal = document.getElementById('modalAsignar');
    modal.classList.remove('open');
    document.body.style.overflow = '';
}

// Cerrar modal al hacer clic fuera
document.getElementById('modalAsignar').addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalAsignar();
    }
});

// Función para cargar las gráficas
function cargarGraficas() {
    console.log('📊 Cargando estadísticas...');
    
    fetch('/ticketing/dashboard/estadisticas')
      .then(res => res.json())
      .then(data => {
        console.log('✅ Datos cargados:', data);
        
        // ───────────────────────────────────────────────────
        // 1. TICKETS POR DEPARTAMENTO (Barras)
        // ───────────────────────────────────────────────────
        const chartDeptos = new ApexCharts(document.querySelector("#chart-departamentos"), {
          series: [{
            name: 'Tickets',
            data: data.tickets_por_departamento.data
          }],
          chart: {
            type: 'bar',
            height: 300,
            toolbar: { show: false }
          },
          plotOptions: {
            bar: {
              borderRadius: 8,
              distributed: true,
              dataLabels: { position: 'top' }
            }
          },
          colors: ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff', '#e0f2fe', '#bae6fd'],
          dataLabels: {
            enabled: true,
            offsetY: -20,
            style: {
              fontSize: '12px',
              fontWeight: 600,
              colors: ["#304758"]
            }
          },
          xaxis: {
            categories: data.tickets_por_departamento.labels,
            labels: {
              style: { fontSize: '11px' },
              rotate: -45
            }
          },
          yaxis: {
            title: { text: 'Cantidad de Tickets' }
          },
          legend: { show: false },
          grid: {
            borderColor: '#e5e7eb',
            strokeDashArray: 4
          }
        });
        chartDeptos.render();
        
        // ───────────────────────────────────────────────────
        // 2. TENDENCIA MENSUAL (Área)
        // ───────────────────────────────────────────────────
        const chartTendencia = new ApexCharts(document.querySelector("#chart-tendencia"), {
          series: [{
            name: 'Tickets',
            data: data.tickets_por_mes.data
          }],
          chart: {
            type: 'area',
            height: 300,
            toolbar: { show: false }
          },
          stroke: {
            curve: 'smooth',
            width: 3
          },
          fill: {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: 0.6,
              opacityTo: 0.1,
              stops: [0, 90, 100]
            }
          },
          colors: ['#2563eb'],
          xaxis: {
            categories: data.tickets_por_mes.labels,
            labels: { style: { fontSize: '11px' } }
          },
          yaxis: {
            title: { text: 'Tickets Creados' }
          },
          dataLabels: { enabled: false },
          grid: {
            borderColor: '#e5e7eb',
            strokeDashArray: 4
          }
        });
        chartTendencia.render();
        
        // ───────────────────────────────────────────────────
        // 3. TIPOS DE PROBLEMA (Dona)
        // ───────────────────────────────────────────────────
        const chartCategorias = new ApexCharts(document.querySelector("#chart-categorias"), {
          series: data.tipos_problema.data,
          chart: {
            type: 'donut',
            height: 300
          },
          labels: data.tipos_problema.labels,
          colors: ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff'],
          legend: {
            position: 'bottom',
            fontSize: '12px'
          },
          plotOptions: {
            pie: {
              donut: {
                size: '65%',
                labels: {
                  show: true,
                  total: {
                    show: true,
                    label: 'Total Tickets',
                    fontSize: '14px',
                    fontWeight: 600
                  }
                }
              }
            }
          },
          dataLabels: {
            enabled: true,
            formatter: function(val) {
              return val.toFixed(1) + '%';
            }
          }
        });
        chartCategorias.render();
        
        // ───────────────────────────────────────────────────
        // 4. TIEMPO DE RESOLUCIÓN (Barras horizontales)
        // ───────────────────────────────────────────────────
        const chartTiempo = new ApexCharts(document.querySelector("#chart-tiempo"), {
          series: [{
            name: 'Horas Promedio',
            data: data.tiempo_resolucion.data
          }],
          chart: {
            type: 'bar',
            height: 300,
            toolbar: { show: false }
          },
          plotOptions: {
            bar: {
              horizontal: true,
              borderRadius: 6,
              distributed: true,
              dataLabels: { position: 'top' }
            }
          },
          colors: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5', '#ecfdf5', '#f0fdfa', '#ccfbf1', '#99f6e4', '#5eead4'],
          dataLabels: {
            enabled: true,
            offsetX: 30,
            style: {
              fontSize: '12px',
              fontWeight: 600
            },
            formatter: function(val) {
              return val + ' hrs';
            }
          },
          xaxis: {
            categories: data.tiempo_resolucion.labels,
            title: { text: 'Horas promedio' }
          },
          yaxis: {
            labels: { style: { fontSize: '11px' } }
          },
          legend: { show: false },
          grid: {
            borderColor: '#e5e7eb',
            strokeDashArray: 4
          }
        });
        chartTiempo.render();
        
        console.log('🎉 Gráficas renderizadas correctamente');
        
      })
      .catch(err => {
        console.error('❌ Error cargando estadísticas:', err);
        alert('Error al cargar estadísticas');
      });
}

// ═══════════════════════════════════════════════════════
// TOGGLE ESTADÍSTICAS (Expandir/Colapsar)
// ═══════════════════════════════════════════════════════
function toggleEstadisticas() {
    const estadisticasSection = document.getElementById('estadisticasSection');
    const activosSection = document.querySelector('.tickets-section');
    const estadisticasCard = document.querySelector('.estadisticas-card');
    
    if (estadisticasSection.style.display === 'none') {
        // Mostrar gráficas y OCULTAR tabla
        estadisticasSection.style.display = 'block';
        activosSection.style.display = 'none';
        
        // QUITAR .active de TODOS los filtros y activar SOLO estadísticas
        document.querySelectorAll('.metric-card').forEach(card => {
            card.classList.remove('active');
        });
        estadisticasCard.classList.add('active');
        
        // Cargar gráficas solo la primera vez
        if (!graficasCargadas) {
            cargarGraficas();
            graficasCargadas = true;
        }
        
        // Scroll suave hacia las gráficas
        estadisticasSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        // Ocultar gráficas y MOSTRAR tabla
        estadisticasSection.style.display = 'none';
        activosSection.style.display = 'block';
        estadisticasCard.classList.remove('active');
        
        // Reactivar el filtro actual
        applyFilter(currentFilter);
    }
}