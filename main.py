from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random as rd
import requests

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


def make_bool(val: int) -> bool:
    """
    Takes in a numeric value and converts to boolean

    :param val: Expecting number
    :return: Boolean
    """
    return bool(int(val))


@app.route('/')
def home():
    return render_template('index.html')


## HTTP GET - Read Record

@app.route('/random', methods=['GET'])
def random_cafe():
    cafe = rd.choice(db.session.query(Cafe).all())
    result = vars(cafe)
    result.pop('_sa_instance_state')
    return jsonify(result)


@app.route('/all', methods=['GET'])
def all_cafes():
    all_records = db.session.query(Cafe).all()
    all_cafes_list = []
    for i in all_records:
        record = vars(i)
        record.pop('_sa_instance_state')
        all_cafes_list.append(record)
    return jsonify(all_cafes_list)


@app.route('/search', methods=['GET'])
def search_cafes_by_location():
    loc = request.url.split('=')[1]
    if '%20' in loc:
        loc = loc.replace('%20', ' ')
    records_by_loc = Cafe.query.filter_by(location=loc).all()
    list_records_by_loc = []
    for i in records_by_loc:
        temp = vars(i)
        temp.pop('_sa_instance_state')
        list_records_by_loc.append(temp)
    if not records_by_loc:
        return jsonify({'error': {'Not found': 'Sorry we do not have such cafe'}})
    return jsonify(list_records_by_loc)


## HTTP POST - Create Record

@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=make_bool(int(request.form.get("has_toilet"))),
        has_wifi=make_bool(int(request.form.get("has_wifi"))),
        has_sockets=make_bool(int(request.form.get("has_sockets"))),
        can_take_calls=make_bool(int(request.form.get("can_take_calls"))),
        coffee_price=request.form.get("coffee_price"))

    db.session.add(new_cafe)
    db.session.commit()
    response = {"Success": "Successfully added the new cafe."}
    return jsonify(response)


## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', methods=['GET', 'PATCH'])
def update_price(cafe_id):
    query_price = request.args.get("new_price")
    cafe_price_to_update_record = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_price_to_update_record:
        cafe_price_to_update_record.coffee_price = query_price
        db.session.commit()
        success_response = {"Success": "Successfully updated the price."}
        return jsonify(success_response)
    return jsonify({"Not Found": "Sorry cafe with such id is not in DB"})


## HTTP DELETE - Delete Record

@app.route('/report-closed/<int:cafe_id>', methods=['GET', 'DELETE'])
def delete(cafe_id):
    query_api_key = request.args.get('api-key')
    cafe_to_delete = Cafe.query.get(cafe_id)
    if not cafe_to_delete:
        return jsonify({"Not Found": "Sorry cafe with such id is not in DB"})
    if query_api_key=='TopSecretAPIKey':
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify({"Success": "Successfully removed a cafe."})
    else:
        return jsonify({"Error": "That's not allowed. Make sure that you've provided the correct apy key"})


if __name__=='__main__':
    app.run(debug=True)
