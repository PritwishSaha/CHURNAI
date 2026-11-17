import logging
import os
from pathlib import Path
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from flask import Flask, redirect, render_template, request, url_for

from flask_sqlalchemy import SQLAlchemy

from config import Config


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

app.logger.setLevel(logging.INFO)

LIMITS = {
    "credit_score": {"min": 350, "max": 850},
    "age": {"min": 18, "max": 92},
    "tenure": {"min": 0, "max": 10},
    "balance": {"min": 0, "max": None},
    "products": {"min": 1, "max": 4},
    "salary": {"min": 0, "max": 250_000},
}


# =========================================================
# DATABASE MODEL
# =========================================================

class PredictionHistory(db.Model):

    __tablename__ = "prediction_history"

    id = db.Column(db.Integer, primary_key=True)

    geography = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    tenure = db.Column(db.Integer, nullable=False)

    balance = db.Column(db.Float, nullable=False)
    products = db.Column(db.Integer, nullable=False)

    has_card = db.Column(db.Integer, nullable=False)
    active_member = db.Column(db.Integer, nullable=False)

    salary = db.Column(db.Float, nullable=False)

    churn_probability = db.Column(db.Float, nullable=False)

    prediction = db.Column(db.String(50), nullable=False)
    risk_category = db.Column(db.String(30), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# =========================================================
# LOAD MACHINE LEARNING MODEL
# =========================================================

MODEL_PATH = Path(app.config["MODEL_PATH"])

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model bundle not found: {MODEL_PATH}"
    )

try:

    deployment_bundle = joblib.load(MODEL_PATH)

    pipeline = deployment_bundle["pipeline"]

    THRESHOLD = float(
        deployment_bundle["threshold"]
    )

    LOW_RISK_THRESHOLD = float(
        deployment_bundle["risk_thresholds"]["low"]
    )

    EXPECTED_FEATURES = deployment_bundle["input_features"]

    MODEL_NAME = deployment_bundle.get(
        "model_name",
        "XGBoost"
    )

    print("\n====================================")
    print("MACHINE LEARNING MODEL LOADED")
    print("====================================")
    print("Model:", MODEL_NAME)
    print("Threshold:", THRESHOLD)
    print("Expected features:", len(EXPECTED_FEATURES))
    print("Model path:", MODEL_PATH)
    print("====================================\n")

except Exception:

    app.logger.exception("Failed to load machine learning model")
    raise


@app.context_processor
def template_context():
    low_pct = LOW_RISK_THRESHOLD * 100
    threshold_pct = THRESHOLD * 100
    maker_name = os.environ.get("MAKER_NAME", "ChurnAI Project Team")

    return {
        "limits": LIMITS,
        "low_pct": low_pct,
        "threshold_pct": threshold_pct,
        "samples": (
            low_pct / 2,
            (low_pct + threshold_pct) / 2,
            (threshold_pct + 100) / 2,
        ),
        "maker": {
            "name": maker_name,
            "role": os.environ.get("MAKER_ROLE", "Customer analytics project"),
            "initials": "".join(part[0] for part in maker_name.split()[:2]).upper(),
        },
        "maker_photo": None,
    }


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def create_features(customer):

    df = pd.DataFrame([customer])

    # Age group
    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=[
            "Young",
            "Adult",
            "Middle_Aged",
            "Senior",
            "Elderly"
        ]
    )

    # Balance status
    df["BalanceStatus"] = np.where(
        df["Balance"] == 0,
        "Zero_Balance",
        "Has_Balance"
    )

    # Customer activity
    df["CustomerActivity"] = np.where(
        df["IsActiveMember"] == 1,
        "Active",
        "Inactive"
    )

    # Product category
    product_mapping = {
        1: "Single_Product",
        2: "Two_Products",
        3: "Multiple_Products",
        4: "Multiple_Products"
    }

    df["ProductCategory"] = df[
        "NumOfProducts"
    ].map(product_mapping)

    # Check expected model features
    missing_features = [
        feature
        for feature in EXPECTED_FEATURES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    # Maintain exact training feature order
    df = df[EXPECTED_FEATURES]

    return df


# =========================================================
# CUSTOMER INPUT VALIDATION
# =========================================================

def validate_customer(customer):

    errors = []

    if not LIMITS["credit_score"]["min"] <= customer["CreditScore"] <= LIMITS["credit_score"]["max"]:
        errors.append("Credit Score must be between 350 and 850.")

    if customer["Geography"] not in [
        "France",
        "Germany",
        "Spain"
    ]:
        errors.append("Invalid Geography selected.")

    if customer["Gender"] not in [
        "Male",
        "Female"
    ]:
        errors.append("Invalid Gender selected.")

    if not LIMITS["age"]["min"] <= customer["Age"] <= LIMITS["age"]["max"]:
        errors.append("Age must be between 18 and 92.")

    if not LIMITS["tenure"]["min"] <= customer["Tenure"] <= LIMITS["tenure"]["max"]:
        errors.append("Tenure must be between 0 and 10.")

    if customer["Balance"] < LIMITS["balance"]["min"]:
        errors.append("Balance cannot be negative.")

    if not LIMITS["products"]["min"] <= customer["NumOfProducts"] <= LIMITS["products"]["max"]:
        errors.append("Number of products must be between 1 and 4.")

    if customer["HasCrCard"] not in [0, 1]:
        errors.append("Invalid credit card selection.")

    if customer["IsActiveMember"] not in [0, 1]:
        errors.append("Invalid active member selection.")

    if not LIMITS["salary"]["min"] <= customer["EstimatedSalary"] <= LIMITS["salary"]["max"]:
        errors.append("Estimated Salary must be between 0 and 250000.")

    return errors


# =========================================================
# RISK CLASSIFICATION
# =========================================================

def classify_risk(probability):

    if probability < LOW_RISK_THRESHOLD:
        return "Low Risk"

    elif probability < THRESHOLD:
        return "Medium Risk"

    else:
        return "High Risk"


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    total_predictions = PredictionHistory.query.count()

    high_risk_count = PredictionHistory.query.filter_by(
        risk_category="High Risk"
    ).count()

    return render_template(
        "index.html",
        total_predictions=total_predictions,
        high_risk_count=high_risk_count
    )


def render_predict(errors=None, form=None):
    return render_template(
        "predict.html",
        errors=errors or [],
        form=form or {},
        error_title="Check these details and try again",
    )


# =========================================================
# CUSTOMER CHURN PREDICTION
# =========================================================

@app.route("/predict", methods=["GET", "POST"])
def predict():

    if request.method == "GET":
        return render_predict()

    form = request.form.to_dict()
    required_fields = (
        "credit_score", "geography", "gender", "age", "tenure",
        "balance", "products", "has_card", "active_member", "salary",
    )
    missing_fields = [field for field in required_fields if not form.get(field)]
    if missing_fields:
        return render_predict(
            [f"Complete all required fields. Missing: {', '.join(missing_fields)}."],
            form,
        ), 400

    try:
        customer = {
            "CreditScore": int(request.form["credit_score"]),
            "Geography": request.form["geography"].strip(),
            "Gender": request.form["gender"].strip(),
            "Age": int(request.form["age"]),
            "Tenure": int(request.form["tenure"]),
            "Balance": float(request.form["balance"]),
            "NumOfProducts": int(request.form["products"]),
            "HasCrCard": int(request.form["has_card"]),
            "IsActiveMember": int(request.form["active_member"]),
            "EstimatedSalary": float(request.form["salary"]),
        }

        numeric_values = [
            customer["CreditScore"],
            customer["Age"],
            customer["Tenure"],
            customer["Balance"],
            customer["NumOfProducts"],
            customer["HasCrCard"],
            customer["IsActiveMember"],
            customer["EstimatedSalary"]
        ]

        if not all(np.isfinite(value) for value in numeric_values):
            raise ValueError("Numeric values must be finite.")

        errors = validate_customer(customer)
        if errors:
            return render_predict(errors, form), 400

        input_df = create_features(customer)
        probabilities = pipeline.predict_proba(input_df)
        probability = float(probabilities[0][1])
        if not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("The model returned an invalid probability.")

        prediction = (
            "Churn Risk"
            if probability >= THRESHOLD
            else "Likely to Stay"
        )
        risk_category = classify_risk(probability)
        record = PredictionHistory(
            geography=customer["Geography"],
            gender=customer["Gender"],
            age=customer["Age"],
            credit_score=customer["CreditScore"],
            tenure=customer["Tenure"],
            balance=customer["Balance"],
            products=customer["NumOfProducts"],
            has_card=customer["HasCrCard"],
            active_member=customer["IsActiveMember"],
            salary=customer["EstimatedSalary"],
            churn_probability=probability * 100,
            prediction=prediction,
            risk_category=risk_category,
        )

        db.session.add(record)
        db.session.commit()
        return redirect(url_for("result", record_id=record.id))

    except (ValueError, KeyError) as error:

        db.session.rollback()
        app.logger.info("Invalid prediction input: %s", error)
        return render_predict([f"Input error: {error}"], form), 400

    except Exception as error:

        db.session.rollback()
        app.logger.exception("Prediction failed")
        return render_predict([f"Prediction error: {error}"], form), 500


# =========================================================
# PREDICTION HISTORY
# =========================================================

@app.route("/history")
def history():
    risk = request.args.get("risk", "all")
    if risk not in {"all", "high", "medium", "low"}:
        risk = "all"

    risk_categories = {
        "high": "High Risk",
        "medium": "Medium Risk",
        "low": "Low Risk",
    }

    filter_counts = {"all": PredictionHistory.query.count()}
    for key, category in risk_categories.items():
        filter_counts[key] = PredictionHistory.query.filter_by(
            risk_category=category
        ).count()

    records_query = PredictionHistory.query.order_by(
        PredictionHistory.id.desc()
    )
    if risk != "all":
        records_query = records_query.filter_by(
            risk_category=risk_categories[risk]
        )

    pagination = records_query.paginate(
        page=request.args.get("page", 1, type=int),
        per_page=20,
        error_out=False,
    )

    return render_template(
        "history.html",
        records=pagination.items,
        pagination=pagination,
        filter_counts=filter_counts,
        risk=risk,
    )


@app.route("/result/<int:record_id>")
def result(record_id):
    record = db.get_or_404(PredictionHistory, record_id)
    customer = {
        "Geography": record.geography,
        "Gender": record.gender,
        "Age": record.age,
        "CreditScore": record.credit_score,
        "Tenure": record.tenure,
        "Balance": record.balance,
        "NumOfProducts": record.products,
        "HasCrCard": record.has_card,
        "IsActiveMember": record.active_member,
        "EstimatedSalary": record.salary,
    }
    return render_template("result.html", record=record, customer=customer)


# =========================================================
# ANALYTICS DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    records = PredictionHistory.query.all()
    total = len(records)
    risk_groups = (
        ("low", "Low Risk"),
        ("medium", "Medium Risk"),
        ("high", "High Risk"),
    )
    risk_mix = []

    for key, label in risk_groups:
        count = sum(record.risk_category == label for record in records)
        risk_mix.append({
            "key": key,
            "label": label,
            "count": count,
            "share": round(count / total * 100, 1) if total else 0,
        })

    average = (
        round(sum(record.churn_probability for record in records) / total, 2)
        if total else 0
    )

    geo_stats = []
    for geography in ("France", "Germany", "Spain"):
        geo_records = [
            record for record in records
            if record.geography == geography
        ]
        if not geo_records:
            continue
        geo_average = round(
            sum(record.churn_probability for record in geo_records) / len(geo_records),
            1,
        )
        geo_stats.append({
            "name": geography,
            "count": len(geo_records),
            "average": geo_average,
            "zone": classify_risk(geo_average / 100).split()[0].lower(),
        })

    return render_template(
        "dashboard.html",
        total=total,
        flagged=sum(record.prediction == "Churn Risk" for record in records),
        risk_mix=risk_mix,
        average=average,
        geo_stats=geo_stats,
        recent=records[:5],
    )


# =========================================================
# ABOUT PAGE
# =========================================================

@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(_error):
    del _error
    return render_template(
        "error.html",
        code=404,
        title="Page not found",
        message="The page or prediction you requested could not be found.",
    ), 404


@app.errorhandler(500)
def internal_server_error(_error):
    del _error
    db.session.rollback()
    return render_template(
        "error.html",
        code=500,
        title="Something went wrong",
        message="The request could not be completed. Please try again.",
    ), 500


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()

    print("Database initialized successfully.")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
    )