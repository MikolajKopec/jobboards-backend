from functools import wraps
from flask import request, jsonify, current_app, session
import requests
from authlib.jose import JsonWebKey
from authlib.jose import jwt, JoseError
from app.models import db, User


# Pobierz klucze publiczne Google
def get_google_public_keys():
    resp = requests.get("https://www.googleapis.com/oauth2/v3/certs")
    jwk_set = resp.json()
    return JsonWebKey.import_key_set(jwk_set)


def verify_id_token(id_token):
    try:
        # Pobierz klucze publiczne
        public_keys = get_google_public_keys()
        client_id = current_app.config["GOOGLE_CLIENT_ID"]
        # Zdefiniuj wymagane opcje weryfikacji
        claims_options = {
            "iss": {
                "essential": True,
                "values": ["accounts.google.com", "https://accounts.google.com"],
            },
            "aud": {"essential": True, "values": [client_id]},
            "exp": {"essential": True},
            "iat": {"essential": True},
            "nbf": {"essential": False},
            "sub": {"essential": True},
        }

        # Zdekoduj i zweryfikuj token
        claims = jwt.decode(id_token, key=public_keys, claims_options=claims_options)
        # Zweryfikuj standardowe atrybuty (exp, iat, etc.)
        claims.validate()

        return claims
    except JoseError as e:
        print(f"Błąd weryfikacji tokena: {e}")
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(request.cookies)
        token = (
            request.headers["Authorization"]
            if "Authorization" in request.headers
            else session.get("token")
        )
        if not token:
            return (
                jsonify({"message": "Brak lub nieprawidłowy nagłówek Authorization"}),
                401,
            )
        claims = verify_id_token(token)
        if not claims:
            return jsonify({"message": "Nieprawidłowy lub przeterminowany token"}), 401

        google_id = claims.get("sub")
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            user = User(
                email=claims.get("email"), google_id=google_id, name=claims.get("name")
            )
            db.session.add(user)
            db.session.commit()

        request.user = user
        return f(*args, **kwargs)

    return decorated_function
