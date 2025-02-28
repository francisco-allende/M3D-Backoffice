
class Estado:
    @staticmethod
    def get_all_estados():
        return [
            ('libre', 'Libre'),
            ('asignado', 'Asignado'),
            ('validacion', 'Foto de validación'),
            ('entregado_nodo', 'Bloque entregado en el nodo'),
            ('recibido_m3d', 'Bloque recibido en M3D'),
            ('diploma_entregado', 'Bloque recibido en M3D y diploma entregado'),
        ]
