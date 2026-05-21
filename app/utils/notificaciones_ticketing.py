# app/utils/notificaciones_ticketing.py
"""
Sistema de notificaciones por email para Ticketing
"""
from flask import current_app, render_template_string
from flask_mail import Message
from app.extensions import mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _smtp_send(destinatario, asunto, cuerpo_html):
    """
    Envía un email usando SMTP directo (Gmail).
    Versión centralizada para todas las notificaciones.
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = current_app.config['MAIL_USERNAME']
        msg['To'] = destinatario
        
        # Cuerpo HTML
        html_part = MIMEText(cuerpo_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Conexión SMTP
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD']
            )
            server.send_message(msg)
        
        current_app.logger.info(f'✅ Email enviado a {destinatario}: {asunto}')
        return True
        
    except Exception as e:
        current_app.logger.error(f'❌ Error enviando email a {destinatario}: {str(e)}')
        return False


def _generar_email_base(titulo, contenido, url_ticket=None):
    """
    Template base para todos los emails de ticketing.
    Diseño table-based para compatibilidad con Outlook.
    """
    boton_html = ""
    if url_ticket:
        boton_html = f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
            <tr>
                <td align="center">
                    <a href="{url_ticket}" 
                       style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); 
                              color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px;">
                        Ver Ticket Completo
                    </a>
                </td>
            </tr>
        </table>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); padding: 32px 40px; text-align: center;">
                                <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 800;">
                                    🎫 ActivosApp Ticketing
                                </h1>
                                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500;">
                                    Sistema de Soporte Técnico
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Título -->
                        <tr>
                            <td style="padding: 32px 40px 20px; background-color: #f9fafb; border-bottom: 2px solid #e5e7eb;">
                                <h2 style="margin: 0; color: #1f2937; font-size: 20px; font-weight: 700;">
                                    {titulo}
                                </h2>
                            </td>
                        </tr>
                        
                        <!-- Contenido -->
                        <tr>
                            <td style="padding: 32px 40px; color: #4b5563; font-size: 15px; line-height: 1.6;">
                                {contenido}
                            </td>
                        </tr>
                        
                        <!-- Botón (opcional) -->
                        {boton_html}
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 24px 40px; background-color: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
                                <p style="margin: 0; color: #6b7280; font-size: 13px; line-height: 1.5;">
                                    Este es un mensaje automático del sistema de ticketing.<br>
                                    Por favor no respondas a este correo.
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ══════════════════════════════════════════════════════════
# NOTIFICACIÓN 1: NUEVO TICKET CREADO
# ══════════════════════════════════════════════════════════

def notificar_nuevo_ticket(ticket_data, url_base):
    """
    Notifica al área de TI cuando se crea un nuevo ticket.
    
    Args:
        ticket_data: dict con IdTicket, NumeroTicket, Titulo, UsuarioCreador, EmailCreador, Prioridad
        url_base: str, ej: 'http://localhost:5000'
    """
    url_ticket = f"{url_base}/ticketing/ticket/{ticket_data['IdTicket']}"
    
    # Icono según prioridad
    prioridad_emoji = {
        'Baja': '🟢',
        'Media': '🟡',
        'Alta': '🟠',
        'Urgente': '🔴'
    }
    emoji = prioridad_emoji.get(ticket_data.get('Prioridad', 'Media'), '🟡')
    
    contenido = f"""
    <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 24px;">
        <p style="margin: 0 0 12px; font-size: 14px; color: #1e40af; font-weight: 600;">
            NUEVO TICKET REGISTRADO
        </p>
        <p style="margin: 0; font-size: 24px; font-weight: 800; color: #1f2937;">
            {ticket_data['NumeroTicket']}
        </p>
    </div>
    
    <table width="100%" cellpadding="8" cellspacing="0" style="margin: 20px 0;">
        <tr>
            <td style="padding: 8px 0; color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; width: 120px;">
                Usuario:
            </td>
            <td style="padding: 8px 0; color: #1f2937; font-weight: 600;">
                {ticket_data['UsuarioCreador']}<br>
                <span style="color: #6b7280; font-size: 13px; font-weight: 400;">{ticket_data['EmailCreador']}</span>
            </td>
        </tr>
        <tr>
            <td style="padding: 8px 0; color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                Prioridad:
            </td>
            <td style="padding: 8px 0; color: #1f2937; font-weight: 600;">
                {emoji} {ticket_data.get('Prioridad', 'Media')}
            </td>
        </tr>
        <tr>
            <td style="padding: 8px 0; color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; vertical-align: top;">
                Descripción:
            </td>
            <td style="padding: 8px 0; color: #1f2937;">
                {ticket_data['Titulo'][:200]}{'...' if len(ticket_data['Titulo']) > 200 else ''}
            </td>
        </tr>
    </table>
    
    <div style="background-color: #fef3c7; padding: 16px; border-radius: 8px; margin-top: 24px;">
        <p style="margin: 0; color: #92400e; font-size: 14px;">
            ⚡ <strong>Acción requerida:</strong> Revisa y asigna este ticket a un técnico.
        </p>
    </div>
    """
    
    email_html = _generar_email_base(
        titulo="Nuevo Ticket Requiere Atención",
        contenido=contenido,
        url_ticket=url_ticket
    )
    
    # Enviar a todos los admins TI (esto puedes ajustarlo según tu lógica)
    # Por ahora envío a una lista hardcoded, pero podrías consultar la BD
    destinatarios_ti = ['ti@tuempresa.com']  # ← AJUSTAR SEGÚN TU EMPRESA
    
    for email_ti in destinatarios_ti:
        _smtp_send(
            destinatario=email_ti,
            asunto=f"🎫 Nuevo Ticket: {ticket_data['NumeroTicket']} - {ticket_data.get('Prioridad', 'Media')}",
            cuerpo_html=email_html
        )


# ══════════════════════════════════════════════════════════
# NOTIFICACIÓN 2: TICKET ASIGNADO
# ══════════════════════════════════════════════════════════

def notificar_ticket_asignado(ticket_data, tecnico_data, url_base):
    """
    Notifica al técnico cuando se le asigna un ticket.
    
    Args:
        ticket_data: dict con IdTicket, NumeroTicket, Titulo, Prioridad
        tecnico_data: dict con Nombre, Email
        url_base: str
    """
    url_ticket = f"{url_base}/ticketing/ticket/{ticket_data['IdTicket']}"
    
    contenido = f"""
    <p style="margin: 0 0 24px; font-size: 16px; color: #1f2937;">
        Hola <strong>{tecnico_data['Nombre']}</strong>,
    </p>
    
    <p style="margin: 0 0 20px; color: #4b5563;">
        Se te ha asignado un nuevo ticket para atención:
    </p>
    
    <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 24px;">
        <p style="margin: 0 0 8px; font-size: 14px; color: #1e40af; font-weight: 600;">
            TICKET ASIGNADO
        </p>
        <p style="margin: 0; font-size: 22px; font-weight: 800; color: #1f2937;">
            {ticket_data['NumeroTicket']}
        </p>
    </div>
    
    <table width="100%" cellpadding="8" cellspacing="0" style="margin: 20px 0;">
        <tr>
            <td style="padding: 8px 0; color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase; width: 120px;">
                Prioridad:
            </td>
            <td style="padding: 8px 0; color: #1f2937; font-weight: 600;">
                {ticket_data.get('Prioridad', 'Media')}
            </td>
        </tr>
        <tr>
            <td style="padding: 8px 0; color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase; vertical-align: top;">
                Problema:
            </td>
            <td style="padding: 8px 0; color: #1f2937;">
                {ticket_data['Titulo']}
            </td>
        </tr>
    </table>
    
    <p style="margin: 24px 0 0; color: #4b5563;">
        Por favor revisa los detalles completos y comienza la atención lo antes posible.
    </p>
    """
    
    email_html = _generar_email_base(
        titulo="Ticket Asignado a Ti",
        contenido=contenido,
        url_ticket=url_ticket
    )
    
    _smtp_send(
        destinatario=tecnico_data['Email'],
        asunto=f"🎫 Ticket Asignado: {ticket_data['NumeroTicket']}",
        cuerpo_html=email_html
    )


# ══════════════════════════════════════════════════════════
# NOTIFICACIÓN 3: NUEVO COMENTARIO
# ══════════════════════════════════════════════════════════

def notificar_nuevo_comentario(ticket_data, comentario_data, url_base):
    """
    Notifica al creador del ticket y al técnico asignado cuando hay un nuevo comentario.
    
    Args:
        ticket_data: dict con IdTicket, NumeroTicket, EmailCreador, EmailAsignado
        comentario_data: dict con Autor, Comentario, FechaCreacion
        url_base: str
    """
    url_ticket = f"{url_base}/ticketing/ticket/{ticket_data['IdTicket']}"
    
    contenido = f"""
    <p style="margin: 0 0 20px; color: #4b5563;">
        Se ha agregado una nueva actualización en el ticket <strong>{ticket_data['NumeroTicket']}</strong>:
    </p>
    
    <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; margin: 24px 0;">
        <p style="margin: 0 0 12px; font-size: 13px; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
            💬 Nuevo Comentario
        </p>
        <p style="margin: 0 0 8px; color: #1f2937; font-weight: 600;">
            {comentario_data['Autor']}
        </p>
        <p style="margin: 0 0 12px; color: #6b7280; font-size: 13px;">
            {comentario_data['FechaCreacion']}
        </p>
        <div style="padding: 16px; background-color: white; border-radius: 6px; margin-top: 12px;">
            <p style="margin: 0; color: #1f2937; line-height: 1.6;">
                {comentario_data['Comentario']}
            </p>
        </div>
    </div>
    
    <p style="margin: 24px 0 0; color: #4b5563;">
        Haz clic en el botón para ver el ticket completo y responder.
    </p>
    """
    
    email_html = _generar_email_base(
        titulo="Nueva Actualización en tu Ticket",
        contenido=contenido,
        url_ticket=url_ticket
    )
    
    # Enviar al creador y al técnico asignado (si existe)
    destinatarios = [ticket_data['EmailCreador']]
    if ticket_data.get('EmailAsignado'):
        destinatarios.append(ticket_data['EmailAsignado'])
    
    # Evitar duplicados
    destinatarios = list(set(destinatarios))
    
    for email in destinatarios:
        _smtp_send(
            destinatario=email,
            asunto=f"💬 Nuevo comentario en {ticket_data['NumeroTicket']}",
            cuerpo_html=email_html
        )


# ══════════════════════════════════════════════════════════
# NOTIFICACIÓN 4: CAMBIO DE ESTADO
# ══════════════════════════════════════════════════════════

def notificar_cambio_estado(ticket_data, estado_anterior, estado_nuevo, url_base):
    """
    Notifica al creador cuando el estado del ticket cambia.
    
    Args:
        ticket_data: dict con IdTicket, NumeroTicket, EmailCreador
        estado_anterior: str
        estado_nuevo: str
        url_base: str
    """
    url_ticket = f"{url_base}/ticketing/ticket/{ticket_data['IdTicket']}"
    
    # Emojis por estado
    estados_emoji = {
        'Abierto': '🔴',
        'En Proceso': '⚙️',
        'Escalado': '⬆️',
        'Pendiente': '⏸️',
        'Resuelto': '✅',
        'Cerrado': '🔒'
    }
    
    contenido = f"""
    <p style="margin: 0 0 20px; color: #4b5563;">
        El estado de tu ticket <strong>{ticket_data['NumeroTicket']}</strong> ha cambiado:
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 24px 0;">
        <tr>
            <td align="center" style="padding: 20px; background-color: #fef3c7; border-radius: 8px 0 0 8px; width: 50%;">
                <p style="margin: 0 0 8px; color: #92400e; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                    Estado Anterior
                </p>
                <p style="margin: 0; color: #78350f; font-size: 18px; font-weight: 700;">
                    {estados_emoji.get(estado_anterior, '📋')} {estado_anterior}
                </p>
            </td>
            <td align="center" style="padding: 20px; background-color: #d1fae5; border-radius: 0 8px 8px 0; width: 50%;">
                <p style="margin: 0 0 8px; color: #065f46; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                    Estado Nuevo
                </p>
                <p style="margin: 0; color: #047857; font-size: 18px; font-weight: 700;">
                    {estados_emoji.get(estado_nuevo, '📋')} {estado_nuevo}
                </p>
            </td>
        </tr>
    </table>
    
    <p style="margin: 24px 0 0; color: #4b5563;">
        Puedes revisar el progreso completo en el sistema.
    </p>
    """
    
    email_html = _generar_email_base(
        titulo="Actualización de Estado",
        contenido=contenido,
        url_ticket=url_ticket
    )
    
    _smtp_send(
        destinatario=ticket_data['EmailCreador'],
        asunto=f"🔔 {ticket_data['NumeroTicket']}: {estado_nuevo}",
        cuerpo_html=email_html
    )


# ══════════════════════════════════════════════════════════
# NOTIFICACIÓN 5: TICKET RESUELTO
# ══════════════════════════════════════════════════════════

def notificar_ticket_resuelto(ticket_data, url_base):
    """
    Notifica al creador cuando su ticket ha sido marcado como resuelto.
    
    Args:
        ticket_data: dict con IdTicket, NumeroTicket, EmailCreador, Titulo
        url_base: str
    """
    url_ticket = f"{url_base}/ticketing/ticket/{ticket_data['IdTicket']}"
    
    contenido = f"""
    <div style="text-align: center; padding: 32px 0;">
        <p style="margin: 0; font-size: 48px;">✅</p>
        <p style="margin: 16px 0 0; font-size: 24px; font-weight: 700; color: #1f2937;">
            Ticket Resuelto
        </p>
    </div>
    
    <p style="margin: 0 0 20px; color: #4b5563;">
        Nos complace informarte que tu ticket <strong>{ticket_data['NumeroTicket']}</strong> ha sido marcado como resuelto.
    </p>
    
    <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 24px 0;">
        <p style="margin: 0 0 8px; color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase;">
            Problema reportado:
        </p>
        <p style="margin: 0; color: #1f2937; font-weight: 500;">
            {ticket_data['Titulo']}
        </p>
    </div>
    
    <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin: 24px 0;">
        <p style="margin: 0 0 12px; color: #1e40af; font-weight: 600;">
            ¿El problema fue resuelto satisfactoriamente?
        </p>
        <p style="margin: 0; color: #1e40af; font-size: 14px;">
            Si el problema persiste o necesitas ayuda adicional, puedes reabrir el ticket agregando un comentario.
        </p>
    </div>
    
    <p style="margin: 24px 0 0; color: #4b5563;">
        Gracias por tu paciencia. Si tienes alguna duda, no dudes en contactarnos.
    </p>
    """
    
    email_html = _generar_email_base(
        titulo="Tu Ticket Ha Sido Resuelto",
        contenido=contenido,
        url_ticket=url_ticket
    )
    
    _smtp_send(
        destinatario=ticket_data['EmailCreador'],
        asunto=f"✅ Ticket Resuelto: {ticket_data['NumeroTicket']}",
        cuerpo_html=email_html
    )