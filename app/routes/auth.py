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
from ..extensions import socketio

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
    if puntos <= 25:   nivel = "Debil"
    elif puntos <= 50: nivel = "Regular"
    elif puntos <= 75: nivel = "Buena"
    else:              nivel = "Fuerte"
    return {"fortaleza": puntos, "nivel": nivel, "longitud": n}


# ─── Helper SMTP ──────────────────────────────────────────────
def _smtp_send(destinatario: str, asunto: str, cuerpo_html: str):
    """Envía un correo HTML usando smtplib con UTF-8 correcto."""
    smtp_server = current_app.config.get("MAIL_SERVER",         "smtp.gmail.com")
    smtp_port   = int(current_app.config.get("MAIL_PORT",       587))
    smtp_user   = current_app.config.get("MAIL_USERNAME")
    smtp_pass   = current_app.config.get("MAIL_PASSWORD")
    remitente   = current_app.config.get("MAIL_DEFAULT_SENDER", smtp_user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = remitente
    msg["To"]      = destinatario
    msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.sendmail(remitente, destinatario, msg.as_bytes())


# ─── Helpers de bloqueo ───────────────────────────────────────
def _esta_bloqueado(user: Usuario) -> bool:
    return bool(user.BloqueadoHasta and user.BloqueadoHasta > datetime.now())


def _registrar_fallo(user: Usuario):
    """Suma un intento fallido y bloquea si llega al límite."""
    user.IntentosFallidos = (user.IntentosFallidos or 0) + 1
    if user.IntentosFallidos >= MAX_INTENTOS:
        user.BloqueadoHasta   = datetime(9999, 12, 31)
        user.IntentosFallidos = 0
    db.session.commit()
    if user.BloqueadoHasta:
        socketio.emit('usuario_bloqueado', {'usuario_id': user.IdUsuario})


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


# ─── Correos ──────────────────────────────────────────────────
def _enviar_correo_desbloqueo(usuario_bloqueado: Usuario):
    """Manda correo a todos los admins pidiendo desbloqueo."""
    admins = _obtener_admins_ti()
    if not admins:
        return False

    nombre_bloqueado = f"{usuario_bloqueado.Nombre} {usuario_bloqueado.ApellidoPaterno}"
    user_bloqueado   = usuario_bloqueado.NombreUsuario

    for admin in admins:
        asunto = f"Solicitud de desbloqueo - {nombre_bloqueado}"

        cuerpo_html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background-color:#f4f4f8;margin:0;padding:40px 20px">
  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:#f4f4f8;padding:40px 0">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" border="0"
             style="background-color:#ffffff;border:1px solid #e0e0ef;">

        <!-- Header -->
        <tr>
          <td align="center" bgcolor="#9B2335"
              style="background-color:#9B2335;padding:28px 40px;">
            <p style="margin:0;font-family:Arial,sans-serif;font-size:20px;
                      font-weight:800;color:#ffffff;">ActivosApp</p>
            <p style="margin:4px 0 0;font-family:Arial,sans-serif;font-size:12px;
                      color:#f8b4bc;">Sistema de gestion de activos</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px 40px;">
            <h2 style="margin:0 0 8px;font-family:Arial,sans-serif;
                       font-size:18px;color:#1a1a2e;">
              Solicitud de desbloqueo de cuenta
            </h2>
            <p style="margin:0 0 20px;font-family:Arial,sans-serif;
                       font-size:14px;color:#6b6b8a;line-height:1.6;">
              Hola <strong style="color:#1a1a2e">{admin.NombreCompleto}</strong>,<br>
              el siguiente usuario ha sido bloqueado por multiples intentos fallidos
              de inicio de sesion y solicita que se desbloquee su cuenta.
            </p>

            <!-- Datos usuario -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background-color:#f8f8fc;border:1px solid #e0e0ef;margin-bottom:24px;">
              <tr>
                <td style="padding:10px 16px;font-family:Arial,sans-serif;font-size:12px;
                           color:#6b6b8a;font-weight:700;width:130px;
                           border-bottom:1px solid #e0e0ef;">Usuario</td>
                <td style="padding:10px 16px;font-family:Arial,sans-serif;font-size:13px;
                           color:#1a1a2e;font-weight:700;
                           border-bottom:1px solid #e0e0ef;">{user_bloqueado}</td>
              </tr>
              <tr>
                <td style="padding:10px 16px;font-family:Arial,sans-serif;font-size:12px;
                           color:#6b6b8a;font-weight:700;
                           border-bottom:1px solid #e0e0ef;">Nombre</td>
                <td style="padding:10px 16px;font-family:Arial,sans-serif;font-size:13px;
                           color:#1a1a2e;border-bottom:1px solid #e0e0ef;">{nombre_bloqueado}</td>
              </tr>
              <tr>
                <td style="padding:10px 16px;font-family:Arial,sans-serif;font-size:12px;
                           color:#6b6b8a;font-weight:700;">Correo</td>
                <td style="padding:10px 16px;font-family:Arial,sans-serif;font-size:13px;
                           color:#1a1a2e;">{usuario_bloqueado.Correo}</td>
              </tr>
            </table>

            <p style="margin:0 0 16px;font-family:Arial,sans-serif;font-size:13px;
                      color:#6b6b8a;line-height:1.6;">
              Para desbloquearlo, ingresa al sistema con tu cuenta de administrador,
              ve a <strong>Administracion &rarr; Usuarios</strong> y usa el boton
              <strong>"Desbloquear"</strong> en la fila de este usuario.
            </p>

            <!-- Aviso -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background-color:#fff3cd;border:1px solid #ffc107;">
              <tr>
                <td style="padding:12px 16px;font-family:Arial,sans-serif;
                           font-size:12px;color:#856404;line-height:1.5;">
                  Si no reconoces a este usuario o sospechas de actividad maliciosa,
                  no desbloquees la cuenta y reportalo al administrador del sistema.
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td align="center" style="padding:16px 40px;background-color:#f8f8fc;
              border-top:1px solid #e0e0ef;">
            <p style="margin:0;font-family:Arial,sans-serif;font-size:11px;color:#b0b0c8;">
              Este correo fue generado automaticamente por ActivosApp.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

        try:
            _smtp_send(admin.Correo, asunto, cuerpo_html)
        except Exception as e:
            current_app.logger.error(f"Error enviando correo a {admin.Correo}: {e}")

    return True


def _enviar_correo_reset(email: str, nombre: str, link: str):
    asunto = "Recuperacion de contrasena - ActivosApp"

    cuerpo_html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#f1f5f9;">
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:#f1f5f9;padding:40px 0;">
  <tr><td align="center">
    <table width="480" cellpadding="0" cellspacing="0" border="0"
           style="background-color:#ffffff;border:1px solid #e2e8f0;">

      <!-- Header -->
      <tr>
        <td align="center" bgcolor="#9B2335"
            style="background-color:#9B2335;padding:32px 40px;">
          <p style="margin:0;font-family:Arial,sans-serif;font-size:22px;
                    font-weight:800;color:#ffffff;">ActivosApp</p>
          <p style="margin:4px 0 0;font-family:Arial,sans-serif;font-size:12px;
                    color:#ffffff;">Sistema de gestion de activos</p>
        </td>
      </tr>

      <!-- Body -->
      <tr>
        <td style="padding:36px 40px;">
          <h2 style="margin:0 0 8px;font-family:Arial,sans-serif;
                     font-size:20px;color:#1e1b4b;">
            Recupera tu contrasena
          </h2>
          <p style="margin:0 0 24px;font-family:Arial,sans-serif;
                    font-size:14px;color:#64748b;line-height:1.6;">
            Hola <strong style="color:#1e1b4b;">{nombre}</strong>,
            recibimos una solicitud para restablecer la contrasena de tu cuenta.
          </p>

          <!-- Boton -->
          <table width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="margin-bottom:24px;">
            <tr>
              <td align="center">
                <a href="{link}"
                   style="display:inline-block;background-color:#9B2335;
                          color:#ffffff;text-decoration:none;
                          font-family:Arial,sans-serif;font-size:15px;
                          font-weight:700;padding:14px 40px;">
                  Restablecer contrasena
                </a>
              </td>
            </tr>
          </table>

          <!-- Aviso expiracion -->
          <table width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background-color:#f8fafc;border:1px solid #e2e8f0;">
            <tr>
              <td style="padding:12px 16px;font-family:Arial,sans-serif;
                         font-size:12px;color:#64748b;line-height:1.6;">
                Este enlace expira en <strong>5 minutos</strong>.<br>
                Si no solicitaste este cambio, ignora este correo.
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td align="center" style="padding:16px 40px;background-color:#f8fafc;
            border-top:1px solid #e2e8f0;">
          <p style="margin:0;font-family:Arial,sans-serif;font-size:11px;color:#94a3b8;">
            Mensaje automatico, no respondas a este correo.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

    _smtp_send(email, asunto, cuerpo_html)


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
            flash("Usuario o contrasena incorrectos.", "error")
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
        flash("Usuario o contrasena incorrectos.")

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
        flash("Esta cuenta no esta bloqueada.", "info")
        return redirect(url_for("auth.login"))

    try:
        ok = _enviar_correo_desbloqueo(user)
        if ok:
            flash(
                "Solicitud enviada. Un administrador recibira tu solicitud "
                "y desbloqueara tu cuenta en breve.",
                "success"
            )
        else:
            flash(
                "No se encontraron administradores disponibles. "
                "Contacta directamente al area de TI.",
                "warning"
            )
    except Exception as e:
        current_app.logger.error(f"Error al enviar solicitud de desbloqueo: {e}")
        flash("Error al enviar la solicitud. Contacta directamente al area de TI.", "error")

    return redirect(url_for("auth.login"))


# ─── Desbloquear usuario (solo admin) ────────────────────────
@auth_bp.route("/admin/desbloquear/<int:uid>", methods=["POST"])
@login_required
def desbloquear_usuario(uid):
    if current_user.rol != 'admin':
        flash("Sin permiso para esta accion.", "error")
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
            error = "La contrasena debe tener al menos 6 caracteres."
        elif nueva != confirmar:
            error = "Las contrasenas no coinciden."
        elif current_user.check_password(nueva):
            error = "La nueva contrasena no puede ser igual a la temporal."
        else:
            try:
                current_user.set_password(nueva)
                current_user.PrimerLogin = False
                db.session.commit()
                flash("Contrasena actualizada correctamente!", "success")
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
            error = "Ingresa tu correo electronico."
        else:
            token = secrets.token_urlsafe(48)
            try:
                user = Usuario.query.filter(
                    Usuario.Correo.ilike(email),
                    Usuario.Estatus == True
                ).first()

                if not user:
                    error = "El correo ingresado no está registrado en el sistema."
                else:
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
            error = "La contrasena debe tener al menos 6 caracteres."
        elif nueva != confirmar:
            error = "Las contrasenas no coinciden."
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
                        flash("Contrasena restablecida. Ya puedes iniciar sesion.", "success")
                        return redirect(url_for("auth.login"))
                    else:
                        error = "Usuario no encontrado."
            except Exception as e:
                db.session.rollback()
                error = f"Error: {str(e)}"

    return render_template("reset_password.html", token=token, error=error, expirado=expirado)


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