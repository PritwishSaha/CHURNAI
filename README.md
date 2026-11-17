<div align="center">

# 🧡 CHURNAI
### Customer Churn Prediction System

**Predict customer churn. Identify at-risk customers. Make smarter retention decisions.**

An end-to-end Machine Learning web application powered by XGBoost that predicts customer churn probability and categorizes customers into actionable risk levels.

<br>

[🚀 Live Demo](https://churn-ai-o48x.onrender.com/) · [💻 GitHub Repository](https://github.com/PritwishSaha/CHURNAI)

<br>

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?style=for-the-badge&logo=flask&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-XGBoost-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-See%20LICENSE-blue?style=for-the-badge)

</div>

---

## 📌 Overview

Customer churn is one of the major challenges faced by banks and financial institutions. Losing existing customers can affect revenue, customer relationships, and long-term business growth.

**CHURNAI** is a machine learning-based customer churn prediction platform designed to help identify customers who are likely to leave a banking service.

The application takes customer information as input, processes it through a trained XGBoost classification pipeline, and generates:

- Customer churn probability.
- Predicted churn classification.
- Low, Medium, or High risk categorization.
- Customer prediction history.
- Analytical dashboard for monitoring prediction activity.

The objective is to transform customer data into meaningful insights that support proactive customer retention strategies.

## 🌐 Live Application

### Try CHURNAI

**[Launch CHURNAI Web Application](https://churn-ai-o48x.onrender.com/)**

The application includes:

| Section | Description |
|---|---|
| Home | Project introduction and prediction overview |
| Predict | Enter customer information and generate predictions |
| Dashboard | Explore customer prediction statistics |
| History | Review previous prediction records |
| About | Learn about the project and its technology |

---

## ✨ Key Features

### 1. Customer Churn Prediction
Uses a trained XGBoost classification model to estimate the probability of customer churn.

### 2. Risk Classification
Classifies customers into three risk categories:

- 🟢 **Low Risk:** Lower estimated probability of churn.
- 🟡 **Medium Risk:** Customers requiring monitoring.
- 🔴 **High Risk:** Customers who may need immediate retention attention.

### 3. Probability-Based Prediction
Provides a churn probability score rather than relying only on a binary prediction.

### 4. Interactive Dashboard
Displays prediction statistics and customer risk distribution.

### 5. Prediction History
Stores prediction records using an SQLite database for reviewing previous predictions.

### 6. Feature Engineering
Uses engineered customer attributes alongside original input features to improve predictive performance.

### 7. Responsive Web Interface
Provides a modern web interface for interacting with the machine learning model.

---

## 🧠 Machine Learning Approach

CHURNAI uses **XGBoost (Extreme Gradient Boosting)**, a powerful gradient boosting algorithm designed for structured and tabular datasets.

### Machine Learning Workflow

1. Dataset collection
2. Data exploration and understanding
3. Data preprocessing
4. Feature engineering
5. Train-test splitting
6. Model training
7. Model evaluation
8. Probability threshold optimization
9. Model serialization
10. Flask application integration
11. Deployment

### Model Information

| Component | Details |
|---|---|
| Problem Type | Binary Classification |
| Algorithm | XGBoost Classifier |
| Dataset | Bank Customer Churn Dataset |
| Dataset Size | 10,000 records |
| Original Input Features | 10 |
| Engineered Features | 4 |
| Model Format | Pickle (`.pkl`) |
| Prediction Output | Churn / No Churn |
| Risk Levels | Low / Medium / High |

### Model Performance

The following are the approximate test-set results reported by the project:

| Evaluation Metric | Score |
|---|---:|
| Accuracy | 83% |
| Precision | 56% |
| Recall | 67% |
| F1-Score | 61% |
| ROC-AUC | 87% |
| PR-AUC | 72% |

**Note:** These values are approximate. Actual performance can vary depending on the evaluation data and decision threshold.

---

## 📊 Input Features

The prediction pipeline uses customer information and engineered features.

### Original Features

| Feature | Description |
|---|---|
| CreditScore | Customer credit score |
| Geography | Customer geographical location |
| Gender | Customer gender |
| Age | Customer age |
| Tenure | Number of years with the bank |
| Balance | Customer account balance |
| NumOfProducts | Number of bank products used |
| HasCrCard | Whether the customer owns a credit card |
| IsActiveMember | Whether the customer is an active member |
| EstimatedSalary | Estimated annual salary |

### Engineered Features

| Feature | Description |
|---|---|
| AgeGroup | Customer age category |
| BalanceStatus | Categorized account balance |
| CustomerActivity | Customer activity category |
| ProductCategory | Categorized number of products |

Feature engineering is incorporated into the saved machine learning pipeline.

---

## 🛠️ Technology Stack

### Programming Language
- Python

### Machine Learning & Data Analysis
- NumPy
- Pandas
- Scikit-learn
- XGBoost
- SciPy
- Joblib

### Backend
- Flask
- Flask-SQLAlchemy
- SQLAlchemy

### Frontend
- HTML5
- CSS3
- JavaScript

### Database
- SQLite

### Deployment
- Render
- Gunicorn
- Git
- GitHub

---

## 📁 Project Structure

```text
CHURNAI/
│
├── app.py
├── config.py
├── requirements.txt
├── .python-version
├── .gitignore
├── README.md
│
├── models/
│   └── churn_deployment_bundle.pkl
│
├── database/
│   └── churn_history.db
│
├── data/
│
├── notebooks/
│   └── Customer_Churn_Prediction.ipynb
│
├── reports/
│
├── templates/
│   ├── index.html
│   ├── predict.html
│   ├── dashboard.html
│   ├── history.html
│   └── about.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── main.js
```

*This is a representative structure; adjust filenames to match the actual repository.*

---

## ⚙️ Installation and Local Setup

Follow these instructions to run CHURNAI locally.

### 1. Clone the Repository

```bash
git clone https://github.com/PritwishSaha/CHURNAI.git
```

### 2. Navigate to the Project

```bash
cd CHURNAI
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open in Your Browser

```text
http://127.0.0.1:5000/
```

Make sure the trained model bundle is present inside the `models/` directory.

---

## 🚀 Deployment

CHURNAI is deployed using **Render**.

### Deployment Configuration

| Configuration | Value |
|---|---|
| Platform | Render |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Entry Point | `app.py` |
| WSGI Application | `app` |

### Environment Variables

Configure the following environment variables in Render:

```text
SECRET_KEY=your-secure-secret-key
FLASK_DEBUG=0
```

Render provides the application port automatically.

---

## 🎯 Business Applications

CHURNAI can support banking and financial institutions in:

- Identifying customers with elevated churn risk.
- Prioritizing customer retention activities.
- Understanding customer behavior patterns.
- Supporting data-driven business decisions.
- Monitoring customer prediction trends.
- Improving customer relationship management strategies.

**Important:** Predictions are estimates, not guarantees of customer behavior. They should support—not replace—business judgment.

---

## 🔮 Future Improvements

- Integration with live banking datasets.
- Advanced customer segmentation.
- Explainable AI using SHAP.
- Personalized customer retention recommendations.
- Automated email or notification alerts.
- Model monitoring and performance tracking.
- PostgreSQL integration for persistent prediction history.
- Advanced analytics and visualization.

---

## 👨‍💻 Author

<div align="center">

### Pritwish Saha

B.Tech Computer Science & Engineering  
Artificial Intelligence & Machine Learning

**Interested in Data Analytics, Machine Learning, and AI-driven applications.**

[GitHub](https://github.com/PritwishSaha) · [LinkedIn](https://www.linkedin.com/in/pritwish-saha-b49604362/) · [Portfolio](https://infotact.in/pritwish-hk5nxp)

</div>

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

Your support and feedback are appreciated!

<div align="center">

**CHURNAI — Turning Customer Data into Predictive Insights.**

</div>
