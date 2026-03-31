from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from ..models.usuario import Usuario, pwd_context
from ..extensions import db
import random
import secrets
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

auth_bp = Blueprint("auth", __name__)


# ─── Generador de contraseña ──────────────────────────────────────────────────
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


# ─── Rutas principales ────────────────────────────────────────────────────────
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

        # ── Nueva tabla Usuario ──────────────────────────────
        user = Usuario.query.filter_by(
            NombreUsuario=username,
            Estatus=True
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get("remember") == "on")
            if user.PrimerLogin:
                return redirect(url_for("auth.sugerir_cambio"))
            return redirect(request.args.get("next") or url_for("activos.dashboard"))

        flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")


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


# ─── Recuperación de contraseña ───────────────────────────────────────────────
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
                # Buscar por Correo en nueva tabla
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
                    link = f"{request.host_url}reset-password/{token}"
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
                # Buscar usuario por token y actualizar contraseña directamente
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
                        user.PrimerLogin = False
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
    smtp_server = current_app.config.get("MAIL_SERVER",   "smtp.gmail.com")
    smtp_port   = int(current_app.config.get("MAIL_PORT", 587))
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


# ─── APIs ─────────────────────────────────────────────────────────────────────
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