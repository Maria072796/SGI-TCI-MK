from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Egreso
from datetime import datetime
from decimal import Decimal

egresos_bp = Blueprint('egresos', __name__, url_prefix='/egresos')

@egresos_bp.route('/')
@login_required
def listar():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para acceder a los egresos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    egresos = Egreso.query.order_by(Egreso.fecha_hora.desc()).all()
    return render_template('egresos.html', egresos=egresos)

@egresos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para registrar egresos.', 'danger')
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
                usuario_id=current_user.id
            )
            
            db.session.add(egreso)
            db.session.commit()
            
            flash('Egreso registrado exitosamente.', 'success')
            return redirect(url_for('egresos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el egreso: {str(e)}', 'danger')
            return render_template('egreso_form.html', action='crear')
    
    return render_template('egreso_form.html', action='crear')

@egresos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para editar egresos.', 'danger')
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
            flash('Egreso actualizado exitosamente.', 'success')
            return redirect(url_for('egresos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el egreso: {str(e)}', 'danger')
            return render_template('egreso_form.html', egreso=egreso, action='editar')
    
    return render_template('egreso_form.html', egreso=egreso, action='editar')

@egresos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para eliminar egresos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    egreso = Egreso.query.get_or_404(id)
    
    try:
        db.session.delete(egreso)
        db.session.commit()
        flash('Egreso eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el egreso: {str(e)}', 'danger')
    
    return redirect(url_for('egresos.listar'))
