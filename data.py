import requests

# URL API OpenDataSoft (restaurants France via OSM)
url = "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/osm-france-food-service%40public/exports/csv"

# Fichier de sortie
output_file = "restaurants_france_raw.csv"

print("Téléchargement en cours...")

response = requests.get(url)

if response.status_code == 200:
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"✔️ Téléchargement terminé : {output_file}")
else:
    print(f"❌ Erreur HTTP : {response.status_code}")
