Projet d'analyse de la qualité de l'air dans Paris et Ile de france

presentation :https://gamma.app/docs/Hackathon-Data-Science-IA-EFREI-2025-1hmkwf003yswaku

Source de données :
https://object.infra.data.gouv.fr/browser/ineris-prod/lcsqa%2Fconcentrations-de-polluants-atmospheriques-reglementes%2Ftemps-reel%2F

download_csv_minio.py

Script qui télécharge automatiquement tous les fichiers CSV de qualité de l’air 2023 depuis data.gouv.fr.
	•	Génère les noms de fichiers quotidiens.
	•	Télécharge chaque fichier avec requests.
	•	Stocke les données dans ./data

data_cleaning.ipynb :
Cleaning des donnees (retirer les valeurs nulles, colonnes inutiles et preparation des données pour le ML), le fichier fait également une agrégation des données en regroupant les données des sites par jours en récupérant la valeur minimale, maximale et moyenne pour chaque site par jour par type de polluant

Clustering.ipynb:
Le fichier charge les données de pollution (all_years_grouped_data.csv) et les met en forme.
-Il calcule la pollution moyenne par site et standardise les données.
-Il applique un clustering K-Means (par défaut 4 groupes).
-Il génère un scatter plot avec les sites, colorés selon leur cluster et proportionnels à leur pollution.
-Il exporte les résultats (site, pollution moyenne, cluster) dans sites_clusters.csv.

ml_predictor.py

Script de prédiction de pollution atmosphérique avec XGBoost.
	•	Charge et nettoie les données (all_years_grouped_data.csv).
	•	Crée des features temporelles (mois, weekday, saisonnalité sin/cos).
	•	Encode les variables catégorielles (site, polluant, influence, implantation).
	•	Entraîne un modèle XGBRegressor pour prédire la valeur moyenne des polluants.
	•	Évalue le modèle (R², RMSE).
	•	Génère des prédictions futures par site et polluant jusqu’en 2027, exportées en CSV.
