import pandas as pd

# Fichier brut téléchargé précédemment
input_file = "restaurants_france_raw.csv"
output_file = "restaurants_bretagne_clean.csv"

print("Chargement du fichier brut...")
try:
    df = pd.read_csv(input_file, low_memory=False, on_bad_lines='skip', encoding='utf-8', sep=';')
except:
    # Essayer avec d'autres paramètres si ça échoue
    df = pd.read_csv(input_file, low_memory=False, on_bad_lines='skip', encoding='latin-1', sep=';', quotechar='"')

print("Colonnes disponibles :")
print(df.columns.tolist())

# Colonnes utiles selon ce dataset
colonnes_utiles = [
    "name",
    "type",
    "cuisine",
    "phone",
    "website",
    "capacity",
    "stars",
    "meta_name_com",
    "meta_code_com",
    "meta_name_dep",
    "meta_code_dep",
    "meta_geo_point"
]

# Garder les colonnes existantes seulement
colonnes_utiles = [c for c in colonnes_utiles if c in df.columns]
df = df[colonnes_utiles]

print("\nFiltrage : Bretagne uniquement...")

# Liste des départements bretons (codes département)
departements_bretagne = ["22", "29", "35", "56"]

def is_bretagne(code):
    if pd.isna(code):
        return False
    code_str = str(code).strip()
    return code_str in departements_bretagne

df_bretagne = df[df["meta_code_dep"].apply(is_bretagne)]

print(f"Restaurants trouvés en Bretagne : {len(df_bretagne)}")

# Nettoyage : suppression valeurs vides du nom
df_bretagne = df_bretagne.dropna(subset=["name"])

# Ajout d'un identifiant unique
df_bretagne["id"] = df_bretagne.index + 1

# Réordonner colonnes
cols_final = ["id"] + [c for c in df_bretagne.columns if c != "id"]
df_bretagne = df_bretagne[cols_final]

# Sauvegarde
df_bretagne.to_csv(output_file, index=False, encoding="utf-8")
print(f"✔️ Fichier propre créé : {output_file}")
