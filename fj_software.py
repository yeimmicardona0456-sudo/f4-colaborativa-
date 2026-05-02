# =============================================================================
# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS (Software FJ)
# Curso: Programación 213023 | Fase 4
# Autor: [Tu yeimmi cardona peña] & [paola reyes roa]
# =============================================================================
# GUÍA DE COLABORACIÓN PARA GITHUB:
# 1. Crear rama principal: main
# 2. Estudiante A: Trabaja en [SECCIÓN 1: EXCEPCIONES Y CLASES BASE] + [SECCIÓN 2: CLIENTE]
# 3. Estudiante B: Trabaja en [SECCIÓN 3: SERVICIOS] + [SECCIÓN 4: RESERVA]
# 4. Ambos: Integran en [SECCIÓN 5: GESTOR Y SIMULACIÓN] + [SECCIÓN 6: EJECUCIÓN]
# 5. Usar commits descriptivos y pull requests para revisión mutua.
# =============================================================================

import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# CONFIGURACIÓN DE LOGS
# [MANEJO AVANZADO: Registro de eventos y errores en archivo externo]
LOG_FILE = "sistema_fj.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

# =============================================================================
# [SECCIÓN 1: EXCEPCIONES PERSONALIZADAS]
# =============================================================================
class ErrorCliente(Exception):
    """Excepción lanzada cuando los datos del cliente son inválidos."""
    pass

class ErrorServicio(Exception):
    """Excepción lanzada cuando los parámetros del servicio son incorrectos."""
    pass

class ErrorReserva(Exception):
    """Excepción lanzada durante la creación o procesamiento de reservas."""
    pass

# =============================================================================
# [SECCIÓN 2: CLASES BASE Y CLIENTE (ABSTRACCIÓN, ENCAPSULAMIENTO)]
# =============================================================================
class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    @abstractmethod
    def obtener_info(self) -> str:
        pass

    @abstractmethod
    def validar_datos(self) -> bool:
        pass

class Cliente(EntidadSistema):
    """
    Clase Cliente con validaciones robustas y encapsulación de datos.
    [PRINCIPIO: ENCAPSULAMIENTO] Se usan propiedades para controlar acceso/modificación.
    """
    def __init__(self, cliente_id: str, nombre: str, email: str, telefono: str):
        self._cliente_id = cliente_id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.validar_datos()
        logging.info(f"Cliente creado exitosamente: {self._cliente_id}")

    @property
    def cliente_id(self) -> str:
        return self._cliente_id

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise ErrorCliente("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, valor):
            raise ErrorCliente(f"Email inválido: {valor}")
        self._email = valor.lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor.isdigit() or len(valor) < 7:
            raise ErrorCliente("Teléfono debe ser numérico y tener al menos 7 dígitos.")
        self._telefono = valor

    def obtener_info(self) -> str:
        return f"Cliente[ID:{self._cliente_id}, {self._nombre}, {self._email}]"

    def validar_datos(self) -> bool:
        # Validación explícita usando setters
        return True

# =============================================================================
# [SECCIÓN 3: SERVICIOS (HERENCIA, POLIMORFISMO, MÉTODOS SOBRECARGADOS)]
# =============================================================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta para servicios. Define la interfaz común."""
    def __init__(self, codigo: str, nombre: str, precio_base: float):
        self._codigo = codigo
        self.nombre = nombre
        self.precio_base = precio_base
        self.validar_datos()

    @property
    def codigo(self): return self._codigo
    @property
    def precio_base(self): return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float):
        if valor <= 0:
            raise ErrorServicio("El precio base debe ser mayor a 0.")
        self._precio_base = valor

    # [PRINCIPIO: POLIMORFISMO] Cada clase hija implementa su propia lógica
    @abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        pass

    @abstractmethod
    def describir(self) -> str:
        pass

    def obtener_info(self) -> str:
        return f"Servicio[{self.nombre} | Base: ${self.precio_base:.2f}]"

    def validar_datos(self) -> bool:
        return True

# [MÉTODOS SOBRECARGADOS SIMULADOS] Python no soporta sobrecarga nativa,
# pero se logra mediante parámetros opcionales, *args/**kwargs y validación interna.
class ReservaSala(Servicio):
    def _init_(self, codigo, nombre, precio_base, capacidad: int = 10):
        self.capacidad = capacidad
        super()._init_(codigo, nombre, precio_base)
    def calcular_costo(self, duracion_horas: float, impuesto: float = 0.0, descuento: float = 0.0, **kwargs) -> float:
        """Sobrecarga simulada: acepta impuestos, descuentos y kwargs adicionales."""
        try:
            if duracion_horas <= 0:
                raise ValueError("Duración debe ser positiva.")
            costo = self.precio_base * duracion_horas
            costo += costo * (impuesto / 100)
            costo -= costo * (descuento / 100)
            return max(0.0, costo)
        except Exception as e:
            raise ErrorServicio(f"Error calculando costo Sala: {e}") from e

    def describir(self) -> str:
        return f"Sala de reuniones. Capacidad: {self.capacidad} personas."

    def validar_datos(self) -> bool:
        if self.capacidad < 2:
            raise ErrorServicio("Capacidad mínima de sala: 2 personas.")
        return True

class AlquilerEquipo(Servicio):
    def calcular_costo(self, duracion_horas: float, seguro: bool = False, **kwargs) -> float:
        try:
            costo = self.precio_base * duracion_horas
            if seguro:
                costo += 50.0  # Tarifa fija de seguro
            return costo
        except Exception as e:
            raise ErrorServicio(f"Error calculando costo Equipo: {e}") from e

    def describir(self) -> str:
        return "Alquiler de equipos tecnológicos (laptops, proyectores, etc.)."

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, duracion_horas: float, nivel_experiencia: str = "junior", **kwargs) -> float:
        """Sobrecarga con parámetro opcional 'nivel_experiencia'."""
        try:
            multiplicador = {"junior": 1.0, "mid": 1.5, "senior": 2.0}.get(nivel_experiencia.lower(), 1.0)
            return self.precio_base * duracion_horas * multiplicador
        except Exception as e:
            raise ErrorServicio(f"Error calculando costo Asesoría: {e}") from e

    def describir(self) -> str:
        return "Consultoría especializada en desarrollo, arquitectura o seguridad."
# =============================================================================
# [SECCIÓN 4: RESERVA (ESTADO, FLUJO DE TRABAJO, EXCEPCIONES)]
# =============================================================================
class Reserva:
    """Integra cliente, servicio, duración y estado. Maneja confirmación/cancelación."""
    def _init_(self, cliente: Cliente, servicio: Servicio, duracion_horas: float):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = duracion_horas
        self.estado = "PENDIENTE"
        self.fecha_creacion = datetime.now()
        self.codigo_reserva = f"RSV-{cliente.cliente_id}-{servicio.codigo}"

    def confirmar(self) -> None:
        if self.estado != "PENDIENTE":
            raise ErrorReserva(f"No se puede confirmar una reserva con estado '{self.estado}'.")
        self.estado = "CONFIRMADA"
        logging.info(f"Reserva {self.codigo_reserva} confirmada exitosamente.")

    def cancelar(self) -> None:
        if self.estado == "CANCELADA":
            raise ErrorReserva("La reserva ya está cancelada.")
        self.estado = "CANCELADA"
        logging.info(f"Reserva {self.codigo_reserva} cancelada.")

    def procesar(self, aplicar_impuesto: float = 0.0, aplicar_descuento: float = 0.0, **kwargs) -> float:
        """Procesa la reserva, calcula costos y maneja excepciones encadenadas."""
        try:
            self.confirmar()
        except ErrorReserva as e:
            logging.error(f"Falló confirmación de {self.codigo_reserva}: {e}")
            raise ErrorReserva("No se puede procesar sin confirmación previa.") from e

        try:
            # [POLIMORFISMO] Llama a calcular_costo del servicio correspondiente
            costo_final = self.servicio.calcular_costo(
                self.duracion_horas,
                impuesto=aplicar_impuesto,
                descuento=aplicar_descuento,
                **kwargs
            )
            return costo_final
        except ErrorServicio as e:
            logging.error(f"Error en cálculo de costo para {self.codigo_reserva}: {e}")
            self.cancelar()  # Rollback automático
            raise ErrorReserva("Proceso fallido. Reserva cancelada por error de cálculo.") from e
        except Exception as e:
            self.cancelar()
            raise ErrorReserva(f"Error inesperado durante procesamiento: {e}") from e
        finally:
            logging.debug(f"Estado final de {self.codigo_reserva}: {self.estado}")

# =============================================================================
# [SECCIÓN 5: SISTEMA GESTOR (LISTAS, CONTROL, PATRONES TRY/EXCEPT)]
# =============================================================================
class SistemaGestor:
    """Gestiona listas internas, operaciones y demuestra manejo robusto de errores."""
    def _init_(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, cid, nombre, email, telefono) -> Cliente:
        try:
            nuevo = Cliente(cid, nombre, email, telefono)
            self.clientes.append(nuevo)
            return nuevo
        except ErrorCliente as e:
            logging.error(f"Registro de cliente fallido [{cid}]: {e}")
            raise
        except Exception as e:
            logging.error(f"Error inesperado al registrar cliente: {e}")
            raise ErrorSistema("Fallo crítico en registro de cliente.") from e
        finally:
            logging.debug(f"Lista de clientes actualizada: {len(self.clientes)} registros.")

    def agregar_servicio(self, servicio: Servicio) -> None:
        try:
            if any(s.codigo == servicio.codigo for s in self.servicios):
                raise ErrorServicio(f"Servicio con código {servicio.codigo} ya existe.")
            self.servicios.append(servicio)
        except ErrorServicio as e:
            logging.error(f"Error agregando servicio: {e}")
            raise
        else:
            logging.info(f"Servicio '{servicio.nombre}' agregado correctamente.")

    def crear_reserva(self, cliente_id: str, servicio_codigo: str, duracion: float, **kwargs) -> Reserva:
        try:
            cliente = next((c for c in self.clientes if c.cliente_id == cliente_id), None)
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado.")
            
            servicio = next((s for s in self.servicios if s.codigo == servicio_codigo), None)
            if not servicio:
                raise ValueError(f"Servicio {servicio_codigo} no disponible.")
            
            reserva = Reserva(cliente, servicio, duracion)
            self.reservas.append(reserva)
            return reserva
        except (ValueError, ErrorServicio) as e:
            logging.error(f"Fallo al crear reserva: {e}")
            raise ErrorReserva(f"No se pudo crear reserva: {e}") from e
        finally:
            logging.debug(f"Total reservas en sistema: {len(self.reservas)}")

    def ejecutar_simulaciones(self) -> None:
        """Simula 10 operaciones completas (válidas e inválidas) para demostrar robustez."""
        logging.info("=== INICIANDO SIMULACIÓN DE 10 OPERACIONES ===")
        operaciones_exitosas = 0
        operaciones_fallidas = 0

        escenarios = [
            # 1. Cliente válido
            lambda: self.registrar_cliente("C001", "Ana Torres", "ana@email.com", "3105551234"),
            # 2. Cliente inválido (email malo)
            lambda: self.registrar_cliente("C002", "Luis", "luis@correo", "3105551234"),
            # 3. Agregar servicios válidos
            lambda: [self.agregar_servicio(ServicioSala("SRV01", "Sala Ejecutiva", 150.0, 15)),
                     self.agregar_servicio(ReservaSala("SRV02", "Sala Capacitación", 100.0, 30)),
                     self.agregar_servicio(AlquilerEquipo("SRV03", "Laptop Pro", 80.0)),
                     self.agregar_servicio(AsesoriaEspecializada("SRV04", "Consultoría Cloud", 200.0))],
            # 4. Reserva exitosa (Sala)
            lambda: self.crear_reserva("C001", "SRV01", 4.0).procesar(aplicar_impuesto=10.0),
            # 5. Reserva fallida (Servicio no existe)
            lambda: self.crear_reserva("C001", "SRV99", 2.0).procesar(),
            # 6. Reserva exitosa (Equipo con seguro)
            lambda: self.crear_reserva("C001", "SRV03", 8.0).procesar(seguro=True),
            # 7. Reserva fallida (Duración negativa)
            lambda: self.crear_reserva("C001", "SRV02", -2.0).procesar(),
            # 8. Cliente inválido (teléfono corto)
            lambda: self.registrar_cliente("C003", "Pedro", "pedro@mail.com", "123"),
            # 9. Reserva exitosa (Asesoría Senior con descuento)
            lambda: self.crear_reserva("C001", "SRV04", 3.0).procesar(nivel_experiencia="senior", aplicar_descuento=15.0),
            # 10. Intento de procesar reserva ya confirmada/cancelada
            lambda: self._prueba_doble_proceso()
        ]

        for i, operacion in enumerate(escenarios, 1):
            logging.info(f"--- Operación {i}/10 ---")
            try:
                resultado = operacion()
                if isinstance(resultado, (list, tuple)):
                    pass  # Operaciones múltiples
                elif isinstance(resultado, (int, float)):
                    logging.info(f"💰 Costo procesado: ${resultado:.2f}")
                elif isinstance(resultado, Reserva):
                    logging.info(f"✅ Reserva creada y lista: {resultado.codigo_reserva}")
                operaciones_exitosas += 1
            except Exception as e:
                logging.error(f"❌ Operación {i} falló: {e}")
                operaciones_fallidas += 1
            finally:
                logging.debug(f"Estado del sistema tras op {i}: Clientes:{len(self.clientes)} | Servicios:{len(self.servicios)} | Reservas:{len(self.reservas)}\n")

        logging.info("=== SIMULACIÓN FINALIZADA ===")
        logging.info(f"Resultados: {operaciones_exitosas} exitosas | {operaciones_fallidas} fallidas (manejadas correctamente)")

    def _prueba_doble_proceso(self):
        """Auxiliar para demostrar manejo de estado y excepciones encadenadas."""
        res = self.crear_reserva("C001", "SRV01", 2.0)
        res.procesar(aplicar_descuento=5.0)
        try:
            res.procesar()  # Debe fallar porque ya está CONFIRMADA
        except ErrorReserva as e:
            logging.warning("Prueba de doble proceso capturada correctamente.")
            raise ErrorReserva("No se permite reprocesar reservas finalizadas.") from e

# =============================================================================
# [SECCIÓN 6: EJECUCIÓN PRINCIPAL]
# =============================================================================
if _name_ == "_main_":
    print("🚀 Iniciando Sistema Integral de Gestión - Software FJ")
    print("📄 Los logs se guardarán en:", os.path.abspath(LOG_FILE))
    
    sistema = SistemaGestor()
    
    try:
        sistema.ejecutar_simulaciones()
    except Exception as e:
        logging.critical(f"⚠️ Error crítico en ejecución principal: {e}")
        print("El sistema encontró un error crítico. Revise el archivo de logs.")
    finally:
        print("✅ Sistema finalizado correctamente. Verifique sistema_fj.log para detalles.")