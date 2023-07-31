# -*- coding: utf-8 -*-
from app.run import db


class Place(db.Model):
    __tablename__ = 'geo_places'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    p1_x = db.Column(db.Numeric(11, 8), nullable=False)
    p1_y = db.Column(db.Numeric(11, 8), nullable=False)
    p2_x = db.Column(db.Numeric(11, 8), nullable=False)
    p2_y = db.Column(db.Numeric(11, 8), nullable=False)
    p3_x = db.Column(db.Numeric(11, 8), nullable=False)
    p3_y = db.Column(db.Numeric(11, 8), nullable=False)
    p4_x = db.Column(db.Numeric(11, 8), nullable=False)
    p4_y = db.Column(db.Numeric(11, 8), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now()
    )

    def __repr__(self):
        return f'<Place {self.name}>'

    def save(self):
        if not self.id:
            db.session.add(self)

        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Place.query.get(id)
