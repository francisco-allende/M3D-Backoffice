from .base import ExcelManagerBase
from .manage_subs import ExcelManagerForSubs
from .manage_nodos import ExcelManagerForNodos
from .manage_bloques import ExcelManagerForBloques

class ExcelManager(ExcelManagerBase):
    """
    Clase principal que coordina los distintos gestores de Excel especializados.
    Actúa como fachada para acceder a los métodos de importación específicos.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa el gestor de Excel principal y sus subgestores.
        
        Args:
            logger: Objeto de registro para guardar mensajes de depuración y errores.
        """
        super().__init__(logger)
        self.subs_manager = ExcelManagerForSubs(logger)
        self.nodos_manager = ExcelManagerForNodos(logger)
        self.bloques_manager = ExcelManagerForBloques(logger)
    
    # Métodos para importación de suscriptores
    def import_particulares_con_impresora(self, file_path, sheet_name=0):
        return self.subs_manager.import_particulares_con_impresora(file_path, sheet_name)
    
    def import_particulares_sin_impresora(self, file_path, sheet_name=0):
        return self.subs_manager.import_particulares_sin_impresora(file_path, sheet_name)
    
    def import_instituciones_con_impresora(self, file_path, sheet_name=0):
        return self.subs_manager.import_instituciones_con_impresora(file_path, sheet_name)
    
    def import_instituciones_sin_impresora(self, file_path, sheet_name=0):
        return self.subs_manager.import_instituciones_sin_impresora(file_path, sheet_name)
    
    # Métodos para importación de nodos
    def import_nodos_recepcion(self, file_path, sheet_name=0):
        return self.nodos_manager.import_nodos_recepcion(file_path, sheet_name)
    
    # Métodos para importación de bloques
    def import_bloques_participantes(self, file_path, sheet_name=0):
        return self.bloques_manager.import_bloques_participantes(file_path, sheet_name)