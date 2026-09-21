# tools/backup_db.py
"""
Nightly SQLite backup — copies all *.db files in data/ to data/backups/
with a datestamp. Keeps last 30 backups.
"""
import logging, shutil, sqlite3, time
from pathlib import Path

logger = logging.getLogger("backup_db")

def run(data_dir: str = None) -> dict:
    data = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
    backup_dir = data / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    backed_up, errors = [], []
    for db_file in data.glob("*.db"):
        dest = backup_dir / f"{db_file.stem}_{stamp}.db"
        try:
            src_conn = sqlite3.connect(str(db_file))
            dst_conn = sqlite3.connect(str(dest))
            src_conn.backup(dst_conn)
            src_conn.close(); dst_conn.close()
            backed_up.append(str(dest.name))
            logger.info("Backed up %s → %s", db_file.name, dest.name)
        except Exception as exc:
            errors.append(f"{db_file.name}: {exc}")
            logger.error("Backup failed for %s: %s", db_file.name, exc)
    # Prune: keep last 30 backups per db stem
    for db_file in data.glob("*.db"):
        old = sorted(backup_dir.glob(f"{db_file.stem}_*.db"))
        for f in old[:-30]:
            f.unlink()
    return {"stamp": stamp, "backed_up": backed_up, "errors": errors}
