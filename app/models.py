from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from app.utils.enums import JobTypeEnum, ContractEnum, ExperienceEnum, WorkModeEnum
from sqlalchemy import Enum as SAEnum


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(512), nullable=True)
    jobs = db.relationship("Job", backref="company", lazy=True)

    def __repr__(self):
        return f"<Company {self.name}>"


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    contract_type = db.Column(ARRAY(SAEnum(ContractEnum)), nullable=False)
    work_mode = db.Column(ARRAY(SAEnum(WorkModeEnum)), nullable=False)
    experience_level = db.Column(ARRAY(SAEnum(ExperienceEnum)), nullable=True)
    job_type = db.Column(ARRAY(SAEnum(JobTypeEnum)), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.JSON, nullable=True)
    location = db.Column(ARRAY(db.String), nullable=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    def __repr__(self):
        return f"<Job {self.title}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)  # Google SSO ID
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    companies = db.relationship("Company", secondary="user_company", backref="users")

    def __repr__(self):
        return f"<User {self.email}>"


user_company = db.Table(
    "user_company",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column(
        "company_id", db.Integer, db.ForeignKey("companies.id"), primary_key=True
    ),
)
