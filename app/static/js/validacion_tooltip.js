/* ═══════════════════════════════════════════════════════
   VALIDACIÓN AL ENVIAR (con tooltips estilo Bootstrap)
   Ubicación: app/static/js/validacion_tooltip.js

   Función global validarFormulario(idForm) que usan
   submitEquipo(), submitVehiculo(), etc.
═══════════════════════════════════════════════════════ */

/**
 * Valida todos los campos required de un formulario.
 * Marca los inválidos con clase 'is-invalid' (muestra el tooltip).
 *
 * @param {string} idForm - ID del formulario a validar
 * @returns {boolean} true si todos los campos requeridos están llenos
 */
function validarFormulario(idForm) {
  const form = document.getElementById(idForm);
  if (!form) {
    console.warn('validarFormulario: no se encontró el form #' + idForm);
    return true;
  }

  const campos = form.querySelectorAll('[required]');
  let primerInvalido = null;
  let hayErrores = false;

  campos.forEach(function(campo) {
    // Limpiar estado previo
    campo.classList.remove('is-invalid');

    const valor = (campo.value || '').trim();

    if (!valor) {
      campo.classList.add('is-invalid');
      hayErrores = true;
      if (!primerInvalido) primerInvalido = campo;
    }
  });

  // Si hay errores, enfocar el primer campo inválido
  if (hayErrores && primerInvalido) {
    primerInvalido.focus();
    primerInvalido.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return !hayErrores;
}

/* Limpiar el error cuando el usuario empieza a escribir */
document.addEventListener('DOMContentLoaded', function() {
  document.addEventListener('input', function(e) {
    if (e.target.matches('.necesita-validacion [required]') &&
        e.target.classList.contains('is-invalid') &&
        e.target.value.trim()) {
      e.target.classList.remove('is-invalid');
    }
  });

  document.addEventListener('change', function(e) {
    if (e.target.matches('.necesita-validacion [required]') &&
        e.target.classList.contains('is-invalid') &&
        e.target.value.trim()) {
      e.target.classList.remove('is-invalid');
    }
  });
});