// cambiar_password.js — Lógica para la pantalla de nueva contraseña

const NIVEL_COLOR = {
  "Débil":   "#f87171",
  "Regular": "#fbbf24",
  "Buena":   "#a78bfa",
  "Fuerte":  "#22d3a5",
};

function aplicarBarra(fillId, fortaleza, nivel) {
  const fill = document.getElementById(fillId);
  if (!fill) return;
  fill.style.width      = fortaleza + "%";
  fill.style.background = NIVEL_COLOR[nivel] || "#f87171";
}

function toggleVer(id, btn) {
  const input = document.getElementById(id);
  if (!input) return;
  input.type      = input.type === "password" ? "text" : "password";
  btn.textContent = input.type === "password" ? "👁" : "🙈";
}

function limpiar() {
  document.getElementById("nueva").value = "";
  document.getElementById("manual-strength").style.display = "none";
  validarBtn();
}

function validarBtn() {
  const nueva     = document.getElementById("nueva").value;
  const confirmar = document.getElementById("confirmar").value;
  document.getElementById("btn-guardar").disabled =
    nueva.length < 6 || nueva !== confirmar;
}

async function generarSugerida() {
  const frase = document.getElementById("frase-input").value.trim();
  if (frase.length < 4) { alert("Escribe al menos 4 caracteres."); return; }

  const res  = await fetch("/api/reforzar?frase=" + encodeURIComponent(frase));
  const data = await res.json();
  if (data.error) { alert(data.error); return; }

  document.getElementById("sugerida-valor").textContent = data.sugerida;
  document.getElementById("sugerida-len").textContent   =
    `${data.longitud} caracteres · ${data.nivel}`;

  aplicarBarra("sug-fill", data.fortaleza, data.nivel);
  document.getElementById("sugerida-box").classList.add("visible");
}

function usarSugerida() {
  const val = document.getElementById("sugerida-valor").textContent;
  document.getElementById("nueva").value     = val;
  document.getElementById("confirmar").value = val;
  document.getElementById("nueva").type      = "text";
  analizarManual(val);
  validarBtn();
  document.getElementById("form-guardar").scrollIntoView({ behavior: "smooth" });
}

async function analizarManual(val) {
  const wrap = document.getElementById("manual-strength");
  if (!val) { if (wrap) wrap.style.display = "none"; validarBtn(); return; }
  if (wrap) wrap.style.display = "block";

  const res  = await fetch("/api/analizar?password=" + encodeURIComponent(val));
  const data = await res.json();
  aplicarBarra("man-fill", data.fortaleza, data.nivel);
  validarBtn();
}