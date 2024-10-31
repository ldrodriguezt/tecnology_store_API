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

app = FastAPI(
    title="Tecnology Store API",
    description="API para gestión de inventario de tienda tecnológica",
    version="1.0.0"
)


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configura según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Tecnology Store",
        "documentacion": "/docs"
    }

