from functools import wraps
from flask import session, redirect, url_for

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorada

def rol_requerido(rol_permitido):
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if 'rol' not in session or session['rol'] != rol_permitido:
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorada
    return decorador
