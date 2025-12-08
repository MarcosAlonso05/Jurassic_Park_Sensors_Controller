import logging
import os
import sys

def setup_logging():
    # 1. Asegurar que existe la carpeta
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "jurassic_system.log")

    # 2. Definir el formato
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # 3. Configurar el FileHandler (Escribir en disco)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 4. Configurar el StreamHandler (Escribir en consola)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers = []
    
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    app_logger = logging.getLogger("JurassicReactor")
    app_logger.setLevel(logging.INFO)
    
    print(f">>> Logging setup complete. Writing to: {os.path.abspath(log_file)}")