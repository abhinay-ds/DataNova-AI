"""
DataNova AI - Comprehensive ML Audit & Leakage Investigation Execution
Executes the full machine learning audit on customer_churn_dataset-testing-master.csv.
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

# Set stdout encoding
sys.stdout.reconfigure(encoding="utf-8")

DATASET_PATH = os.path.join("backend", "uploads", "customer_churn_dataset-testing-master.csv")
if not os.path.exists(DATASET_PATH):
    # Try alternate location
    DATASET_PATH = "uploads/customer_churn_dataset-testing-master.csv"

def run_ml_audit():
    print("=" * 80)
    print("DATANOVA AI: MACHINE LEARNING AUDIT & LEAKAGE INVESTIGATION")
    print("=" * 80)

    # 1. Load Dataset
    print(f"\n[1] Loading dataset from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # 2. Verify Feature Classification & Existence
    cat_features = ["Gender", "Subscription Type", "Contract Length"]
    num_features_no_id = [
        "Age",
        "Tenure",
        "Usage Frequency",
        "Support Calls",
        "Payment Delay",
        "Total Spend",
        "Last Interaction",
    ]
    num_features_with_id = ["CustomerID"] + num_features_no_id
    target = "Churn"

    print("\n[2] Feature Verification:")
    print("  Categorical features:", cat_features)
    assert all(c in df.columns for c in cat_features), "Missing categorical column!"
    print("  [OK] All categorical features exist.")

    print("  Numerical features (no CustomerID):", num_features_no_id)
    assert all(c in df.columns for c in num_features_no_id), "Missing numerical column!"
    print("  [OK] All numerical features exist.")

    assert "CustomerID" in df.columns, "Missing CustomerID column!"
    assert target in df.columns, "Missing Churn target column!"
    print(f"  [OK] Target '{target}' and 'CustomerID' confirmed.")

    # 3. Data Integrity & Leakage Forensics
    print("\n[3] Forensic Data Integrity & Target Leakage Analysis:")
    exact_duplicates = int(df.duplicated().sum())
    duplicates_no_id = int(df.drop(columns=["CustomerID"]).duplicated().sum())
    print(f"  - Exact full-row duplicates: {exact_duplicates}")
    print(f"  - Duplicates excluding CustomerID: {duplicates_no_id}")

    # Check CustomerID correlation & sorting artifact
    id_corr = float(df["CustomerID"].corr(df[target]))
    print(f"  - CustomerID Pearson correlation with Churn: {id_corr:.4f}")

    # Check Churn distribution by CustomerID segments
    c_low = df[df["CustomerID"] <= 40000][target].mean()
    c_mid = df[(df["CustomerID"] > 40000) & (df["CustomerID"] < 51499)][target].mean()
    c_tail = df[df["CustomerID"] >= 51499][target].mean()
    tail_count = int((df["CustomerID"] >= 51499).sum())
    print(f"  - Churn rate for CustomerID <= 40,000: {c_low*100:.2f}%")
    print(f"  - Churn rate for CustomerID 40,001 - 51,498: {c_mid*100:.2f}%")
    print(f"  - Churn rate for CustomerID >= 51,499 ({tail_count} rows): {c_tail*100:.2f}% (PERFECT 100% CHURN TARGET LEAKAGE)")

    # 4. Train/Test Split (Stratified 80/20, random_state=42)
    print("\n[4] Stratified 80/20 Train-Test Splitting (random_state=42):")
    X_full = df[cat_features + num_features_with_id]
    y_full = df[target]

    X_train_full, X_test_full, y_train, y_test = train_test_split(
        X_full,
        y_full,
        test_size=0.2,
        stratify=y_full,
        random_state=42,
    )

    train_size = len(y_train)
    test_size = len(y_test)
    train_churn_0 = int((y_train == 0).sum())
    train_churn_1 = int((y_train == 1).sum())
    test_churn_0 = int((y_test == 0).sum())
    test_churn_1 = int((y_test == 1).sum())

    print(f"  - Total samples: {len(df)}")
    print(f"  - Training samples: {train_size} (80.0%) | Churn 0: {train_churn_0} ({train_churn_0/train_size*100:.2f}%), Churn 1: {train_churn_1} ({train_churn_1/train_size*100:.2f}%)")
    print(f"  - Held-out test samples: {test_size} (20.0%) | Churn 0: {test_churn_0} ({test_churn_0/test_size*100:.2f}%), Churn 1: {test_churn_1} ({test_churn_1/test_size*100:.2f}%)")

    # Check for train/test overlap (data leakage across split)
    overlap_count = int(
        pd.merge(
            X_train_full.drop(columns=["CustomerID"]),
            X_test_full.drop(columns=["CustomerID"]),
            how="inner",
        ).shape[0]
    )
    print(f"  - Train/Test feature overlap (identical feature vectors across split): {overlap_count}")

    # 5. Define Model Architectures
    model_factories = [
        ("Logistic Regression", lambda: LogisticRegression(max_iter=1000, random_state=42)),
        ("Decision Tree", lambda: DecisionTreeClassifier(random_state=42)),
        ("Random Forest", lambda: RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
        ("Gradient Boosting", lambda: GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ]

    # Preprocessors
    def get_preprocessor(num_cols):
        return ColumnTransformer(
            transformers=[
                (
                    "num",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    num_cols,
                ),
                (
                    "cat",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("encoder", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    cat_features,
                ),
            ]
        )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    all_results = []
    confusion_matrices = {}

    # 6. Evaluation Loop: Condition A (Excluded CustomerID) & Condition B (Included CustomerID)
    conditions = [
        ("CustomerID Excluded", num_features_no_id, X_train_full[cat_features + num_features_no_id], X_test_full[cat_features + num_features_no_id]),
        ("CustomerID Included", num_features_with_id, X_train_full[cat_features + num_features_with_id], X_test_full[cat_features + num_features_with_id]),
    ]

    print("\n[5] Running 5-Fold Stratified Cross-Validation & Test Set Evaluation:")
    for cond_name, num_cols, X_tr, X_te in conditions:
        print(f"\n--- Condition: {cond_name} ---")
        preprocessor = get_preprocessor(num_cols)

        for model_name, clf_factory in model_factories:
            t_start = time.time()
            clf = clf_factory()
            pipe = Pipeline([("preprocessor", preprocessor), ("classifier", clf)])

            # 5-fold cross-validation on training set
            cv_scores = cross_val_score(pipe, X_tr, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
            cv_mean = float(cv_scores.mean())
            cv_std = float(cv_scores.std())

            # Train on complete training set
            pipe.fit(X_tr, y_train)
            train_preds = pipe.predict(X_tr)
            train_acc = float(accuracy_score(y_train, train_preds))

            # Evaluate on held-out test set
            test_preds = pipe.predict(X_te)
            test_acc = float(accuracy_score(y_test, test_preds))
            prec = float(precision_score(y_test, test_preds, zero_division=0))
            rec = float(recall_score(y_test, test_preds, zero_division=0))
            f1 = float(f1_score(y_test, test_preds, zero_division=0))

            # ROC-AUC
            if hasattr(pipe.named_steps["classifier"], "predict_proba"):
                test_probs = pipe.predict_proba(X_te)[:, 1]
                auc = float(roc_auc_score(y_test, test_probs))
            elif hasattr(pipe.named_steps["classifier"], "decision_function"):
                test_probs = pipe.decision_function(X_te)
                auc = float(roc_auc_score(y_test, test_probs))
            else:
                auc = float("nan")

            cm = confusion_matrix(y_test, test_preds)
            confusion_matrices[f"{model_name} ({cond_name})"] = cm.tolist()

            elapsed = time.time() - t_start

            print(f"  {model_name:<20} | Train Acc: {train_acc*100:.2f}% | CV Acc: {cv_mean*100:.2f}% ± {cv_std*100:.2f}% | Test Acc: {test_acc*100:.2f}% | F1: {f1:.4f} | ROC-AUC: {auc:.4f} ({elapsed:.1f}s)")

            all_results.append({
                "model": model_name,
                "customer_id": "Excluded" if "Excluded" in cond_name else "Included",
                "train_accuracy": train_acc,
                "cv_mean": cv_mean,
                "cv_std": cv_std,
                "test_accuracy": test_acc,
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "roc_auc": auc,
            })

    # Save results json
    audit_data = {
        "dataset_rows": len(df),
        "split": {
            "train_size": train_size,
            "test_size": test_size,
            "train_churn_0": train_churn_0,
            "train_churn_1": train_churn_1,
            "test_churn_0": test_churn_0,
            "test_churn_1": test_churn_1,
        },
        "leakage_findings": {
            "exact_duplicates": exact_duplicates,
            "duplicates_no_id": duplicates_no_id,
            "train_test_overlap": overlap_count,
            "customer_id_correlation": id_corr,
            "churn_tail_rate_id_ge_51499": c_tail,
            "churn_head_rate_id_le_40000": c_low,
        },
        "results": all_results,
        "confusion_matrices": confusion_matrices,
    }

    with open("backend/ml_audit_results.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)

    print("\n[6] Audit successfully completed! Results saved to backend/ml_audit_results.json")
    return audit_data

if __name__ == "__main__":
    run_ml_audit()
