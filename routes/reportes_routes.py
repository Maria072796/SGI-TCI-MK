from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from models import db, Venta, DetalleVenta, Egreso, CierreCaja, Producto
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func
from utils.seguridad import rol_requerido
from utils.finanzas import valor_inventario_total, productos_bajo_stock
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

# Pantalla intermedia de reportes
@reportes_bp.route('/')
@login_required
@rol_requerido('administrador')
def reportes_menu():
    return render_template('reportes_menu.html')

@reportes_bp.route('/utilidad-diaria')
@login_required
@rol_requerido('administrador')
def utilidad_diaria():
    fecha_str = request.args.get('fecha')
    if fecha_str:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha = date.today()
    
    # Calcular ventas del día
    ventas_dia = Venta.query.filter(
        Venta.estado == 'confirmada',
        func.date(Venta.fecha_hora) == fecha
    ).all()
    
    total_ventas = sum(v.total for v in ventas_dia)
    
    # Calcular costos de productos vendidos (usando costo_unitario guardado al momento de venta - RN-10)
    total_costos = Decimal('0')
    for venta in ventas_dia:
        for detalle in venta.detalles:
            total_costos += detalle.costo_unitario * detalle.cantidad
    
    # Calcular egresos del día
    egresos_dia = Egreso.query.filter(
        func.date(Egreso.fecha_hora) == fecha
    ).all()
    
    total_egresos = sum(e.monto for e in egresos_dia)
    
    # Calcular utilidad real
    utilidad_real = total_ventas - total_costos - total_egresos
    
    return render_template('utilidad_diaria.html',
                          fecha=fecha,
                          ventas=ventas_dia,
                          egresos=egresos_dia,
                          total_ventas=total_ventas,
                          total_costos=total_costos,
                          total_egresos=total_egresos,
                          utilidad_real=utilidad_real)

@reportes_bp.route('/cierre-caja', methods=['GET', 'POST'])
@login_required
def cierre_caja():
    fecha_str = request.args.get('fecha')
    if fecha_str:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha = date.today()
    
    if request.method == 'POST':
        observaciones = request.form.get('observaciones')
        
        if current_user.rol == 'vendedor':
            # Cierre de turno del vendedor
            tipo = 'turno'
            
            # Verificar si ya existe cierre de turno del vendedor para esta fecha
            cierre_existente = CierreCaja.query.filter_by(
                fecha=fecha, 
                usuario_id=current_user.id, 
                tipo='turno'
            ).first()
            if cierre_existente:
                flash('Ya has realizado el cierre de tu turno para hoy.', 'warning')
                return redirect(url_for('reportes.cierre_caja'))
            
            # Calcular ventas del vendedor en el día
            ventas_dia = Venta.query.filter(
                Venta.estado == 'confirmada',
                Venta.usuario_id == current_user.id,
                func.date(Venta.fecha_hora) == fecha
            ).all()
            
            total_ventas = sum(v.total for v in ventas_dia)
            
            # Calcular costos de productos vendidos (usando costo_unitario guardado al momento de venta - RN-10)
            total_costos = Decimal('0')
            for venta in ventas_dia:
                for detalle in venta.detalles:
                    total_costos += detalle.costo_unitario * detalle.cantidad
            
            # Para el vendedor, egresos y utilidad no se calculan
            total_egresos = Decimal('0')
            utilidad_real = Decimal('0')
            
        else:
            # Cierre del día del administrador
            tipo = 'dia'
            
            # Verificar si ya existe cierre del día para esta fecha
            cierre_existente = CierreCaja.query.filter_by(
                fecha=fecha, 
                tipo='dia'
            ).first()
            if cierre_existente:
                flash('Ya existe un cierre del día para esta fecha.', 'warning')
                return redirect(url_for('reportes.cierre_caja'))
            
            # Calcular ventas del día
            ventas_dia = Venta.query.filter(
                Venta.estado == 'confirmada',
                func.date(Venta.fecha_hora) == fecha
            ).all()
            
            total_ventas = sum(v.total for v in ventas_dia)
            
            # Calcular costos de productos vendidos (usando costo_unitario guardado al momento de venta - RN-10)
            total_costos = Decimal('0')
            for venta in ventas_dia:
                for detalle in venta.detalles:
                    total_costos += detalle.costo_unitario * detalle.cantidad
            
            # Calcular egresos del día
            egresos_dia = Egreso.query.filter(
                func.date(Egreso.fecha_hora) == fecha
            ).all()
            
            total_egresos = sum(e.monto for e in egresos_dia)
            
            # Calcular utilidad real
            utilidad_real = total_ventas - total_costos - total_egresos
        
        # Crear cierre de caja
        cierre = CierreCaja(
            fecha=fecha,
            usuario_id=current_user.id,
            total_ventas=total_ventas,
            total_egresos=total_egresos,
            total_costos=total_costos,
            utilidad_real=utilidad_real,
            observaciones=observaciones,
            tipo=tipo
        )
        
        try:
            db.session.add(cierre)
            db.session.commit()
            flash('Cierre de caja realizado exitosamente.', 'success')
            return redirect(url_for('reportes.cierre_resumen', cierre_id=cierre.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al realizar el cierre de caja: {str(e)}', 'danger')
    
    # Calcular datos preliminares según rol
    if current_user.rol == 'vendedor':
        # Solo ventas del vendedor
        ventas_dia = Venta.query.filter(
            Venta.estado == 'confirmada',
            Venta.usuario_id == current_user.id,
            func.date(Venta.fecha_hora) == fecha
        ).all()
        
        total_ventas = sum(v.total for v in ventas_dia)
        
        total_costos = Decimal('0')
        for venta in ventas_dia:
            for detalle in venta.detalles:
                producto = Producto.query.get(detalle.producto_id)
                if producto:
                    total_costos += producto.precio_costo * detalle.cantidad
        
        # Para el vendedor no se muestran egresos ni utilidad
        total_egresos = Decimal('0')
        utilidad_real = Decimal('0')
        mostrar_egresos = False
    else:
        # Todas las ventas y egresos del día
        ventas_dia = Venta.query.filter(
            Venta.estado == 'confirmada',
            func.date(Venta.fecha_hora) == fecha
        ).all()
        
        total_ventas = sum(v.total for v in ventas_dia)
        
        total_costos = Decimal('0')
        for venta in ventas_dia:
            for detalle in venta.detalles:
                producto = Producto.query.get(detalle.producto_id)
                if producto:
                    total_costos += producto.precio_costo * detalle.cantidad
        
        egresos_dia = Egreso.query.filter(
            func.date(Egreso.fecha_hora) == fecha
        ).all()
        
        total_egresos = sum(e.monto for e in egresos_dia)
        utilidad_real = total_ventas - total_costos - total_egresos
        mostrar_egresos = True
    
    # Verificar si ya existe cierre para esta fecha y usuario
    cierre_existente = CierreCaja.query.filter_by(
        fecha=fecha, 
        usuario_id=current_user.id
    ).first()
    
    return render_template('cierre_caja.html',
                          fecha=fecha,
                          total_ventas=total_ventas,
                          total_costos=total_costos,
                          total_egresos=total_egresos,
                          utilidad_real=utilidad_real,
                          mostrar_egresos=mostrar_egresos,
                          cierre_existente=cierre_existente)

# Resumen de cierre de caja (para impresión)
@reportes_bp.route('/cierre-resumen/<int:cierre_id>')
@login_required
def cierre_resumen(cierre_id):
    cierre = CierreCaja.query.get_or_404(cierre_id)
    
    # Verificar permisos: vendedor solo puede ver sus propios cierres
    if current_user.rol == 'vendedor' and cierre.usuario_id != current_user.id:
        flash('No tienes permiso para ver este cierre.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    return render_template('cierre_resumen.html', cierre=cierre)

@reportes_bp.route('/historial-cierres')
@login_required
@rol_requerido('administrador')
def historial_cierres():
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).all()
    return render_template('historial_cierres.html', cierres=cierres)

@reportes_bp.route('/reporte-financiero')
@login_required
@rol_requerido('administrador')
def reporte_financiero():
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    else:
        fecha_inicio = date.today().replace(day=1)  # Primer día del mes actual
        fecha_fin = date.today()
    
    # Calcular ventas en el período
    ventas_periodo = Venta.query.filter(
        Venta.estado == 'confirmada',
        func.date(Venta.fecha_hora) >= fecha_inicio,
        func.date(Venta.fecha_hora) <= fecha_fin
    ).all()
    
    total_ventas = sum(v.total for v in ventas_periodo)
    
    # Calcular costos
    total_costos = Decimal('0')
    for venta in ventas_periodo:
        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.producto_id)
            if producto:
                total_costos += producto.precio_costo * detalle.cantidad
    
    # Calcular egresos
    egresos_periodo = Egreso.query.filter(
        func.date(Egreso.fecha_hora) >= fecha_inicio,
        func.date(Egreso.fecha_hora) <= fecha_fin
    ).all()
    
    total_egresos = sum(e.monto for e in egresos_periodo)
    
    utilidad_real = total_ventas - total_costos - total_egresos
    
    return render_template('reporte_financiero.html',
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin,
                          total_ventas=total_ventas,
                          total_costos=total_costos,
                          total_egresos=total_egresos,
                          utilidad_real=utilidad_real,
                          ventas=ventas_periodo,
                          egresos=egresos_periodo)

@reportes_bp.route('/reporte-financiero-pdf')
@login_required
@rol_requerido('administrador')
def reporte_financiero_pdf():
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    else:
        fecha_inicio = date.today().replace(day=1)  # Primer día del mes actual
        fecha_fin = date.today()
    
    # Calcular ventas en el período
    ventas_periodo = Venta.query.filter(
        Venta.estado == 'confirmada',
        func.date(Venta.fecha_hora) >= fecha_inicio,
        func.date(Venta.fecha_hora) <= fecha_fin
    ).all()
    
    total_ventas = sum(v.total for v in ventas_periodo)
    
    # Calcular costos
    total_costos = Decimal('0')
    for venta in ventas_periodo:
        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.producto_id)
            if producto:
                total_costos += producto.precio_costo * detalle.cantidad
    
    # Calcular egresos
    egresos_periodo = Egreso.query.filter(
        func.date(Egreso.fecha_hora) >= fecha_inicio,
        func.date(Egreso.fecha_hora) <= fecha_fin
    ).all()
    
    total_egresos = sum(e.monto for e in egresos_periodo)
    
    utilidad_real = total_ventas - total_costos - total_egresos
    
    # Crear PDF
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_financiero_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.pdf'
    
    # Crear buffer para el PDF
    from io import BytesIO
    buffer = BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("SGI-TCI MK - Sistema de Gestión de Inventario", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    subtitle = Paragraph("Miscelánea Karen", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Período
    periodo_text = f"Reporte Financiero del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    periodo = Paragraph(periodo_text, styles['Heading2'])
    elements.append(periodo)
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen de métricas
    resumen_data = [
        ['Métrica', 'Monto'],
        ['Total Ingresos', f'${total_ventas:,.2f}'],
        ['Total Costos', f'${total_costos:,.2f}'],
        ['Total Egresos', f'${total_egresos:,.2f}'],
        ['Utilidad Real', f'${utilidad_real:,.2f}']
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.beige),
        ('GRID', (0, 0), (1, -1), 1, colors.black)
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de ventas
    ventas_heading = Paragraph(f"Ventas en el Período ({len(ventas_periodo)})", styles['Heading3'])
    elements.append(ventas_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    if ventas_periodo:
        ventas_data = [['ID', 'Fecha', 'Vendedor', 'Total']]
        for venta in ventas_periodo:
            ventas_data.append([
                str(venta.id),
                venta.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                venta.usuario.nombre_completo or venta.usuario.username,
                f'${venta.total:,.2f}'
            ])
        
        ventas_table = Table(ventas_data, colWidths=[0.5*inch, 1.5*inch, 2*inch, 1*inch])
        ventas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
            ('ALIGN', (0, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 10),
            ('BOTTOMPADDING', (0, 0), (3, 0), 8),
            ('BACKGROUND', (0, 1), (3, -1), colors.beige),
            ('GRID', (0, 0), (3, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (3, -1), 9)
        ]))
        elements.append(ventas_table)
    else:
        no_ventas = Paragraph("No hay ventas en el período seleccionado.", styles['Normal'])
        elements.append(no_ventas)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de egresos
    egresos_heading = Paragraph(f"Egresos en el Período ({len(egresos_periodo)})", styles['Heading3'])
    elements.append(egresos_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    if egresos_periodo:
        egresos_data = [['ID', 'Fecha', 'Descripción', 'Monto']]
        for egreso in egresos_periodo:
            egresos_data.append([
                str(egreso.id),
                egreso.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                egreso.descripcion,
                f'${egreso.monto:,.2f}'
            ])
        
        egresos_table = Table(egresos_data, colWidths=[0.5*inch, 1.5*inch, 2*inch, 1*inch])
        egresos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
            ('ALIGN', (0, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 10),
            ('BOTTOMPADDING', (0, 0), (3, 0), 8),
            ('BACKGROUND', (0, 1), (3, -1), colors.beige),
            ('GRID', (0, 0), (3, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (3, -1), 9)
        ]))
        elements.append(egresos_table)
    else:
        no_egresos = Paragraph("No hay egresos en el período seleccionado.", styles['Normal'])
        elements.append(no_egresos)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen financiero
    resumen_financiero_heading = Paragraph("Resumen Financiero", styles['Heading3'])
    elements.append(resumen_financiero_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    resumen_financiero_data = [
        ['Concepto', 'Monto'],
        ['Período', f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'],
        ['Total Ingresos', f'${total_ventas:,.2f}'],
        ['Total Costos de Productos', f'${total_costos:,.2f}'],
        ['Total Egresos', f'${total_egresos:,.2f}'],
        ['Utilidad Real', f'${utilidad_real:,.2f}']
    ]
    
    resumen_financiero_table = Table(resumen_financiero_data, colWidths=[2.5*inch, 2*inch])
    resumen_financiero_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, 1), (1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#cce5ff')),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (1, -1), 9)
    ]))
    elements.append(resumen_financiero_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Margen de utilidad
    margen_utilidad_heading = Paragraph("Margen de Utilidad", styles['Heading3'])
    elements.append(margen_utilidad_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    if total_ventas > 0:
        margen = (utilidad_real / total_ventas) * 100
        margen_text = f"{margen:.2f}%"
    else:
        margen_text = "0%"
    
    margen_utilidad_data = [
        ['Margen de Utilidad', margen_text],
        ['Porcentaje de utilidad sobre los ingresos totales', '']
    ]
    
    margen_utilidad_table = Table(margen_utilidad_data, colWidths=[3*inch, 2*inch])
    margen_utilidad_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, 1), colors.HexColor('#d4edda')),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (1, -1), 10)
    ]))
    elements.append(margen_utilidad_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    footer2 = Paragraph("SGI-TCI MK - Sistema de Gestión de Inventario", styles['Normal'])
    elements.append(footer2)
    
    # Generar PDF
    doc.build(elements)
    
    # Obtener el contenido del PDF
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Enviar el PDF
    response.data = pdf_content
    
    return response

@reportes_bp.route('/reporte-inventario')
@login_required
@rol_requerido('administrador')
def reporte_inventario():
    # Query productos activos
    productos = Producto.query.filter_by(activo=True).all()
    
    # Calcular datos para cada producto
    productos_data = []
    for producto in productos:
        valor_total_producto = producto.stock_actual * producto.precio_costo
        productos_data.append({
            'producto': producto,
            'valor_total': valor_total_producto,
            'stock_bajo': producto.stock_actual <= producto.stock_minimo
        })
    
    # Calcular totales
    total_productos = len(productos)
    productos_stock_bajo = productos_bajo_stock()
    total_stock_bajo = len(productos_stock_bajo)
    valor_total_inventario = valor_inventario_total()
    
    return render_template('reporte_inventario.html',
                          productos=productos_data,
                          total_productos=total_productos,
                          total_stock_bajo=total_stock_bajo,
                          valor_total_inventario=valor_total_inventario)

@reportes_bp.route('/reporte-inventario-pdf')
@login_required
@rol_requerido('administrador')
def reporte_inventario_pdf():
    # Query productos activos
    productos = Producto.query.filter_by(activo=True).all()
    
    # Calcular datos para cada producto
    productos_data = []
    for producto in productos:
        valor_total_producto = producto.stock_actual * producto.precio_costo
        productos_data.append({
            'producto': producto,
            'valor_total': valor_total_producto,
            'stock_bajo': producto.stock_actual <= producto.stock_minimo
        })
    
    # Calcular totales
    total_productos = len(productos)
    productos_stock_bajo = productos_bajo_stock()
    total_stock_bajo = len(productos_stock_bajo)
    valor_total_inventario = valor_inventario_total()
    
    # Crear PDF
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_inventario_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    # Crear buffer para el PDF
    from io import BytesIO
    buffer = BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("SGI-TCI MK - Sistema de Gestión de Inventario", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    subtitle = Paragraph("Miscelánea Karen", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Subtítulo
    inventario_heading = Paragraph("Reporte de Inventario", styles['Heading2'])
    elements.append(inventario_heading)
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen de métricas
    resumen_data = [
        ['Métrica', 'Valor'],
        ['Total Productos', str(total_productos)],
        ['Productos con Stock Bajo', str(total_stock_bajo)],
        ['Valor Total del Inventario', f'${valor_total_inventario:,.2f}']
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.beige),
        ('GRID', (0, 0), (1, -1), 1, colors.black)
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de inventario
    inventario_heading = Paragraph("Detalle del Inventario", styles['Heading3'])
    elements.append(inventario_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    if productos_data:
        inventario_data = [['ID', 'Nombre', 'Descripción', 'Precio Costo', 'Precio Venta', 'Stock Actual', 'Stock Mínimo', 'Valor Total', 'Estado']]
        
        for item in productos_data:
            prod = item['producto']
            estado = 'Stock Bajo' if item['stock_bajo'] else 'Normal'
            
            inventario_data.append([
                str(prod.id),
                prod.nombre,
                (prod.descripcion[:50] + '...') if prod.descripcion and len(prod.descripcion) > 50 else (prod.descripcion or '-'),
                f'${prod.precio_costo:,.2f}',
                f'${prod.precio_venta:,.2f}',
                str(prod.stock_actual),
                str(prod.stock_minimo),
                f'${item["valor_total"]:,.2f}',
                estado
            ])
        
        inventario_table = Table(inventario_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.7*inch])
        inventario_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (8, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (8, 0), colors.white),
            ('ALIGN', (0, 0), (8, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (8, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (8, 0), 8),
            ('BOTTOMPADDING', (0, 0), (8, 0), 8),
            ('BACKGROUND', (0, 1), (8, -1), colors.beige),
            ('GRID', (0, 0), (8, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (8, -1), 7)
        ]))
        elements.append(inventario_table)
    else:
        no_productos = Paragraph("No hay productos en el inventario.", styles['Normal'])
        elements.append(no_productos)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    footer2 = Paragraph("SGI-TCI MK - Sistema de Gestión de Inventario", styles['Normal'])
    elements.append(footer2)
    
    # Generar PDF
    doc.build(elements)
    
    # Obtener el contenido del PDF
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Enviar el PDF
    response.data = pdf_content
    
    return response
