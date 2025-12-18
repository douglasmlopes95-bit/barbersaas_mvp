from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, abort
)
from datetime import datetime

from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.available_slot import AvailableSlot

# =========================================================
# BLUEPRINT
# =========================================================

booking_bp = Blueprint(
    "booking",
    __name__
)

# =========================================================
# AGENDAMENTO PÚBLICO
# =========================================================

@booking_bp.route("/<slug>/agendar", methods=["GET", "POST"])
def agendar(slug):
    """
    Página pública de agendamento:
    - Cliente escolhe barbeiro
    - Cliente escolhe serviço
    - Cliente escolhe horário DISPONÍVEL
    """

    tenant = Tenant.query.filter_by(
        slug=slug,
        ativo=True
    ).first_or_404()

    services = Service.query.filter_by(
        tenant_id=tenant.id,
        ativo=True
    ).all()

    barbers = User.query.filter_by(
        tenant_id=tenant.id,
        role="BARBER",
        ativo=True
    ).all()

    # -------------------------------------------------
    # POST - CONFIRMAR AGENDAMENTO
    # -------------------------------------------------
    if request.method == "POST":
        try:
            slot_id = int(request.form.get("slot_id"))
            service_id = int(request.form.get("service_id"))
            cliente_nome = request.form.get("cliente_nome")
            cliente_whatsapp = request.form.get("cliente_whatsapp")
        except Exception:
            flash("Dados inválidos", "danger")
            return redirect(request.url)

        if not all([slot_id, service_id, cliente_nome, cliente_whatsapp]):
            flash("Preencha todos os campos", "danger")
            return redirect(request.url)

        slot = AvailableSlot.query.filter_by(
            id=slot_id,
            tenant_id=tenant.id,
            disponivel=True
        ).first()

        if not slot:
            flash("Horário indisponível", "danger")
            return redirect(request.url)

        # Cria data/hora final a partir do slot
        data_hora = datetime.combine(slot.data, slot.hora)

        # Cria agendamento
        appointment = Appointment(
            tenant_id=tenant.id,
            barber_id=slot.barber_id,
            service_id=service_id,
            cliente_nome=cliente_nome,
            cliente_whatsapp=cliente_whatsapp,
            data_hora=data_hora,
            status="AGENDADO"
        )

        # Marca slot como ocupado
        slot.disponivel = False

        db.session.add(appointment)
        db.session.commit()

        flash("Agendamento realizado com sucesso!", "success")
        return redirect(request.url)

    # -------------------------------------------------
    # GET - LISTAR HORÁRIOS DISPONÍVEIS
    # -------------------------------------------------
    slots = AvailableSlot.query.filter_by(
        tenant_id=tenant.id,
        disponivel=True
    ).order_by(
        AvailableSlot.data.asc(),
        AvailableSlot.hora.asc()
    ).all()

    return render_template(
        "booking.html",
        tenant=tenant,
        services=services,
        barbers=barbers,
        slots=slots
    )
