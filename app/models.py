from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

# Modelos base para Proveedor
class ProveedorCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    telefono: str = Field(..., max_length=15)
    direccion: str = Field(..., max_length=255)

class Proveedor(ProveedorCreate):
    id_proveedor: int

# Modelos base para Producto
class ProductoCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: str
    precio: Decimal = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    id_categoria: int

class Producto(ProductoCreate):
    id_producto: int

# Modelos base para Categoria
class CategoriaCreate(BaseModel):
    nombre: str = Field(..., max_length=100)

class Categoria(CategoriaCreate):
    id_categoria: int

# Modelos base para Cliente
class ClienteCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    correo: str = Field(..., max_length=100)
    telefono: str = Field(..., max_length=15)

class Cliente(ClienteCreate):
    id_cliente: int

# Modelos base para movimientos de inventario
class SalidaInventarioCreate(BaseModel):
    fecha: datetime
    id_producto: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)
    id_cliente: int

class SalidaInventario(SalidaInventarioCreate):
    id_salida: int

class EntradaInventarioCreate(BaseModel):
    fecha: datetime
    id_producto: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)
    id_proveedor: int

class EntradaInventario(EntradaInventarioCreate):
    id_entrada: int

# Modelos para consultas y respuestas específicas
class ProductoResponse(Producto):
    categoria_nombre: str
    stock_disponible: int

class InventarioResponse(BaseModel):
    id_producto: int
    nombre_producto: str
    stock_actual: int
    valor_total: Decimal
    ultima_entrada: Optional[datetime]
    ultima_salida: Optional[datetime]

class MovimientoInventario(BaseModel):
    fecha: datetime
    tipo_movimiento: str  # "entrada" o "salida"
    cantidad: int
    precio_unitario: Decimal
    nombre_producto: str
    nombre_proveedor: Optional[str]
    nombre_cliente: Optional[str]

class ResumenProveedor(BaseModel):
    id_proveedor: int
    nombre: str
    total_productos_suministrados: int
    total_compras: Decimal
    ultima_entrega: Optional[datetime]

class VentasPorPeriodo(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    total_ventas: Decimal
    productos_vendidos: int
    clientes_atendidos: int

class ProductoMasVendido(BaseModel):
    id_producto: int
    nombre: str
    cantidad_vendida: int
    ingresos_generados: Decimal
    categoria: str

    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        }
    )

# Modelos para filtros y búsquedas
class FiltroInventario(BaseModel):
    categoria_id: Optional[int]
    stock_minimo: Optional[int]
    precio_minimo: Optional[float]
    precio_maximo: Optional[float]

class FiltroVentas(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    categoria_id: Optional[int]
    cliente_id: Optional[int]
