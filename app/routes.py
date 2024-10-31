from fastapi import APIRouter, HTTPException
from app.models import *
from app.database import get_db_connection
from typing import List
from datetime import datetime

router = APIRouter()

# Rutas de Productos
@router.post("/productos/", response_model=Producto)
async def crear_producto(producto: ProductoCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar si existe la categoría
        cursor.execute("SELECT id_categoria FROM categorias WHERE id_categoria = %s", 
                      (producto.id_categoria,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        query = """
        INSERT INTO productos (nombre, descripcion, precio, stock, id_categoria)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (producto.nombre, producto.descripcion, producto.precio, 
                 producto.stock, producto.id_categoria)
        
        cursor.execute(query, values)
        conn.commit()
        
        producto_id = cursor.lastrowid
        return Producto(id_producto=producto_id, **producto.dict())
    finally:
        cursor.close()
        conn.close()

@router.get("/productos/", response_model=List[ProductoResponse])
async def listar_productos(stock_minimo: int = None, categoria_id: int = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        SELECT p.*, c.nombre as categoria_nombre, p.stock as stock_disponible
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        WHERE 1=1
        """
        params = []
        
        if stock_minimo is not None:
            query += " AND p.stock >= %s"
            params.append(stock_minimo)
        
        if categoria_id is not None:
            query += " AND p.id_categoria = %s"
            params.append(categoria_id)
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        return [ProductoResponse(**producto) for producto in productos]
    finally:
        cursor.close()
        conn.close()

# Rutas de Inventario
@router.post("/inventario/entradas/", response_model=EntradaInventario)
async def registrar_entrada(entrada: EntradaInventarioCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar si existe el producto
        cursor.execute("SELECT stock FROM productos WHERE id_producto = %s", 
                      (entrada.id_producto,))
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Registrar entrada
        query_entrada = """
        INSERT INTO entradas_inventario 
        (fecha, id_producto, cantidad, precio_unitario, id_proveedor)
        VALUES (%s, %s, %s, %s, %s)
        """
        values_entrada = (entrada.fecha, entrada.id_producto, entrada.cantidad,
                         entrada.precio_unitario, entrada.id_proveedor)
        
        cursor.execute(query_entrada, values_entrada)
        
        # Actualizar stock
        query_update = """
        UPDATE productos 
        SET stock = stock + %s 
        WHERE id_producto = %s
        """
        cursor.execute(query_update, (entrada.cantidad, entrada.id_producto))
        
        conn.commit()
        return EntradaInventario(id_entrada=cursor.lastrowid, **entrada.dict())
    finally:
        cursor.close()
        conn.close()

@router.post("/inventario/salidas/", response_model=SalidaInventario)
async def registrar_salida(salida: SalidaInventarioCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar stock disponible
        cursor.execute("SELECT stock FROM productos WHERE id_producto = %s", 
                      (salida.id_producto,))
        producto = cursor.fetchone()
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if producto['stock'] < salida.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        
        # Registrar salida
        query_salida = """
        INSERT INTO salidas_inventario 
        (fecha, id_producto, cantidad, precio_unitario, id_cliente)
        VALUES (%s, %s, %s, %s, %s)
        """
        values_salida = (salida.fecha, salida.id_producto, salida.cantidad,
                        salida.precio_unitario, salida.id_cliente)
        
        cursor.execute(query_salida, values_salida)
        
        # Actualizar stock
        query_update = """
        UPDATE productos 
        SET stock = stock - %s 
        WHERE id_producto = %s
        """
        cursor.execute(query_update, (salida.cantidad, salida.id_producto))
        
        conn.commit()
        return SalidaInventario(id_salida=cursor.lastrowid, **salida.dict())
    finally:
        cursor.close()
        conn.close()

# Ruta para obtener movimientos de inventario
@router.get("/inventario/movimientos/", response_model=List[MovimientoInventario])
async def obtener_movimientos(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        SELECT 
            'entrada' as tipo_movimiento,
            e.fecha,
            e.cantidad,
            e.precio_unitario,
            p.nombre as nombre_producto,
            pr.nombre as nombre_proveedor,
            NULL as nombre_cliente
        FROM entradas_inventario e
        JOIN productos p ON e.id_producto = p.id_producto
        JOIN proveedores pr ON e.id_proveedor = pr.id_proveedor
        WHERE 1=1
        
        UNION ALL
        
        SELECT 
            'salida' as tipo_movimiento,
            s.fecha,
            s.cantidad,
            s.precio_unitario,
            p.nombre as nombre_producto,
            NULL as nombre_proveedor,
            c.nombre as nombre_cliente
        FROM salidas_inventario s
        JOIN productos p ON s.id_producto = p.id_producto
        JOIN clientes c ON s.id_cliente = c.id_cliente
        WHERE 1=1
        """
        params = []
        
        if fecha_inicio:
            query += " AND fecha >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND fecha <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY fecha DESC"
        
        cursor.execute(query, params)
        movimientos = cursor.fetchall()
        return [MovimientoInventario(**movimiento) for movimiento in movimientos]
    finally:
        cursor.close()
        conn.close()

# Rutas de Categorías
@router.post("/categorias/", response_model=Categoria)
async def crear_categoria(categoria: CategoriaCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "INSERT INTO categorias (nombre) VALUES (%s)"
        cursor.execute(query, (categoria.nombre,))
        conn.commit()
        
        return Categoria(id_categoria=cursor.lastrowid, **categoria.dict())
    finally:
        cursor.close()
        conn.close()

@router.get("/categorias/", response_model=List[Categoria])
async def listar_categorias():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM categorias")
        categorias = cursor.fetchall()
        return [Categoria(**categoria) for categoria in categorias]
    finally:
        cursor.close()
        conn.close()

# Rutas de Clientes
@router.post("/clientes/", response_model=Cliente)
async def crear_cliente(cliente: ClienteCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO clientes (nombre, correo, telefono)
        VALUES (%s, %s, %s)
        """
        values = (cliente.nombre, cliente.correo, cliente.telefono)
        cursor.execute(query, values)
        conn.commit()
        
        return Cliente(id_cliente=cursor.lastrowid, **cliente.dict())
    finally:
        cursor.close()
        conn.close()

@router.get("/clientes/", response_model=List[Cliente])
async def listar_clientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        return [Cliente(**cliente) for cliente in clientes]
    finally:
        cursor.close()
        conn.close()

# Rutas de Proveedores
@router.post("/proveedores/", response_model=Proveedor)
async def crear_proveedor(proveedor: ProveedorCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO proveedores (nombre, telefono, direccion)
        VALUES (%s, %s, %s)
        """
        values = (proveedor.nombre, proveedor.telefono, proveedor.direccion)
        cursor.execute(query, values)
        conn.commit()
        
        return Proveedor(id_proveedor=cursor.lastrowid, **proveedor.dict())
    finally:
        cursor.close()
        conn.close()

@router.get("/proveedores/", response_model=List[Proveedor])
async def listar_proveedores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM proveedores")
        proveedores = cursor.fetchall()
        return [Proveedor(**proveedor) for proveedor in proveedores]
    finally:
        cursor.close()
        conn.close()

# Rutas de Reportes
@router.get("/reportes/ventas/", response_model=VentasPorPeriodo)
async def obtener_reporte_ventas(
    fecha_inicio: datetime,
    fecha_fin: datetime,
    categoria_id: Optional[int] = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        SELECT 
            COUNT(DISTINCT s.id_cliente) as clientes_atendidos,
            SUM(s.cantidad) as productos_vendidos,
            SUM(s.cantidad * s.precio_unitario) as total_ventas
        FROM salidas_inventario s
        JOIN productos p ON s.id_producto = p.id_producto
        WHERE s.fecha BETWEEN %s AND %s
        """
        params = [fecha_inicio, fecha_fin]
        
        if categoria_id:
            query += " AND p.id_categoria = %s"
            params.append(categoria_id)
            
        cursor.execute(query, params)
        resultado = cursor.fetchone()
        
        return VentasPorPeriodo(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            **resultado
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/reportes/productos-mas-vendidos/", response_model=List[ProductoMasVendido])
async def obtener_productos_mas_vendidos(
    limite: int = 10,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        SELECT 
            p.id_producto,
            p.nombre,
            c.nombre as categoria,
            SUM(s.cantidad) as cantidad_vendida,
            SUM(s.cantidad * s.precio_unitario) as ingresos_generados
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        JOIN salidas_inventario s ON p.id_producto = s.id_producto
        WHERE 1=1
        """
        params = []
        
        if fecha_inicio:
            query += " AND s.fecha >= %s"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND s.fecha <= %s"
            params.append(fecha_fin)
            
        query += """
        GROUP BY p.id_producto, p.nombre, c.nombre
        ORDER BY cantidad_vendida DESC
        LIMIT %s
        """
        params.append(limite)
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        return [ProductoMasVendido(**producto) for producto in productos]
    finally:
        cursor.close()
        conn.close()

@router.get("/proveedores/{proveedor_id}/resumen", response_model=ResumenProveedor)
async def obtener_resumen_proveedor(proveedor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        SELECT 
            p.id_proveedor,
            p.nombre,
            COUNT(e.id_entrada) as total_productos_suministrados,
            SUM(e.cantidad * e.precio_unitario) as total_compras,
            MAX(e.fecha) as ultima_entrega
        FROM proveedores p
        LEFT JOIN entradas_inventario e ON p.id_proveedor = e.id_proveedor
        WHERE p.id_proveedor = %s
        GROUP BY p.id_proveedor, p.nombre
        """
        
        cursor.execute(query, (proveedor_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
            
        return ResumenProveedor(**resultado)
    finally:
        cursor.close()
        conn.close()
