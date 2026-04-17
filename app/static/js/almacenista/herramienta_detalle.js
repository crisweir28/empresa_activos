// ── Tabs ─────────────────────────────────────────────────────
function showTab(name, btn) {
  document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).style.display = 'block';
  btn.classList.add('active');
}

const ICONOS_MIME = {
  'application/pdf': '📄',
  'application/msword': '📝',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '📝',
  'application/vnd.ms-excel': '📊',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '📊',
  'text/plain': '📃', 'text/csv': '📊',
};
const EXTS_IMAGEN = new Set(['png','jpg','jpeg','gif','webp']);

function previewAdjunto(input) {
  const panel = document.getElementById('adjunto-preview');
  if (!input.files || !input.files[0]) { panel.style.display = 'none'; return; }
  const file = input.files[0];
  const ext  = file.name.split('.').pop().toLowerCase();
  const size = file.size > 1024*1024
    ? (file.size/(1024*1024)).toFixed(1)+' MB'
    : (file.size/1024).toFixed(0)+' KB';
  document.getElementById('adjunto-icono').textContent  = EXTS_IMAGEN.has(ext) ? '🖼️' : (ICONOS_MIME[file.type] || '📎');
  document.getElementById('adjunto-nombre').textContent = file.name;
  document.getElementById('adjunto-size').textContent   = size;
  panel.style.display = 'flex';
}
// ── Preview antes de subir ────────────────────────────────────
function previewAntes(input) {
  const wrap = document.getElementById('preview-wrap');
  const img  = document.getElementById('preview-img');
  const nom  = document.getElementById('preview-nombre');
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      img.src = e.target.result;
      nom.textContent = input.files[0].name;
      wrap.style.display = 'block';
    };
    reader.readAsDataURL(input.files[0]);
  } else {
    wrap.style.display = 'none';
  }
}

// ── Lightbox ──────────────────────────────────────────────────
function abrirLightbox(url, tipo, fecha, nombre) {
  document.getElementById('lb-img').src               = url;
  document.getElementById('lb-tipo').textContent      = tipo;
  document.getElementById('lb-fecha').textContent     = fecha;
  document.getElementById('lb-nombre').textContent    = nombre;
  document.getElementById('lb-download').href         = url;
  document.getElementById('lb-download').download     = nombre;
  document.getElementById('lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function cerrarLightbox() {
  document.getElementById('lightbox').classList.remove('open');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') cerrarLightbox();
});