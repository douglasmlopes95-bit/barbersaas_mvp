from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash
)
from datetime import datetime

from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.available_slot import AvailableSlot


booking_bp = Blueprint(
    "booking",
    __name__
)


# =========================================================
# AGENDAMENTO PÚBLICO
# =========================================================
@booking_bp.route("/<slug>/agendar", methods=["GET", "POST"])
def agendar(slug):

    tenant = Tenant.query.filter_by(
        slug=slug,
        ativo=True
    ).first_or_404()

    # =========================
    # LISTA BARBEIROS
    # =========================
    barbers = User.query.filter_by(
        tenant_id=tenant.id,
        role="BARBER",
        ativo=True,
        excluido=False
    ).all()

    # =========================
    # POST — CONFIRMAR AGENDAMENTO
    # =========================
    if request.method == "POST":

        barber_id = request.form.get("barber_id", type=int)
        service_id = request.form.get("service_id", type=int)
        slot_id = request.form.get("slot_id", type=int)
        cliente_nome = request.form.get("cliente_nome")
        cliente_whatsapp = request.form.get("cliente_whatsapp")

        if not all([barber_id, service_id, slot_id, cliente_nome, cliente_whatsapp]):
            flash("Preencha todos os campos.", "danger")
            return redirect(request.url)

        # =========================
        # VALIDAR BARBEIRO
        # =========================
        barber = User.query.filter_by(
            id=barber_id,
            tenant_id=tenant.id,
            role="BARBER",
            ativo=True,
            excluido=False
        ).first()

        if not barber:
            flash("Barbeiro inválido.", "danger")
            return redirect(request.url)

        # =========================
        # VALIDAR SERVIÇO DO BARBEIRO
        # =========================
        service = Service.query.filter_by(
            id=service_id,
            tenant_id=tenant.id,
            barber_id=barber_id,
            ativo=True,
            excluido=False
        ).first()

        if not service:
            flash("Este serviço não pertence ao barbeiro selecionado.", "danger")
            return redirect(request.url)

        # =========================
        # VALIDAR HORÁRIO
        # =========================
        slot = AvailableSlot.query.filter_by(
            id=slot_id,
            tenant_id=tenant.id,
            barber_id=barber_id,
            disponivel=True
        ).first()

        if not slot:
            flash("Horário indisponível para este barbeiro.", "danger")
            return redirect(request.url)

        data_hora = datetime.combine(slot.data, slot.hora)

        appointment = Appointment(
            tenant_id=tenant.id,
            barber_id=barber_id,
            service_id=service.id,
            cliente_nome=cliente_nome,
            cliente_whatsapp=cliente_whatsapp,
            data_hora=data_hora,
            status="AGENDADO"
        )

        slot.disponivel = False

        db.session.add(appointment)
        db.session.commit()

        flash("Agendamento realizado com sucesso!", "success")
        return redirect(request.url)

    # =========================================================
    # GET — LISTAR DADOS PARA O FRONT
    # =========================================================

    # Pegamos TODOS porque o filtro agora é no Front
    services = Service.query.filter_by(
        tenant_id=tenant.id,
        ativo=True,
        excluido=False
    ).all()

    slots = AvailableSlot.query.filter_by(
        tenant_id=tenant.id,
        disponivel=True
    ).all()

    # =========================
    # CONVERTER PARA JSON
    # =========================
    services_json = [
        {
            "id": s.id,
            "nome": s.nome,
            "preco": float(s.preco),
            "barber_id": s.barber_id
        }
        for s in services
    ]

    slots_json = [
        {
            "id": s.id,
            "barber_id": s.barber_id,
            "data": s.data.strftime("%Y-%m-%d"),
            "hora": s.hora.strftime("%H:%M")
        }
        for s in slots
    ]

    return render_template(
        "booking.html",
        tenant=tenant,
        barbers=barbers,
        services=services_json,
        slots=slots_json
    )
