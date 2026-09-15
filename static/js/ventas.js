// JavaScript para el módulo de ventas del vendedor (5 pasos)

let productosCarrito = [];
let productosDisponibles = [];

// Error handler global para capturar errores de JavaScript
window.onerror = function(message, source, lineno, colno, error) {
    console.error('Error global de JavaScript:', message, 'en', source, 'línea', lineno);
    console.error('Error completo:', error);
};

// Cargar productos disponibles al iniciar
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Iniciando carga de productos');
    cargarProductosDisponibles();
});

function cargarProductosDisponibles() {
    fetch('/ventas/api/productos-disponibles')
        .then(response => response.json())
        .then(data => {
            productosDisponibles = data;
            configurarAutocompletado();
        })
        .catch(error => console.error('Error al cargar productos:', error));
}

function configurarAutocompletado() {
    const inputBusqueda = document.getElementById('productoBusqueda');
    if (!inputBusqueda) return;
    
    const datalist = document.getElementById('productosList');
    if (!datalist) return;
    
    // Limpiar opciones existentes
    datalist.innerHTML = '';
    
    // Agregar productos al datalist
    productosDisponibles.forEach(producto => {
        const option = document.createElement('option');
        option.value = producto.nombre;
        option.dataset.id = producto.id;
        option.dataset.precio = producto.precio_venta;
        option.dataset.costo = producto.precio_costo;
        option.dataset.stock = producto.stock_actual;
        datalist.appendChild(option);
    });
}

// Agregar producto al carrito
function agregarProducto() {
    const inputBusqueda = document.getElementById('productoBusqueda');
    const nombreProducto = inputBusqueda.value;
    
    if (!nombreProducto) {
        mostrarError('Selecciona un producto de la lista');
        return;
    }
    
    // Buscar el producto seleccionado
    const producto = productosDisponibles.find(p => p.nombre === nombreProducto);
    if (!producto) {
        mostrarError('Producto no encontrado');
        return;
    }
    
    // Verificar que no esté ya en el carrito
    if (productosCarrito.find(p => p.producto_id === producto.id)) {
        mostrarError('Este producto ya está en el carrito');
        return;
    }
    
    // Verificar stock disponible
    if (producto.stock_actual <= 0) {
        mostrarError('Este producto no tiene stock disponible');
        return;
    }
    
    // Agregar al carrito con cantidad 1
    productosCarrito.push({
        producto_id: producto.id,
        nombre: producto.nombre,
        precio_unitario: producto.precio_venta,
        costo_unitario: producto.precio_costo,
        stock_disponible: producto.stock_actual,
        cantidad: 1,
        subtotal: producto.precio_venta
    });
    
    // Limpiar el campo de búsqueda
    inputBusqueda.value = '';
    
    // Actualizar el carrito
    actualizarCarrito();
}

function actualizarCarrito() {
    const carritoContainer = document.getElementById('carritoItems');
    if (!carritoContainer) return;
    
    carritoContainer.innerHTML = '';
    
    if (productosCarrito.length === 0) {
        carritoContainer.innerHTML = '<p class="text-muted">No hay productos en el carrito</p>';
        return;
    }
    
    productosCarrito.forEach((producto, index) => {
        const fila = document.createElement('div');
        fila.className = 'd-flex align-items-center mb-2 producto-item';
        
        // HTML de advertencia si existe
        const advertenciaHTML = producto.advertencia ? 
            `<div class="text-warning small mt-1" style="color: #d97706;">⚠️ ${producto.advertencia}</div>` : '';
        
        fila.innerHTML = `
            <div class="flex-grow-1">
                <strong>${producto.nombre}</strong>
                <div class="small text-muted">$${producto.precio_unitario.toFixed(2)} c/u - Stock: ${producto.stock_disponible}</div>
                ${advertenciaHTML}
            </div>
            <div class="d-flex align-items-center">
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad(${index}, -1)">-</button>
                <input type="number" class="form-control form-control-sm mx-2 cantidad-input" style="width: 60px" 
                       value="${producto.cantidad}" min="1" max="${producto.stock_disponible}"
                       onchange="cambiarCantidadManual(${index}, this.value)">
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad(${index}, 1)">+</button>
            </div>
            <div class="text-end ms-3" style="min-width: 80px">
                <strong>$${producto.subtotal.toFixed(2)}</strong>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="eliminarProducto(${index})">
                <i class="bi bi-trash"></i>
            </button>
        `;
        carritoContainer.appendChild(fila);
    });
    
    // Actualizar totales
    actualizarTotales();
}

function cambiarCantidad(index, delta) {
    console.log('cambiarCantidad called with index:', index, 'delta:', delta);
    
    const producto = productosCarrito[index];
    if (!producto) {
        console.error('Producto no encontrado en índice:', index);
        return;
    }
    
    // Calcular nueva cantidad basada en el valor acumulado del carrito
    const nuevaCantidad = producto.cantidad + delta;
    
    console.log('Cantidad actual:', producto.cantidad, 'Delta:', delta, 'Nueva cantidad:', nuevaCantidad);
    
    // Validar stock
    if (nuevaCantidad > producto.stock_disponible) {
        mostrarError(`Stock máximo alcanzado (${producto.stock_disponible} disponibles)`);
        // Añadir mensaje de advertencia al producto
        producto.advertencia = `Stock máximo: ${producto.stock_disponible}`;
        actualizarCarrito();
        return;
    }
    
    if (nuevaCantidad < 1) {
        mostrarError('La cantidad mínima es 1');
        return;
    }
    
    // Limpiar advertencia si está todo bien
    producto.advertencia = null;
    
    // Modificar el objeto real en el array del carrito
    producto.cantidad = nuevaCantidad;
    producto.subtotal = producto.precio_unitario * producto.cantidad;
    
    console.log('Producto actualizado:', producto);
    
    // Volver a renderizar el carrito para mostrar los cambios
    actualizarCarrito();
}

function cambiarCantidadManual(index, valorManual) {
    console.log('cambiarCantidadManual called with index:', index, 'valor:', valorManual);
    
    const producto = productosCarrito[index];
    if (!producto) {
        console.error('Producto no encontrado en índice:', index);
        return;
    }
    
    // Validar que sea un número válido
    let nuevaCantidad = parseInt(valorManual);
    if (isNaN(nuevaCantidad) || nuevaCantidad < 1) {
        nuevaCantidad = 1;
    }
    
    // Validar stock máximo
    if (nuevaCantidad > producto.stock_disponible) {
        nuevaCantidad = producto.stock_disponible;
        mostrarError(`Stock máximo alcanzado (${producto.stock_disponible} disponibles)`);
        // Añadir mensaje de advertencia al producto
        producto.advertencia = `Stock máximo: ${producto.stock_disponible}`;
    } else {
        // Limpiar advertencia si está todo bien
        producto.advertencia = null;
    }
    
    // Modificar el objeto real en el array del carrito
    producto.cantidad = nuevaCantidad;
    producto.subtotal = producto.precio_unitario * producto.cantidad;
    
    console.log('Producto actualizado manualmente:', producto);
    
    // Volver a renderizar el carrito para mostrar los cambios
    actualizarCarrito();
}

function eliminarProducto(index) {
    productosCarrito.splice(index, 1);
    actualizarCarrito();
}

function actualizarTotales() {
    const totalElement = document.getElementById('totalVenta');
    const productosCountElement = document.getElementById('productosCount');
    const unidadesCountElement = document.getElementById('unidadesCount');
    const confirmarBtn = document.getElementById('btnConfirmarVenta');
    
    if (!totalElement) return;
    
    const total = productosCarrito.reduce((sum, p) => sum + p.subtotal, 0);
    const productosCount = productosCarrito.length;
    const unidadesCount = productosCarrito.reduce((sum, p) => sum + p.cantidad, 0);
    
    totalElement.textContent = `$${total.toFixed(2)}`;
    
    if (productosCountElement) {
        productosCountElement.textContent = productosCount;
    }
    
    if (unidadesCountElement) {
        unidadesCountElement.textContent = unidadesCount;
    }
    
    // Habilitar/deshabilitar botón de confirmar
    if (confirmarBtn) {
        confirmarBtn.disabled = productosCount === 0;
    }
}

function mostrarError(mensaje) {
    const errorElement = document.getElementById('errorVenta');
    if (errorElement) {
        errorElement.textContent = mensaje;
        errorElement.style.display = 'block';
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

// Validar antes de enviar el formulario
function validarVenta() {
    if (productosCarrito.length === 0) {
        mostrarError('Agrega al menos un producto para confirmar la venta');
        return false;
    }
    
    // Validar stock de cada producto
    for (let producto of productosCarrito) {
        if (producto.cantidad > producto.stock_disponible) {
            mostrarError(`Stock insuficiente para ${producto.nombre}`);
            return false;
        }
    }
    
    // Convertir el carrito a JSON para enviar al servidor
    const productosJson = JSON.stringify(productosCarrito);
    const productosJsonInput = document.getElementById('productos_json');
    if (productosJsonInput) {
        productosJsonInput.value = productosJson;
    }
    
    return true;
}

// Permitir agregar producto con Enter
document.addEventListener('DOMContentLoaded', function() {
    const inputBusqueda = document.getElementById('productoBusqueda');
    if (inputBusqueda) {
        inputBusqueda.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                agregarProducto();
            }
        });
    }
});