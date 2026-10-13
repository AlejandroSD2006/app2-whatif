# Desplegar en AWS EC2, desde cero (explicado para principiantes)

Esta es la guía para poner `app2-whatif` funcionando de verdad en internet, usando una máquina virtual de Amazon (una instancia **EC2**). Está escrita asumiendo que **nunca has tocado AWS**, así que no se da nada por sabido.

**Cómo usar esta guía:** está pensada para seguirla paso a paso, verificando cada parte antes de pasar a la siguiente (no para leerla entera y ejecutarlo todo de golpe). Hay pasos que solo puedes hacer tú (crear la cuenta de AWS, pulsar botones en la consola web, pegar tus claves secretas) porque dependen de tu cuenta y tus credenciales; en esos puntos, para y hazlo tú, y seguimos a partir de ahí. Todavía no se ha hecho ningún paso de esta guía (ver PEN-02 en el [README](../README.md)).

## 0. Ideas previas, en plan sencillo

- **EC2** = "Elastic Compute Cloud". Es, básicamente, **alquilar un ordenador de Amazon** al que te conectas por internet. Ese ordenador (la "instancia") se queda encendido todo el tiempo que tú quieras, ejecutando tu aplicación.
- Para controlar ese ordenador no hay pantalla ni ratón: te conectas por **SSH**, que es como abrir una terminal remota desde tu propio ordenador.
- Una vez dentro, instalamos **Docker**, que es la misma herramienta que ya usa este proyecto en local (`deploy/docker-compose.yml`). Así, el comando para levantar la aplicación en AWS es prácticamente el mismo que en tu ordenador.
- No hace falta instalar Python, Node, FastAPI ni nada de eso "a pelo" en la instancia: todo eso vive dentro de los contenedores Docker, igual que en local.

## 1. Crear la cuenta de AWS (lo haces tú)

1. Entra en la web oficial de AWS y crea una cuenta gratuita (pide una tarjeta de crédito/débito para verificar la identidad, aunque uses solo la capa gratuita).
2. AWS tiene una **capa gratuita** (*Free Tier*) que incluye, durante 12 meses, una cantidad de horas gratis de instancias pequeñas (tipo `t2.micro` o `t3.micro`). Para este proyecto es más que suficiente.
3. Importante: aunque uses la capa gratuita, **revisa siempre la sección de facturación** (*Billing*) de tu cuenta de vez en cuando, para asegurarte de que no se te está cobrando nada inesperado.

> Para a avisarme cuando tengas la cuenta creada y hayas entrado en la consola de AWS (la web donde se gestiona todo). A partir de aquí seguimos juntos, porque los siguientes pasos implican pulsar botones concretos en esa consola.

## 2. Crear la instancia EC2

Dentro de la consola de AWS, buscas el servicio **EC2** y le das a "Launch instance" (Lanzar instancia). Ahí tendrás que elegir varias cosas; aquí va qué elegir y por qué:

| Qué te pide AWS | Qué elegir | Por qué |
|---|---|---|
| Nombre de la instancia | Algo que reconozcas, por ejemplo `app2-whatif` | Solo es para que la identifiques tú en la lista. |
| AMI (imagen del sistema) | **Ubuntu Server** (la versión LTS más reciente que ofrezca, por ejemplo 24.04) | Es la distribución de Linux más habitual para este tipo de despliegues; todos los comandos de esta guía están pensados para Ubuntu. |
| Tipo de instancia | `t2.micro` o `t3.micro` | Son los tipos que entran en la capa gratuita y son suficientes para esta aplicación. |
| Par de claves (key pair) | Crear una nueva, descargarla y guardarla bien | Es el "DNI" que te deja entrar por SSH. Sin este archivo no puedes conectarte nunca más a esa instancia, así que no lo pierdas ni lo subas a ningún repositorio. |
| Configuración de red / grupo de seguridad | Crear un grupo de seguridad nuevo (ver el punto siguiente) | Es el "cortafuegos" que decide qué puertos están abiertos desde internet. |
| Almacenamiento | El valor por defecto (8–20 GiB) suele bastar | La aplicación es pequeña; no necesita mucho disco. |

### El grupo de seguridad (security group)

Es la lista de "puertas" que dejas abiertas en tu instancia. Al crearla, añade estas reglas de entrada (*inbound rules*):

| Tipo | Puerto | Origen | Para qué |
|---|---|---|---|
| SSH | 22 | **Solo tu IP** (AWS te lo ofrece como opción "My IP") | Para que puedas entrar tú por terminal, pero nadie más. |
| HTTP personalizado (Custom TCP) | 8080 | `0.0.0.0/0` (cualquier IP) | Es el puerto por el que, con la configuración actual del proyecto (`deploy/docker-compose.yml`), se sirve la aplicación. Luego, en el paso 8, veremos cómo pasar a los puertos normales 80/443 con un dominio propio. |

> No abras el puerto 22 a "cualquier IP" (`0.0.0.0/0`): es la puerta por la que la gente intenta entrar para atacar servidores. Déjala restringida a tu IP.

Cuando termines, lanza la instancia. AWS te dará una **IP pública** (por ejemplo `34.201.XX.XX`); la necesitarás en los siguientes pasos.

## 3. Conectarte a la instancia por SSH

Desde tu ordenador (en una terminal, con el archivo de la clave que descargaste antes):

```bash
chmod 400 ruta/a/tu-clave.pem
ssh -i ruta/a/tu-clave.pem ubuntu@IP_PUBLICA_DE_TU_INSTANCIA
```

- `chmod 400` deja la clave en modo "solo lectura para ti"; SSH rechaza claves con permisos más abiertos.
- El usuario por defecto en una instancia Ubuntu de AWS es `ubuntu`.
- Si te pregunta si confías en el host, responde `yes` (es la primera vez que te conectas a esa máquina).

Si ves un prompt como `ubuntu@ip-xxx-xx-xx-xx:~$`, ya estás dentro del servidor.

## 4. Instalar Docker en la instancia

Ya conectado por SSH, copia y pega estos comandos uno a uno (son los oficiales de Docker para Ubuntu):

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

Para no tener que escribir `sudo` delante de cada comando de Docker:

```bash
sudo usermod -aG docker $USER
```

Después de este último comando, **cierra la sesión SSH y vuelve a conectarte** (sal con `exit` y repite el comando `ssh` del paso 3) para que el cambio de permisos se aplique.

Comprueba que todo ha quedado bien:

```bash
docker --version
docker compose version
```

Si ambos comandos devuelven un número de versión (en vez de un error), Docker está listo.

## 5. Subir el código del proyecto a la instancia

La forma más sencilla es usar `git clone`, igual que en tu ordenador. Dentro de la instancia:

```bash
sudo apt-get install -y git
git clone <URL_DE_TU_REPOSITORIO>
cd app2-whatif
```

> Para: dime cuál es la URL de tu repositorio (o si el código no está todavía en ningún repositorio Git, lo vemos antes de este paso — puede ser un repositorio privado de GitHub, y entonces hay que configurar también una clave de acceso para poder clonarlo).

Si en algún momento cambias el código en tu ordenador y quieres actualizar la instancia, no hace falta repetir el `clone`: basta con entrar en la carpeta del proyecto dentro de la instancia y ejecutar `git pull`.

## 6. Configurar las variables de entorno reales

Dentro de la instancia, en la carpeta del proyecto:

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

`nano` es un editor de texto sencillo para la terminal. Rellena ahí las claves **reales** de Clerk y de OpenRouter (las mismas que usas en local, descritas en la sección "Configurar Clerk y OpenRouter" del [README](../README.md)). Para guardar y salir de `nano`: `Ctrl+O`, `Enter`, y luego `Ctrl+X`.

Algunas variables cambian respecto a tu entorno local, porque ya no estás en `localhost`:

- `CLERK_AUTHORIZED_PARTIES`: debe incluir la dirección pública por la que se va a acceder a la aplicación, por ejemplo `["http://IP_PUBLICA:8080"]` (o tu dominio, si ya tienes uno — ver el paso 8).
- `CORS_ORIGINS`: el mismo valor que `CLERK_AUTHORIZED_PARTIES`.

El archivo `backend/.env` **no se sube nunca a Git** (está en `.gitignore`); tienes que crearlo y rellenarlo a mano en cada sitio donde despliegues la aplicación.

La clave publicable de Clerk (`VITE_CLERK_PUBLISHABLE_KEY`) no va en un archivo `.env` en este caso: se pasa como variable al construir el contenedor del frontend, en el siguiente paso.

## 7. Levantar la aplicación con Docker Compose

Todavía dentro de la carpeta del proyecto, en la instancia:

```bash
export VITE_CLERK_PUBLISHABLE_KEY="tu_clave_publicable_de_clerk"
docker compose -f deploy/docker-compose.yml up --build -d
```

- `--build` construye las imágenes de backend y frontend a partir de los `Dockerfile` del proyecto (puede tardar un par de minutos la primera vez).
- `-d` ("detached") deja los contenedores funcionando en segundo plano, para que sigan corriendo aunque cierres la sesión SSH.

Para comprobar que los dos servicios están levantados:

```bash
docker compose -f deploy/docker-compose.yml ps
```

Deberías ver `backend` y `frontend` con estado `running`.

Ahora, desde tu propio navegador (no desde la instancia), abre:

```
http://IP_PUBLICA_DE_TU_INSTANCIA:8080
```

Si todo ha ido bien, verás la pantalla de la aplicación. Si no carga, revisa primero que el puerto 8080 esté abierto en el grupo de seguridad (paso 2) y después los registros de los contenedores:

```bash
docker compose -f deploy/docker-compose.yml logs -f
```

(`Ctrl+C` para salir de los registros sin apagar nada).

## 8. (Recomendado antes de un uso real) Dominio propio y HTTPS

Ahora mismo la aplicación se ve en `http://IP_PUBLICA:8080`, es decir, sin cifrar (HTTP) y con un puerto raro. Para algo más serio que una prueba de clase, conviene:

1. **Una IP fija**: por defecto, la IP pública de una instancia EC2 puede cambiar si la apagas y la vuelves a encender. AWS ofrece una **Elastic IP** gratuita (mientras esté asociada a una instancia en marcha) para fijarla.
2. **Un dominio**: comprar un dominio (o usar uno que ya tengas) y apuntarlo a esa Elastic IP.
3. **HTTPS**: instalar un certificado gratuito con [Let's Encrypt](https://letsencrypt.org/) (normalmente con la herramienta `certbot`), y cambiar `deploy/proxy.conf` para escuchar en el puerto 443 con ese certificate, en vez de en el 80/8080 sin cifrar.
4. Después de tener dominio y HTTPS, hay que **volver a actualizar** `CLERK_AUTHORIZED_PARTIES`, `CORS_ORIGINS` (en `backend/.env`) y abrir el puerto 443 en el grupo de seguridad, para que coincidan con la nueva dirección pública.

Este paso es opcional para una entrega de clase, pero es el que lo deja ya "listo para producción de verdad". Si llegado el momento quieres hacerlo, lo vemos juntos paso a paso igual que el resto de esta guía.

## 9. Actualizar la aplicación cuando cambie el código

Cada vez que hagas cambios en el proyecto y quieras llevarlos a la instancia:

```bash
cd app2-whatif
git pull
docker compose -f deploy/docker-compose.yml up --build -d
```

Docker Compose se encarga de reconstruir solo lo que ha cambiado y de reiniciar los contenedores sin perder la configuración.

## 10. Apagar o parar todo

- Para **detener** la aplicación sin borrar nada: `docker compose -f deploy/docker-compose.yml down` (desde la carpeta del proyecto, en la instancia).
- Para **apagar la instancia** (y dejar de generar actividad, aunque en la capa gratuita no te van a cobrar por horas dentro del límite): hazlo desde la consola de AWS, seleccionando la instancia y eligiendo "Stop".
- Si además quieres dejar de pagar por el disco asociado, tendrías que "Terminate" (terminar) la instancia, pero eso la borra por completo, incluido el código que hayas subido solo ahí. Antes de terminarla, asegúrate de que todo lo importante está también en tu repositorio Git.

## 11. Lista de comprobación de seguridad básica

Antes de considerar esto "desplegado en serio", repasa:

- [ ] El puerto 22 (SSH) solo está abierto para tu IP, no para `0.0.0.0/0`.
- [ ] El archivo de la clave `.pem` no está subido a ningún repositorio ni carpeta compartida.
- [ ] `backend/.env` existe solo en la instancia (y en tu máquina local), nunca en Git.
- [ ] `CLERK_AUTHORIZED_PARTIES` y `CORS_ORIGINS` apuntan exactamente a la dirección pública real de la aplicación, no a `localhost`.
- [ ] Revisas de vez en cuando la sección de facturación de AWS para confirmar que sigues dentro de la capa gratuita.

## Glosario rápido

| Término | Significado sencillo |
|---|---|
| EC2 | El servicio de AWS que te presta un ordenador virtual ("instancia") al que te conectas por internet. |
| AMI | La "imagen" del sistema operativo con la que arranca la instancia (en esta guía, Ubuntu). |
| Instancia | El ordenador virtual en sí, ya encendido y funcionando. |
| Key pair (par de claves) | El archivo que usas en lugar de una contraseña para entrar por SSH. |
| Security group (grupo de seguridad) | El cortafuegos de AWS: decide qué puertos están abiertos y desde dónde. |
| SSH | El protocolo para abrir una terminal remota en otro ordenador, en este caso la instancia EC2. |
| Elastic IP | Una IP pública fija que no cambia aunque reinicies la instancia. |
| Docker | La herramienta que empaqueta la aplicación (backend y frontend) en "contenedores" que funcionan igual en tu ordenador y en AWS. |
| Docker Compose | La herramienta que levanta varios contenedores a la vez (aquí, backend y frontend) con un solo comando. |
| Proxy inverso | El programa (en este proyecto, Nginx) que recibe las peticiones del navegador y decide si las sirve él mismo (la página) o las reenvía a otro servicio (el backend en `/api`). |
