# FRONTEND

## INDICE

- [Documentación](./documentacion) 
- [Backend](./backend/)
- [Frontend](./frontend/)
- [Como usar el sistema](#como-usar-el-sistema)
- [Como levantar el proyecto](#como-levantar-el-proyecto)


## COMO USAR EL SISTEMA

Correr el proyecto: 

- Para el proyecto con docker [click acá](#docker)
- Para el proyecto por consola [click acá](#consola)

Los links para acceder son:

- FRONT: http://localhost:4200
- BACK: http://localhost:8000
- MAILS (Mailpit): http://localhost:8025

El de mails se utiliza para cubrir el requisito funcional RF02 de los emails deben ser verificados

Existen 3 tipos de usuarios (rescatista, adoptante y moderador) y el sistema cuenta con un usuario para cada tipo cuyo datos son los siguientes. 

* Adoptante: adoptante1@mail.com / clave 123456
* Rescatista: rescatista1@mail.com / clave 123456
* Moderador: mod1@adoptme.com / clave 123456

Se pueden registrar más siguiendo estos pasos

### Registro

#### Rescatista y Adoptante

entrar a http://localhost:4200/registro y registrarse, el sistema le manda al usuario un mail con un link para verificar su cuenta. Hasta que no abra ese link no puede iniciar sesión (desde el login puede pedir que se lo reenviemos). El link vence a las 24 horas.

 En local los mails no llegan a ninguna casilla real llegan a  http://localhost:8025. Por eso se puede registrar cualquier mail, aunque no exista como en los casos genericos que tenemos.

Es decir los pasos de registro para rescatista o adoptante son:

1. Registrarse en http://localhost:4200/registro
2. Abrir http://localhost:8025 (lo hace através de mailpit un servicio para hacer pruebas de verificación de correos en un entorno de pruebas), entrar al mail "Verificá tu cuenta de AdoptMe" y hacer clic en "Verificar mi email"
3. Iniciar sesión normalmente

#### Moderadores
Este usuario no se puede registrar como el resto se crea a través de ejecutar el siguiente comando

```bash
python manage.py crear_moderador --email (unemail) --nombre (unnombre)
```
Si esta corriendo con Docker

```bash
docker compose exec backend python manage.py crear_moderador --email (unemail) --nombre (unnombre)
```

### Que puede hacer cada usuario

#### Rescatista:
    * Crear una publicación de un animal
    * Aceptar o rechazar una solicitud de adopción
    * Chatear con un posible adoptante
    * Poner una publicación como en proceso, que sucede cuando ya hay un posible adoptante para un animal. Acá la publicación ya no le aparecerá al resto de adoptantes
    * Poner la publicación como adoptado que es cuando se concretó una adopción
    * Eliminar una publicación

#### Adoptante

    * Buscar una publicación acorde al animal que quiera adoptar
    * Chatear con un rescatista que tenga una posible mascota que busque


Ambos pueden reportar usuarios, publicaciones y bloquear usuarios

### Moderador 
    
    el moderador entra con su usuario y contraseña a

    http://localhost:4200/moderacion

    aqui mismo puede ver los reportes tanto de publicaciones como de chat y tomar acciones sobre ellos como

    * Ignorar el reporte
    * Advertir al usuario reportado
    * Bloquear al usuario reportado
    * Sancionar al que reporto, esto ocurre si el usuario reporta desmedidamente y genera 3 strikes a la tercera se le bloquea las herramientas de reporte por un tiempo asignado por el mod.

## Como levantar el proyecto

### Docker
Se puede levantar con docker a través de docker

crear la imagen por primera vez con
```bash
docker compose build
```
luego levantar la imagen con

```bash
docker compose up -d
```

ver los puertos con

```bash
docker compose ps
```

Los links para acceder son:
```
FRONT: http://localhost:4200
BACK: http://localhost:8000
MAILS: http://localhost:8025 
```

Al levantar, el backend corre solo las migraciones, que crean los 3 usuarios genericos, y carga los tipos de usuario. No hace falta ningun paso extra. Mailpit tambien se levanta solo.

Si el login no anda (por ejemplo despues de reiniciar la PC o Docker Desktop), revisar con `docker compose ps` que los 4 contenedores (`db`, `backend`, `frontend` y `mailpit`) esten `Up`. Si `db` aparece `Exited` o `backend` aparece `Restarting`, ejecutar:

```bash
docker compose up -d
docker compose restart backend
```
### Consola

#### Backend

Para levantar el backend hacer estos pasos

Si es la primera vez hacer los pasos del 1 al 7. Si no, hacer el paso 1 y del 5 al 7

1) Abrir un terminal y ejecutar

    ```bash
    CD backend 
    ```

2) Una vez entramos en la directorio del backend cargamos los requerimientos con
    ```bash
    pip install -r requirements.txt
    ```

    Que instalará los requerimientos de nuestro proyecto (Django, Django REST Framework, mysqlclient y django-cors-headers.)

3) luego abrimos MySQL Workbench en el 
    ```Local instance MySQL80``` escribimos

    ```sql
    CREATE DATABASE adopcionesdb CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
    ```

    y ejecutar (rayito ⚡) con esto creamos la tabla adopcionesbd que estará vacia.

4) ahora abrimos el archivo settings.py que se encuentra en ```backend/adopciones``` y buscamos  ```DATABASE``` esta parte del código

    ```python
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adopcionesdb',
        'USER': 'root',
        'PASSWORD': 'tu_password_de_root',   # <-- cada uno pone la suya
        'HOST': 'localhost',
        'PORT': '3306',
        }
    }
    ```
    y poner nuestra constraseña en 'PASSWORD'

5) Ahora ya podemos crear las tablas. Las migraciones ya vienen en el repo, no hace falta correr makemigrations

    ```bash
    python manage.py migrate
    ```

    Esto tambien crea los 3 usuarios genericos (adoptante1, rescatista1 y mod1).

    Despues cargamos los tipos de usuario (adoptante, rescatista y moderador) con

    ```bash
    python manage.py loaddata datos_iniciales
    ```

6) (Opcional, solo para entrar al admin de Django en http://localhost:8000/admin) creamos el super usuario con
    ```bash
    python manage.py createsuperuser
    ```
7) Ahora finalmente levantamos el backend con
    ```bash
    python manage.py runserver
    ```
Ya tendremos el backend corriendo en http://127.0.0.1:8000/

#### Mails (verificación de email)

Para que lleguen los mails de verificación hay que tener Mailpit corriendo. Hay dos formas:

- **Con Mailpit (recomendado):** si se tiene Docker, levantar solo Mailpit con
    ```bash
    docker compose up -d mailpit
    ```
    o sin Docker, bajar `mailpit-windows-amd64.zip` de https://github.com/axllent/mailpit/releases, descomprimirlo y ejecutar `mailpit.exe`. Los mails se ven en http://localhost:8025

- **Sin Mailpit:** antes del paso 7 ejecutar (en PowerShell)
    ```powershell
    $env:EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
    ```
    y el mail, con el link de verificación, se imprime en la consola del backend.

Si no hay ninguno de los dos, el registro funciona igual pero el mail no se envía: el usuario lo puede reenviar desde el login cuando Mailpit esté levantado.

### Frontend

Si es la primera vez que se levanta el frontend ejecutar todos los pasos si no el 1 y 3

1) Abrir un terminal y ejecutar

    ```bash
    CD frontend
    ```

2) ejecutar el siguiente comando
    ```bash
    npm install
    ```
    en caso de error ejecutar

    ```bash
    npm install --legacy-peer-deps
    ```

3) ejecutar el siguiente comando para levantar el frontend

    ```bash
    npm start
    ```
    (equivale a `ng serve`, pero no necesita tener Angular CLI instalado globalmente)

    El backend tiene que estar corriendo en el puerto 8000: el front le manda los pedidos a `/api` a traves del proxy (`src/proxy.conf.json`).
    ya tenemos el proyecto levantado en
    http://localhost:4200/

