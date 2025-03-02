import re
import pandas as pd
from datetime import datetime

class ExcelParser:
   
    @staticmethod
    def clean_phone_number(phone_str):
        """
        Limpia un número de teléfono, eliminando apóstrofes iniciales y otros caracteres no deseados.
        
        Args:
            phone_str: Cadena de texto que representa un número de teléfono.
            
        Returns:
            str: Número de teléfono limpio.
        """
        if not phone_str or pd.isna(phone_str):
            return ""
            
        # Convertir a string si no lo es
        phone_str = str(phone_str).strip()
        
        # Eliminar apóstrofes al inicio
        phone_str = phone_str.lstrip("'")
        
        return phone_str
    
    @staticmethod
    def parse_date(date_str):
        """
        Intenta parsear una fecha en varios formatos posibles.
        
        Args:
            date_str: Cadena de texto que representa una fecha.
            
        Returns:
            datetime: Objeto datetime con la fecha parseada o None si no se pudo parsear.
        """
        if not date_str or pd.isna(date_str):
            return None
            
        # Convertir a string si no lo es
        date_str = str(date_str).strip()
        
        # Lista de formatos a intentar
        formats = [
            '%d/%m/%Y',          # 18/02/1985
            '%d-%m-%Y',          # 22-07-1962
            '%Y-%m-%d',          # 1985-02-18 (formato ISO)
            '%d %m %Y',          # 20 08 1961
            '%d de %B de %Y',    # 31 de Marzo de 1995
            '%d %B %Y',          # 12 Enero 1988
            '%d%m%Y'             # 06081990
        ]
        
        # Meses en español
        spanish_months = {
            'enero': 'January',
            'febrero': 'February',
            'marzo': 'March',
            'abril': 'April',
            'mayo': 'May',
            'junio': 'June',
            'julio': 'July',
            'agosto': 'August',
            'septiembre': 'September',
            'octubre': 'October',
            'noviembre': 'November',
            'diciembre': 'December'
        }
        
        # Reemplazar nombres de meses en español por sus equivalentes en inglés
        lower_date_str = date_str.lower()
        for es_month, en_month in spanish_months.items():
            if es_month in lower_date_str:
                lower_date_str = lower_date_str.replace(es_month, en_month)
        
        # Intentar cada formato
        for fmt in formats:
            try:
                if fmt == '%d de %B de %Y' or fmt == '%d %B %Y':
                    return datetime.strptime(lower_date_str, fmt).date()
                else:
                    return datetime.strptime(date_str, fmt).date()
            except (ValueError, TypeError):
                continue
                
        # Si llegamos aquí, no se pudo parsear la fecha
        print(f"[WARNING] No se pudo parsear la fecha: {date_str}")
        return None
    
    @staticmethod
    def parse_years_experience(exp_str):
        """
        Parsea una cadena que representa años de experiencia a un número entero.
        
        Args:
            exp_str: Cadena de texto que representa años de experiencia (ej: "5 años", "Un año", etc.).
            
        Returns:
            int: Número de años de experiencia o None si no se pudo parsear.
        """
        if not exp_str or pd.isna(exp_str):
            return None
            
        # Convertir a string si no lo es
        exp_str = str(exp_str).lower().strip()
        
        # Si ya es un número, convertirlo directamente
        if exp_str.isdigit():
            return int(exp_str)
            
        # Buscar patrones comunes
        
        # Patrón "X años" o "X año"
        match = re.search(r'(\d+)\s*(año|años|year|years|anio|anios)', exp_str)
        if match:
            return int(match.group(1))
            
        # Patrón "X meses" o "X mes"
        match = re.search(r'(\d+)\s*(mes|meses|month|months)', exp_str)
        if match:
            # Convertir meses a años (redondeando a 0 para menos de 12 meses)
            months = int(match.group(1))
            return max(0, months // 12)
            
        # Palabras numéricas
        num_words = {
            'un': 1, 'uno': 1, 'una': 1, 'one': 1,
            'dos': 2, 'two': 2,
            'tres': 3, 'three': 3,
            'cuatro': 4, 'four': 4,
            'cinco': 5, 'five': 5,
            'seis': 6, 'six': 6,
            'siete': 7, 'seven': 7,
            'ocho': 8, 'eight': 8,
            'nueve': 9, 'nine': 9,
            'diez': 10, 'ten': 10
        }
        
        for word, value in num_words.items():
            if word in exp_str and ('año' in exp_str or 'anio' in exp_str or 'year' in exp_str):
                return value
                
        # Casos específicos
        if 'menos de un año' in exp_str or 'recién comienzo' in exp_str or '0 años' in exp_str:
            return 0
            
        if 'desde el 2022' in exp_str:
            current_year = datetime.now().year
            return current_year - 2022
        
        # No se pudo parsear, loguear y retornar un valor por defecto
        print(f"[WARNING] No se pudo parsear años de experiencia: {exp_str}")
        return 0  # Valor por defecto
    
    @staticmethod
    def parse_equipment_count(count_str):
        """
        Parsea una cadena que representa cantidad de equipos a un número entero.
        
        Args:
            count_str: Cadena de texto que representa cantidad de equipos (ej: "Uno", "2 de fábrica y una que armé yo", etc.).
            
        Returns:
            int: Número de equipos o 1 como valor por defecto.
        """
        if not count_str or pd.isna(count_str):
            return 1  # Valor por defecto si no hay información
            
        # Convertir a string si no lo es
        count_str = str(count_str).lower().strip()
        
        # Si ya es un número, convertirlo directamente
        if count_str.isdigit():
            return int(count_str)
            
        # Diccionario de palabras numéricas
        num_words = {
            'uno': 1, 'un': 1, 'una': 1, 'one': 1, '1 solo': 1, 'solo uno': 1, 'poseo un equipo': 1,
            'dos': 2, 'two': 2, 'par': 2,
            'tres': 3, 'three': 3,
            'cuatro': 4, 'four': 4, 'tengo cuatro equipos': 4,
            'cinco': 5, 'five': 5,
            'seis': 6, 'six': 6,
            'siete': 7, 'seven': 7,
            'ocho': 8, 'eight': 8,
            'nueve': 9, 'nine': 9,
            'diez': 10, 'ten': 10
        }
        
        # Buscar palabras numéricas exactas
        for word, value in num_words.items():
            if count_str == word:
                return value
        
        # Buscar números en el texto
        import re
        numbers = re.findall(r'\d+', count_str)
        if numbers:
            # Sumar todos los números encontrados (útil para casos como "2 de fábrica y 1 que armé yo")
            return sum(int(num) for num in numbers)
            
        # Buscar palabras numéricas en el texto
        for word, value in num_words.items():
            if word in count_str:
                return value
                
        # Casos específicos
        if '2 en funcionamiento' in count_str:
            return 2
            
        if '2 de fábrica y una que armé yo' in count_str:
            return 3
            
        # No se pudo parsear, loguear y retornar valor por defecto
        print(f"[WARNING] No se pudo parsear cantidad de equipos: {count_str}")
        return 1  # Valor por defecto