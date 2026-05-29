/* ═══════════════════════════════════════════════════════
   VALIDACIÓN DE FORMULARIOS - Reutilizable
   Cualquier <form class="necesita-validacion"> se valida automáticamente
═══════════════════════════════════════════════════════ */

(function() {
  'use strict';

  // Activar al cargar el DOM
  document.addEventListener('DOMContentLoaded', function() {
    const formularios = document.querySelectorAll('form.necesita-validacion');

    formularios.forEach(function(form) {
      form.addEventListener('submit', function(event) {
        // Validar todos los campos requeridos del formulario
        const campos = form.querySelectorAll('[required]');
        let primerInvalido = null;
        let hayErrores = false;

        campos.forEach(function(campo) {
          // Limpiar estado previo
          campo.classList.remove('is-invalid', 'is-valid');

          const valor = campo.value.trim();

          if (!valor) {
            // Campo vacío → marcar como inválido
            campo.classList.add('is-invalid');
            hayErrores = true;
            if (!primerInvalido) primerInvalido = campo;
          } else {
            // Validación adicional por tipo
            if (campo.type === 'email' && !validarEmail(valor)) {
              campo.classList.add('is-invalid');
              hayErrores = true;
              if (!primerInvalido) primerInvalido = campo;
            } else if (campo.type === 'number' && isNaN(parseFloat(valor))) {
              campo.classList.add('is-invalid');
              hayErrores = true;
              if (!primerInvalido) primerInvalido = campo;
            } else {
              campo.classList.add('is-valid');
            }
          }
        });

        // Si hay errores → cancelar envío y enfocar el primero
        if (hayErrores) {
          event.preventDefault();
          event.stopPropagation();
          if (primerInvalido) {
            primerInvalido.focus();
            primerInvalido.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      });

      // Limpiar estado de error al empezar a escribir
      form.querySelectorAll('[required]').forEach(function(campo) {
        campo.addEventListener('input', function() {
          if (campo.classList.contains('is-invalid') && campo.value.trim()) {
            campo.classList.remove('is-invalid');
            campo.classList.add('is-valid');
          }
        });

        campo.addEventListener('change', function() {
          if (campo.classList.contains('is-invalid') && campo.value.trim()) {
            campo.classList.remove('is-invalid');
            campo.classList.add('is-valid');
          }
        });
      });
    });
  });

  function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
})();