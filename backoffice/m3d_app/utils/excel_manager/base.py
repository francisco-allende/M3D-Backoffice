import pandas as pd
from django.db import transaction

class ExcelManagerBase:
    """
    Clase base para gestores de Excel que contiene métodos comunes.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa el gestor de Excel.
        
        Args:
            logger: Objeto de registro para guardar mensajes de depuración y errores.
        """
        self.logger = logger
        
    def log(self, message, level='info'):
        """
        Registra un mensaje utilizando el logger proporcionado.
        
        Args:
            message: Mensaje a registrar.
            level: Nivel de registro ('info', 'warning', 'error', etc.).
        """
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message)
        else:
            print(f"[{level.upper()}] {message}")
            
    def read_excel(self, file_path, sheet_name=0):
        """
        Lee un archivo Excel y devuelve un DataFrame de pandas.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer (por defecto: 0 - primera hoja).
            
        Returns:
            DataFrame de pandas con los datos del Excel.
        """
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            self.log(f"Error al leer el archivo Excel {file_path}: {str(e)}", 'error')
            raise
            
    def find_column(self, df, search_terms):
        """
        Busca una columna en el DataFrame por términos de búsqueda.
        
        Args:
            df: DataFrame de pandas.
            search_terms: Lista de términos para buscar en los nombres de columna.
            
        Returns:
            Nombre de la columna encontrada o None si no se encuentra.
        """
        for col in df.columns:
            col_str = str(col).lower()
            if any(term.lower() in col_str for term in search_terms):
                return col
        return None