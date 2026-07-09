import os
import subprocess
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict
from app.core.config import settings

class BackupService:
    def __init__(self):
        # We use a path relative to the app root
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir = Path(settings.UPLOAD_DIR)

    def create_backup(self) -> str:
        """
        Creates a ZIP backup containing the database dump and uploads folder.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        temp_dir = self.backup_dir / backup_name
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Database Dump
            db_url = settings.DATABASE_URL
            sql_file = temp_dir / "database.sql"
            
            # Using pg_dump with --dbname flag which handles the URL
            # Note: postgresql-client must be installed in the environment
            result = subprocess.run(
                ["pg_dump", "--dbname=" + db_url, "-f", str(sql_file), "--clean", "--if-exists"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Error al exportar base de datos: {result.stderr}")

            # 2. Copy Uploads
            if self.uploads_dir.exists():
                shutil.copytree(self.uploads_dir, temp_dir / "uploads", dirs_exist_ok=True)

            # 3. Create Zip
            zip_file_path = self.backup_dir / f"{backup_name}.zip"
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = Path(root) / file
                        # Store relative to temp_dir
                        zf.write(file_path, file_path.relative_to(temp_dir))

            return str(zip_file_path.name)

        except Exception as e:
            raise e
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def list_backups(self) -> List[Dict]:
        """
        Returns a list of available backups.
        """
        backups = []
        for file in self.backup_dir.glob("*.zip"):
            stats = file.stat()
            backups.append({
                "filename": file.name,
                "size_bytes": stats.st_size,
                "created_at": datetime.fromtimestamp(stats.st_mtime).isoformat()
            })
        # Sort by creation time (newest first)
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def restore_backup(self, filename: str):
        """
        Restores a backup from a ZIP file.
        """
        zip_path = self.backup_dir / filename
        if not zip_path.exists():
            raise FileNotFoundError(f"Archivo de respaldo {filename} no encontrado")

        temp_extract_dir = self.backup_dir / "temp_restore"
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)
        temp_extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_extract_dir)

            # 1. Restore Database
            sql_file = temp_extract_dir / "database.sql"
            if not sql_file.exists():
                raise Exception("El archivo database.sql no se encuentra en el respaldo")

            db_url = settings.DATABASE_URL
            
            # Using psql to restore the dump
            # --clean in pg_dump helps by dropping objects before creating them
            result = subprocess.run(
                ["psql", "--dbname=" + db_url, "-f", str(sql_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Error al restaurar base de datos: {result.stderr}")

            # 2. Restore Uploads
            backup_uploads = temp_extract_dir / "uploads"
            if backup_uploads.exists():
                # Clear current uploads and copy from backup
                if self.uploads_dir.exists():
                    shutil.rmtree(self.uploads_dir)
                shutil.copytree(backup_uploads, self.uploads_dir)

            return True
        except Exception as e:
            raise e
        finally:
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)

    def delete_backup(self, filename: str) -> bool:
        """
        Deletes a backup file.
        """
        file_path = self.backup_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get_backup_path(self, filename: str) -> Path:
        """
        Returns the absolute path to a backup file.
        """
        file_path = self.backup_dir / filename
        if not file_path.exists():
             raise FileNotFoundError("Archivo no encontrado")
        return file_path

    def cleanup_old_backups(self, keep_last: int = 7):
        """
        Deletes old backups, keeping only the 'keep_last' most recent ones.
        """
        backups = self.list_backups()
        if len(backups) > keep_last:
            to_delete = backups[keep_last:]
            for b in to_delete:
                self.delete_backup(b["filename"])
            return len(to_delete)
        return 0
