# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from ..models.usuario import Usuario, pwd_context
from ..extensions import db
from datetime import datetime, timedelta
import random
import secrets
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

auth_bp = Blueprint("auth", __name__)

# ─── Configuración de bloqueo ─────────────────────────────────
MAX_INTENTOS    = 3



# ─── Generador de contraseña ──────────────────────────────────
ESPECIALES = ['!', '@', '#', '$', '%', '&', '*', '?', ',', '.', '-', '_', '|', '=', '+', '^']

def generar_password(frase: str) -> str:
    chars = list(frase)
    n = len(frase)
    if n < 9:
        pos = random.randint(1, max(1, n - 1))
        chars.insert(pos, random.choice(ESPECIALES))
    elif n > 12:
        posiciones = sorted(random.sample(range(1, n), min(2, n - 1)))
        for pos in reversed(posiciones):
            chars.insert(pos, random.choice(ESPECIALES))
    return "".join(chars)


def analizar_password(password: str) -> dict:
    n = len(password)
    tiene_especial = any(c in "".join(ESPECIALES) + "!@#$%^&*()" for c in password)
    puntos = 0
    if n >= 6:  puntos += 20
    if n >= 9:  puntos += 20
    if n >= 12: puntos += 20
    if n >= 16: puntos += 10
    if tiene_especial: puntos += 30
    if puntos <= 25:   nivel = "Débil"
    elif puntos <= 50: nivel = "Regular"
    elif puntos <= 75: nivel = "Buena"
    else:              nivel = "Fuerte"
    return {"fortaleza": puntos, "nivel": nivel, "longitud": n}


# ─── Helpers de bloqueo ───────────────────────────────────────
def _esta_bloqueado(user: Usuario) -> bool:
    return bool(user.BloqueadoHasta and user.BloqueadoHasta > datetime.now())


def _registrar_fallo(user: Usuario):
    """Suma un intento fallido y bloquea si llega al límite."""
    user.IntentosFallidos = (user.IntentosFallidos or 0) + 1
    if user.IntentosFallidos >= MAX_INTENTOS:
        user.BloqueadoHasta = datetime(9999, 12, 31)
        user.IntentosFallidos = 0
    db.session.commit()


def _resetear_intentos(user: Usuario):
    """Limpia intentos al hacer login exitoso."""
    if user.IntentosFallidos or user.BloqueadoHasta:
        user.IntentosFallidos = 0
        user.BloqueadoHasta   = None
        db.session.commit()


def _obtener_admins_ti():
    """Obtiene los correos de todos los Administradores (IdRol=1)."""
    admins = db.session.execute(text("""
        SELECT CONCAT(Nombre,' ',ApellidoPaterno) AS NombreCompleto, Correo
        FROM usuario
        WHERE IdRol = 1 AND Estatus = 1
    """)).fetchall()
    return admins


def _enviar_correo_desbloqueo(usuario_bloqueado: Usuario):
    """Manda correo a todos los admins pidiendo desbloqueo."""
    admins = _obtener_admins_ti()
    if not admins:
        return False

    smtp_server = current_app.config.get("MAIL_SERVER",        "smtp.gmail.com")
    smtp_port   = int(current_app.config.get("MAIL_PORT",      587))
    smtp_user   = current_app.config.get("MAIL_USERNAME")
    smtp_pass   = current_app.config.get("MAIL_PASSWORD")
    remitente   = current_app.config.get("MAIL_DEFAULT_SENDER", smtp_user)

    nombre_bloqueado = f"{usuario_bloqueado.Nombre} {usuario_bloqueado.ApellidoPaterno}"
    user_bloqueado   = usuario_bloqueado.NombreUsuario

    for admin in admins:
        asunto = f"🔒 Solicitud de desbloqueo — {nombre_bloqueado}"

        cuerpo_html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family:'DM Sans',Arial,sans-serif;background:#f4f4f8;margin:0;padding:40px 20px">
  <div style="max-width:520px;margin:0 auto;background:#fff;border:1px solid #e0e0ef;
              border-radius:16px;padding:40px;box-shadow:0 4px 20px rgba(0,0,0,.06)">

    <div style="margin-bottom:24px">
      <span style="font-weight:800;font-size:18px;color:#9B2335">🏢 ActivosApp</span>
    </div>

    <h1 style="color:#1a1a2e;font-size:20px;font-weight:800;margin-bottom:8px">
      Solicitud de desbloqueo de cuenta
    </h1>
    <p style="color:#6b6b8a;font-size:14px;line-height:1.7;margin-bottom:24px">
      Hola <strong style="color:#1a1a2e">{admin.NombreCompleto}</strong>,<br>
      el siguiente usuario ha sido bloqueado por múltiples intentos fallidos
      de inicio de sesión y solicita que se desbloquee su cuenta.
    </p>

    <div style="background:#f8f8fc;border:1px solid #e0e0ef;border-radius:10px;
                padding:18px 20px;margin-bottom:28px">
      <table style="font-size:13px;width:100%">
        <tr>
          <td style="color:#6b6b8a;padding:4px 0;width:130px">Usuario</td>
          <td style="font-weight:700;color:#1a1a2e;font-family:monospace">{user_bloqueado}</td>
        </tr>
        <tr>
          <td style="color:#6b6b8a;padding:4px 0">Nombre</td>
          <td style="font-weight:600;color:#1a1a2e">{nombre_bloqueado}</td>
        </tr>
        <tr>
          <td style="color:#6b6b8a;padding:4px 0">Correo</td>
          <td style="color:#1a1a2e">{usuario_bloqueado.Correo}</td>
        </tr>
        <tr>
          <td style="color:#6b6b8a;padding:4px 0">Bloqueado hasta</td>
          <td style="color:#e53e3e;font-weight:600">
            {usuario_bloqueado.BloqueadoHasta.strftime('%d/%m/%Y %H:%M') if usuario_bloqueado.BloqueadoHasta else 'indefinido'}
          </td>
        </tr>
      </table>
    </div>

    <p style="color:#6b6b8a;font-size:13px;line-height:1.7;margin-bottom:20px">
      Para desbloquearlo, ingresa al sistema con tu cuenta de administrador,
      ve a <strong>Administración → Usuarios</strong> y usa el botón
      <strong>"Desbloquear"</strong> en la fila de este usuario.
    </p>

    <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;
                padding:12px 16px;font-size:12px;color:#856404">
      ⚠️ Si no reconoces a este usuario o sospechas de actividad maliciosa,
      no desbloquees la cuenta y repórtalo al administrador del sistema.
    </div>

    <p style="color:#b0b0c8;font-size:11px;margin-top:24px;border-top:1px solid #f0f0f8;
              padding-top:16px">
      Este correo fue generado automáticamente por ActivosApp.
    </p>
  </div>
</body>
</html>"""

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = asunto
            msg["From"]    = remitente
            msg["To"]      = admin.Correo
            msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(smtp_user, smtp_pass)
                server.sendmail(remitente, admin.Correo, msg.as_string())
        except Exception as e:
            current_app.logger.error(f"Error enviando correo a {admin.Correo}: {e}")

    return True


# ─── Rutas principales ────────────────────────────────────────
@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("activos.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("activos.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = Usuario.query.filter_by(
            NombreUsuario=username,
            Estatus=True
        ).first()

        if not user:
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("login.html")

        # ── Verificar si está bloqueado ──────────────────────
        bloqueado = _esta_bloqueado(user)
        if bloqueado:
            return render_template("login.html",
                                   bloqueado=True,
                                   username=username)

        # ── Verificar contraseña ─────────────────────────────
        if user.check_password(password):
            _resetear_intentos(user)
            login_user(user, remember=request.form.get("remember") == "on")
            if user.PrimerLogin:
                return redirect(url_for("auth.sugerir_cambio"))
            return redirect(request.args.get("next") or url_for("activos.dashboard"))

        # ── Contraseña incorrecta ────────────────────────────
        _registrar_fallo(user)

        bloqueado = _esta_bloqueado(user)
        if bloqueado:
            return render_template("login.html",
                           bloqueado=True,
                           username=username)
        flash(
            f"Usuario o contraseña incorrectos. ")

    return render_template("login.html")


# ─── Solicitar desbloqueo (sin login) ────────────────────────
@auth_bp.route("/solicitar-desbloqueo", methods=["POST"])
def solicitar_desbloqueo():
    username = request.form.get("username", "").strip()

    user = Usuario.query.filter_by(NombreUsuario=username, Estatus=True).first()

    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("auth.login"))

    bloqueado = _esta_bloqueado(user)
    if not bloqueado:
        flash("Esta cuenta no está bloqueada.", "info")
        return redirect(url_for("auth.login"))

    try:
        ok = _enviar_correo_desbloqueo(user)
        if ok:
            flash(
                "✅ Solicitud enviada. Un administrador de TI recibirá tu solicitud "
                "y desbloqueará tu cuenta en breve.",
                "success"
            )
        else:
            flash(
                "No se encontraron administradores disponibles. "
                "Contacta directamente al área de TI.",
                "warning"
            )
    except Exception as e:
        current_app.logger.error(f"Error al enviar solicitud de desbloqueo: {e}")
        flash("Error al enviar la solicitud. Contacta directamente al área de TI.", "error")

    return redirect(url_for("auth.login"))

# ─── Desbloquear usuario (solo admin) ────────────────────────
@auth_bp.route("/admin/desbloquear/<int:uid>", methods=["POST"])
@login_required
def desbloquear_usuario(uid):
    if current_user.rol != 'admin':
        flash("Sin permiso para esta acción.", "error")
        return redirect(url_for("activos.dashboard"))

    user = Usuario.query.get_or_404(uid)
    user.IntentosFallidos = 0
    user.BloqueadoHasta   = None
    db.session.commit()
    flash(f"Usuario {user.NombreUsuario} desbloqueado correctamente.", "success")
    return redirect(url_for("usuarios.lista"))

@auth_bp.route("/sugerir-cambio", methods=["GET", "POST"])
@login_required
def sugerir_cambio():
    if not current_user.PrimerLogin:
        return redirect(url_for("activos.dashboard"))

    if request.method == "POST":
        if request.form.get("decision") == "si":
            return redirect(url_for("auth.cambiar_password"))
        try:
            current_user.PrimerLogin = False
            db.session.commit()
        except Exception:
            db.session.rollback()
        return redirect(url_for("activos.dashboard"))

    return render_template("sugerir_cambio.html")


@auth_bp.route("/cambiar-password", methods=["GET", "POST"])
@login_required
def cambiar_password():
    if not current_user.PrimerLogin:
        return redirect(url_for("activos.dashboard"))

    error = None
    if request.method == "POST":
        nueva     = request.form.get("nueva_password", "").strip()
        confirmar = request.form.get("confirmar_password", "").strip()

        if len(nueva) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        elif nueva != confirmar:
            error = "Las contraseñas no coinciden."
        else:
            try:
                current_user.set_password(nueva)
                current_user.PrimerLogin = False
                db.session.commit()
                flash("¡Contraseña actualizada correctamente!", "success")
                return redirect(url_for("activos.dashboard"))
            except Exception as e:
                db.session.rollback()
                error = f"Error al guardar: {str(e)}"

    return render_template("cambiar_password.html", error=error)


# ─── Recuperación de contraseña ───────────────────────────────
@auth_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if current_user.is_authenticated:
        return redirect(url_for("activos.dashboard"))

    enviado       = False
    error         = None
    email_enviado = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            error = "Ingresa tu correo electrónico."
        else:
            token = secrets.token_urlsafe(48)
            try:
                user = Usuario.query.filter(
                    Usuario.Correo.ilike(email),
                    Usuario.Estatus == True
                ).first()

                if user:
                    db.session.execute(
                        text("UPDATE password_reset_tokens SET usado = 1 WHERE usuario_id = :uid AND usado = 0"),
                        {"uid": user.IdUsuario}
                    )
                    db.session.execute(
                        text("INSERT INTO password_reset_tokens (usuario_id, token, expira_en) VALUES (:uid, :token, DATE_ADD(NOW(), INTERVAL 5 MINUTE))"),
                        {"uid": user.IdUsuario, "token": token}
                    )
                    db.session.commit()

                    import os
                    host = request.host_url
                    if 'localhost' in host or '127.0.0.1' in host:
                        app_host = os.getenv('APP_HOST', '').strip()
                        if app_host:
                            host = f"http://{app_host}:5000/"
                    link = f"{host}reset-password/{token}"
                    _enviar_correo_reset(email, user.Nombre, link)

                enviado       = True
                email_enviado = email

            except Exception as e:
                import traceback
                traceback.print_exc()
                error = f"Error al procesar: {str(e)}"

    return render_template("recuperar.html", enviado=enviado, error=error, email_enviado=email_enviado)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("activos.dashboard"))

    error    = None
    expirado = False

    if request.method == "GET":
        try:
            row = db.session.execute(
                text("""
                    SELECT IF(expira_en < NOW(), 1, 0) AS expirado, usado
                    FROM password_reset_tokens WHERE token = :token
                """),
                {"token": token}
            ).fetchone()
            if not row or row.expirado or row.usado:
                expirado = True
        except Exception:
            expirado = True

    if request.method == "POST":
        nueva     = request.form.get("nueva_password", "").strip()
        confirmar = request.form.get("confirmar_password", "").strip()

        if len(nueva) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        elif nueva != confirmar:
            error = "Las contraseñas no coinciden."
        else:
            try:
                row = db.session.execute(
                    text("""
                        SELECT usuario_id FROM password_reset_tokens
                        WHERE token = :token AND usado = 0
                          AND expira_en > NOW()
                    """),
                    {"token": token}
                ).fetchone()

                if not row:
                    expirado = True
                else:
                    user = Usuario.query.get(row.usuario_id)
                    if user:
                        user.set_password(nueva)
                        user.PrimerLogin      = False
                        user.IntentosFallidos = 0
                        user.BloqueadoHasta   = None
                        db.session.execute(
                            text("UPDATE password_reset_tokens SET usado = 1 WHERE token = :token"),
                            {"token": token}
                        )
                        db.session.commit()
                        flash("✅ Contraseña restablecida. Ya puedes iniciar sesión.", "success")
                        return redirect(url_for("auth.login"))
                    else:
                        error = "Usuario no encontrado."
            except Exception as e:
                db.session.rollback()
                error = f"Error: {str(e)}"

    return render_template("reset_password.html", token=token, error=error, expirado=expirado)


def _enviar_correo_reset(email: str, nombre: str, link: str):
    smtp_server = current_app.config.get("MAIL_SERVER",        "smtp.gmail.com")
    smtp_port   = int(current_app.config.get("MAIL_PORT",      587))
    smtp_user   = current_app.config.get("MAIL_USERNAME")
    smtp_pass   = current_app.config.get("MAIL_PASSWORD")
    remitente   = current_app.config.get("MAIL_DEFAULT_SENDER", smtp_user)

    asunto = "Recuperación de contraseña — ActivosApp"
    cuerpo_html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family:'DM Sans',Arial,sans-serif;background:#0a0a0f;margin:0;padding:40px 20px">
  <div style="max-width:480px;margin:0 auto;background:#12121a;border:1px solid #2a2a3a;border-radius:16px;padding:40px">
    <div style="margin-bottom:28px">
      <span style="font-family:Arial,sans-serif;font-weight:800;font-size:18px;color:#7c5cfc">🏢 ActivosApp</span>
    </div>
    <h1 style="color:#e8e8f0;font-size:22px;font-weight:800;margin-bottom:10px">Recupera tu contraseña</h1>
    <p style="color:#7070a0;font-size:14px;line-height:1.7;margin-bottom:28px">
      Hola <strong style="color:#e8e8f0">{nombre}</strong>, recibimos una solicitud para
      restablecer la contraseña de tu cuenta.
    </p>
    <a href="{link}"
       style="display:block;text-align:center;padding:14px 28px;
              background:linear-gradient(135deg,#7c5cfc,#e040fb);color:#fff;
              border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;
              margin-bottom:24px">
      🔐 Restablecer contraseña
    </a>
    <p style="color:#60607a;font-size:12px;line-height:1.7;border-top:1px solid #1e1e2e;padding-top:18px">
      Este enlace expira en <strong>5 minutos</strong>.<br>
      Si no solicitaste este cambio, ignora este correo.
    </p>
  </div>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = remitente
    msg["To"]      = email
    msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.sendmail(remitente, email, msg.as_string())


# ─── APIs ─────────────────────────────────────────────────────
@auth_bp.route("/api/reforzar-publico")
def api_reforzar_publico():
    frase = request.args.get("frase", "").strip()
    if len(frase) < 4:
        return jsonify({"error": "Escribe al menos 4 caracteres."})
    password = generar_password(frase)
    return jsonify({"sugerida": password, **analizar_password(password)})


@auth_bp.route("/api/reforzar")
@login_required
def api_reforzar():
    frase = request.args.get("frase", "").strip()
    if len(frase) < 4:
        return jsonify({"error": "Escribe al menos 4 caracteres."})
    password = generar_password(frase)
    return jsonify({"sugerida": password, **analizar_password(password)})


@auth_bp.route("/api/analizar")
@login_required
def api_analizar():
    return jsonify(analizar_password(request.args.get("password", "")))


@auth_bp.route("/logout")
def logout():
    logout_user()
    if request.headers.get("X-Requested-With") == "fetch":
        return jsonify({"ok": True})
    return redirect(url_for("auth.login"))


@auth_bp.route("/api/check-session")
def check_session():
    if current_user.is_authenticated:
        return jsonify({"ok": True, "usuario": current_user.username})
    return jsonify({"ok": False}), 401