from flask import url_for, Blueprint, session, redirect, current_app
from app import oauth  # Korzystaj z globalnie zainicjalizowanego OAuth

# Tworzenie namespace dla logowania
bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET"])
def login():
    redirect_uri = url_for("auth.callback", _external=True)
    google = oauth.create_client("google")
    return google.authorize_redirect(redirect_uri)


@bp.route("/callback", methods=["GET"])
def callback():
    token = oauth.google.authorize_access_token()
    jwt_token = token.get("id_token")
    print(jwt_token)
    if jwt_token:
        session["token"] = jwt_token
        return redirect(
            current_app.config["FRONTEND_URL"],
            Response={"message": "Logowanie powiodło się", "token": jwt_token},
            code=200,
        )

    else:
        return {"message": "Błąd logowania"}, 400


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return {"message": "logged out"}, 200


@bp.route("/user_info", methods=["GET"])
def user_info():
    if "user" not in session:
        return {"message": "user not logged in"}, 401

    return session["user"], 200
