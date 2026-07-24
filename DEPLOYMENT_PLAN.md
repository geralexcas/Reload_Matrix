# Plan de Despliegue: VentasPost (Reload Matrix) en VPS

Este documento detalla la estrategia paso a paso para desplegar la nueva aplicación en el VPS (`147.93.187.65`) bajo el dominio `ventaspost.com`, garantizando el aislamiento total y la continuidad operativa de las aplicaciones existentes (`etemis.com` y `evocomputo.com`).

---

## Fase 1: Respaldo (Backup preventivo)
Antes de realizar cualquier modificación, se asegura el estado actual del servidor:
1. Respaldo de configuraciones de Nginx:
   ```bash
   sudo tar -cvzf /root/nginx_backup_$(date +%F).tar.gz /etc/nginx/
   ```
2. Respaldo de directorios de bases de datos/datos críticos de las apps existentes (recomendado manualmente por el administrador).

## Fase 2: Preparación del Entorno
1. Creación del directorio aislado para la nueva aplicación:
   ```bash
   sudo mkdir -p /opt/ventaspost
   ```
2. Configuración de puertos libres en el `docker-compose.yml` de la nueva app para evitar colisiones (`8000` y `8080` ya están ocupados):
   - **Backend:** Puerto host `8002` -> Contenedor `8000`
   - **Frontend:** Puerto host `8082` -> Contenedor `80`

## Fase 3: Configuración del Proxy Inverso (Nginx)
Creación de un bloque independiente en `/etc/nginx/sites-available/ventaspost.conf`:
- Redirección de HTTP a HTTPS.
- Enrutamiento de tráfico general al Frontend (`http://127.0.0.1:8082`).
- Enrutamiento de peticiones de API al Backend (`http://127.0.0.1:8002`).
- Activación mediante enlace simbólico en `sites-enabled/`.

## Fase 4: Certificación SSL y Activación
1. Validación de la sintaxis de Nginx: `sudo nginx -t`
2. Recarga del servidor web: `sudo systemctl reload nginx`
3. Generación y aplicación de certificados Let's Encrypt mediante Certbot:
   ```bash
   sudo certbot --nginx -d ventaspost.com -d www.ventaspost.com
   ```
