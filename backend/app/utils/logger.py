import logging
import sys
from pathlib import Path


def setup_logger(log_level=logging.INFO):
    """
    Configura el sistema de logging.
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configuración básica
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "hydrous.log"),
        ],
    )

    # Reducir verbosidad de algunas librerías
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)

    logger = logging.getLogger("hydrous")
    logger.info("Sistema de logging inicializado")
    return logger


# Crear logger principal
logger = setup_logger()
