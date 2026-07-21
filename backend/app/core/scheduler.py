from apscheduler.schedulers.background import BackgroundScheduler
from app.services.backup_service import BackupService
import logging
from datetime import datetime, timedelta, timezone

# Configuración de logging para ver las tareas en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()

def scheduled_backup():
    """
    Tarea programada para crear un respaldo y limpiar los antiguos.
    """
    logger.info(f"[{datetime.now()}] Iniciando copia de seguridad programada...")
    try:
        service = BackupService()
        # 1. Crear el nuevo respaldo
        filename = service.create_backup()
        logger.info(f"Copia de seguridad creada: {filename}")

        # 2. Subir a almacenamiento offsite (S3-compatible) si esta configurado
        uploaded = service.upload_to_s3(filename)
        if uploaded:
            logger.info(f"Respaldo subido a almacenamiento offsite: {filename}")

        # 3. Mantener solo los últimos 7 días (ajustable)
        deleted_count = service.cleanup_old_backups(keep_last=7)
        if deleted_count > 0:
            logger.info(f"Se eliminaron {deleted_count} respaldos antiguos.")
            
    except Exception as e:
        logger.error(f"Error en la copia de seguridad programada: {str(e)}")

def check_trial_expirations():
    """
    Revisa empresas en periodo de prueba cuyo trial haya expirado (>60 días)
    y las desactiva automáticamente.
    """
    from app.models.sql.company import Company
    from app.core.database import SessionLocal

    logger.info(f"[{datetime.now()}] Revisando empresas en periodo de prueba expirado...")
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=60)
        expired = (
            db.query(Company)
            .filter(
                Company.is_trial == True,
                Company.is_active == True,
                Company.created_at < cutoff,
            )
            .all()
        )
        for company in expired:
            company.is_active = False
            logger.info(
                f"Trial expirado para empresa {company.id} ({company.name}) — desactivada"
            )
        db.commit()
        if expired:
            logger.info(f"Se desactivaron {len(expired)} empresa(s) por trial expirado.")
        else:
            logger.info("No se encontraron empresas con trial expirado.")
    except Exception as e:
        logger.error(f"Error revisando trials expirados: {str(e)}")
    finally:
        db.close()

def start_scheduler():
    """
    Inicia el programador de tareas.
    """
    # Programar cada 24 horas. 
    # También se puede usar 'cron' para que sea a una hora específica (ej: 02:00 AM)
    # scheduler.add_job(scheduled_backup, 'cron', hour=2)
    
    # Por ahora usamos interval de 24h para simplicidad
    scheduler.add_job(
        scheduled_backup, 
        'interval', 
        hours=24, 
        id='daily_backup',
        replace_existing=True
    )
    scheduler.add_job(
        check_trial_expirations,
        'interval',
        hours=24,
        id='trial_expiry',
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("Programador de tareas iniciado. Copia de seguridad y verificación de trials cada 24 horas.")

def stop_scheduler():
    """
    Detiene el programador de tareas.
    """
    scheduler.shutdown()
    logger.info("Programador de tareas detenido.")
