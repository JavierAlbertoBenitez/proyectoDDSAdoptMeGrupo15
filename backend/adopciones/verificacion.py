"""
Verificacion de email (RF02).

Cuando alguien se registra le mandamos un mail con un link del tipo
    http://localhost:4200/verificar-email?token=<token>
La pantalla de Angular le manda ese token a /api/verificar-email/ y ahi marcamos
usuario.email_verificado = True. Hasta entonces el login no lo deja entrar.

El token es el id y el email del usuario firmados con la SECRET_KEY (igual que el
token de sesion de autenticacion.py, pero con otro salt para que uno no sirva
como el otro). Lleva el email para que, si cambia, el link viejo deje de servir.
Vence a las 24 horas; desde el login se puede pedir uno nuevo.
"""

import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.utils.html import escape

logger = logging.getLogger(__name__)

SALT = 'adopciones.verificacion-email'
DURACION_SEGUNDOS = 24 * 60 * 60


def generar_token_verificacion(usuario):
    return signing.dumps({'id_usuario': usuario.id_usuario, 'email': usuario.email}, salt=SALT)


def leer_token_verificacion(token):
    """Devuelve los datos del token. Tira signing.SignatureExpired o signing.BadSignature."""
    return signing.loads(token, salt=SALT, max_age=DURACION_SEGUNDOS)


def enviar_mail_verificacion(usuario):
    """Manda el mail con el link. Devuelve False si no se pudo enviar (por ejemplo,
    si Mailpit no esta levantado): el registro igual se hace y el usuario puede
    pedir que se lo reenviemos desde el login."""
    link = settings.FRONTEND_URL + '/verificar-email?token=' + generar_token_verificacion(usuario)
    texto = (
        'Hola ' + usuario.nombre_completo + ':\n\n'
        'Gracias por registrarte en AdoptMe. Para activar tu cuenta abrí este link:\n\n'
        + link + '\n\n'
        'El link vence en 24 horas. Si no fuiste vos, ignorá este mail.'
    )
    # escape: el nombre lo escribe el usuario, que no pueda meter HTML en el mail.
    html = (
        '<p>Hola ' + escape(usuario.nombre_completo) + ':</p>'
        '<p>Gracias por registrarte en <strong>AdoptMe</strong>. Para activar tu cuenta hacé clic acá:</p>'
        '<p><a href="' + link + '" style="display:inline-block;padding:10px 20px;background:#2f6b4f;'
        'color:#fff;border-radius:6px;text-decoration:none;font-weight:bold">Verificar mi email</a></p>'
        '<p>El link vence en 24 horas. Si no fuiste vos, ignorá este mail.</p>'
    )
    try:
        send_mail('Verificá tu cuenta de AdoptMe', texto, None, [usuario.email], html_message=html)
        return True
    except Exception:
        logger.exception('No se pudo enviar el mail de verificacion a %s', usuario.email)
        return False
