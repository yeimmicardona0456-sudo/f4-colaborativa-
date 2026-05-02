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
    def __init__(self, codigo, nombre, precio_base, capacidad: int = 10):
        super().__init__(codigo, nombre, precio_base)
        self.capacidad = capacidad

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
