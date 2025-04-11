#!/bin/bash

# Étape 1 : Scraper les données
bash scraper.sh

# Étape 2 : Générer le rapport
python generate_report.py

# Étape 3 : Config GitHub
git config --global user.name "$GITHUB_USER"
git config --global user.email "$GITHUB_USER@users.noreply.github.com"

# Étape 4 : Clone du dépôt
git clone https://$GH_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git repo
cd repo

# Étape 5 : Fusion des données
cat ../data.csv >> data.csv

# Étape 6 : Nettoyage des NaN
grep -v ',NaN$' data.csv > tmp && mv tmp data.csv

# Étape 7 : Tri + dédoublonnage en gardant l’ordre chronologique
sort -u data.csv | sort -k1,1 > tmp && mv tmp data.csv

# Étape 8 : Copie du rapport du jour
cp ../report.json .

# Étape 9 : Git push
git add data.csv report.json
git commit -m "Auto update on $(date +'%Y-%m-%d %H:%M:%S')" || echo "Rien à commit"
git push origin main
