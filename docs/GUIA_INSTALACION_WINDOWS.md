# 🍽️ KaiRest POS — Guía de instalación en Windows

Esta guía te lleva paso a paso para instalar KaiRest en tu laptop o PC con Windows
y dejar tu restaurante funcionando en menos de 30 minutos. No necesitas saber de
computación — solo sigue cada paso en orden.

---

## ✅ Antes de empezar: ¿qué necesitas?

| Requisito | Detalle |
|---|---|
| **Computadora** | Laptop o PC con Windows 10 u 11 (64 bits) |
| **Memoria** | 8 GB de RAM o más |
| **Espacio libre** | Al menos 10 GB en el disco |
| **Internet** | Solo para la instalación (después el sistema funciona sin internet) |
| **La carpeta del programa** | Te la entrega tu proveedor (en USB o descarga) |

> 💡 **Tip:** usa la computadora que se va a quedar en el negocio. Esta computadora
> será el "cerebro" del sistema — las tablets y celulares de los meseros se
> conectarán a ella por wifi.

---

## Parte 1 — Instalar Docker Desktop (una sola vez)

Docker es el programa que hace funcionar a KaiRest. Es gratis.

1. Abre tu navegador y entra a: **https://www.docker.com/products/docker-desktop**
2. Haz clic en **"Download for Windows"** y espera la descarga.
3. Abre el archivo descargado (`Docker Desktop Installer.exe`) y dale
   **Siguiente / OK** a todo. Si te pregunta por "WSL 2", déjalo marcado.
4. Al terminar, **reinicia la computadora**.
5. Después de reiniciar, abre **Docker Desktop** desde el menú de inicio y espera
   a que en la esquina inferior izquierda diga **"Engine running"** (motor corriendo,
   con un puntito verde). La primera vez puede tardar unos minutos.

> ⚠️ Si Docker te pide aceptar términos de servicio o crear cuenta, puedes aceptar
> los términos y **omitir** la creación de cuenta (no es necesaria).

---

## Parte 2 — Instalar KaiRest

1. Copia la carpeta **`kairest`** que te entregó tu proveedor a tus **Documentos**
   (o al Escritorio, donde la encuentres fácil).
2. Abre la carpeta y localiza el archivo **`install.ps1`**.
3. Haz **clic derecho** sobre `install.ps1` → **"Ejecutar con PowerShell"**.
   - Si Windows pregunta "¿Deseas permitir que esta aplicación haga cambios?",
     responde **Sí**.
   - Si aparece un aviso de seguridad de PowerShell, escribe `R` (una vez) y Enter.
4. Aparecerá una ventana negra con letras — es normal. El instalador va a:
   - ✔ Verificar que Docker esté corriendo
   - ✔ Crear la configuración con contraseñas seguras automáticas
   - ✔ Armar el sistema (la primera vez tarda **2 a 5 minutos** — paciencia ☕)
   - ✔ Abrir tu navegador automáticamente cuando esté listo
5. Si Windows pregunta si permites el acceso a la red ("Firewall de Windows"),
   haz clic en **"Permitir acceso"** — esto es lo que deja que las tablets se conecten.

Cuando veas el mensaje verde **"KaiRest instalado exitosamente"**, pasa a la Parte 3.

---

## Parte 3 — Configurar tu restaurante (asistente de 5 pasos)

Al abrir el navegador verás el asistente de configuración. Solo se hace una vez.

### Paso 1 de 5 — Tu Negocio 🏪
Escribe el **nombre de tu restaurante o puesto** (ej. "Barbacoa Don Chuy") y da
clic en **Siguiente**. Este nombre aparecerá en los tickets.

### Paso 2 de 5 — Tu cuenta de administrador 👤
Crea **tu** usuario (el del dueño o encargado):
- **Nombre**: tu nombre.
- **Email**: será tu usuario para entrar al sistema (ej. `dueno@minegocio.com` —
  no necesita ser un correo real, pero apúntalo).
- **Contraseña**: mínimo 8 caracteres, con al menos una mayúscula, una minúscula
  y un número (ej. `Barbacoa2026`). **Apúntala en un lugar seguro.**

### Paso 3 de 5 — Tu Menú 🌮
Elige cómo cargar tus productos:
- **Plantilla** (recomendado para empezar): elige "Taquería", "Restaurante/Fonda"
  o "Cafetería" y tendrás un menú de ejemplo listo, con precios que después puedes
  cambiar.
- **¿Cuántas estaciones de cocina tienes?** Aquí eliges cuántas áreas de
  preparación hay en tu cocina y cómo se llaman (ej. 2 estaciones: "Barbacoa" y
  "Bebidas"). El sistema reparte los productos entre tus estaciones — cada
  estación tendrá su propia pantalla de cocina.
- **Manual**: si prefieres, captura tus productos uno por uno con nombre, precio,
  categoría y estación.

> 💡 No te preocupes por dejarlo perfecto: todo el menú se puede editar después
> desde el panel de administración.

### Paso 4 de 5 — Mesas 🪑
Indica **cuántas mesas** tiene tu negocio (ej. 8). El sistema las numera
automáticamente. Si vendes solo para llevar, deja una mesa — no estorba.

### Paso 5 de 5 — Tu Equipo 👥
Crea los usuarios de tu personal (puedes agregar más después):
- Por cada **mesero**: nombre, email (ej. `juan@minegocio.com`), contraseña y
  rol **"Mesero"**.
- Por cada **cocinero**: igual, pero elige el rol **"Cocina — [su estación]"**
  (ej. "Cocina — Barbacoa"). Así, al entrar al sistema, esa persona verá
  directamente los pedidos de su estación.

Da clic en **Finalizar** y el sistema te llevará a la pantalla de inicio de sesión.
**¡Listo!** Entra con el email y contraseña que creaste en el Paso 2.

---

## Parte 4 — Conectar las tablets y celulares de los meseros 📱

1. En la computadora, presiona la tecla **Windows**, escribe `cmd` y abre el
   "Símbolo del sistema". Escribe `ipconfig` y presiona Enter.
2. Busca la línea **"Dirección IPv4"** — es algo como `192.168.1.50`. Apúntala.
3. En cada tablet o celular (conectado a **la misma red wifi** del negocio), abre
   el navegador y entra a: `http://192.168.1.50:5005` (con la IP que apuntaste).
4. Cada mesero inicia sesión con su usuario → verá su pantalla de mesero.
   Cada cocinero inicia sesión → verá la pantalla de su estación de cocina.
5. **Tip:** en el navegador de la tablet, usa "Agregar a pantalla de inicio" para
   que quede como una app con su propio ícono.

> 📶 El sistema funciona en tu red wifi local **aunque se caiga el internet**.
> Solo asegúrate de que el módem/router siga prendido (el wifi local sigue
> funcionando sin internet).

---

## Uso diario

| Acción | Cómo |
|---|---|
| **Encender el sistema** | Prende la computadora y abre Docker Desktop. KaiRest arranca solo. |
| **Entrar al sistema** | Navegador → `http://localhost:5005` (o la IP desde tablets) |
| **Apagar el sistema** | Basta con apagar la computadora normalmente. |
| **Respaldo de datos** | Automático cada hora, en la carpeta `backups`. |

### Si algo no funciona
1. Revisa que **Docker Desktop** esté abierto y diga "Engine running".
2. Cierra y vuelve a abrir el navegador, entra de nuevo a `http://localhost:5005`.
3. Si sigue sin funcionar: reinicia la computadora, abre Docker Desktop, espera
   1 minuto y vuelve a intentar.
4. Si nada de esto funciona, contacta a tu proveedor — tus datos están seguros
   en los respaldos automáticos.

### Para actualizar el sistema (cuando tu proveedor te lo indique)
Clic derecho en **`update.ps1`** → "Ejecutar con PowerShell". El sistema hace un
respaldo automático antes de actualizar.

---

*KaiRest POS — hecho por KAINET*
