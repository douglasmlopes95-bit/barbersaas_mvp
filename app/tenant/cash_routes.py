from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, abort
)
from flask_login import login_required, current_user
from decimal import Decimal

from app.extensions import db
from app.models.cash_session import CashSession
from app.models.cash_movement import CashMovement
from app.models.payment import Payment

# =========================================================
# BLUEPRINT
# =========================================================

cash_bp = Blueprint(
    "cash",
    __name__,
    url_prefix="/dashboard/cash"
)

# =========================================================
# VISÃO GERAL DO CAIXA
# =========================================================

@cash_bp.route("/", methods=["GET"])
@login_required
def overview():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant_id = current_user.tenant_id

    caixa_aberto = CashSession.caixa_aberto(tenant_id)

    movimentos = []
    saldo_atual = Decimal("0.00")

    if caixa_aberto:
        movimentos = CashMovement.query.filter_by(
            cash_session_id=caixa_aberto.id
        ).order_by(
            CashMovement.criado_em.desc()
        ).all()

        saldo_atual = caixa_aberto.saldo_calculado

    return render_template(
        "tenant_cash.html",
        caixa_aberto=caixa_aberto,
        movimentos=movimentos,
        saldo_atual=saldo_atual
    )

# =========================================================
# ABRIR CAIXA
# =========================================================

@cash_bp.route("/open", methods=["POST"])
@login_required
def open_cash():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant_id = current_user.tenant_id

    try:
        valor_inicial = Decimal(request.form.get("saldo_inicial", "0"))
    except Exception:
        valor_inicial = Decimal("0.00")

    try:
        caixa = CashSession.abrir_caixa(
            tenant_id=tenant_id,
            usuario_id=current_user.id,
            valor_inicial=valor_inicial,
            observacoes="Abertura de caixa"
        )
    except Exception as e:
        flash(str(e), "warning")
        return redirect(url_for("cash.overview"))

    if valor_inicial > 0:
        CashMovement.registrar_entrada(
            tenant_id=tenant_id,
            cash_session=caixa,
            usuario_id=current_user.id,
            valor=valor_inicial,
            categoria="CAIXA",
            descricao="Saldo inicial do caixa"
        )

    flash("Caixa aberto com sucesso", "success")
    return redirect(url_for("cash.overview"))

# =========================================================
# FECHAR CAIXA
# =========================================================

@cash_bp.route("/close", methods=["POST"])
@login_required
def close_cash():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant_id = current_user.tenant_id
    caixa = CashSession.caixa_aberto(tenant_id)

    if not caixa:
        flash("Nenhum caixa aberto para fechar", "warning")
        return redirect(url_for("cash.overview"))

    caixa.fechar_caixa(
        usuario_id=current_user.id,
        valor_final=caixa.saldo_calculado,
        observacoes="Fechamento de caixa"
    )

    flash("Caixa fechado com sucesso", "success")
    return redirect(url_for("cash.overview"))

# =========================================================
# REGISTRAR MOVIMENTAÇÃO MANUAL
# =========================================================

@cash_bp.route("/movement", methods=["POST"])
@login_required
def manual_movement():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant_id = current_user.tenant_id
    caixa = CashSession.caixa_aberto(tenant_id)

    if not caixa:
        flash("Abra o caixa antes de registrar movimentações", "danger")
        return redirect(url_for("cash.overview"))

    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao")

    try:
        valor = Decimal(request.form.get("valor", "0"))
    except Exception:
        valor = Decimal("0.00")

    if valor <= 0 or tipo not in ["ENTRADA", "SAIDA"]:
        flash("Movimentação inválida", "danger")
        return redirect(url_for("cash.overview"))

    if tipo == "ENTRADA":
        CashMovement.registrar_entrada(
            tenant_id=tenant_id,
            cash_session=caixa,
            usuario_id=current_user.id,
            valor=valor,
            categoria="MANUAL",
            descricao=descricao
        )
    else:
        CashMovement.registrar_saida(
            tenant_id=tenant_id,
            cash_session=caixa,
            usuario_id=current_user.id,
            valor=valor,
            categoria="MANUAL",
            descricao=descricao
        )

    flash("Movimentação registrada com sucesso", "success")
    return redirect(url_for("cash.overview"))

# =========================================================
# SINCRONIZAR PAGAMENTOS COM O CAIXA
# =========================================================

@cash_bp.route("/sync/payments", methods=["POST"])
@login_required
def sync_payments():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant_id = current_user.tenant_id
    caixa = CashSession.caixa_aberto(tenant_id)

    if not caixa:
        flash("Abra o caixa antes de sincronizar pagamentos", "danger")
        return redirect(url_for("cash.overview"))

    pagamentos = Payment.query.filter_by(
        tenant_id=tenant_id,
        status="PAGO",
        sincronizado_caixa=False
    ).all()

    if not pagamentos:
        flash("Nenhum pagamento pendente para sincronizar", "warning")
        return redirect(url_for("cash.overview"))

    for p in pagamentos:
        CashMovement.registrar_entrada(
            tenant_id=tenant_id,
            cash_session=caixa,
            usuario_id=current_user.id,
            valor=p.valor,
            categoria="PAGAMENTO",
            descricao=f"Pagamento #{p.id}",
            metodo_pagamento=p.metodo_pagamento,
            payment_id=p.id
        )

        p.sincronizado_caixa = True
        db.session.add(p)

    db.session.commit()

    flash("Pagamentos sincronizados com o caixa", "success")
    return redirect(url_for("cash.overview"))
