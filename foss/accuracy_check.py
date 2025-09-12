# accuracy_check.py
import pandas as pd
import numpy as np
import ast
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from visualization import plot_actual_vs_predicted  # <-- moved plotting
from summary import analyze_classification_results  # <-- moved summary utils

def run_classification(csv_path="clean_reviews.csv"):
    import pandas as pd
    import numpy as np
    import ast
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, accuracy_score

    # ----------------- Load dataset -----------------
    df = pd.read_csv(csv_path)

    # Convert embeddings from string to numpy arrays
    df["fnet_embedding"] = df["fnet_embedding"].apply(lambda x: np.array(ast.literal_eval(x)))
    X = np.vstack(df["fnet_embedding"].values)
    y = df["overall"]

    # ----------------- Sentiment mapping -----------------
    y_num = y.apply(lambda r: -1 if r <= 2 else (0 if r == 3 else 1))

    # ----------------- Train-test split -----------------
    X_train, X_test, y_train, y_test = train_test_split(X, y_num, test_size=0.50, random_state=42)

    # ----------------- Train model -----------------
    clf = LogisticRegression(max_iter=200)
    clf.fit(X_train, y_train)

    # Predictions
    y_pred = clf.predict(X_test)

    # ----------------- Metrics -----------------
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # ----------------- Return dictionary -----------------
    return {
        "accuracy": float(acc),
        "summary": {
            "total_samples": len(y_test),
            "correct_pre_predictions": int((y_pred == y_test).sum()),
            "wrong_predictions": int((y_pred != y_test).sum()),
        },
        "report": report
    }
