export interface paths {
    "/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Verificar que la API está viva */
        get: operations["health_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/clientes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar clientes
         * @description Devuelve una página de clientes dados de alta, con orden estable y la cantidad total de los que cumplen el filtro. Un filtro sin coincidencias devuelve la lista vacía con el total en cero, no un error.
         */
        get: operations["listar_clientes_api_clientes_get"];
        put?: never;
        /**
         * Registrar un cliente
         * @description Da de alta un cliente con razón social, teléfono, dirección habitual e indicador de cuenta corriente. La razón social no puede repetirse, aunque cambie de mayúsculas, minúsculas o acentos. El identificador y las fechas los asigna el sistema.
         */
        post: operations["registrar_cliente_api_clientes_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/clientes/{cliente_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Ver el detalle de un cliente
         * @description Devuelve razón social, teléfono, dirección habitual, indicador de cuenta corriente y las fechas de alta y última modificación. Un cliente dado de baja se trata como inexistente.
         */
        get: operations["obtener_cliente_api_clientes__cliente_id__get"];
        /**
         * Modificar un cliente
         * @description Corrige los cuatro datos de un cliente existente. El identificador y la fecha de creación no se pueden cambiar, y la razón social no puede quedar igual a la de otro cliente. Guardar los mismos datos también refresca la fecha de última modificación.
         */
        put: operations["actualizar_cliente_api_clientes__cliente_id__put"];
        post?: never;
        /**
         * Dar de baja un cliente
         * @description Elimina un cliente que no tenga servicios registrados. La baja es lógica —el registro queda desactivado pero conserva su identidad— por lo que repetir la baja no da error y la razón social no vuelve a estar disponible para otro cliente. Un cliente con servicios recién podrá eliminarse cuando se resuelva su historial.
         */
        delete: operations["eliminar_cliente_api_clientes__cliente_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/servicios/disponibilidad": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Consultar choferes y vehículos disponibles
         * @description Devuelve los choferes activos y los vehículos activos del tipo indicado que no están ocupados por otro servicio no cancelado en la ventana solicitada. Si el servicio nuevo no informa hora de inicio, o un servicio existente del día tampoco la informa, el recurso se considera ocupado durante todo el día (supuesto conservador hasta que el cliente confirme la regla de agenda).
         */
        get: operations["consultar_disponibilidad_api_servicios_disponibilidad_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/servicios/cotizar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Cotizar un viaje
         * @description Calcula el precio en ARS con las tarifas activas del tipo de vehículo. La distancia recibida es de ida; el servidor la duplica y aplica una franquicia de 10 km.
         */
        post: operations["cotizar_servicio_api_servicios_cotizar_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/servicios": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar servicios
         * @description Devuelve servicios paginados con cliente, tipo, estado y nombres legibles de las asignaciones opcionales.
         */
        get: operations["listar_servicios_api_servicios_get"];
        put?: never;
        /**
         * Registrar un servicio
         * @description Registra un servicio en estado pendiente. El servidor obtiene las tarifas vigentes, recalcula el precio y guarda el detalle tarifario; el cliente no puede enviar importes.
         */
        post: operations["crear_servicio_api_servicios_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/servicios/{id_servicio}/cancelar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * Cancelar un servicio
         * @description Cancela un servicio en estado pendiente, confirmado o en curso. Exige un motivo y registra la hora de finalización con la hora del servidor; no acepta hora ni estado.
         */
        patch: operations["cancelar_servicio_api_servicios__id_servicio__cancelar_patch"];
        trace?: never;
    };
    "/api/choferes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar choferes activos
         * @description Devuelve una página de choferes activos, con orden estable y la cantidad total de los que cumplen el filtro. Los choferes dados de baja no aparecen.
         */
        get: operations["listar_choferes_api_choferes_get"];
        put?: never;
        /**
         * Registrar un chofer
         * @description Da de alta un chofer con nombre completo y teléfono. El identificador, las fechas, `activo` y `saldo_a_favor` los asigna el sistema.
         */
        post: operations["registrar_chofer_api_choferes_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/choferes/{chofer_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Ver el detalle de un chofer
         * @description Devuelve nombre completo, teléfono, estado, saldo a favor y las fechas de alta y última modificación. Un chofer dado de baja se trata como inexistente.
         */
        get: operations["obtener_chofer_api_choferes__chofer_id__get"];
        /**
         * Modificar un chofer
         * @description Corrige el nombre completo y el teléfono de un chofer existente. El identificador, la fecha de creación y el saldo no se pueden cambiar.
         */
        put: operations["actualizar_chofer_api_choferes__chofer_id__put"];
        post?: never;
        /**
         * Dar de baja un chofer
         * @description Da de baja un chofer. La baja es lógica: la fila queda con `activo=false`.
         */
        delete: operations["eliminar_chofer_api_choferes__chofer_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tipos-vehiculo": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar tipos de vehículo
         * @description Devuelve una página de tipos de vehículo dados de alta, con orden estable y la cantidad total de los que cumplen el filtro.
         */
        get: operations["listar_tipos_vehiculo_api_tipos_vehiculo_get"];
        put?: never;
        /**
         * Registrar un tipo de vehículo
         * @description Da de alta un tipo de vehículo con descripción, capacidad de carga y tarifas base. La descripción no puede repetirse. El identificador y las fechas los asigna el sistema.
         */
        post: operations["registrar_tipo_vehiculo_api_tipos_vehiculo_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tipos-vehiculo/{tipo_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Ver el detalle de un tipo de vehículo
         * @description Devuelve descripción, capacidad de carga, tarifas y las fechas de alta y última modificación. Un tipo de vehículo dado de baja se trata como inexistente.
         */
        get: operations["obtener_tipo_vehiculo_api_tipos_vehiculo__tipo_id__get"];
        /**
         * Modificar un tipo de vehículo
         * @description Corrige los datos de un tipo de vehículo existente. El identificador y la fecha de creación no se pueden cambiar, y la descripción no puede quedar igual a la de otro tipo de vehículo.
         */
        put: operations["actualizar_tipo_vehiculo_api_tipos_vehiculo__tipo_id__put"];
        post?: never;
        /**
         * Dar de baja un tipo de vehículo
         * @description Elimina un tipo de vehículo que no tenga vehículos asociados. La baja es lógica.
         */
        delete: operations["eliminar_tipo_vehiculo_api_tipos_vehiculo__tipo_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/vehiculos": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar vehículos
         * @description Devuelve una página de vehículos dados de alta, con orden estable y la cantidad total de los que cumplen el filtro.
         */
        get: operations["listar_vehiculos_api_vehiculos_get"];
        put?: never;
        /**
         * Registrar un vehículo
         * @description Da de alta un vehículo con patente, tipo de vehículo y opcionalmente un chofer habitual. La patente no puede repetirse. El identificador y las fechas los asigna el sistema.
         */
        post: operations["registrar_vehiculo_api_vehiculos_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/vehiculos/{vehiculo_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Ver el detalle de un vehículo
         * @description Devuelve patente, tipo de vehículo, chofer habitual y las fechas de alta y última modificación. Un vehículo dado de baja se trata como inexistente.
         */
        get: operations["obtener_vehiculo_api_vehiculos__vehiculo_id__get"];
        /**
         * Modificar un vehículo
         * @description Corrige los datos de un vehículo existente. El identificador y la fecha de creación no se pueden cambiar, y la patente no puede quedar igual a la de otro vehículo.
         */
        put: operations["actualizar_vehiculo_api_vehiculos__vehiculo_id__put"];
        post?: never;
        /**
         * Dar de baja un vehículo
         * @description Elimina un vehículo que no tenga servicios asociados. La baja es lógica.
         */
        delete: operations["eliminar_vehiculo_api_vehiculos__vehiculo_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /**
         * ChoferCreate
         * @description Los datos requeridos del alta (FR-001, FR-002).
         *
         *     `activo` y `saldo_a_favor` no se aceptan del usuario (FR-006): el dominio los fija por
         *     defecto y `extra="forbid"` rechaza el intento con `422`.
         */
        ChoferCreate: {
            /**
             * Nombre Completo
             * @description Nombre completo del chofer.
             * @example Juan Pérez
             */
            nombre_completo: string;
            /**
             * Telefono
             * @description Teléfono de contacto. Se aceptan espacios, guiones y el prefijo internacional `+`; solo se exige que tenga entre 7 y 20 dígitos y que el texto no supere los 20 caracteres que admite la columna.
             * @example 351 555 0100
             */
            telefono: string;
        };
        /**
         * ChoferListado
         * @description Página de choferes activos con el total de los que cumplen el filtro (FR-007).
         */
        ChoferListado: {
            /** Items */
            items: components["schemas"]["ChoferRead"][];
            /**
             * Total
             * @description Cantidad total de registros que cumplen el filtro.
             */
            total: number;
            /**
             * Page
             * @description Número de página actual (base 1).
             */
            page: number;
            /**
             * Size
             * @description Cantidad de elementos por página.
             */
            size: number;
        };
        /**
         * ChoferRead
         * @description Chofer tal como lo devuelve el sistema.
         */
        ChoferRead: {
            /**
             * Id
             * @description Identificador del chofer, asignado por el sistema.
             */
            id: number;
            /** Nombre Completo */
            nombre_completo: string;
            /** Telefono */
            telefono: string;
            /**
             * Activo
             * @description False cuando el chofer fue dado de baja (FR-013).
             */
            activo: boolean;
            /**
             * Saldo A Favor
             * @description Saldo económico a favor del chofer.
             */
            saldo_a_favor: number;
            /**
             * Creado En
             * Format: date-time
             * @description Fecha de alta, asignada por el sistema.
             */
            creado_en: string;
            /**
             * Actualizado En
             * Format: date-time
             * @description Fecha de la última modificación (FR-019).
             */
            actualizado_en: string;
        };
        /**
         * ChoferUpdate
         * @description La edición toma los mismos campos obligatorios que el alta (DD-5).
         */
        ChoferUpdate: {
            /**
             * Nombre Completo
             * @description Nombre completo del chofer.
             * @example Juan Pérez
             */
            nombre_completo: string;
            /**
             * Telefono
             * @description Teléfono de contacto. Se aceptan espacios, guiones y el prefijo internacional `+`; solo se exige que tenga entre 7 y 20 dígitos y que el texto no supere los 20 caracteres que admite la columna.
             * @example 351 555 0100
             */
            telefono: string;
        };
        /**
         * ClienteCreate
         * @description Los cuatro datos requeridos del alta (FR-001, FR-002).
         */
        ClienteCreate: {
            /**
             * Razon Social
             * @description Razón social del cliente. Es el dato que lo identifica y no puede repetirse.
             * @example Distribuidora del Sur S.A.
             */
            razon_social: string;
            /**
             * Telefono
             * @description Teléfono de contacto. Se aceptan espacios, guiones y el prefijo internacional `+`; solo se exige que tenga entre 7 y 20 dígitos y que el texto no supere los 20 caracteres que admite la columna.
             * @example 351 555 0100
             */
            telefono: string;
            /**
             * Direccion Habitual
             * @description Domicilio habitual del cliente.
             * @example Av. Colón 1250, Córdoba
             */
            direccion_habitual: string;
            /**
             * Tiene Cuenta Corriente
             * @description Si el cliente maneja cuenta corriente. Es obligatorio, pero si el usuario no lo elige explícitamente se guarda en `false` (FR-002).
             * @default false
             */
            tiene_cuenta_corriente: boolean;
        };
        /**
         * ClienteListado
         * @description Página de clientes con el total de los que cumplen el filtro (FR-007).
         */
        ClienteListado: {
            /** Items */
            items: components["schemas"]["ClienteRead"][];
            /**
             * Total
             * @description Cantidad total de registros que cumplen el filtro.
             */
            total: number;
            /**
             * Page
             * @description Número de página actual (base 1).
             */
            page: number;
            /**
             * Size
             * @description Cantidad de elementos por página.
             */
            size: number;
        };
        /**
         * ClienteRead
         * @description Cliente tal como lo devuelve el sistema, con los datos que calcula él (FR-003, FR-009).
         */
        ClienteRead: {
            /**
             * Id
             * @description Identificador del cliente, asignado por el sistema.
             */
            id: number;
            /** Razon Social */
            razon_social: string;
            /** Telefono */
            telefono: string;
            /** Direccion Habitual */
            direccion_habitual: string;
            /** Tiene Cuenta Corriente */
            tiene_cuenta_corriente: boolean;
            /**
             * Activo
             * @description False cuando el cliente fue dado de baja (FR-014).
             */
            activo: boolean;
            /**
             * Creado En
             * Format: date-time
             * @description Fecha de alta, asignada por el sistema.
             */
            creado_en: string;
            /**
             * Actualizado En
             * Format: date-time
             * @description Fecha de la última modificación (FR-020).
             */
            actualizado_en: string;
        };
        /**
         * ClienteUpdate
         * @description La edición toma los mismos cuatro datos obligatorios que el alta (DD-5).
         *
         *     No es un `PATCH`: se manda el cliente completo. Así el dominio siempre valida un cliente
         *     entero y nunca queda un registro a medio modificar por un campo que se olvidó enviar.
         */
        ClienteUpdate: {
            /**
             * Razon Social
             * @description Razón social del cliente. Es el dato que lo identifica y no puede repetirse.
             * @example Distribuidora del Sur S.A.
             */
            razon_social: string;
            /**
             * Telefono
             * @description Teléfono de contacto. Se aceptan espacios, guiones y el prefijo internacional `+`; solo se exige que tenga entre 7 y 20 dígitos y que el texto no supere los 20 caracteres que admite la columna.
             * @example 351 555 0100
             */
            telefono: string;
            /**
             * Direccion Habitual
             * @description Domicilio habitual del cliente.
             * @example Av. Colón 1250, Córdoba
             */
            direccion_habitual: string;
            /**
             * Tiene Cuenta Corriente
             * @description Si el cliente maneja cuenta corriente. Es obligatorio, pero si el usuario no lo elige explícitamente se guarda en `false` (FR-002).
             * @default false
             */
            tiene_cuenta_corriente: boolean;
        };
        /** CotizacionRead */
        CotizacionRead: {
            /** Id Tipo Vehiculo */
            id_tipo_vehiculo: number;
            /** Descripcion Tipo Vehiculo */
            descripcion_tipo_vehiculo: string;
            /** Horas Estimadas */
            horas_estimadas: string;
            /** Distancia Ida Km */
            distancia_ida_km: string;
            /** Distancia Total Km */
            distancia_total_km: string;
            /** Km Franquicia */
            km_franquicia: string;
            /** Km Excedente */
            km_excedente: string;
            /** Tarifa Hora Base */
            tarifa_hora_base: string;
            /** Tarifa Km Excedente */
            tarifa_km_excedente: string;
            /** Precio Final */
            precio_final: string;
            /**
             * Moneda
             * @default ARS
             * @constant
             */
            moneda: "ARS";
        };
        /** CotizacionRequest */
        CotizacionRequest: {
            /**
             * Id Tipo Vehiculo
             * @description Tipo de vehículo cuya tarifa se utilizará.
             */
            id_tipo_vehiculo: number;
            /**
             * Horas Estimadas
             * @description Duración estimada ingresada por el operador; mínimo 1 hora.
             */
            horas_estimadas: number | string;
            /**
             * Distancia Ida Km
             * @description Kilómetros de ida. El backend los duplica para obtener el recorrido total.
             */
            distancia_ida_km: number | string;
        };
        /**
         * DisponibilidadRead
         * @description Disponibilidad calculada para una ventana de servicio.
         */
        DisponibilidadRead: {
            /** Id Tipo Vehiculo */
            id_tipo_vehiculo: number;
            /**
             * Fecha
             * Format: date
             */
            fecha: string;
            /** Hora Inicio */
            hora_inicio: string | null;
            /** Hora Fin */
            hora_fin: string | null;
            /** Choferes */
            choferes: components["schemas"]["ChoferRead"][];
            /** Vehiculos */
            vehiculos: components["schemas"]["VehiculoListadoRead"][];
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** ServicioCancelar */
        ServicioCancelar: {
            /**
             * Motivo
             * @description Motivo de la cancelación; se recortan los espacios de los extremos.
             * @example El cliente reprogramó el viaje
             */
            motivo: string;
        };
        /** ServicioCreate */
        ServicioCreate: {
            /**
             * Id Tipo Vehiculo
             * @description Tipo de vehículo cuya tarifa se utilizará.
             */
            id_tipo_vehiculo: number;
            /**
             * Horas Estimadas
             * @description Duración estimada ingresada por el operador; mínimo 1 hora.
             */
            horas_estimadas: number | string;
            /**
             * Distancia Ida Km
             * @description Kilómetros de ida. El backend los duplica para obtener el recorrido total.
             */
            distancia_ida_km: number | string;
            /**
             * Id Cliente
             * @description Cliente existente que solicita el servicio. Excluyente con `nuevo_cliente`.
             */
            id_cliente?: number | null;
            /** @description Datos de un cliente nuevo. El backend lo crea y lo vincula al servicio; si ya existe uno activo con la misma razón social, reutiliza ese registro. */
            nuevo_cliente?: components["schemas"]["ClienteCreate"] | null;
            /**
             * Id Chofer
             * @description Chofer asignado, si se conoce.
             */
            id_chofer?: number | null;
            /**
             * Id Vehiculo
             * @description Vehículo asignado; debe pertenecer al tipo seleccionado.
             */
            id_vehiculo?: number | null;
            /**
             * Fecha
             * Format: date
             */
            fecha: string;
            /** Hora Inicio */
            hora_inicio?: string | null;
        };
        /**
         * ServicioListado
         * @description Página de Servicios con relaciones legibles.
         */
        ServicioListado: {
            /** Items */
            items: components["schemas"]["ServicioRead"][];
            /**
             * Total
             * @description Cantidad total de registros que cumplen el filtro.
             */
            total: number;
            /**
             * Page
             * @description Número de página actual (base 1).
             */
            page: number;
            /**
             * Size
             * @description Cantidad de elementos por página.
             */
            size: number;
        };
        /** ServicioRead */
        ServicioRead: {
            /** Id Servicio */
            id_servicio: number;
            /** Id Cliente */
            id_cliente: number;
            /** Razon Social Cliente */
            razon_social_cliente: string;
            /** Id Tipo Vehiculo */
            id_tipo_vehiculo: number;
            /** Descripcion Tipo Vehiculo */
            descripcion_tipo_vehiculo: string;
            /** Id Chofer */
            id_chofer: number | null;
            /** Nombre Chofer */
            nombre_chofer: string | null;
            /** Id Vehiculo */
            id_vehiculo: number | null;
            /** Patente Vehiculo */
            patente_vehiculo: string | null;
            /**
             * Fecha
             * Format: date
             */
            fecha: string;
            /** Hora Inicio */
            hora_inicio: string | null;
            /** Hora Fin */
            hora_fin: string | null;
            /** Horas Estimadas */
            horas_estimadas: string;
            /** Distancia Ida Km */
            distancia_ida_km: string;
            /** Distancia Total Km */
            distancia_total_km: string;
            /** Km Franquicia */
            km_franquicia: string;
            /** Km Excedente */
            km_excedente: string;
            /** Tarifa Hora Aplicada */
            tarifa_hora_aplicada: string;
            /** Tarifa Km Aplicada */
            tarifa_km_aplicada: string;
            /** Precio Total */
            precio_total: string;
            /**
             * Moneda
             * @default ARS
             * @constant
             */
            moneda: "ARS";
            /** Estado */
            estado: string;
            /** Motivo Cancelacion */
            motivo_cancelacion: string | null;
            /**
             * Creado En
             * Format: date-time
             */
            creado_en: string;
            /**
             * Actualizado En
             * Format: date-time
             */
            actualizado_en: string;
        };
        /**
         * TipoVehiculoCreate
         * @description Los datos requeridos del alta de un tipo de vehículo.
         */
        TipoVehiculoCreate: {
            /**
             * Descripcion
             * @description Descripción del tipo de vehículo (ej. Utilitario, Furgón Grande)
             * @example Camioneta 1/2 tonelada
             */
            descripcion: string;
            /**
             * Capacidad Carga Kg
             * @description Capacidad de carga en kilogramos. Debe ser positiva.
             * @example 500.0
             */
            capacidad_carga_kg: number | string;
            /**
             * Tarifa Hora Base
             * @description Tarifa base por hora de uso del vehículo. No puede ser negativa.
             * @example 3000.0
             */
            tarifa_hora_base: number | string;
            /**
             * Tarifa Km Excedente
             * @description Tarifa por kilómetro excedente. No puede ser negativa.
             * @example 150.0
             */
            tarifa_km_excedente: number | string;
        };
        /**
         * TipoVehiculoListado
         * @description Página de tipos de vehículo con el total de los que cumplen el filtro.
         */
        TipoVehiculoListado: {
            /** Items */
            items: components["schemas"]["TipoVehiculoRead"][];
            /**
             * Total
             * @description Cantidad total de registros que cumplen el filtro.
             */
            total: number;
            /**
             * Page
             * @description Número de página actual (base 1).
             */
            page: number;
            /**
             * Size
             * @description Cantidad de elementos por página.
             */
            size: number;
        };
        /**
         * TipoVehiculoRead
         * @description Tipo de vehículo tal como lo devuelve el sistema.
         */
        TipoVehiculoRead: {
            /**
             * Descripcion
             * @description Descripción del tipo de vehículo (ej. Utilitario, Furgón Grande)
             * @example Camioneta 1/2 tonelada
             */
            descripcion: string;
            /**
             * Capacidad Carga Kg
             * @description Capacidad de carga en kilogramos. Debe ser positiva.
             * @example 500.0
             */
            capacidad_carga_kg: string;
            /**
             * Tarifa Hora Base
             * @description Tarifa base por hora de uso del vehículo. No puede ser negativa.
             * @example 3000.0
             */
            tarifa_hora_base: string;
            /**
             * Tarifa Km Excedente
             * @description Tarifa por kilómetro excedente. No puede ser negativa.
             * @example 150.0
             */
            tarifa_km_excedente: string;
            /**
             * Id
             * @description Identificador del tipo de vehículo, asignado por el sistema.
             */
            id: number;
            /**
             * Activo
             * @description False cuando el tipo de vehículo fue dado de baja.
             * @default true
             */
            activo: boolean;
            /**
             * Creado En
             * @description Fecha de alta, asignada por el sistema.
             */
            creado_en?: string | null;
            /**
             * Actualizado En
             * @description Fecha de la última modificación.
             */
            actualizado_en?: string | null;
        };
        /**
         * TipoVehiculoUpdate
         * @description La edición toma los mismos datos obligatorios que el alta (DD-5).
         */
        TipoVehiculoUpdate: {
            /**
             * Descripcion
             * @description Descripción del tipo de vehículo (ej. Utilitario, Furgón Grande)
             * @example Camioneta 1/2 tonelada
             */
            descripcion: string;
            /**
             * Capacidad Carga Kg
             * @description Capacidad de carga en kilogramos. Debe ser positiva.
             * @example 500.0
             */
            capacidad_carga_kg: number | string;
            /**
             * Tarifa Hora Base
             * @description Tarifa base por hora de uso del vehículo. No puede ser negativa.
             * @example 3000.0
             */
            tarifa_hora_base: number | string;
            /**
             * Tarifa Km Excedente
             * @description Tarifa por kilómetro excedente. No puede ser negativa.
             * @example 150.0
             */
            tarifa_km_excedente: number | string;
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
            /** Input */
            input?: unknown;
            /** Context */
            ctx?: Record<string, never>;
        };
        /**
         * VehiculoCreate
         * @description Los datos requeridos del alta de un vehículo.
         */
        VehiculoCreate: {
            /**
             * Patente
             * @description Patente del vehículo. Formato argentino: AAA 123 o AA 123 ABC.
             * @example ABC 123
             */
            patente: string;
            /**
             * Id Tipo Vehiculo
             * @description Identificador del tipo de vehículo.
             */
            id_tipo_vehiculo: number;
            /**
             * Id Chofer Habitual
             * @description Identificador del chofer habitual. Opcional.
             */
            id_chofer_habitual?: number | null;
        };
        /**
         * VehiculoListado
         * @description Página de vehículos con el total de los que cumplen el filtro.
         */
        VehiculoListado: {
            /** Items */
            items: components["schemas"]["VehiculoListadoRead"][];
            /**
             * Total
             * @description Cantidad total de registros que cumplen el filtro.
             */
            total: number;
            /**
             * Page
             * @description Número de página actual (base 1).
             */
            page: number;
            /**
             * Size
             * @description Cantidad de elementos por página.
             */
            size: number;
        };
        /** VehiculoListadoRead */
        VehiculoListadoRead: {
            /**
             * Patente
             * @description Patente del vehículo. Formato argentino: AAA 123 o AA 123 ABC.
             * @example ABC 123
             */
            patente: string;
            /**
             * Id Tipo Vehiculo
             * @description Identificador del tipo de vehículo.
             */
            id_tipo_vehiculo: number;
            /**
             * Id Chofer Habitual
             * @description Identificador del chofer habitual. Opcional.
             */
            id_chofer_habitual?: number | null;
            /**
             * Id
             * @description Identificador del vehículo, asignado por el sistema.
             */
            id: number;
            /**
             * Activo
             * @description False cuando el vehículo fue dado de baja.
             * @default true
             */
            activo: boolean;
            /**
             * Creado En
             * Format: date-time
             */
            creado_en: string;
            /**
             * Actualizado En
             * @description Fecha de la última modificación.
             */
            actualizado_en?: string | null;
            /** Descripcion Tipo Vehiculo */
            descripcion_tipo_vehiculo: string;
            /** Capacidad Carga Kg */
            capacidad_carga_kg: number;
            /** Nombre Chofer Habitual */
            nombre_chofer_habitual: string | null;
        };
        /**
         * VehiculoRead
         * @description Vehículo tal como lo devuelve el sistema.
         */
        VehiculoRead: {
            /**
             * Patente
             * @description Patente del vehículo. Formato argentino: AAA 123 o AA 123 ABC.
             * @example ABC 123
             */
            patente: string;
            /**
             * Id Tipo Vehiculo
             * @description Identificador del tipo de vehículo.
             */
            id_tipo_vehiculo: number;
            /**
             * Id Chofer Habitual
             * @description Identificador del chofer habitual. Opcional.
             */
            id_chofer_habitual?: number | null;
            /**
             * Id
             * @description Identificador del vehículo, asignado por el sistema.
             */
            id: number;
            /**
             * Activo
             * @description False cuando el vehículo fue dado de baja.
             * @default true
             */
            activo: boolean;
            /**
             * Creado En
             * @description Fecha de alta, asignada por el sistema.
             */
            creado_en?: string | null;
            /**
             * Actualizado En
             * @description Fecha de la última modificación.
             */
            actualizado_en?: string | null;
            /**
             * Descripcion Tipo Vehiculo
             * @description Descripción legible del tipo de vehículo asociado.
             */
            descripcion_tipo_vehiculo?: string | null;
            /**
             * Capacidad Carga Kg
             * @description Capacidad de carga en kilogramos del tipo de vehículo asociado.
             */
            capacidad_carga_kg?: number | null;
            /**
             * Nombre Chofer Habitual
             * @description Nombre completo del chofer habitual, si está asignado.
             */
            nombre_chofer_habitual?: string | null;
        };
        /**
         * VehiculoUpdate
         * @description La edición toma los mismos datos obligatorios que el alta (DD-5).
         */
        VehiculoUpdate: {
            /**
             * Patente
             * @description Patente del vehículo. Formato argentino: AAA 123 o AA 123 ABC.
             * @example ABC 123
             */
            patente: string;
            /**
             * Id Tipo Vehiculo
             * @description Identificador del tipo de vehículo.
             */
            id_tipo_vehiculo: number;
            /**
             * Id Chofer Habitual
             * @description Identificador del chofer habitual. Opcional.
             */
            id_chofer_habitual?: number | null;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    health_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
        };
    };
    listar_clientes_api_clientes_get: {
        parameters: {
            query?: {
                /** @description Texto a buscar dentro de la razón social. No distingue mayúsculas. */
                q?: string | null;
                /** @description Número de página, empezando en 1. */
                page?: number;
                /** @description Cantidad de clientes por página. */
                size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClienteListado"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    registrar_cliente_api_clientes_post: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ClienteCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClienteRead"];
                };
            };
            /** @description El rol del usuario no permite dar de alta clientes (FR-018). */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Ya existe un cliente registrado con esa razón social (FR-004). */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los cuatro datos requeridos falta o no cumple el formato (FR-011). */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtener_cliente_api_clientes__cliente_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                /** @description Identificador del cliente. */
                cliente_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClienteRead"];
                };
            };
            /** @description No existe un cliente activo con ese identificador (FR-016). */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    actualizar_cliente_api_clientes__cliente_id__put: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del cliente. */
                cliente_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ClienteUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClienteRead"];
                };
            };
            /** @description El rol del usuario no permite modificar clientes (FR-018). */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un cliente activo con ese identificador (FR-016). */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La razón social nueva ya pertenece a otro cliente (FR-012). */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los cuatro datos requeridos falta o no cumple el formato, y no se guarda ningún cambio parcial (FR-011). */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminar_cliente_api_clientes__cliente_id__delete: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del cliente. */
                cliente_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El rol del usuario no permite dar de baja clientes (FR-018). */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un cliente activo con ese identificador (FR-016). */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El cliente tiene servicios registrados y no se puede dar de baja (FR-015). */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    consultar_disponibilidad_api_servicios_disponibilidad_get: {
        parameters: {
            query: {
                /** @description Fecha del servicio a programar. */
                fecha: string;
                /** @description Tipo de vehículo que se va a asignar. */
                id_tipo_vehiculo: number;
                /** @description Duración estimada del servicio; mínimo 1 hora. */
                horas_estimadas: number | string;
                /** @description Hora de inicio; si falta se bloquea el día completo. */
                hora_inicio?: string | null;
            };
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DisponibilidadRead"];
                };
            };
            /** @description La autenticación no está habilitada para este entorno. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La operación requiere el rol admin. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La fecha, el tipo o las horas son inválidos. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    cotizar_servicio_api_servicios_cotizar_post: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CotizacionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CotizacionRead"];
                };
            };
            /** @description La autenticación no está habilitada para este entorno. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La operación requiere el rol admin. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Los datos son inválidos o el tipo no está activo. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listar_servicios_api_servicios_get: {
        parameters: {
            query?: {
                /** @description Número de página, empezando en 1. */
                page?: number;
                /** @description Cantidad de servicios por página. */
                size?: number;
            };
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ServicioListado"];
                };
            };
            /** @description La autenticación no está habilitada para este entorno. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    crear_servicio_api_servicios_post: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ServicioCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ServicioRead"];
                };
            };
            /** @description La autenticación no está habilitada para este entorno. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La operación requiere el rol admin. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Los datos o las referencias activas del servicio son inválidos. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    cancelar_servicio_api_servicios__id_servicio__cancelar_patch: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del servicio. */
                id_servicio: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ServicioCancelar"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ServicioRead"];
                };
            };
            /** @description La autenticación no está habilitada para este entorno. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La operación requiere el rol admin. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un servicio con ese id. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El servicio está finalizado, cobrado o ya cancelado. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El motivo es obligatorio o supera la longitud permitida. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listar_choferes_api_choferes_get: {
        parameters: {
            query?: {
                /** @description Texto a buscar dentro del nombre. */
                q?: string | null;
                /** @description Número de página, empezando en 1. */
                page?: number;
                /** @description Cantidad de choferes por página. */
                size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChoferListado"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    registrar_chofer_api_choferes_post: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChoferCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChoferRead"];
                };
            };
            /** @description El rol del usuario no permite dar de alta choferes. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los datos requeridos falta o no cumple el formato. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtener_chofer_api_choferes__chofer_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                /** @description Identificador del chofer. */
                chofer_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChoferRead"];
                };
            };
            /** @description No existe un chofer activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    actualizar_chofer_api_choferes__chofer_id__put: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del chofer. */
                chofer_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChoferUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChoferRead"];
                };
            };
            /** @description El rol del usuario no permite modificar choferes. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un chofer activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los datos requeridos falta o no cumple el formato. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminar_chofer_api_choferes__chofer_id__delete: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del chofer. */
                chofer_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El rol del usuario no permite dar de baja choferes. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un chofer activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    listar_tipos_vehiculo_api_tipos_vehiculo_get: {
        parameters: {
            query?: {
                /** @description Texto a buscar dentro de la descripción. No distingue mayúsculas. */
                q?: string | null;
                /** @description Número de página, empezando en 1. */
                page?: number;
                /** @description Cantidad de tipos de vehículo por página. */
                size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TipoVehiculoListado"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    registrar_tipo_vehiculo_api_tipos_vehiculo_post: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TipoVehiculoCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TipoVehiculoRead"];
                };
            };
            /** @description El rol del usuario no permite dar de alta tipos de vehículo. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Ya existe un tipo de vehículo con esa descripción. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los datos requeridos falta o no cumple el formato. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtener_tipo_vehiculo_api_tipos_vehiculo__tipo_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                /** @description Identificador del tipo de vehículo. */
                tipo_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TipoVehiculoRead"];
                };
            };
            /** @description No existe un tipo de vehículo activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    actualizar_tipo_vehiculo_api_tipos_vehiculo__tipo_id__put: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del tipo de vehículo. */
                tipo_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TipoVehiculoUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TipoVehiculoRead"];
                };
            };
            /** @description El rol del usuario no permite modificar tipos de vehículo. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un tipo de vehículo activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La descripción nueva ya pertenece a otro tipo de vehículo. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los datos requeridos falta o no cumple el formato. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminar_tipo_vehiculo_api_tipos_vehiculo__tipo_id__delete: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del tipo de vehículo. */
                tipo_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El rol del usuario no permite dar de baja tipos de vehículo. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un tipo de vehículo activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El tipo de vehículo tiene vehículos asociados. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    listar_vehiculos_api_vehiculos_get: {
        parameters: {
            query?: {
                /** @description Texto a buscar dentro de la patente. */
                q?: string | null;
                /** @description Número de página, empezando en 1. */
                page?: number;
                /** @description Cantidad de vehículos por página. */
                size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VehiculoListado"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    registrar_vehiculo_api_vehiculos_post: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["VehiculoCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VehiculoRead"];
                };
            };
            /** @description El rol del usuario no permite dar de alta vehículos. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Ya existe un vehículo con esa patente. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los datos requeridos falta o no cumple el formato. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtener_vehiculo_api_vehiculos__vehiculo_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                /** @description Identificador del vehículo. */
                vehiculo_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VehiculoRead"];
                };
            };
            /** @description No existe un vehículo activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    actualizar_vehiculo_api_vehiculos__vehiculo_id__put: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del vehículo. */
                vehiculo_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["VehiculoUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VehiculoRead"];
                };
            };
            /** @description El rol del usuario no permite modificar vehículos. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un vehículo activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La patente nueva ya pertenece a otro vehículo. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Alguno de los datos requeridos falta o no cumple el formato. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminar_vehiculo_api_vehiculos__vehiculo_id__delete: {
        parameters: {
            query?: never;
            header?: {
                /** @description Rol de prueba en modo desarrollo local. */
                "X-Rol"?: string | null;
            };
            path: {
                /** @description Identificador del vehículo. */
                vehiculo_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El rol del usuario no permite dar de baja vehículos. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No existe un vehículo activo con ese identificador. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El vehículo tiene servicios asociados. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}

