const SOLO_LETRAS = /^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+$/;
    const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function soloLetras(input) {
        input.value = input.value.replace(/[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]/g, '');
    }
    function soloNumeros(input) {
        input.value = input.value.replace(/[^0-9]/g, '');
    }

    function setEstado(input, msgId, ok, msg) {
        const msgEl = document.getElementById('msg-' + msgId);
        input.classList.toggle('input-ok', ok);
        input.classList.toggle('input-err', !ok);
        if (msgEl) {
            msgEl.className = 'field-msg ' + (ok ? 'ok' : 'err');
            msgEl.textContent = ok ? '✓ ' + msg : '✗ ' + msg;
        }
        return ok;
    }

    function validarCampo(input, key) {
        const v = input.value.trim();
        switch (key) {
            case 'nombre':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, SOLO_LETRAS.test(v), SOLO_LETRAS.test(v) ? 'Se ve bien' : 'Solo letras y espacios');
            case 'ap':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, SOLO_LETRAS.test(v), SOLO_LETRAS.test(v) ? 'Se ve bien' : 'Solo letras y espacios');
            case 'am':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, SOLO_LETRAS.test(v), SOLO_LETRAS.test(v) ? 'Se ve bien' : 'Solo letras y espacios');
            case 'tel':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, /^\d{10}$/.test(v), /^\d{10}$/.test(v) ? 'Se ve bien' : '10 dígitos requeridos');
            case 'user':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, v.length >= 3, v.length >= 3 ? 'Se ve bien' : 'Mínimo 3 caracteres');
            case 'correo':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, REGEX_EMAIL.test(v), REGEX_EMAIL.test(v) ? 'Se ve bien' : 'Correo inválido');
            case 'pass':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, v.length >= 6, v.length >= 6 ? 'Se ve bien' : 'Mínimo 6 caracteres');
            case 'e-nombre':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, SOLO_LETRAS.test(v), SOLO_LETRAS.test(v) ? 'Se ve bien' : 'Solo letras y espacios');
            case 'e-ap':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, SOLO_LETRAS.test(v), SOLO_LETRAS.test(v) ? 'Se ve bien' : 'Solo letras y espacios');
            case 'e-am':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, SOLO_LETRAS.test(v), SOLO_LETRAS.test(v) ? 'Se ve bien' : 'Solo letras y espacios');
            case 'e-tel':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, /^\d{10}$/.test(v), /^\d{10}$/.test(v) ? 'Se ve bien' : '10 dígitos requeridos');
            case 'e-user':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, v.length >= 3, v.length >= 3 ? 'Se ve bien' : 'Mínimo 3 caracteres');
            case 'e-correo':
                if (!v) return setEstado(input, key, false, 'Campo obligatorio');
                return setEstado(input, key, REGEX_EMAIL.test(v), REGEX_EMAIL.test(v) ? 'Se ve bien' : 'Correo inválido');
            case 'e-pass':
                if (!v) {
                    input.classList.remove('input-ok', 'input-err');
                    const msgEl = document.getElementById('msg-e-pass');
                    if (msgEl) msgEl.textContent = '';
                    return true;
                }
                return setEstado(input, key, v.length >= 6, v.length >= 6 ? 'Se ve bien' : 'Mínimo 6 caracteres');
        }
        return true;
    }

    function submitValidado(formId) {
        const isNuevo = formId === 'form-nuevo-usuario';
        const form = document.getElementById(formId);

        const campos = isNuevo
            ? [
                { el: form.querySelector('[name="nombre"]'), key: 'nombre' },
                { el: form.querySelector('[name="apellido_paterno"]'), key: 'ap' },
                { el: form.querySelector('[name="apellido_materno"]'), key: 'am' },
                { el: form.querySelector('[name="telefono"]'), key: 'tel' },
                { el: form.querySelector('[name="username"]'), key: 'user' },
                { el: form.querySelector('[name="correo"]'), key: 'correo' },
                { el: form.querySelector('[name="password"]'), key: 'pass' },
            ]
            : [
                { el: document.getElementById('e-nombre'), key: 'e-nombre' },
                { el: document.getElementById('e-ap'), key: 'e-ap' },
                { el: document.getElementById('e-am'), key: 'e-am' },
                { el: document.getElementById('e-tel'), key: 'e-tel' },
                { el: document.getElementById('e-user'), key: 'e-user' },
                { el: document.getElementById('e-correo'), key: 'e-correo' },
                { el: document.getElementById('e-pass'), key: 'e-pass' },
            ];

        let ok = true;
        for (const c of campos) {
            if (c.el && !validarCampo(c.el, c.key)) ok = false;
        }
        if (ok) form.submit();
        else {
            const primer = form.querySelector('.input-err');
            if (primer) primer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    async function editarUsuario(id) {
        const res = await fetch(`/usuarios/api/${id}`);
        const u = await res.json();

        document.getElementById('form-editar').action = `/usuarios/${id}/editar`;

        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) { el.value = val || ''; el.classList.remove('input-ok', 'input-err'); }
            const msg = document.getElementById('msg-' + id);
            if (msg) msg.textContent = '';
        };

        setVal('e-nombre', u.nombre);
        setVal('e-ap', u.apellido_paterno);
        setVal('e-am', u.apellido_materno);
        setVal('e-tel', u.telefono);
        setVal('e-user', u.username);
        setVal('e-correo', u.correo);
        setVal('e-pass', '');

        // ✅ Estatus
        if (document.getElementById('e-estatus'))
            document.getElementById('e-estatus').value = u.estatus ? '1' : '0';
        
        // ✅ Área (solo Super Admin puede cambiar)
        if (document.getElementById('e-depto')) {
            document.getElementById('e-depto').value = u.departamento_id || '';
        }
        
        // ✅ Tipo (solo Super Admin puede cambiar)
        if (document.getElementById('e-tipo')) {
            document.getElementById('e-tipo').value = u.tipo_usuario || 'empleado';
        }
        
        // ✅ Rol del sistema (solo Super Admin puede cambiar)
        if (document.getElementById('e-rol')) {
            document.getElementById('e-rol').value = u.rol_id || '';
        }

        const panel = document.getElementById('panel-bloqueado');
        if (panel) {
            panel.style.display = u.bloqueado ? 'flex' : 'none';
            document.getElementById('form-desbloquear').action = `/admin/desbloquear/${id}`;
        }

        document.getElementById('modal-editar').classList.add('open');
    }

    function desbloquearConfirm() {
        Swal.fire({
            title: '¿Desbloquear cuenta?',
            html: 'El usuario podrá volver a iniciar sesión normalmente.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#f59e0b',
            cancelButtonColor: '#6b7280',
            confirmButtonText: '🔓 Sí, desbloquear',
            cancelButtonText: 'Cancelar',
            reverseButtons: true,
        }).then(result => {
            if (result.isConfirmed) document.getElementById('form-desbloquear').submit();
        });
    }

    function eliminarUsuario(username, url) {
        Swal.fire({
            title: '¿Eliminar usuario?',
            html: `El usuario <strong>${username}</strong> será eliminado permanentemente.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc2626',
            cancelButtonColor: '#6b7280',
            confirmButtonText: '🗑️ Sí, eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true,
            focusCancel: true,
        }).then(result => {
            if (result.isConfirmed) {
                const form = document.getElementById('form-eliminar');
                form.action = url;
                form.submit();
            }
        });
    }

// ══════════════════════════════════════════════════════════════
// DROPDOWN SIMPLE DE ÁREAS
// ══════════════════════════════════════════════════════════════

function toggleAreaDropdown() {
    const dropdown = document.getElementById('area-dropdown');
    dropdown.classList.toggle('show');
}

// Cerrar al hacer clic fuera
document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('area-dropdown');
    const button = document.querySelector('.area-filter-btn');
    
    if (dropdown && button) {
        if (!button.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    }
});