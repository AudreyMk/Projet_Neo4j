import pandas as pd
import random

# Paramètres
nb_users = 50
min_ratings_per_user = 5
max_ratings_per_user = 15

# Charger restaurants existants
restaurants = pd.read_csv("restaurants_bretagne_clean.csv")
restaurant_ids = restaurants["id"].tolist()  # identifiant existant

# 1️⃣ Générer les utilisateurs
users = []
for i in range(1, nb_users + 1):
    users.append({
        "userId": f"u{i}",
        "name": f"User{i}"
    })

df_users = pd.DataFrame(users)
df_users.to_csv("users.csv", index=False)
print("CSV users généré : users.csv")

# 2️⃣ Générer les notes aléatoires
ratings = []
for user in users:
    nb_ratings = random.randint(min_ratings_per_user, max_ratings_per_user)
    sampled_restaurants = random.sample(restaurant_ids, nb_ratings)
    for rest_id in sampled_restaurants:
        rating = random.randint(1, 5)
        ratings.append({
            "userId": user["userId"],
            "restaurantId": rest_id,
            "score": rating
        })

df_ratings = pd.DataFrame(ratings)
df_ratings.to_csv("ratings.csv", index=False)
print("CSV ratings généré : ratings.csv")
