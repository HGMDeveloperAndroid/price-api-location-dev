# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validates, ValidationError

from app.run import ma
from app.models import Place


class PlaceSchema(ma.SQLAlchemySchema):
    point1 = fields.Function(lambda obj: '{0},{1}'.format(obj.p1_x, obj.p1_y))
    point2 = fields.Function(lambda obj: '{0},{1}'.format(obj.p2_x, obj.p2_y))
    point3 = fields.Function(lambda obj: '{0},{1}'.format(obj.p3_x, obj.p3_y))
    point4 = fields.Function(lambda obj: '{0},{1}'.format(obj.p4_x, obj.p4_y))

    class Meta:
        model = Place
        fields = (
            'id',
            'name',
            'point1',
            'point2',
            'point3',
            'point4',
            'created_at',
            'updated_at'
        )


class PlaceCreateSchema(Schema):
    name = fields.Str(required=True)
    point1 = fields.Str(required=True)
    point2 = fields.Str(required=True)
    point3 = fields.Str(required=True)
    point4 = fields.Str(required=True)

    @validates('point1')
    def required_coordinates_p1(self, value):
        try:
            x, y = value.split(",")
            float(x)
            float(y)
        except ValueError:
            raise ValidationError("The values for point1 was wrong")

    @validates('point2')
    def required_coordinates_p2(self, value):
        try:
            x, y = value.split(",")
            float(x)
            float(y)
        except ValueError:
            raise ValidationError("The values for point2 was wrong")

    @validates('point3')
    def required_coordinates_p3(self, value):
        try:
            x, y = value.split(",")
            float(x)
            float(y)
        except ValueError:
            raise ValidationError("The values for point3 was wrong")

    @validates('point4')
    def required_coordinates_p4(self, value):
        try:
            x, y = value.split(",")
            float(x)
            float(y)
        except ValueError:
            raise ValidationError("The values for point4 was wrong")
