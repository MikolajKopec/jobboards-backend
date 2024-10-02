from flask import request, jsonify, Blueprint
from flask.views import MethodView
from marshmallow import ValidationError
from app.models import Job, Company, db
from app.utils.decorators import login_required
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from app.utils.enums import JobTypeEnum, ContractEnum, ExperienceEnum, WorkModeEnum

# Utworzenie namespace dla ofert pracy
bp = Blueprint("job", __name__, url_prefix="/jobs")


class JobListAPI(MethodView):
    decorators = [login_required]

    def get(self):
        # Get a list of jobs with pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 50)

        pagination = Job.query.paginate(page=page, per_page=per_page, error_out=False)
        jobs = pagination.items

        job_schema = JobSchema(many=True)
        result = job_schema.dump(jobs)

        return (
            jsonify(
                {
                    "jobs": result,
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                    "next_page": pagination.next_num,
                    "prev_page": pagination.prev_num,
                }
            ),
            200,
        )

    def post(self):
        # Create a new job
        data = request.get_json()
        job_schema = JobSchema()
        try:
            job_data = job_schema.load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        # Verify that the user is associated with the company
        company_id = job_data.get("company_id")
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"message": "Company not found"}), 404

        if company not in request.user.companies:
            return jsonify({"message": "Unauthorized to add job to this company"}), 403

        new_job = Job(**job_data)
        db.session.add(new_job)
        db.session.commit()

        result = job_schema.dump(new_job)
        return jsonify(result), 201


class JobDetailAPI(MethodView):
    decorators = [login_required]

    def get(self, job_id):
        job = Job.query.get_or_404(job_id)
        job_schema = JobSchema()
        result = job_schema.dump(job)
        return jsonify(result), 200

    def put(self, job_id):
        # Update a job
        job = Job.query.get_or_404(job_id)

        # Verify that the user is authorized to update this job
        if job.company not in request.user.companies:
            return jsonify({"message": "Unauthorized to update this job"}), 403

        data = request.get_json()
        job_schema = JobSchema(partial=True)
        try:
            job_data = job_schema.load(data, partial=True)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        for key, value in job_data.items():
            setattr(job, key, value)

        db.session.commit()
        result = job_schema.dump(job)
        return jsonify(result), 200

    def delete(self, job_id):
        # Delete a job
        job = Job.query.get_or_404(job_id)

        # Verify that the user is authorized to delete this job
        if job.company not in request.user.companies:
            return jsonify({"message": "Unauthorized to delete this job"}), 403

        db.session.delete(job)
        db.session.commit()
        return jsonify({"message": "Job deleted"}), 200


class JobListAPIPublic(MethodView):

    def get(self, job_id):
        job = Job.query.get_or_404(job_id)
        job_schema = JobSchema()
        result = job_schema.dump(job)
        return jsonify(result), 200


class JobSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    salary_min = fields.Int()
    salary_max = fields.Int()
    contract_type = fields.List(EnumField(ContractEnum), required=True)
    work_mode = fields.List(EnumField(WorkModeEnum), required=True)
    experience_level = fields.List(EnumField(ExperienceEnum))
    job_type = fields.List(EnumField(JobTypeEnum), required=True)
    description = fields.Str(required=True)
    requirements = fields.Dict()
    location = fields.List(fields.Str())
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    company_id = fields.Int(required=True)

    company = fields.Nested("CompanySchema", only=("id", "name"), dump_only=True)


job_list_view = JobListAPI.as_view("job_list_api")
job_list_view_public = JobListAPIPublic.as_view("job_list_api_public")
job_detail_view = JobDetailAPI.as_view("job_detail_api")

bp.add_url_rule("/public/", view_func=job_list_view, methods=["GET", "POST"])
bp.add_url_rule("/", view_func=job_list_view, methods=["GET", "POST"])
bp.add_url_rule(
    "/<int:job_id>", view_func=job_detail_view, methods=["GET", "PUT", "DELETE"]
)
