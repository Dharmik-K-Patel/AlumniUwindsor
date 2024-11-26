from . import db

class Obituary(db.Model):
    __tablename__ = "obituaries"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    university = db.Column(db.String(200), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)  # Nullable
    death_date = db.Column(db.Date, nullable=True)  # Nullable
    obituary_url = db.Column(db.String(500), nullable=False, unique=True)

    def __repr__(self):
        return f"<Obituary {self.full_name}>"
