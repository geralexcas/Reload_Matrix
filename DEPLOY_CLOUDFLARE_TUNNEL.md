# Deploy Reload Matrix con Cloudflare Tunnel

## Arquitectura resultante

```
Usuario → Cloudflare (CDN + SSL + WAF) → Cloudflare Tunnel → 192.168.1.13:80 → nginx (frontend) → backend:8000 → PostgreSQL
```

**Ventajas clave:**

- No abres NINGUN puerto en el router
- Tu IP publica nunca se expone en DNS
- Funciona incluso con ISP que bloquea puertos
- Cloudflare maneja el SSL automaticamente
- Gratis para uso individual

---

## Paso 1: Registrar dominio y configurar Cloudflare

1. Registrar un dominio (Cloudflare Registrar, Namecheap, GoDaddy, etc.)
2. Crear cuenta en [cloudflare.com](https://cloudflare.com) y agregar el dominio
3. Cambiar los nameservers del dominio a los que Cloudflare indique
4. Esperar propagacion (1-48h)

---

## Paso 2: Instalar `cloudflared` en el servidor (192.168.1.13)

```bash
# Debian/Ubuntu
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Verificar
cloudflared --version
```

---

## Paso 3: Autenticar cloudflared con Cloudflare

```bash
cloudflared tunnel login
```

Esto abre un navegador (o da una URL) para autorizar `cloudflared` con tu cuenta de Cloudflare. Se guarda una credencial en `~/.cloudflared/cert.pem`.

---

## Paso 4: Crear el tunel

```bash
cloudflared tunnel create reload-matrix
```

Esto genera:

- Un **tunnel ID** (UUID) — anotarlo
- Un archivo de credenciales en `~/.cloudflared/<tunnel-id>.json`

---

## Paso 5: Configurar DNS en Cloudflare

```bash
# Reemplazar <tunnel-id> con el UUID del paso anterior
# Reemplazar midominio.com con tu dominio real
cloudflared tunnel route dns reload-matrix midominio.com
cloudflared tunnel route dns reload-matrix www.midominio.com
```

Esto crea registros CNAME apuntando a `<tunnel-id>.cfargotunnel.com` con proxy activado.

---

## Paso 6: Crear archivo de configuracion del tunel

Crear `~/.cloudflared/config.yml`:

```yaml
tunnel: <tunnel-id>
credentials-file: /home/tu_usuario/.cloudflared/<tunnel-id>.json

ingress:
  # Frontend + API (todo va por nginx en el puerto 80)
  - hostname: midominio.com
    service: http://localhost:80
  - hostname: www.midominio.com
    service: http://localhost:80
  # Catch-all rule (requerido)
  - service: http_status:404
```

Todo el trafico (frontend y API) pasa por nginx en el puerto 80 del contenedor frontend. Nginx ya hace el proxy de `/api/` al backend internamente.

---

## Paso 7: Modificar `docker-compose.yml` para produccion

Cambios:

- Frontend expone puerto 80 al host (solo local, para el tunel)
- Backend y PostgreSQL NO exponen puertos al host (solo comunicacion interna entre contenedores)
- Credenciales PostgreSQL seguras

```yaml
services:
  backend:
    build: ./backend
    # NO exponer puerto al host - solo comunicacion interna
    expose:
      - "8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://usuario_seguro:password_seguro@db:5432/business_db
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    volumes:
      - ./backend/backups:/app/backups
      - ./uploads:/app/uploads
    networks:
      - app_network

  frontend:
    build: ./frontend
    ports:
      - "127.0.0.1:80:80"  # Solo accesible localmente (para cloudflared)
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - app_network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=business_db
      - POSTGRES_USER=usuario_seguro
      - POSTGRES_PASSWORD=password_seguro
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # NO exponer puerto al host
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U usuario_seguro -d business_db"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - app_network

volumes:
  postgres_data:

networks:
  app_network:
    driver: bridge
```

**Clave:** `127.0.0.1:80:80` asegura que solo el servidor local (donde corre `cloudflared`) pueda acceder al frontend. Desde internet es imposible conectarse directamente.

---

## Paso 8: Actualizar `frontend/nginx.conf`

Cambiar `server_name` al dominio real y agregar headers de seguridad:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name midominio.com www.midominio.com;

    # Headers de seguridad
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

---

## Paso 9: Configurar `.env` para produccion

Crear `.env` en la raiz del proyecto:

```env
# Backend
SECRET_KEY=<generar_con_openssl_rand_hex_32>
DATABASE_URL=postgresql://usuario_seguro:password_seguro@db:5432/business_db
ALLOWED_ORIGINS=https://midominio.com,https://www.midominio.com
LOG_LEVEL=WARNING
UPLOAD_DIR=uploads
ENVIRONMENT=production

# DIAN
DIAN_ENVIRONMENT=test
DIAN_CERT_PATH=
DIAN_CERT_PASSWORD=
```

`ALLOWED_ORIGINS` debe usar `https://` ya que Cloudflare sirve SSL al cliente.

---

## Paso 10: Levantar la aplicacion

```bash
cd /ruta/Reload_Matrix

# Generar SECRET_KEY
openssl rand -hex 32

# Editar .env con los valores correctos

# Construir e iniciar
docker compose up -d --build

# Inicializar DB
docker compose exec backend python scripts/init_database.py
docker compose exec backend python scripts/init_permissions.py
docker compose exec backend python scripts/create_admin.py

# Verificar internamente
curl http://localhost:80
```

---

## Paso 11: Probar el tunel manualmente

```bash
cloudflared tunnel run reload-matrix
```

En otra terminal, verificar desde fuera:

```bash
curl -I https://midominio.com
```

Si funciona, continuar al paso 12.

---

## Paso 12: Configurar `cloudflared` como servicio systemd

```bash
# Crear el servicio
sudo cloudflared service install

# Iniciar y habilitar
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Verificar estado
sudo systemctl status cloudflared
```

`cloudflared service install` usa el `config.yml` de `~/.cloudflared/` y corre como servicio del sistema. Se reinicia automaticamente si falla o si el servidor se reinicia.

---

## Paso 13: Configurar SSL en Cloudflare

En el dashboard de Cloudflare:

1. **SSL/TLS > Overview:** Modo **Full** (no Flexible)
2. **SSL/TLS > Edge Certificates:** Activar "Always Use HTTPS" y "Automatic HTTPS Rewrites"
3. **Security > Settings:** Security Level en "Medium"

---

## Paso 14: Verificacion final

```bash
# Desde fuera de tu red (ej: celular con datos)
curl -I https://midominio.com           # Frontend
curl -I https://midominio.com/api/v1/   # Backend API

# Verificar que NO se puede acceder directamente a la IP
curl -I http://TU_IP_PUBLICA:80         # Debe fallar

# Verificar que los puertos internos no estan expuestos
curl -I http://TU_IP_PUBLICA:8001       # Debe fallar
```

---

## Archivos a modificar (resumen)

| Archivo | Cambio |
|---------|--------|
| `.env` (nuevo) | Variables de produccion con SECRET_KEY, ALLOWED_ORIGINS con dominio |
| `docker-compose.yml` | Exponer solo `127.0.0.1:80:80` en frontend, eliminar puertos externos de backend/DB, credenciales seguras |
| `frontend/nginx.conf` | `server_name` con dominio real, headers de seguridad |
| `~/.cloudflared/config.yml` (nuevo) | Configuracion del tunel Cloudflare |

---

## Notas adicionales

- **No necesitas abrir puertos en el router** — `cloudflared` inicia conexiones salientes a Cloudflare, no entrantes
- **Si el servidor se reinicia**, tanto Docker Compose como `cloudflared` se levantan automaticamente si configuraste systemd
- **Tu IP publica nunca aparece en DNS** — Cloudflare muestra sus propias IPs
- **Cloudflare Tunnel es gratuito** para uso individual/pequeno negocio
- Considera hacer **backups regulares** de PostgreSQL:
  ```bash
  docker compose exec db pg_dump -U usuario_seguro business_db > backup.sql
  ```
- Para restaurar un backup:
  ```bash
  cat backup.sql | docker compose exec -T db psql -U usuario_seguro business_db
  ```
