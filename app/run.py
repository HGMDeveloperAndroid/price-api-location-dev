# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os

from flask import abort, jsonify, Flask, make_response, request

from flask_cors import CORS, cross_origin

from flask_marshmallow import Marshmallow

from flask_sqlalchemy import SQLAlchemy

from app.utils import apikey_required

app = Flask(__name__)
cors = CORS(
    app,
    resources={
        r"/*": {
            "origins": os.environ.get("CORS_ORIGIN_WHITELIST", "*").split(",")
        }
    },
    methods='GET, HEAD, POST, OPTIONS, PATCH, DELETE',
)
app.config['CORS_HEADERS'] = '*'
# Mysql database
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI', 'mysql+pymysql://root:wendy@127.0.0.1:3306/3b'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Import models
from app.models import Place  # noqa


@app.route("/api/scans", methods=['GET'])
@cross_origin()
@apikey_required
def localize():
    required_args = (
        'point1',
        'point2',
        'point3',
        'point4',
    )

    for arg in required_args:
        if arg not in request.args:
            abort(
                make_response(
                    jsonify(message='Param {} expected'.format(arg)), 400
                )
            )

        if not request.args[arg]:
            abort(
                make_response(
                    jsonify(
                        message='Param {} expected a value'.format(arg)
                    ),
                    400
                )
            )

    # Filter coordinates
    p1_y, p1_x = map(float, request.args.get('point1').split(','))
    p2_y, p2_x = map(float, request.args.get('point2').split(','))
    p3_y, p3_x = map(float, request.args.get('point3').split(','))
    p4_y, p4_x = map(float, request.args.get('point4').split(','))
    min_y = p3_y if p4_y > p3_y else p4_y
    max_y = p2_y if p2_y > p1_y else p1_y
    min_x = p3_x if p1_x > p3_x else p1_x
    max_x = p2_x if p2_x > p4_x else p4_x
    # Set order
    order = 'DESC'

    if request.args.get('order') in ['asc', 'desc']:
        order = request.args.get('order').upper()

    # Filter dates
    where_date = ""
    format = "%Y-%m-%d"

    if 'range' in request.args and request.args['range']:
        start_date, end_date = request.args.get('range').split(',')

        try:
            datetime.strptime(start_date, format)
            datetime.strptime(end_date, format)
        except ValueError as e:
            abort(
                make_response(
                    jsonify(message='Format for dates must be YYYY-MM-DD'),
                    400
                )
            )

        where_date = "AND scans.capture_date BETWEEN '{0}' AND '{1}' ".format(
            start_date, end_date
        )
    elif "date" in request.args and request.args["date"]:
        date = request.args.get("date")

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            abort(
                make_response(
                    jsonify(message="Format for date must be YYYY-MM-DD"),
                    400
                )
            )

        where_date = "AND DATE(scans.capture_date) = '{0}'".format(date)

    #
    # Filters
    #
    filter_status = ""
    if "status" in request.args and request.args["status"]:
        if request.args["status"] == "validated":
            filter_status = "AND scans.is_valid = 1 AND scans.is_rejected = 0"
        elif request.args["status"] == "rejected":
            filter_status = "AND scans.is_valid = 0 AND scans.is_rejected = 1"
        elif request.args["status"] == "pending":
            filter_status = "AND scans.is_valid = 0 AND scans.is_rejected = 0 AND scans.is_locked = 0"

    filter_photo = ""
    if "photo" in request.args and request.args["photo"]:
        if request.args["photo"] == "yes":
            filter_photo = "AND EXISTS (SELECT id FROM scan_pictures WHERE id_scan = scans.id)"
        elif request.args["photo"] == "no":
            filter_photo = "AND NOT EXISTS (SELECT id FROM scan_pictures WHERE id_scan = scans.id)"

    filter_price = ""
    if "price" in request.args and request.args["price"]:
        if request.args["price"] == "normal":
            filter_price = "AND scans.special_price = 0"
        elif request.args["price"] == "special":
            filter_price = "AND scans.special_price = 1"

    filter_brandtype = ""
    if "brandtype" in request.args and request.args["brandtype"]:
        if request.args["brandtype"] in ("mc", "mp"):
            filter_brandtype = "AND products.type = '{0}'".format(
                request.args.get("brandtype").upper()
            )

    filter_brands = ""
    if "brands" in request.args and request.args["brands"]:
        brands = ""
        for brand in request.args.get("brands").split(","):
            brands += "'{}',".format(brand.strip())
        filter_brands = "AND brands.name IN ({0})".format(brands[:-1])

    filter_groups = ""
    if "groups" in request.args and request.args["groups"]:
        groups = ""
        for group in request.args.get("groups").split(","):
            groups += "'{}',".format(group.strip())
        filter_groups = "AND groups.name IN ({0})".format(groups[:-1])

    filter_lines = ""
    if "lines" in request.args and request.args["lines"]:
        lines = ""
        for line in request.args.get("lines").split(","):
            lines += "'{}',".format(line.strip())
        filter_lines = "AND `lines`.name IN ({0})".format(lines[:-1])

    filter_stores = ""
    if "stores" in request.args and request.args["stores"]:
        stores = ""
        for store in request.args.get("stores").split(","):
            stores += "'{}',".format(store.strip())
        filter_stores = "AND stores.name IN ({0})".format(stores[:-1])

    filter_units = ""
    if "units" in request.args and request.args["units"]:
        units = ""
        for unit in request.args.get("units").split(","):
            units += "'{}',".format(unit.strip())
        filter_units = "AND units.name IN ({0})".format(units[:-1])

    filter_search = ""
    if "search" in request.args and request.args["search"]:
        filter_search = "AND products.name like \'%%{0}%%\' OR products.barcode like \'%%{0}%%\'".format(
            request.args.get("search").strip()
        )

    sql = """
    SELECT
    scans.id AS id,
    products.picture_path AS productPhoto,
    scans.barcode AS barcode,
    (SELECT product_picture FROM scan_pictures WHERE id_scan = scans.id) AS productPicture,
    (SELECT shelf_picture FROM scan_pictures WHERE id_scan = scans.id) AS shelfPicture,
    products.barcode AS productBarcode,
    products.name AS productName,
    brands.name AS brandName,
    stores.name AS storeName,
    stores.address AS storeAddress,
    CONVERT(scans.capture_date, CHAR) AS captureDate,
    CONVERT(scans.price, CHAR) AS price,
    CONVERT(CASE WHEN products.unit_quantity <> 0.00 THEN scans.price / products.unit_quantity ELSE 0.000000 END, CHAR) AS unitPrice,
    CONVERT(products.unit_quantity, CHAR) AS productUnitQuantity,
    (SELECT name from zones WHERE id = (SELECT id_zone FROM zone_users WHERE id_user = scans.id_scanned_by LIMIT 1)) AS region,
    scans.comments AS comments,
    products.type AS productType,
    groups.name AS groupName,
    `lines`.name AS lineName,
    CONVERT(products.price, CHAR) AS productPrice,
    CONVERT(products.min_price, CHAR) AS productMinPrice,
    CONVERT(products.max_price, CHAR) AS productMaxPrice,
    scans.is_rejected AS isRejected,
    scans.is_valid AS isValid,
    scans.id_scanned_by AS capturistId,
    (SELECT TRIM(CONCAT(first_name, " ", last_name)) FROM users WHERE id = scans.id_scanned_by) AS capturist,
    (SELECT TRIM(CONCAT(users.first_name, " ", last_name)) FROM users WHERE id = scans.id_reviewed_by) AS validator,
    CONVERT(products.created_at, CHAR) AS productCreation,
    scans.special_price AS specialPrice,
    scans.id_store AS idStore
    FROM scans
    INNER JOIN stores ON stores.id = scans.id_store
    INNER JOIN products ON products.id = scans.id_product
    INNER JOIN brands ON brands.id = products.id_brand
    INNER JOIN units ON units.id = products.id_unit
    INNER JOIN groups ON groups.id = products.id_group
    INNER JOIN `lines` ON `lines`.id = products.id_line
    WHERE ST_Y(stores.location) BETWEEN '{0}' AND '{1}' AND
    ST_X(stores.location) BETWEEN '{2}' AND '{3}' {4}
    {5}
    {6}
    {7}
    {8}
    {9}
    {10}
    {11}
    {12}
    {13}
    {14}
    ORDER BY captureDate {15};
    """.format(
        min_y,
        max_y,
        min_x,
        max_x,
        where_date,
        filter_status,
        filter_photo,
        filter_price,
        filter_brandtype,
        filter_brands,
        filter_groups,
        filter_lines,
        filter_stores,
        filter_units,
        filter_search,
        order
    )
    data = [dict(item) for item in db.engine.execute(sql).fetchall()]
    return make_response({'results': len(data), 'data': data}, 200)


@app.route("/api/places", methods=['GET'])
@cross_origin()
@apikey_required
def places_list():
    from app.schemas import PlaceSchema
    place_schema = PlaceSchema(many=True)
    places = Place.query.order_by("name").all()
    return make_response(
        {'results': len(places), 'data': place_schema.dump(places)}, 200
    )


@app.route("/api/places/<int:pk>", methods=['GET'])
@cross_origin()
@apikey_required
def places_retrieve(pk):
    from app.schemas import PlaceSchema
    place_schema = PlaceSchema()
    place = Place.query.get(pk)

    if not place:
        abort(make_response(jsonify(message=f'{pk} does not exists'), 404))

    return make_response(place_schema.dump(place), 200)


@app.route("/api/places", methods=['POST'])
@cross_origin()
@apikey_required
def places_create():
    from app.schemas import PlaceSchema, PlaceCreateSchema
    data = json.loads(request.data)
    place_schema = PlaceSchema()
    place_create_schema = PlaceCreateSchema()
    errors = place_create_schema.validate(data)

    if errors:
        abort(make_response(jsonify(message=errors), 400))

    p1_x, p1_y = data['point1'].strip().split(',')
    p2_x, p2_y = data['point2'].strip().split(',')
    p3_x, p3_y = data['point3'].strip().split(',')
    p4_x, p4_y = data['point4'].strip().split(',')
    place = Place(
        name=data['name'].strip(),
        p1_x=p1_x, p1_y=p1_y,
        p2_x=p2_x, p2_y=p2_y,
        p3_x=p3_x, p3_y=p3_y,
        p4_x=p4_x, p4_y=p4_y
    )
    # post.image_name = image_name
    place.created_at = datetime.now()
    place.updated_at = datetime.now()
    place.save()
    return make_response(place_schema.dump(place), 201)


@app.route("/api/places/<int:pk>", methods=['PATCH'])
@cross_origin()
@apikey_required
def places_update(pk):
    from app.schemas import PlaceSchema, PlaceCreateSchema

    data = json.loads(request.data)
    place_schema = PlaceSchema()
    place_update_schema = PlaceCreateSchema()
    place = Place.query.get(pk)

    if not place:
        abort(make_response(jsonify(message=f'{pk} does not exists'), 404))

    errors = place_update_schema.validate(data, partial=True)

    if errors:
        abort(make_response(jsonify(message=errors), 400))

    validated_data = {}

    for key, value in data.items():
        validated_data[key] = value.strip()

    if 'name' in validated_data and validated_data['name']:
        place.name = validated_data['name']

    if 'point1' in validated_data and validated_data['point1']:
        place.p1_x, place.p1_y = validated_data['point1'].split(',')

    if 'point2' in validated_data and validated_data['point2']:
        place.p2_x, place.p2_y = validated_data['point2'].split(',')

    if 'point3' in validated_data and validated_data['point3']:
        place.p3_x, place.p3_y = validated_data['point3'].split(',')

    if 'point4' in validated_data and validated_data['point4']:
        place.p4_x, place.p4_y = validated_data['point4'].split(',')

    place.updated_at = datetime.now()
    place.save()
    return make_response(place_schema.dump(place), 200)


@app.route("/api/places/<int:pk>", methods=['DELETE'])
@cross_origin()
@apikey_required
def places_destroy(pk):
    place = Place.query.get(pk)

    if not place:
        abort(make_response(jsonify(message=f'{pk} does not exists'), 404))

    place.delete()
    return make_response({}, 204)
