from app.extensions import db


class Barber(db.Model):
    __tablename__ = "barbers"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    ativo = db.Column(db.Boolean, default=True)

    # relação com serviços
    services = db.relationship(
        "Service",
        backref="barber",
        lazy=True
    )

    def __repr__(self):
        return f"<Barber {self.nome}>"
