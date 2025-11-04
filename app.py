"""
Punt d'entrada principal de l'aplicació
Gestor de Treballadors - Sistema d'Assignacions
"""
import sys
import logging
from pathlib import Path

# Configurar logging abans d'importar altres mòduls
import config

# Crear directori de logs si no existeix
config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Funció principal de l'aplicació"""
    try:
        logger.info("=" * 60)
        logger.info("Iniciant aplicació Gestor de Treballadors")
        logger.info("=" * 60)
        
        # Verificar que existeix la base de dades
        if not config.DB_PATH.exists():
            logger.error(f"Base de dades no trobada: {config.DB_PATH}")
            
            # Mostrar error en GUI
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error",
                f"No s'ha trobat la base de dades:\n{config.DB_PATH}\n\n"
                f"Assegura't que el fitxer existeix abans d'executar l'aplicació."
            )
            root.destroy()
            sys.exit(1)
        
        # Importar i crear finestra principal
        from gui.main_window import MainWindow
        
        app = MainWindow()
        logger.info("Finestra principal creada")
        
        # Executar aplicació
        logger.info("Iniciant bucle principal de l'aplicació")
        app.mainloop()
        
        logger.info("Aplicació tancada correctament")
        
    except Exception as e:
        logger.error(f"Error fatal en l'aplicació: {e}", exc_info=True)
        
        # Intentar mostrar error en GUI
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error Fatal",
                f"S'ha produït un error crític:\n\n{str(e)}\n\n"
                f"Consulta el fitxer de log per més detalls:\n{config.LOG_FILE}"
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
