from flask import Flask, Response, jsonify, request
from flask.views import MethodView
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from models import Ads, User, Session
from schema import UserCreate, AdsCreate, UpdateAds


app = Flask("rest-api")
app.config["JWT_SECRET_KEY"] = "dhs7e8fy8s7ef6y78seyf78esfy"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)


def hash_password(password: str):
    password = password.encode()
    password = bcrypt.generate_password_hash(password)
    password = password.decode()
    return password

def check_password(user_password: str, db_password: str):
    user_password = user_password.encode()
    db_password = db_password.encode()
    return bcrypt.check_password_hash(db_password, user_password)

@app.before_request
def before_request():
    session = Session()
    request.session = session
    pass

@app.after_request
def after_requests(http_response: Response):
    request.session.close()
    return http_response

class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

@app.errorhandler(HttpError)
def error_handler(error):
    http_response = jsonify({"error": error.message})
    http_response.status_code = error.status_code
    return http_response

def validate(json_data, schema_cls):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)

def get_user(user_id: int):
    user = request.session.get(User, user_id)
    if user is None:
        raise HttpError(404, "User not found")
    return user

def get_ads(ads_id: int):
    ads = request.session.get(Ads, ads_id)
    if ads is None:
        raise HttpError(404, "Advertisement not found")
    return ads

def post_ads(ads):
    request.session.add(ads)
    request.session.commit()
    return ads

def login():
    json_data = request.json
    user = get_user(json_data["id"])
    if check_password(json_data["password"], user.password):
        token = create_access_token(identity=user.id)
        return jsonify({"token": token})
    raise HttpError(401, "Invalid credentials")

class UserView(MethodView):
    def get(self, user_id: int):
        user = get_user(user_id)
        return jsonify(user.json)

    def post(self):
        json_data = validate(request.json, UserCreate)
        user = User(
            name=json_data["name"],
            email=json_data["email"],
            password=hash_password(json_data["password"]),
        )
        try:
            request.session.add(user)
            request.session.commit()
        except IntegrityError:
            raise HttpError(409, "User already exists")
        return jsonify({"msg": "User created successfully", "id": user.id})


class AdsView(MethodView):
    def get(self, ads_id: int = None):
        ads = get_ads(ads_id)
        return jsonify(ads.json)
        
    @jwt_required()
    def post(self):
        json_data = validate(request.json, AdsCreate)
        author_id = get_jwt_identity()
        ads = post_ads(Ads(
            title=json_data["title"],
            description=json_data["description"],
            author_id=author_id
        ))
        return jsonify(ads.json)

    @jwt_required()
    def patch(self, ads_id: int):
        json_data = validate(request.json, UpdateAds)
        author_id = get_jwt_identity()
        ads = get_ads(ads_id)
        if ads.author_id != author_id:
            raise HttpError(403, "Permission denied")
        for field, value in json_data.items():
            setattr(ads, field, value)
        ads = post_ads(ads)
        return jsonify(ads.json)

    @jwt_required()
    def delete(self, ads_id: int):
        ads = get_ads(ads_id)
        author_id = get_jwt_identity()
        if ads.author_id != author_id:
            raise HttpError(403, "Permission denied")
        request.session.delete(ads)
        request.session.commit()
        return jsonify({"status": "deleted"})

ads_view = AdsView.as_view("ads")
user_view = UserView.as_view("user")

app.add_url_rule("/api/ads", methods=["POST"], view_func=ads_view)
app.add_url_rule("/api/ads/<int:ads_id>", methods=["GET", "PATCH", "DELETE"], view_func=ads_view)
app.add_url_rule("/api/register", methods=["POST"], view_func=user_view)
app.add_url_rule("/api/login", methods=["POST"], view_func=login)
app.add_url_rule("/api/users/<int:user_id>", methods=["GET"], view_func=user_view)

if __name__ == "__main__":
    app.run(debug=True)
