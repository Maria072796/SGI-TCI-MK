// JavaScript para el módulo de gastos

let productosCarritoGasto = [];
let productosDisponiblesGasto = [];

// Función para formatear moneda colombiana
function formatearMonedaColombiana(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}

// Cargar productos disponibles al iniciar y configurar formulario
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Iniciando gastos.js');
    
    // Cargar productos disponibles
    cargarProductosDisponiblesGasto();
    
    // Configurar event listener del formulario
    const gastoForm = document.getElementById('gastoForm');
    if (gastoForm) {
        console.log('Formulario encontrado, agregando event listener');
        gastoForm.addEventListener('submit', function(e) {
            console.log('=== FORMULARIO SUBMIT INICIADO ===');
            const tipoGasto = document.getElementById('tipo_gasto').value;
            console.log('Tipo de gasto:', tipoGasto);
            
            if (tipoGasto === 'compra_insumos') {
                console.log('Procesando compra de insumos');
                console.log('Productos en carrito:', productosCarritoGasto.length);
                
                if (productosCarritoGasto.length === 0) {
                    e.preventDefault();
                    showNotification('Agrega al menos un producto para registrar la compra de insumos', 'warning');
                    console.log('Formulario PREVENIDO: no hay productos');
                    return;
                }
                
                // Generar descripción automática
                const descripcionInput = document.getElementById('descripcion');
                let productosTexto = productosCarritoGasto.map(p => `${p.cantidad} ${p.nombre}`).join(', ');
                descripcionInput.value = `Compra de insumos: ${productosTexto}`;
                console.log('Descripción generada:', descripcionInput.value);
                
                // Agregar datos del carrito al formulario
                const productosJson = JSON.stringify(productosCarritoGasto);
                console.log('JSON de productos:', productosJson);
                
                const inputProductos = document.createElement('input');
                inputProductos.type = 'hidden';
                inputProductos.name = 'productos_json';
                inputProductos.value = productosJson;
                this.appendChild(inputProductos);
                
                console.log('Formulario listo para enviar, permitiendo submit');
            } else {
                console.log('Procesando gasto normal');
            }
        });
    } else {
        console.error('ERROR: No se encontró el formulario gastoForm');
    }
});

function cargarProductosDisponiblesGasto() {
    fetch('/inventario/api/productos-disponibles')
        .then(response => response.json())
        .then(data => {
            productosDisponiblesGasto = data;
            configurarAutocompletadoGasto();
        })
        .catch(error => console.error('Error al cargar productos:', error));
}

function configurarAutocompletadoGasto() {
    const inputBusqueda = document.getElementById('productoBusqueda');
    if (!inputBusqueda) return;
    
    const datalist = document.getElementById('productosList');
    if (!datalist) return;
    
    // Limpiar opciones existentes
    datalist.innerHTML = '';
    
    // Agregar productos al datalist
    productosDisponiblesGasto.forEach(producto => {
        const option = document.createElement('option');
        option.value = producto.nombre;
        option.dataset.id = producto.id;
        option.dataset.precio_costo = producto.precio_costo;
        option.dataset.precio_venta = producto.precio_venta;
        option.dataset.stock = producto.stock_actual;
        datalist.appendChild(option);
    });
}

function cambiarTipoGasto() {
    const tipoGasto = document.getElementById('tipo_gasto').value;
    const formularioSimple = document.getElementById('formularioSimple');
    const formularioCarrito = document.getElementById('formularioCarrito');
    const campoOtroTipo = document.getElementById('campoOtroTipo');
    const campoDescripcion = document.getElementById('campoDescripcion');
    const campoMonto = document.getElementById('monto');
    const inputDescripcion = document.getElementById('descripcion');
    
    console.log('Cambiando tipo de gasto a:', tipoGasto);
    
    // Ocultar/mostrar campos según tipo y manejar atributos required
    if (tipoGasto === 'compra_insumos') {
        formularioSimple.style.display = 'none';
        formularioCarrito.style.display = 'block';
        campoOtroTipo.style.display = 'none';
        // Para compra insumos, descripción se genera automáticamente, monto no se muestra
        campoDescripcion.style.display = 'none';
        if (inputDescripcion) inputDescripcion.required = false;
        if (campoMonto) campoMonto.required = false;
        console.log('Modo compra insumos: descripcion y monto no son required');
    } else if (tipoGasto === 'otro') {
        formularioSimple.style.display = 'block';
        formularioCarrito.style.display = 'none';
        campoOtroTipo.style.display = 'block';
        // Para otros gastos, descripción y monto son requeridos
        campoDescripcion.style.display = 'block';
        if (inputDescripcion) inputDescripcion.required = true;
        if (campoMonto) campoMonto.required = true;
        console.log('Modo otro: descripcion y monto son required');
    } else {
        formularioSimple.style.display = 'block';
        formularioCarrito.style.display = 'none';
        campoOtroTipo.style.display = 'none';
        // Para gastos normales, descripción y monto son requeridos
        campoDescripcion.style.display = 'block';
        if (inputDescripcion) inputDescripcion.required = true;
        if (campoMonto) campoMonto.required = true;
        console.log('Modo normal: descripcion y monto son required');
    }
}

function agregarProductoGasto() {
    const inputBusqueda = document.getElementById('productoBusqueda');
    const nombreProducto = inputBusqueda.value;
    
    if (!nombreProducto) {
        showNotification('Selecciona un producto de la lista', 'warning');
        return;
    }
    
    // Buscar el producto seleccionado
    const producto = productosDisponiblesGasto.find(p => p.nombre === nombreProducto);
    if (!producto) {
        showNotification('Producto no encontrado', 'danger');
        return;
    }
    
    // Verificar que no esté ya en el carrito
    if (productosCarritoGasto.find(p => p.producto_id === producto.id)) {
        showNotification('Este producto ya está en el carrito', 'warning');
        return;
    }
    
    // Agregar al carrito con cantidad 1
    productosCarritoGasto.push({
        producto_id: producto.id,
        nombre: producto.nombre,
        precio_costo: producto.precio_costo,
        cantidad: 1,
        subtotal: producto.precio_costo
    });
    
    // Limpiar el campo de búsqueda
    inputBusqueda.value = '';
    
    // Actualizar el carrito
    actualizarCarritoGasto();
}

function actualizarCarritoGasto() {
    const carritoContainer = document.getElementById('carritoItemsGasto');
    if (!carritoContainer) return;
    
    carritoContainer.innerHTML = '';
    
    if (productosCarritoGasto.length === 0) {
        carritoContainer.innerHTML = '<p class="text-muted">No hay productos en el carrito</p>';
        actualizarTotalGasto();
        return;
    }
    
    productosCarritoGasto.forEach((producto, index) => {
        const fila = document.createElement('div');
        fila.className = 'd-flex align-items-center mb-2 producto-item';
        fila.innerHTML = `
            <div class="flex-grow-1">
                <strong>${producto.nombre}</strong>
                <div class="small text-muted">
                    Costo unitario: 
                    <div class="input-group input-group-sm" style="width: 120px">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-sm cantidad-input" 
                               style="width: 80px" 
                               value="${producto.precio_costo}" 
                               min="0" step="1"
                               onchange="cambiarCostoGasto(${index}, this.value)">
                    </div>
                </div>
            </div>
            <div class="d-flex align-items-center">
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidadGasto(${index}, -1)">-</button>
                <input type="number" class="form-control form-control-sm mx-2 cantidad-input" style="width: 60px" 
                       value="${producto.cantidad}" min="1" 
                       onchange="cambiarCantidadManualGasto(${index}, this.value)">
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidadGasto(${index}, 1)">+</button>
            </div>
            <div class="text-end ms-3" style="min-width: 80px">
                <strong>${formatearMonedaColombiana(producto.subtotal)}</strong>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="eliminarProductoGasto(${index})">
                <i class="bi bi-trash"></i>
            </button>
        `;
        carritoContainer.appendChild(fila);
    });
    
    actualizarTotalGasto();
}

function cambiarCantidadGasto(index, delta) {
    console.log('cambiarCantidadGasto called with index:', index, 'delta:', delta);
    
    const producto = productosCarritoGasto[index];
    if (!producto) {
        console.error('Producto no encontrado en índice:', index);
        return;
    }
    
    // Calcular nueva cantidad basada en el valor acumulado del carrito
    const nuevaCantidad = producto.cantidad + delta;
    
    console.log('Cantidad actual:', producto.cantidad, 'Delta:', delta, 'Nueva cantidad:', nuevaCantidad);
    
    if (nuevaCantidad < 1) {
        console.log('La cantidad mínima es 1');
        return;
    }
    
    // Modificar el objeto real en el array del carrito
    producto.cantidad = nuevaCantidad;
    producto.subtotal = producto.precio_costo * producto.cantidad;
    
    console.log('Producto actualizado:', producto);
    
    // Volver a renderizar el carrito para mostrar los cambios
    actualizarCarritoGasto();
}

function cambiarCantidadManualGasto(index, valorManual) {
    console.log('cambiarCantidadManualGasto called with index:', index, 'valor:', valorManual);
    
    const producto = productosCarritoGasto[index];
    if (!producto) {
        console.error('Producto no encontrado en índice:', index);
        return;
    }
    
    // Validar que sea un número válido
    let nuevaCantidad = parseInt(valorManual);
    if (isNaN(nuevaCantidad) || nuevaCantidad < 1) {
        nuevaCantidad = 1;
    }
    
    // Modificar el objeto real en el array del carrito
    producto.cantidad = nuevaCantidad;
    producto.subtotal = producto.precio_costo * producto.cantidad;
    
    console.log('Producto actualizado manualmente:', producto);
    
    // Volver a renderizar el carrito para mostrar los cambios
    actualizarCarritoGasto();
}

function cambiarCostoGasto(index, valor) {
    const producto = productosCarritoGasto[index];
    if (!producto) return;
    
    const nuevoCosto = parseFloat(valor);
    if (nuevoCosto < 0) return;
    
    producto.precio_costo = nuevoCosto;
    producto.subtotal = producto.precio_costo * producto.cantidad;
    
    actualizarCarritoGasto();
}

function eliminarProductoGasto(index) {
    productosCarritoGasto.splice(index, 1);
    actualizarCarritoGasto();
}

function actualizarTotalGasto() {
    const totalElement = document.getElementById('totalGasto');
    if (!totalElement) return;
    
    const total = productosCarritoGasto.reduce((sum, p) => sum + p.subtotal, 0);
    totalElement.textContent = formatearMonedaColombiana(total);
}

// Funciones para crear producto nuevo
function mostrarModalCrearProducto() {
    const modal = new bootstrap.Modal(document.getElementById('modalCrearProducto'));
    modal.show();
    
    // Limpiar el formulario (verificar que exista antes de hacer reset)
    const formCrearProducto = document.getElementById('formCrearProducto');
    if (formCrearProducto) {
        formCrearProducto.reset();
        const nuevoProductoCantidad = document.getElementById('nuevoProductoCantidad');
        const nuevoProductoStockMinimo = document.getElementById('nuevoProductoStockMinimo');
        if (nuevoProductoCantidad) nuevoProductoCantidad.value = 1;
        if (nuevoProductoStockMinimo) nuevoProductoStockMinimo.value = 5;
    }
}

function crearProductoNuevo() {
    const nombre = document.getElementById('nuevoProductoNombre').value.trim();
    const costo = parseFloat(document.getElementById('nuevoProductoCosto').value);
    const venta = parseFloat(document.getElementById('nuevoProductoVenta').value);
    const cantidad = parseInt(document.getElementById('nuevoProductoCantidad').value);
    const stockMinimo = parseInt(document.getElementById('nuevoProductoStockMinimo').value);
    
    if (!nombre) {
        showNotification('El nombre del producto es obligatorio', 'warning');
        return;
    }
    
    if (isNaN(costo) || costo < 0) {
        showNotification('El precio de costo debe ser un número válido', 'warning');
        return;
    }
    
    if (isNaN(venta) || venta < 0) {
        showNotification('El precio de venta debe ser un número válido', 'warning');
        return;
    }
    
    if (isNaN(cantidad) || cantidad < 1) {
        showNotification('La cantidad debe ser al menos 1', 'warning');
        return;
    }
    
    // Agregar el producto al carrito local (marcado como nuevo) - NO crear en DB aún
    productosCarritoGasto.push({
        producto_id: null, // null indica que es un producto nuevo
        es_nuevo_producto: true,
        nombre: nombre,
        precio_costo: costo,
        precio_venta: venta,
        cantidad: cantidad,
        stock_minimo: stockMinimo,
        subtotal: costo * cantidad
    });
    
    // Cerrar el modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearProducto'));
    modal.hide();
    
    actualizarCarritoGasto();
    showNotification('Producto agregado al carrito (se creará al confirmar el gasto)', 'success');
}
