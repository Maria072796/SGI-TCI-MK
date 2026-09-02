from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Venta, DetalleVenta, Egreso, CierreCaja, Producto
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/utilidad-diaria')
@login_required
def utilidad_diaria():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para ver reportes financieros.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
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
    
    # Calcular costos de productos vendidos
    total_costos = Decimal('0')
    for venta in ventas_dia:
        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.producto_id)
            if producto:
                total_costos += producto.precio_costo * detalle.cantidad
    
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
    if request.method == 'POST':
        fecha_str = request.form.get('fecha')
        observaciones = request.form.get('observaciones')
        
        if fecha_str:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            fecha = date.today()
        
        # Verificar si ya existe cierre para esta fecha
        cierre_existente = CierreCaja.query.filter_by(fecha=fecha).first()
        if cierre_existente:
            flash('Ya existe un cierre de caja para esta fecha.', 'warning')
            return redirect(url_for('reportes.cierre_caja'))
        
        # Calcular totales
        ventas_dia = Venta.query.filter(
            Venta.estado == 'confirmada',
            func.date(Venta.fecha_hora) == fecha
        ).all()
        
        total_ventas = sum(v.total for v in ventas_dia)
        
        # Calcular costos de productos vendidos
        total_costos = Decimal('0')
        for venta in ventas_dia:
            for detalle in venta.detalles:
                producto = Producto.query.get(detalle.producto_id)
                if producto:
                    total_costos += producto.precio_costo * detalle.cantidad
        
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
            observaciones=observaciones
        )
        
        try:
            db.session.add(cierre)
            db.session.commit()
            flash('Cierre de caja realizado exitosamente.', 'success')
            return redirect(url_for('reportes.historial_cierres'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al realizar el cierre de caja: {str(e)}', 'danger')
    
    fecha_str = request.args.get('fecha')
    if fecha_str:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha = date.today()
    
    # Calcular datos preliminares para mostrar
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
    
    return render_template('cierre_caja.html',
                          fecha=fecha,
                          total_ventas=total_ventas,
                          total_costos=total_costos,
                          total_egresos=total_egresos,
                          utilidad_real=utilidad_real)

@reportes_bp.route('/historial-cierres')
@login_required
def historial_cierres():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para ver el historial de cierres.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).all()
    return render_template('historial_cierres.html', cierres=cierres)

@reportes_bp.route('/reporte-financiero')
@login_required
def reporte_financiero():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para ver reportes financieros.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
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
