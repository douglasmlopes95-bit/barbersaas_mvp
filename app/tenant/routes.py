from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, abort
)
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

from app.extensions import db
from app.models.user import User
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.available_slot import AvailableSlot

# =========================================================
# BLUEPRINT
# =========================================================

tenant_bp = Blueprint(
    "tenant",
    __name__,
    url_prefix="/dashboard"
)

# =========================================================
# DASHBOARD PRINCIPAL
# =========================================================

@tenant_bp.route("/", methods=["GET", "POST"])
@login_required
def dashboard():

    if not (current_user.is_tenant_admin() or current_user.is_barber()):
        abort(403)

    tenant_id = current_user.tenant_id

    # =====================================================
    # LISTAGENS
    # =====================================================

    services = Service.query.filter_by(
        tenant_id=tenant_id,
        ativo=True
    ).all()

    barbers = User.query.filter_by(
        tenant_id=tenant_id,
        role="BARBER",
        ativo=True
    ).all()

    if current_user.is_barber():
        appointments = Appointment.query.filter_by(
            tenant_id=tenant_id,
            barber_id=current_user.id
        ).order_by(
            Appointment.data_hora.asc()
        ).all()
    else:
        appointments = Appointment.query.filter_by(
            tenant_id=tenant_id
        ).order_by(
            Appointment.data_hora.asc()
        ).all()

    slots = AvailableSlot.query.filter_by(
        tenant_id=tenant_id
    ).order_by(
        AvailableSlot.data.asc(),
        AvailableSlot.hora.asc()
    ).all()

    # =====================================================
    # AÇÕES DO TENANT_ADMIN
    # =====================================================

    if request.method == "POST" and current_user.is_tenant_admin():

        action = request.form.get("action")

        # -----------------------------
        # CADASTRAR SERVIÇO
        # -----------------------------
        if action == "create_service":

            nome = request.form.get("nome")
            descricao = request.form.get("descricao")
            preco = request.form.get("preco")
            duracao = request.form.get("duracao")

            if not nome or not preco:
                flash("Nome e preço são obrigatórios", "danger")
                return redirect(url_for("tenant.dashboard"))

            service = Service(
                nome=nome,
                descricao=descricao,
                preco=float(preco),
                duracao_min=int(duracao or 30),
                tenant_id=tenant_id
            )

            db.session.add(service)
            db.session.commit()

            flash("Serviço cadastrado com sucesso", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # CADASTRAR BARBEIRO
        # -----------------------------
        if action == "create_barber":

            nome = request.form.get("nome")
            email = request.form.get("email")
            senha = request.form.get("senha")

            if not all([nome, email, senha]):
                flash("Preencha todos os campos do barbeiro", "danger")
                return redirect(url_for("tenant.dashboard"))

            if User.query.filter_by(email=email).first():
                flash("E-mail já cadastrado", "danger")
                return redirect(url_for("tenant.dashboard"))

            barber = User(
                nome=nome,
                email=email,
                role="BARBER",
                tenant_id=tenant_id,
                ativo=True
            )
            barber.senha = generate_password_hash(senha)

            db.session.add(barber)
            db.session.commit()

            flash("Barbeiro cadastrado com sucesso", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # GERAR HORÁRIOS (SEMANAL)
        # -----------------------------
        if action == "generate_slots":

            barber_id = request.form.get("barber_id")
            weekdays = request.form.getlist("weekdays")
            hora_inicio = request.form.get("hora_inicio")
            hora_fim = request.form.get("hora_fim")
            intervalo = int(request.form.get("intervalo", 30))
            data_inicio = request.form.get("data_inicio")
            data_fim = request.form.get("data_fim")

            if not all([
                barber_id, weekdays, hora_inicio,
                hora_fim, data_inicio, data_fim
            ]):
                flash("Preencha todos os campos de horário", "danger")
                return redirect(url_for("tenant.dashboard"))

            barber_id = int(barber_id)
            weekdays = [int(d) for d in weekdays]

            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

            hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
            hora_fim = datetime.strptime(hora_fim, "%H:%M").time()

            dia_atual = data_inicio

            while dia_atual <= data_fim:

                if dia_atual.weekday() in weekdays:
                    inicio = datetime.combine(dia_atual, hora_inicio)
                    fim = datetime.combine(dia_atual, hora_fim)

                    atual = inicio
                    while atual < fim:

                        existe = AvailableSlot.query.filter_by(
                            tenant_id=tenant_id,
                            barber_id=barber_id,
                            data=dia_atual,
                            hora=atual.time()
                        ).first()

                        if not existe:
                            db.session.add(
                                AvailableSlot(
                                    tenant_id=tenant_id,
                                    barber_id=barber_id,
                                    data=dia_atual,
                                    hora=atual.time(),
                                    disponivel=True
                                )
                            )

                        atual += timedelta(minutes=intervalo)

                dia_atual += timedelta(days=1)

            db.session.commit()
            flash("Horários gerados com sucesso", "success")
            return redirect(url_for("tenant.dashboard"))

    return render_template(
        "tenant_dashboard.html",
        services=services,
        barbers=barbers,
        appointments=appointments,
        slots=slots
    )

# =========================================================
# REDIRECIONAMENTOS (HUB)
# =========================================================

@tenant_bp.route("/reports")
@login_required
def go_reports():
    return redirect(url_for("tenant_reports.overview"))

@tenant_bp.route("/cash")
@login_required
def go_cash():
    return redirect(url_for("cash.overview"))

# =========================================================
# BLOQUEAR / LIBERAR HORÁRIO
# =========================================================

@tenant_bp.route("/slot/<int:slot_id>/toggle", methods=["POST"])
@login_required
def toggle_slot(slot_id):

    if not current_user.is_tenant_admin():
        abort(403)

    slot = AvailableSlot.query.get_or_404(slot_id)

    if slot.tenant_id != current_user.tenant_id:
        abort(403)

    slot.disponivel = not slot.disponivel
    db.session.commit()

    flash("Status do horário atualizado", "success")
    return redirect(url_for("tenant.dashboard"))

# =========================================================
# EXCLUIR HORÁRIO
# =========================================================

@tenant_bp.route("/slot/<int:slot_id>/delete", methods=["POST"])
@login_required
def delete_slot(slot_id):

    if not current_user.is_tenant_admin():
        abort(403)

    slot = AvailableSlot.query.get_or_404(slot_id)

    if slot.tenant_id != current_user.tenant_id:
        abort(403)

    existe_agendamento = Appointment.query.filter_by(
        barber_id=slot.barber_id,
        data_hora=datetime.combine(slot.data, slot.hora)
    ).first()

    if existe_agendamento:
        flash("Não é possível excluir horário já agendado", "danger")
        return redirect(url_for("tenant.dashboard"))

    db.session.delete(slot)
    db.session.commit()

    flash("Horário excluído com sucesso", "success")
    return redirect(url_for("tenant.dashboard"))
