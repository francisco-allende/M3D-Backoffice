from django.db import models

class TipoBloque:
    @staticmethod
    def get_all_tipos():
        return [
            ("Histórico", "Histórico"),
            ("Geográfico", "Geográfico"),
            ("Militar", "Militar"),
            ("Caídos en batalla", "Caídos en batalla"),
            ("Cultural", "Cultural"),
            ("Proyecto Malvinas 3D", "Proyecto Malvinas 3D"),
            ("Post-guerra y veteranos", "Post-guerra y veteranos"),
            ("Tecnológico", "Tecnológico"),
            ("Diplomático y político", "Diplomático y político"),
            ("Civiles y personal no militar", "Civiles y personal no militar"),
        ]