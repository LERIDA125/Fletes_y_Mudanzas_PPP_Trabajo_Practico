class HistorialClienteRepoVacio:
    """Implementación temporal del puerto ConsultaHistorialCliente.

    TODO(AGENTS): reemplazar por la consulta real sobre servicios, cotizaciones y rendiciones
    cuando exista la historia de Servicios. Mientras tanto devuelve False, así que ninguna baja
    queda bloqueada por historial.

    La regla de negocio (FR-015) ya vive y está testeada en GestorClientes.eliminar: este stub
    solo alcanza el dato, no la decisión. Al llegar la historia de Servicios se cambia únicamente
    la inyección en app/main.py.
    """

    def tiene_historial(self, cliente_id: int) -> bool:
        return False
