from functools import wraps
from flask import abort
from flask_login import current_user, login_required

# =========================================================
# DECORATOR: LOGIN OBRIGATÓRIO
# =========================================================

def login_required_view(func):
    """
    Wrapper para garantir login antes de acessar a view.
    (Útil se quiser customizar depois)
    """
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


# =========================================================
# DECORATOR: APENAS ADMIN GLOBAL
# =========================================================

def admin_global_required(func):
    """
    Permite acesso apenas ao ADMIN_GLOBAL
    """
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin_global():
            abort(403)
        return func(*args, **kwargs)
    return wrapper


# =========================================================
# DECORATOR: ADMIN DA BARBEARIA
# =========================================================

def tenant_admin_required(func):
    """
    Permite acesso apenas ao TENANT_ADMIN
    """
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_tenant_admin():
            abort(403)
        return func(*args, **kwargs)
    return wrapper


# =========================================================
# DECORATOR: BARBEIRO
# =========================================================

def barber_required(func):
    """
    Permite acesso apenas ao BARBER
    """
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_barber():
            abort(403)
        return func(*args, **kwargs)
    return wrapper


# =========================================================
# DECORATOR: TENANT ADMIN OU BARBEIRO
# =========================================================

def tenant_or_barber_required(func):
    """
    Permite acesso ao TENANT_ADMIN ou BARBER
    """
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)

        if not (current_user.is_tenant_admin() or current_user.is_barber()):
            abort(403)

        return func(*args, **kwargs)
    return wrapper
