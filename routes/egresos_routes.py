from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Egreso
from datetime import datetime
from decimal import Decimal

egresos_bp = Blueprint('egresos', __name__, url_prefix='/gastos')

@egresos_bp.route('/')
@login_required
def listar():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para acceder a los gastos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    # RN-07: Solo mostrar egresos activos
    egresos = Egreso.query.filter_by(activo=True).order_by(Egreso.fecha_hora.desc()).all()
    return render_template('egresos.html', egresos=egresos)

@egresos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_egreso():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para registrar gastos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        try:
            descripcion = request.form.get('descripcion')
            monto = Decimal(request.form.get('monto'))
            categoria = request.form.get('categoria')
            observaciones = request.form.get('observaciones')
            
            if not descripcion:
                flash('La descripción es obligatoria.', 'warning')
                return render_template('egreso_form.html', action='crear')
            
            if monto <= 0:
                flash('El monto debe ser mayor a cero.', 'warning')
                return render_template('egreso_form.html', action='crear')
            
            egreso = Egreso(
                descripcion=descripcion,
                monto=monto,
                categoria=categoria,
                observaciones=observaciones,
                usuario_id=current_user.id,
                activo=True
            )
            
            db.session.add(egreso)
            db.session.commit()
            
            flash('Gasto registrado exitosamente.', 'success')
            return redirect(url_for('egresos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el gasto: {str(e)}', 'danger')
            return render_template('egreso_form.html', action='crear')
    
    return render_template('egreso_form.html', action='crear')

@egresos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_egreso(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para editar gastos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    egreso = Egreso.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            egreso.descripcion = request.form.get('descripcion')
            egreso.monto = Decimal(request.form.get('monto'))
            egreso.categoria = request.form.get('categoria')
            egreso.observaciones = request.form.get('observaciones')
            
            if not egreso.descripcion:
                flash('La descripción es obligatoria.', 'warning')
                return render_template('egreso_form.html', egreso=egreso, action='editar')
            
            if egreso.monto <= 0:
                flash('El monto debe ser mayor a cero.', 'warning')
                return render_template('egreso_form.html', egreso=egreso, action='editar')
            
            db.session.commit()
            flash('Gasto actualizado exitosamente.', 'success')
            return redirect(url_for('egresos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el gasto: {str(e)}', 'danger')
            return render_template('egreso_form.html', egreso=egreso, action='editar')
    
    return render_template('egreso_form.html', egreso=egreso, action='editar')

@egresos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_egreso(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para eliminar gastos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    egreso = Egreso.query.get_or_404(id)
    
    try:
        # RN-07: Eliminación lógica en lugar de física
        egreso.activo = False
        db.session.commit()
        flash('Gasto eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el gasto: {str(e)}', 'danger')
    
    return redirect(url_for('egresos.listar'))
