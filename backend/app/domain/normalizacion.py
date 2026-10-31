from __future__ import annotations

import unicodedata


def normalizar_espacios(texto: str) -> str:
    """Colapsa espacios sobrantes y quita los de los extremos. Para mostrar y guardar."""
    return " ".join(texto.split())


def normalizar_clave_sin_acentos(texto: str) -> str:
    """Clave de comparación: sin acentos, en minúsculas y sin espacios sobrantes."""
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if not unicodedata.combining(caracter)
    )
    return normalizar_espacios(sin_acentos).lower()


def contar_digitos(texto: str) -> int:
    """Cuenta la cantidad de caracteres numéricos presentes en un texto (ej. teléfono)."""
    return sum(caracter.isdigit() for caracter in texto)
