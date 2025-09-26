import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import sys

# ===============================
# 🔹 Charger les données
# ===============================
csv_path = "data/all_years_grouped_data.csv"
df = pd.read_csv(csv_path, sep=";")

# Vérifier la colonne date ("Jour")
jour_col = None
for col in df.columns:
    if col.strip().lower() == "jour":
        jour_col = col
        break
if not jour_col:
    print("Erreur : aucune colonne 'Jour' trouvée dans le CSV.")
    sys.exit(1)
df["date"] = pd.to_datetime(df[jour_col])

# ===============================
# 🔹 Features temporelles
# ===============================
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["weekday"] = df["date"].dt.weekday
df["is_weekend"] = (df["weekday"] >= 5).astype(int)

df["time_index"] = (df["year"] - df["year"].min()) * 12 + df["month"]
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

# ===============================
# 🔹 Encodage des variables catégorielles (on garde les encodeurs)
# ===============================
label_encoders = {}
for col in ["nom site", "Polluant", "type d'influence", "type d'implantation"]:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

# Nettoyage
df = df.dropna(subset=["valeur_moyenne"])

# ===============================
# 🔹 Features finales
# ===============================
features = [
    "time_index", "month_sin", "month_cos",
    "weekday", "is_weekend",
    "valeur_minimale", "valeur_maximale",
    "nom site", "Polluant", "type d'influence", "type d'implantation"
]

X = df[features]
y = df["valeur_moyenne"]

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# ===============================
# 🔹 Modèle XGBoost
# ===============================
model = XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# Évaluation globale
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n=== Accuracy globale ===")
print(f"R² global : {r2:.3f}")
print(f"RMSE global : {rmse:.2f}")

# ===============================
# 🔹 Génération des futures dates
# ===============================
future_dates = pd.date_range(
    start=df["date"].max() + pd.offsets.MonthBegin(1),
    end=datetime(2027, 12, 1),
    freq="MS"
)
future_df = pd.DataFrame({
    "year": future_dates.year,
    "month": future_dates.month,
    "weekday": future_dates.weekday,
    "is_weekend": (future_dates.weekday >= 5).astype(int),
    "date": future_dates
})
future_df["time_index"] = (future_df["year"] - df["year"].min()) * 12 + future_df["month"]
future_df["month_sin"] = np.sin(2 * np.pi * future_df["month"] / 12)
future_df["month_cos"] = np.cos(2 * np.pi * future_df["month"] / 12)

# ===============================
# 🔹 Prédictions futures par site et polluant
# ===============================
results = []
for site in df["nom site"].unique():
    for polluant in df["Polluant"].unique():
        base = future_df.copy()
        base["valeur_minimale"] = df["valeur_minimale"].mean()
        base["valeur_maximale"] = df["valeur_maximale"].mean()
        base["nom site"] = site
        base["type d'influence"] = df["type d'influence"].mode()[0]
        base["type d'implantation"] = df["type d'implantation"].mode()[0]
        base["Polluant"] = polluant

        y_future = model.predict(base[features])
        base["valeur_moyenne_predite"] = y_future
        results.append(base)

final_df = pd.concat(results, ignore_index=True)

# ===============================
# 🔹 Décodage des labels pour export clair
# ===============================
if "Polluant" in label_encoders:
    final_df["Polluant"] = label_encoders["Polluant"].inverse_transform(final_df["Polluant"])
if "nom site" in label_encoders:
    final_df["nom site"] = label_encoders["nom site"].inverse_transform(final_df["nom site"])

# Colonnes finales
final_df = final_df[["year", "month", "Polluant", "nom site", "valeur_moyenne_predite"]]
final_df = final_df.sort_values(by=["Polluant", "nom site", "year", "month"]).reset_index(drop=True)

print("\n=== Exemple de prédictions ===")
print(final_df.head(20))

# Export CSV final
final_df.to_csv("data/predictions_valeur_moyenne_2027.csv", index=False)
print("\n✅ Fichier final sauvegardé : data/predictions_valeur_moyenne_2027.csv")
