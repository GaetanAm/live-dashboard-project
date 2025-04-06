#!/bin/bash

# Étape 1 : Scraper les données
bash scraper.sh

# Étape 2 : Générer le rapport
python generate_report.py

# Étape 3 : Push sur GitHub
git config --global user.name "$GITHUB_USER"
git config --global user.email "$GITHUB_USER@users.noreply.github.com"

git clone https://$GH_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git repo
cd repo

cp ../data.csv .
cp ../report.json .

git add data.csv report.json
git commit -m "Auto update on $(date +'%Y-%m-%d %H:%M:%S')" || echo "Rien à commit"
git push origin main
