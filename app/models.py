from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProveedorCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    telefono: str = Field(..., max_length=15)
    direccion: str = Field(..., max_length=255)

class Proveedor(ProveedorCreate):
    id_proveedor: int


class ProductoCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: str
    precio: float = Field(..., decimal_places=2)
    stock: int
    id_categoria: int

class Producto(ProductoCreate):
    id_producto: int


class CategoriaCreate(BaseModel):
    nombre: str = Field(..., max_length=100)

class Categoria(CategoriaCreate):
    id_categoria: int


class ClienteCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    correo: str = Field(..., max_length=100)
    telefono: str = Field(..., max_length=15)

class Cliente(ClienteCreate):
    id_cliente: int


class SalidaInventarioCreate(BaseModel):
    fecha: datetime
    id_producto: int
    cantidad: int
    precio_unitario: float = Field(..., decimal_places=2)
    id_cliente: int

class SalidaInventario(SalidaInventarioCreate):
    id_salida: int

class EntradaInventarioCreate(BaseModel):
    fecha: datetime
    id_producto: int
    cantidad: int
    precio_unitario: float = Field(..., decimal_places=2)
    id_proveedor: int

class EntradaInventario(EntradaInventarioCreate):
    id_entrada: int


class ProductoResponse(Producto):
    categoria_nombre: str
    stock_disponible: int

class InventarioResponse(BaseModel):
    id_producto: int
    nombre_producto: str
    stock_actual: int
    valor_total: float
    ultima_entrada: Optional[datetime]
    ultima_salida: Optional[datetime]

class MovimientoInventario(BaseModel):
    fecha: datetime
    tipo_movimiento: str  # "entrada" o "salida"
    cantidad: int
    precio_unitario: float
    nombre_producto: str
    nombre_proveedor: Optional[str]
    nombre_cliente: Optional[str]

class ResumenProveedor(BaseModel):
    id_proveedor: int
    nombre: str
    total_productos_suministrados: int
    total_compras: float
    ultima_entrega: Optional[datetime]

class VentasPorPeriodo(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    total_ventas: float
    productos_vendidos: int
    clientes_atendidos: int

class ProductoMasVendido(BaseModel):
    id_producto: int
    nombre: str
    cantidad_vendida: int
    ingresos_generados: float
    categoria: str

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
