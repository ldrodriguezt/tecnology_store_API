from fastapi import FastAPI
from app.routes import router
from app.models import (
    # Modelos base
    ProveedorCreate, Proveedor,
    ProductoCreate, Producto,
    CategoriaCreate, Categoria,
    ClienteCreate, Cliente,
    EntradaInventarioCreate, EntradaInventario,
    SalidaInventarioCreate, SalidaInventario,
    
    # Modelos de respuesta
    ProductoResponse,
    InventarioResponse,
    MovimientoInventario,
    ResumenProveedor,
    VentasPorPeriodo,
    ProductoMasVendido,
    
    # Modelos de filtros
    FiltroInventario,
    FiltroVentas
)

app = FastAPI(
    title="Tecnology Store API",
    description="API para gestión de inventario de tienda tecnológica",
    version="1.0.0"
)

# Configuración de CORS si es necesario
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configura según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir el router
app.include_router(router, prefix="/api/v1")

# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Tecnology Store",
        "documentacion": "/docs"
    }

