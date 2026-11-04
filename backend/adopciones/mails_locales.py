"""
Levanta solo el servidor de mails (Mailpit) cuando corremos el backend por
consola con "python manage.py runserver". Lo llama manage.py.

Con Docker no hace falta: docker-compose.yml ya levanta Mailpit.
Por consola probamos, en orden:
  1. Si Mailpit ya esta corriendo (puerto 1025), no hacemos nada.
  2. Si esta Docker, levantamos solo el contenedor: docker compose up -d mailpit
  3. Si esta el ejecutable mailpit (en el PATH), lo arrancamos.
  4. Si no hay ninguno, los mails se imprimen en la consola del backend
     (EMAIL_BACKEND de consola), asi el link de verificacion se puede copiar igual.
"""

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

# La carpeta del repo (donde esta docker-compose.yml).
RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
BANDEJA = 'http://localhost:8025'
BACKEND_CONSOLA = 'django.core.mail.backends.console.EmailBackend'


def puerto_abierto(puerto):
    try:
        with socket.create_connection(('localhost', puerto), timeout=1):
            return True
    except OSError:
        return False


def esperar_puerto(puerto, segundos=15):
    limite = time.time() + segundos
    while time.time() < limite:
        if puerto_abierto(puerto):
            return True
        time.sleep(0.5)
    return False


def levantar_con_docker():
    if shutil.which('docker') is None or not (RAIZ_REPO / 'docker-compose.yml').exists():
        return False
    try:
        # La primera vez baja la imagen, por eso el timeout largo.
        resultado = subprocess.run(['docker', 'compose', 'up', '-d', 'mailpit'], cwd=RAIZ_REPO,
                                   capture_output=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired):
        return False
    # Si Docker Desktop esta cerrado el comando falla y probamos lo siguiente.
    return resultado.returncode == 0


def levantar_ejecutable():
    ejecutable = shutil.which('mailpit')
    if ejecutable is None:
        return False
    # Sin separarlo de la consola: al cortar el runserver con Ctrl+C se corta tambien Mailpit.
    subprocess.Popen([ejecutable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


def preparar_mails():
    # Solo para runserver, y una sola vez: con el autoreload Django vuelve a correr
    # manage.py en un proceso hijo (con RUN_MAIN) que hereda lo que decidimos aca.
    if len(sys.argv) < 2 or sys.argv[1] != 'runserver' or os.environ.get('RUN_MAIN'):
        return
    # Con Docker (EMAIL_HOST=mailpit) o si alguien eligio otro EMAIL_BACKEND, no tocamos nada.
    if os.environ.get('EMAIL_BACKEND') or os.environ.get('EMAIL_HOST', 'localhost') not in ('localhost', '127.0.0.1'):
        return

    puerto = int(os.environ.get('EMAIL_PORT', '1025'))
    if puerto_abierto(puerto):
        print('Mails: Mailpit ya esta corriendo. Bandeja de entrada en ' + BANDEJA, flush=True)
        return

    print('Mails: levantando Mailpit...', flush=True)
    if (levantar_con_docker() or levantar_ejecutable()) and esperar_puerto(puerto):
        print('Mails: Mailpit listo. Bandeja de entrada en ' + BANDEJA, flush=True)
        return

    os.environ['EMAIL_BACKEND'] = BACKEND_CONSOLA
    print('Mails: no se pudo levantar Mailpit (ni Docker ni mailpit.exe). '
          'Los mails de verificacion se van a imprimir en esta consola.', flush=True)
