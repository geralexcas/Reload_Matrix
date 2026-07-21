import io
import zipfile

import pytest

from app.services.backup_service import BackupService


@pytest.fixture
def backup_svc(tmp_path, monkeypatch):
    svc = BackupService()
    svc.backup_dir = tmp_path / "backups"
    svc.backup_dir.mkdir()
    svc.uploads_dir = tmp_path / "uploads"
    return svc


class TestResolveBackupPath:
    def test_valid_name(self, backup_svc):
        path = backup_svc._resolve_backup_path("backup_20260101_120000.zip")
        assert path.parent == backup_svc.backup_dir.resolve()
        assert path.name == "backup_20260101_120000.zip"

    def test_strips_directory_components(self, backup_svc):
        path = backup_svc._resolve_backup_path("../../etc/passwd.zip")
        assert path.name == "passwd.zip"
        assert path.is_relative_to(backup_svc.backup_dir.resolve())

    def test_rejects_non_zip(self, backup_svc):
        with pytest.raises(ValueError):
            backup_svc._resolve_backup_path("backup.sql")

    def test_rejects_empty(self, backup_svc):
        with pytest.raises(ValueError):
            backup_svc._resolve_backup_path("")

    def test_get_missing_raises(self, backup_svc):
        with pytest.raises(FileNotFoundError):
            backup_svc.get_backup_path("nope.zip")


class TestSafeExtract:
    def test_extracts_safe_members(self, backup_svc, tmp_path):
        dest = tmp_path / "out"
        dest.mkdir()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("database.sql", "SELECT 1;")
            zf.writestr("uploads/logo.png", b"png")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            backup_svc._safe_extract(zf, dest)
        assert (dest / "database.sql").read_text() == "SELECT 1;"
        assert (dest / "uploads" / "logo.png").read_bytes() == b"png"

    def test_rejects_zip_slip(self, backup_svc, tmp_path):
        dest = tmp_path / "out"
        dest.mkdir()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../evil.txt", "pwned")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            with pytest.raises(ValueError, match="insegura"):
                backup_svc._safe_extract(zf, dest)
        assert not (tmp_path / "evil.txt").exists()
