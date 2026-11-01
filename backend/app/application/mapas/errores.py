"""Errores de integración con los proveedores públicos de mapas."""


class MapasNoDisponible(Exception):
    """El proveedor no respondió o rechazó temporalmente la solicitud."""


class RespuestaMapasInvalida(Exception):
    """El proveedor devolvió una respuesta inesperada."""


class RutaMapasNoEncontrada(Exception):
    """No existe una ruta entre las ubicaciones solicitadas."""
