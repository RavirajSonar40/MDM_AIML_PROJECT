import streamlit as st
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import skew, kurtosis, pearsonr
from matplotlib import pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder, OneHotEncoder
from sklearn.metrics import classification_report, ConfusionMatrixDisplay, confusion_matrix, auc, roc_curve
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

__import__('warnings').filterwarnings('ignore')

st.set_page_config(page_title="Student Depression Analysis", layout="wide")

st.title("📊 Student Depression Analysis & Prediction")

# Load dataset
df = pd.read_csv('./data/Student Depression Dataset.csv')
numerical_vars = [col for col in df.select_dtypes(include=np.number).columns.tolist() if col not in ['Depression', 'id']]
categorical_vars = df.select_dtypes(exclude=np.number).columns.tolist()

# Fill missing values
for var in numerical_vars:
    df[var] = df[var].fillna(df[var].median())
for var in categorical_vars:
    df[var] = df[var].fillna(df[var].mode()[0])

# Data preprocessing functions
def process_city_column(df, anomaly_mapping=None, threshold=50, top_n=10, other_label='Other'):
    if anomaly_mapping is None:
        anomaly_mapping = {
            'Less than 5 Kalyan': 'Kalyan',
            'Less Delhi': 'Delhi',
            'M.Com': other_label,
            'ME': other_label,
            '3.0': other_label
        }
    df = df.copy()
    df['City'] = df['City'].replace(anomaly_mapping)
    city_counts = df['City'].value_counts()
    replace_cities = city_counts[city_counts < threshold].index
    df['City'] = df['City'].replace(replace_cities, other_label)
    top_cities = df['City'][df['City'] != other_label].value_counts().nlargest(top_n).index
    df['City'] = np.where(df['City'].isin(top_cities), df['City'], other_label)
    city_order = [other_label] + list(top_cities)
    df['City'] = pd.Categorical(df['City'], categories=city_order, ordered=True)
    return df

df = process_city_column(df)

# Encoding hierarchies
hierarchies = {
    'degree': [
        'Class 12', 'B.Arch', 'B.Pharm', 'B.Tech', 'B.Com', 'BBA', 'BHM', 'B.Ed', 'BSc', 'BA', 'BCA', 'LLB', 'BE', 'MBBS',
        'M.Tech', 'MBA', 'MCA', 'MA', 'M.Com', 'M.Ed', 'ME', 'MHM', 'M.Pharm', 'MSc', 'LLM', 'PhD', 'MD', 'Others'
    ],
    'sleep': ['More than 8 hours', '7-8 hours', '5-6 hours', 'Less than 5 hours', 'Others'],
    'dietary': ['Healthy', 'Moderate', 'Unhealthy', 'Others']
}

categorical_pipeline = Pipeline(steps=[
    ('encoder', ColumnTransformer(
        transformers=[
            ('binary', OrdinalEncoder(), [
                'Gender', 'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness'
            ]),
            ('degree', OrdinalEncoder(categories=[hierarchies['degree']]), ['Degree']),
            ('dietary', OrdinalEncoder(categories=[hierarchies['dietary']]), ['Dietary Habits']),
            ('sleep', OrdinalEncoder(categories=[hierarchies['sleep']]), ['Sleep Duration']),
            ('categorical', OneHotEncoder(drop='first'), ['City', 'Profession'])
        ],
        remainder='drop'
    ))
])

numeric_pipeline = Pipeline(steps=[('scaler', MinMaxScaler())])

pipeline = ColumnTransformer(
    transformers=[
        ('cat', categorical_pipeline, categorical_vars),
        ('num', numeric_pipeline, numerical_vars)
    ],
    remainder='drop'
)

df_processed = pipeline.fit_transform(df)
X, y = df_processed, df['Depression']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Utility
from time import perf_counter
from functools import wraps
def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        print(f'{func.__name__} took {perf_counter() - start:.2f} seconds')
        return result
    return wrapper

@timeit
def train_model_and_evaluate(model):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)
    st.markdown("### Classification Report")
    st.text(report)
    fig, ax = plt.subplots()
    cm = ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred))
    cm.plot(ax=ax, colorbar=False)
    st.markdown("### Confusion Matrix")
    st.pyplot(fig)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Data Visualization", "📊 Model Evaluation", "📉 ROC Curve", "🧠 Predict Depression"])

# ---- Tab 1 ----
with tab1:
    st.header("Data Visualization")
    analysis = st.selectbox("Select Type of Analysis", ['Univariate', 'Bivariate'])
    var_select = st.selectbox('Variable Type', ['Continous Variables' , 'Categorical Variables'])
    if st.button("Generate Plots", key="viz_button"):
        if analysis == 'Univariate':
            if var_select == 'Continous Variables':
                fig, axs = plt.subplots(len(numerical_vars), figsize=(10, 5 * len(numerical_vars)))
                for i, var in enumerate(numerical_vars):
                    sns.histplot(df[var], kde=True, ax=axs[i])
                    axs[i].set_title(f'Distribution of {var}')
                st.pyplot(fig)
            else:
                for var in categorical_vars:
                    fig, ax = plt.subplots()
                    sns.countplot(x=df[var], ax=ax)
                    plt.xticks(rotation=90)
                    st.pyplot(fig)
        else:
            if var_select == 'Continous Variables':
                for var in numerical_vars:
                    fig, ax = plt.subplots()
                    sns.boxplot(x=df['Depression'], y=df[var], ax=ax)
                    st.pyplot(fig)
            else:
                for var in categorical_vars:
                    fig, ax = plt.subplots()
                    sns.countplot(x=var, hue='Depression', data=df, ax=ax)
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

# ---- Tab 2 ----
with tab2:
    st.header("Model Evaluation")
    algo = ['Logistic Regression', 'Random Forest', 'XGBoost', 'LightGBM']
    algo_select = st.selectbox("Select Model", algo)
    if st.button("Evaluate Model"):
        # model_map = {
        #     'Logistic Regression': LogisticRegression(),
        #     'Random Forest': RandomForestClassifier(),
        #     'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
        #     'LightGBM': LGBMClassifier()
        # }
        if algo_select == "Logistic Regression":
            train_model_and_evaluate(LogisticRegression())
        if algo_select == "Random Forest":
            train_model_and_evaluate(RandomForestClassifier())
        if algo_select == "XGBoost":
            train_model_and_evaluate(XGBClassifier())
        if algo_select == "LightGBM":
            train_model_and_evaluate(LGBMClassifier())
        # train_model_and_evaluate(model_map[algo_select])

# ---- Tab 3 ----
with tab3:
    st.header("ROC Curve Comparison")

    if st.button("Run GridSearch and Plot ROC"):
        models = {
            'LogisticRegression': LogisticRegression(),
            'LGBMClassifier': LGBMClassifier(verbosity=-1),
            'XGBClassifier': XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
            'RandomForestClassifier': RandomForestClassifier()
        }

        params = {
            'LogisticRegression': {'C': [0.1, 1, 10], 'penalty': ['l2'], 'solver': ['lbfgs']},
            'LGBMClassifier': {'n_estimators': [100, 200], 'learning_rate': [0.05, 0.1], 'num_leaves': [31, 50], 'max_depth': [-1, 5]},
            'XGBClassifier': {'n_estimators': [100, 200], 'max_depth': [3, 5], 'learning_rate': [0.05, 0.1], 'subsample': [0.9], 'colsample_bytree': [0.9]},
            'RandomForestClassifier': {'n_estimators': [100, 200], 'max_depth': [None, 5]}
        }

        best_models = {}

        for model_name, model in models.items():
            grid_search = GridSearchCV(model, params[model_name], cv=3, scoring='f1_macro')
            grid_search.fit(X_train, y_train)
            best_models[model_name] = grid_search.best_estimator_
            st.write(f"✅ Best params for {model_name}:", grid_search.best_params_)

        # Voting classifier
        voting_clf = VotingClassifier(estimators=[(name, model) for name, model in best_models.items()], voting='soft')
        voting_clf.fit(X_train, y_train)
        best_models['VotingClassifier'] = voting_clf

        # Plot ROC
        fig, ax = plt.subplots(figsize=(10, 6))
        for model_name, model in best_models.items():
            if hasattr(model, "predict_proba"):
                y_score = model.predict_proba(X_test)[:, 1]
            else:
                y_score = model.decision_function(X_test)
            fpr, tpr, _ = roc_curve(y_test, y_score)
            ax.plot(fpr, tpr, label=f"{model_name} (AUC = {auc(fpr, tpr):.2f})")
        ax.plot([0, 1], [0, 1], 'k--')
        ax.set_title("ROC Curve Comparison")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.legend()
        st.pyplot(fig)

# ---- Tab 4 ----
with tab4:
    st.header("Predict Depression Risk")
    st.write("Fill in the details below:")

    features = [
        'Gender', 'Age', 'Academic Pressure', 'CGPA', 'Sleep Duration', 'Dietary Habits',
        'Degree', 'Have you ever had suicidal thoughts ?', 'Work/Study Hours',
        'Family History of Mental Illness', 'Financial Stress'
    ]

    categorical_options = {
        'Gender': ['Male', 'Female'],
        'Sleep Duration': ['Less than 4 hours', '4-6 hours', '6-8 hours', 'More than 8 hours'],
        'Dietary Habits': ['Healthy', 'Unhealthy'],
        'Degree': ['Undergraduate', 'Graduate', 'Postgraduate'],
        'Have you ever had suicidal thoughts ?': ['Yes', 'No'],
        'Family History of Mental Illness': ['Yes', 'No']
    }

    user_input = {}
    for feature in features:
        if feature in categorical_options:
            user_input[feature] = st.selectbox(f"{feature}", categorical_options[feature])
        else:
            user_input[feature] = st.number_input(f"{feature}", min_value=0.0, step=0.1)

    if st.button("Predict"):
        input_df = pd.DataFrame([user_input])
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)
        prediction = model.predict(input_df)[0]
        if prediction == 1:
            st.error("🚨 High risk of depression detected.")
        else:
            st.success("✅ Low risk of depression predicted.")
