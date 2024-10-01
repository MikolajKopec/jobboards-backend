# api/company.py

from flask import Blueprint, request, jsonify, abort
from flask.views import MethodView
from marshmallow import Schema, fields, ValidationError
from app.models import (
    Company,
    db,
)
from app.utils.decorators import (
    login_required,
)
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint("company", __name__, url_prefix="/company")


class CompanySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    logo_url = fields.Url(allow_none=True)


company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)


class CompanyListAPI(MethodView):
    decorators = [login_required]

    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 50)

        pagination = Company.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        companies = pagination.items

        result = companies_schema.dump(companies)
        return (
            jsonify(
                {
                    "companies": result,
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
        try:
            data = request.get_json()
            company_data = company_schema.load(data)
            new_company = Company(**company_data)
            request.user.companies.append(new_company)

            db.session.add(new_company)
            db.session.commit()

            result = company_schema.dump(new_company)
            return jsonify(result), 201

        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": "Database error", "error": str(e)}), 500


class CompanyDetailAPI(MethodView):
    decorators = [login_required]

    def get(self, company_id):
        company = Company.query.get_or_404(company_id)
        result = company_schema.dump(company)
        return jsonify(result), 200

    def put(self, company_id):
        company = Company.query.get_or_404(company_id)
        if company not in request.user.companies:
            return jsonify({"message": "Unauthorized access"}), 403

        try:
            data = request.get_json()
            company_data = company_schema.load(data, partial=True)

            for key, value in company_data.items():
                setattr(company, key, value)

            db.session.commit()
            result = company_schema.dump(company)
            return jsonify(result), 200

        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": "Database error", "error": str(e)}), 500

    def delete(self, company_id):
        company = Company.query.get_or_404(company_id)
        if company not in request.user.companies:
            return jsonify({"message": "Unauthorized access"}), 403

        try:
            db.session.delete(company)
            db.session.commit()
            return jsonify({"message": "Company deleted"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": "Database error", "error": str(e)}), 500


company_list_view = CompanyListAPI.as_view("company_list_api")
company_detail_view = CompanyDetailAPI.as_view("company_detail_api")

bp.add_url_rule("/", view_func=company_list_view, methods=["GET", "POST"])
bp.add_url_rule(
    "/<int:company_id>", view_func=company_detail_view, methods=["GET", "PUT", "DELETE"]
)
