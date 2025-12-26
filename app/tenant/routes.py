from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, abort
)
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

from app.extensions import db
from app.models.user import User
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.available_slot import AvailableSlot
from app.models.cash_session import CashSession
from app.models.cash_movement import CashMovement
from app.models.tenant import Tenant   # <-- IMPORT IMPORTANTE


# =========================================================
# BLUEPRINT
# =========================================================

tenant_bp = Blueprint(
    "tenant",
    __name__,
    url_prefix="/dashboard"
)

# =========================================================
# DASHBOARD PRINCIPAL + AGENDA
# =========================================================

@tenant_bp.route("/", methods=["GET", "POST"])
@login_required
def dashboard():

    if not (current_user.is_tenant_admin() or current_user.is_barber()):
        abort(403)

    tenant_id = current_user.tenant_id

    # =====================================================
    # FILTROS DA AGENDA
    # =====================================================
    filtro_data = request.args.get("data")
    filtro_status = request.args.get("status")
    filtro_barbeiro = request.args.get("barber_id")

    q_appointments = Appointment.query.filter_by(
        tenant_id=tenant_id
    )

    if current_user.is_barber():
        q_appointments = q_appointments.filter(
            Appointment.barber_id == current_user.id
        )

    if filtro_data:
        data = datetime.strptime(filtro_data, "%Y-%m-%d").date()
        q_appointments = q_appointments.filter(
            db.func.date(Appointment.data_hora) == data
        )

    if filtro_status:
        q_appointments = q_appointments.filter(
            Appointment.status == filtro_status
        )

    if filtro_barbeiro and current_user.is_tenant_admin():
        q_appointments = q_appointments.filter(
            Appointment.barber_id == int(filtro_barbeiro)
        )

    appointments = q_appointments.order_by(
        Appointment.data_hora.asc()
    ).all()

    # =====================================================
    # LISTAGENS
    # =====================================================
    services = Service.query.filter_by(
        tenant_id=tenant_id,
        excluido=False
    ).all()

    barbers = User.query.filter_by(
        tenant_id=tenant_id,
        role="BARBER",
        excluido=False
    ).all()

    slots = AvailableSlot.query.filter_by(
        tenant_id=tenant_id
    ).order_by(
        AvailableSlot.data.asc(),
        AvailableSlot.hora.asc()
    ).all()

    # =====================================================
    # AÇÕES POST (ADMIN)
    # =====================================================
    if request.method == "POST" and current_user.is_tenant_admin():

        action = request.form.get("action")

        # -----------------------------
        # CRIAR SERVIÇO
        # -----------------------------
        if action == "create_service":

            barber_id = request.form.get("barber_id") or None

            if barber_id:
                barber = User.query.filter_by(
                    id=int(barber_id),
                    tenant_id=tenant_id,
                    role="BARBER",
                    excluido=False
                ).first()

                if not barber:
                    flash("Barbeiro inválido", "danger")
                    return redirect(url_for("tenant.dashboard"))

            service = Service(
                nome=request.form.get("nome"),
                descricao=request.form.get("descricao"),
                preco=request.form.get("preco"),
                duracao_min=int(request.form.get("duracao") or 30),
                tenant_id=tenant_id,
                barber_id=barber_id
            )

            db.session.add(service)
            db.session.commit()
            flash("Serviço cadastrado", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # EDITAR SERVIÇO
        # -----------------------------
        if action == "edit_service":
            service = Service.query.get_or_404(
                request.form.get("service_id")
            )

            if service.tenant_id != tenant_id:
                abort(403)

            barber_id = request.form.get("barber_id") or None

            if barber_id:
                barber = User.query.filter_by(
                    id=int(barber_id),
                    tenant_id=tenant_id,
                    role="BARBER",
                    excluido=False
                ).first()

                if not barber:
                    flash("Barbeiro inválido", "danger")
                    return redirect(url_for("tenant.dashboard"))

            service.nome = request.form.get("nome")
            service.descricao = request.form.get("descricao")
            service.preco = request.form.get("preco")
            service.duracao_min = int(request.form.get("duracao") or 30)
            service.ativo = bool(request.form.get("ativo"))
            service.barber_id = barber_id

            db.session.commit()
            flash("Serviço atualizado", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # EXCLUIR SERVIÇO
        # -----------------------------
        if action == "delete_service":
            service = Service.query.get_or_404(
                request.form.get("service_id")
            )
            if service.tenant_id != tenant_id or not service.pode_excluir():
                flash("Não é possível excluir este serviço", "danger")
            else:
                service.soft_delete()
                db.session.commit()
                flash("Serviço excluído", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # CRIAR BARBEIRO
        # -----------------------------
        if action == "create_barber":
            barber = User(
                nome=request.form.get("nome"),
                email=request.form.get("email"),
                role="BARBER",
                tenant_id=tenant_id
            )
            barber.set_password(request.form.get("senha"))
            db.session.add(barber)
            db.session.commit()
            flash("Barbeiro cadastrado", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # EDITAR BARBEIRO
        # -----------------------------
        if action == "edit_barber":
            barber = User.query.get_or_404(
                request.form.get("barber_id")
            )
            if barber.tenant_id != tenant_id:
                abort(403)

            barber.nome = request.form.get("nome")
            barber.email = request.form.get("email")

            if request.form.get("senha"):
                barber.set_password(request.form.get("senha"))

            barber.ativo = bool(request.form.get("ativo"))
            db.session.commit()
            flash("Barbeiro atualizado", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # EXCLUIR BARBEIRO
        # -----------------------------
        if action == "delete_barber":
            barber = User.query.get_or_404(
                request.form.get("barber_id")
            )
            if barber.tenant_id != tenant_id:
                abort(403)

            barber.soft_delete()
            db.session.commit()
            flash("Barbeiro removido", "success")
            return redirect(url_for("tenant.dashboard"))

        # -----------------------------
        # GERAR HORÁRIOS
        # -----------------------------
        if action == "generate_slots":
            barber_id = int(request.form.get("barber_id"))
            weekdays = [int(d) for d in request.form.getlist("weekdays")]
            intervalo = int(request.form.get("intervalo", 30))

            data_inicio = datetime.strptime(
                request.form.get("data_inicio"), "%Y-%m-%d"
            ).date()
            data_fim = datetime.strptime(
                request.form.get("data_fim"), "%Y-%m-%d"
            ).date()

            hora_inicio = datetime.strptime(
                request.form.get("hora_inicio"), "%H:%M"
            ).time()
            hora_fim = datetime.strptime(
                request.form.get("hora_fim"), "%H:%M"
            ).time()

            dia = data_inicio
            while dia <= data_fim:
                if dia.weekday() in weekdays:
                    atual = datetime.combine(dia, hora_inicio)
                    fim = datetime.combine(dia, hora_fim)

                    while atual < fim:
                        if not AvailableSlot.query.filter_by(
                            tenant_id=tenant_id,
                            barber_id=barber_id,
                            data=dia,
                            hora=atual.time()
                        ).first():
                            db.session.add(
                                AvailableSlot(
                                    tenant_id=tenant_id,
                                    barber_id=barber_id,
                                    data=dia,
                                    hora=atual.time()
                                )
                            )
                        atual += timedelta(minutes=intervalo)
                dia += timedelta(days=1)

            db.session.commit()
            flash("Horários gerados", "success")
            return redirect(url_for("tenant.dashboard"))

    return render_template(
        "tenant_dashboard.html",
        services=services,
        barbers=barbers,
        appointments=appointments,
        slots=slots
    )


# =========================================================
# CONCLUIR AGENDAMENTO
# =========================================================

@tenant_bp.route("/appointment/<int:appointment_id>/complete", methods=["POST"])
@login_required
def complete_appointment(appointment_id):

    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.tenant_id != current_user.tenant_id:
        abort(403)

    appointment.concluir()

    service = Service.query.get(appointment.service_id)

    cash_session = CashSession.get_or_create_aberta(
        tenant_id=current_user.tenant_id,
        usuario_id=current_user.id
    )

    CashMovement.registrar_entrada(
        tenant_id=current_user.tenant_id,
        cash_session=cash_session,
        usuario_id=current_user.id,
        valor=service.preco,
        categoria="SERVICO",
        descricao=f"Serviço: {service.nome}",
        appointment_id=appointment.id
    )

    db.session.commit()
    flash("Serviço concluído", "success")
    return redirect(url_for("tenant.dashboard"))


# =========================================================
# HUB
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
# HORÁRIOS
# =========================================================

@tenant_bp.route("/slot/<int:slot_id>/toggle", methods=["POST"])
@login_required
def toggle_slot(slot_id):

    slot = AvailableSlot.query.get_or_404(slot_id)

    if slot.tenant_id != current_user.tenant_id:
        abort(403)

    if slot.disponivel:
        slot.bloquear()
    else:
        slot.liberar()

    db.session.commit()
    flash("Status do horário atualizado", "success")
    return redirect(url_for("tenant.dashboard"))

@tenant_bp.route("/slot/<int:slot_id>/delete", methods=["POST"])
@login_required
def delete_slot(slot_id):

    slot = AvailableSlot.query.get_or_404(slot_id)

    if slot.tenant_id != current_user.tenant_id or not slot.pode_excluir():
        flash("Não é possível excluir este horário", "danger")
        return redirect(url_for("tenant.dashboard"))

    db.session.delete(slot)
    db.session.commit()
    flash("Horário excluído", "success")
    return redirect(url_for("tenant.dashboard"))


# =========================================================
# DADOS DA EMPRESA — NOVA ABA
# =========================================================
@tenant_bp.route("/company", methods=["GET", "POST"])
@login_required
def company_settings():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant = Tenant.query.get_or_404(current_user.tenant_id)

    if request.method == "POST":
        tenant.descricao = request.form.get("descricao")
        tenant.endereco = request.form.get("endereco")
        tenant.whatsapp = request.form.get("whatsapp")

        # ==============================
        # UPLOAD REAL DA LOGO
        # ==============================
        file = request.files.get("logo")

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            upload_dir = os.path.join("static", "uploads", "logos")
            os.makedirs(upload_dir, exist_ok=True)

            filename = f"tenant_{tenant.id}_{int(datetime.utcnow().timestamp())}_{filename}"
            file_path = os.path.join(upload_dir, filename)

            file.save(file_path)

            # SALVA NO CAMPO REAL DO BANCO
            tenant.logo_filename = filename

        db.session.commit()

        flash("Dados da empresa atualizados com sucesso!", "success")
        return redirect(url_for("tenant.company_settings"))

    return render_template(
        "tenant/company.html",
        tenant=tenant
    )
