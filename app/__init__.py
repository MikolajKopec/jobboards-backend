from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from datetime import datetime

db = SQLAlchemy()
oauth = OAuth()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": f"{app.config['FRONTEND_URL']}"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE"],
    )
    oauth.init_app(app)
    oauth.register(
        name="google",
        state="222",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email"},
    )

    db.init_app(app)

    # Rejestracja API i blueprintów

    from .api.company import bp as company_bp
    from .api.auth import bp as auth_bp
    from .api.job import bp as job_bp

    app.register_blueprint(company_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(auth_bp)

    from .models import (
        Company,
        Job,
        user_company,
        User,
    )
    from .utils.enums import ExperienceEnum, JobTypeEnum, ContractEnum, WorkModeEnum

    with app.app_context():
        db.drop_all()
        db.create_all()
        company = Company()
        company.name = "Coflow"
        company.description = "Best IT Company."
        db.session.add(company)
        job = Job()
        job.title = "Python Developer"
        job.salary_min = 10000
        job.salary_max = 15000
        job.contract_type = ["B2B"]
        job.work_mode = ["Remote"]
        job.experience_level = ["Mid"]
        job.job_type = ["Full-time"]
        job.description = (
            "We are looking for an experienced Python Developer to join our team."
        )
        job.requirements = {"skills": ["Python", "Flask", "SQLAlchemy"]}
        job.location = ["Warsaw", "Remote"]
        job.start_date = datetime.utcnow()
        job.end_date = None  # Oferta bez określonej daty zakończenia
        job.company_id = company.id  # Powiązanie oferty pracy z firmą

        db.session.add(job)
        db.session.commit()  # Zapisanie zmiany w bazie
    return app
