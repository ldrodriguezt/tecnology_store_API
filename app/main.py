from fastapi import FastAPI
from app.routes import router
from app.models import (
    
    ProveedorCreate, Proveedor,
    ProductoCreate, Producto,
    CategoriaCreate, Categoria,
    ClienteCreate, Cliente,
    EntradaInventarioCreate, EntradaInventario,
    SalidaInventarioCreate, SalidaInventario,
    
    
    ProductoResponse,
    InventarioResponse,
    MovimientoInventario,
    ResumenProveedor,
    VentasPorPeriodo,
    ProductoMasVendido,
    
    
    FiltroInventario,
    FiltroVentas
)

app = FastAPI(title="Tecnology Store API",)


# Incluir el router
app.include_router(router)

