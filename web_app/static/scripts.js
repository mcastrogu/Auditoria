document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('togglesidebar');
  const sidebar = document.getElementById('sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('oculto');
    });
  }
});

/* SCRIPT PARA FILTRO */
function filtrarPorDNI() {
  const input = document.getElementById("buscarDNI").value.toUpperCase();
  const filas = document.querySelectorAll("#tablaUsuarios tbody tr");

  filas.forEach(fila => {
    const celdaDNI = fila.children[1].textContent.toUpperCase();
    fila.style.display = celdaDNI.includes(input) ? "" : "none";
  });
}

/* ABRIR MODAL PARA NUEVO USUARIO */
function abrirModal() {
  const modal = document.getElementById('modalUsuario');
  modal.style.display = 'flex';

  // Limpiar
  document.getElementById('form-usuario').reset();

  // Título y botón
  document.querySelector('.subtitulo').textContent = 'Nuevo Usuario';
  document.getElementById('btn-submit').textContent = 'Registrar';

  // Estado
  document.getElementById('modo-formulario').value = 'registro';

  document.getElementById('password').required = true;

}


/* CERRAR MODAL */
function cerrarModal() {
  const modal = document.getElementById('modalUsuario');
  modal.style.display = 'none';
}

/* ABRIR MODAL PARA EDITAR USUARIO */
function abrirModalEditar(btn) {
  const modal = document.getElementById('modalUsuario');
  modal.style.display = 'flex';

  // Cambiar título y botón
  document.querySelector('.subtitulo').textContent = 'Editar Usuario';
  const submitBtn = document.querySelector('.form-buttons button[type="submit"]');
  submitBtn.textContent = 'Guardar cambios';

  // Llenar campos
  document.getElementById('dni').value = btn.dataset.dni;
  document.getElementById('nombre_usuario').value = btn.dataset.usuario;
  document.getElementById('nombres').value = btn.dataset.nombres;
  document.getElementById('apellidos').value = btn.dataset.apellidos;
  document.getElementById('correo').value = btn.dataset.correo;
  document.getElementById('rol').value = btn.dataset.rol;


  // Marcar modo edición
  document.getElementById('modo-formulario').value = 'editar';
  document.getElementById('id-usuario').value = btn.dataset.id;

  document.getElementById('password').required = false;

}

// Botón
document.getElementById('btn-submit').textContent = 'Guardar cambios';

/* VALIDACIONES Y TOAST */
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form-usuario');

  if (form) {
    const modo = document.getElementById('modo-formulario').value;
    const password = form.querySelector('input[name="password"]').value.trim();

    if (modo === 'registro' && password === '') {
      e.preventDefault();
      return;
    }

    form.addEventListener('submit', function (e) {
      const dni = form.querySelector('input[name="dni"]').value.trim();
      const nombres = form.querySelector('input[name="nombres"]').value.trim();
      const apellidos = form.querySelector('input[name="apellidos"]').value.trim();

      // Validaciones
      if (!/^\d{8}$/.test(dni)) {
        alert('El DNI debe contener exactamente 8 dígitos.');
        e.preventDefault();
        return;
      }

      if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(nombres)) {
        alert('Los nombres solo deben contener letras.');
        e.preventDefault();
        return;
      }

      if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(apellidos)) {
        alert('Los apellidos solo deben contener letras.');
        e.preventDefault();
        return;
      }

      // Mostrar toast
      const modo = document.getElementById('modo-formulario').value;
      if (modo === 'editar') {
        mostrarToast('Cambios guardados correctamente.');
      } else {
        mostrarToast('Usuario registrado correctamente.');
      }
    });
  }


});

/* TOAST VISUAL */
function mostrarToast(mensaje) {
  const toast = document.getElementById('toast');
  toast.textContent = mensaje;
  toast.classList.add('toast-activo');

  setTimeout(() => {
    toast.classList.remove('toast-activo');
  }, 3000);
}

/*ELIMINAR USUARIO*/
function confirmarEliminacion(btn) {
  const id = btn.dataset.id;
  if (confirm("¿Estás seguro de que deseas eliminar este usuario?")) {
    window.location.href = `/eliminar_usuario/${id}`;
  }
}


