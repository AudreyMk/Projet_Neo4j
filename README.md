# 🍽️ Système d'Analyse de Restaurants en Bretagne avec Neo4j

**Projet de base de données orientée graphe - Master 2 Data Science**


## 📋 Objectif du projet

Construire une base de données graphe avec Neo4j pour analyser les restaurants en Bretagne et explorer les relations entre utilisateurs et établissements via leurs notes.

---

## 🏗️ Architecture des données

### Modèle de graphe

```
(User)-[RATED {score: 1-5}]->(Restaurant)
```

**Nœuds :**
- `User` : Utilisateurs (propriété : userId, name)
- `Restaurant` : Restaurants bretons (propriétés : name, cuisine, city, department, phone, etc.)

**Relations :**
- `RATED` : Note donnée par un utilisateur à un restaurant (score de 1 à 5)

---

## Données collectées

### Sources
- **Restaurants** : OpenStreetMap - extraction des restaurants en Bretagne (4 départements)
- **Utilisateurs** : Générés synthétiquement
- **Notes** : Générées aléatoirement pour créer des interactions

### Fichiers CSV
- `restaurants_bretagne_clean.csv` : 9 248 restaurants
- `users_restaurants.csv` : 50 utilisateurs
- `ratings_restaurants.csv` : 508 notes

---

## 🔧 Nettoyage des données

Script Python `data_clean.py` :
- Filtrage des restaurants par code départemental (22, 29, 35, 56)
- Extraction des colonnes pertinentes
- Nettoyage des valeurs manquantes
- Export CSV propre

---

## 🚀 Import dans Neo4j

### 1. Création des contraintes

```cypher
CREATE CONSTRAINT user_id IF NOT EXISTS 
FOR (u:User) REQUIRE u.userId IS UNIQUE;

CREATE CONSTRAINT restaurant_id IF NOT EXISTS 
FOR (r:Restaurant) REQUIRE r.restaurantId IS UNIQUE;
```

### 2. Import des utilisateurs

```cypher
LOAD CSV WITH HEADERS FROM 'file:///users_restaurants.csv' AS row
CREATE (u:User {userId: row.userId, name: row.name});
```

### 3. Import des restaurants

```cypher
LOAD CSV WITH HEADERS FROM 'file:///restaurants_bretagne_clean.csv' AS row
CREATE (r:Restaurant {
    restaurantId: toInteger(row.id),
    name: row.name,
    type: row.type,
    cuisine: row.cuisine,
    city: row.meta_name_com,
    department: row.meta_name_dep,
    phone: row.phone
});
```

### 4. Import des notes (relations)

```cypher
LOAD CSV WITH HEADERS FROM 'file:///ratings_restaurants.csv' AS row
MATCH (u:User {userId: row.userId})
MATCH (r:Restaurant {restaurantId: toInteger(row.restaurantId)})
CREATE (u)-[:RATED {score: toInteger(row.score)}]->(r);
```

---

## 📈 Analyses et résultats

### Vue d'ensemble de la base

**Requête :**
```cypher
MATCH (n)
RETURN labels(n)[0] as Type, COUNT(n) as Nombre
```

**Résultats :**
- **9 248 Restaurants**
- **50 Utilisateurs**
- **508 Relations RATED**

---

### 1. Meilleur restaurant français à Brest

**Requête :**
```cypher
MATCH (r:Restaurant)<-[rating:RATED]-()
WHERE r.city = 'Brest' AND r.cuisine = 'french'
WITH r, 
     AVG(rating.score) as note_moyenne,
     COUNT(rating) as nb_avis
WHERE nb_avis >= 1
RETURN r.name as Restaurant,
       r.city as Ville,
       r.phone as Telephone,
       ROUND(note_moyenne, 2) as NoteMoyenne
ORDER BY note_moyenne DESC
LIMIT 1
```

**Résultat :** "Le Keravilin" avec 4.0/5 et téléphone +33229617321

![Restaurant Brest](captures/11_francais_brest.png)

---

### 2. Restaurants italiens avec note moyenne ≥ 3 en Bretagne

**Requête :**
```cypher
MATCH (r:Restaurant)<-[rating:RATED]-()
WHERE r.cuisine = 'italian'
WITH r, 
     AVG(rating.score) as note_moyenne,
     COUNT(rating) as nb_avis
WHERE note_moyenne >= 3.0 AND nb_avis >= 1
RETURN r.name as Restaurant,
       r.city as Ville,
       r.department as Departement,
       ROUND(note_moyenne, 2) as NoteMoyenne
ORDER BY note_moyenne DESC
LIMIT 10
```

**Résultats :**
- "Ô'Divino" à Melesse (Ille-et-Vilaine) : 4.0/5
- "Si Ristorante" à Brest (Finistère) : 3.0/5
- "Le casier" à Saint-Gildas-de-Rhuys (Morbihan) : 3.0/5

![Italiens](captures/12_italiens.png)

---

### 3. Tous les restaurants de pizza les mieux notés

**Requête :**
```cypher
MATCH (r:Restaurant)<-[rating:RATED]-()
WHERE r.cuisine CONTAINS 'pizza'
WITH r, 
     AVG(rating.score) as note_moyenne,
     COUNT(rating) as nb_avis
WHERE nb_avis >= 1
RETURN r.name as Restaurant,
       r.cuisine as Cuisine,
       r.city as Ville,
       ROUND(note_moyenne, 2) as NoteMoyenne
ORDER BY note_moyenne DESC
LIMIT 10
```

**Visualisation graphique des pizzerias :**

![Graphe pizza](captures/14_graphe_pizza.png)

*25 utilisateurs, 33 pizzerias, 34 relations RATED*

---

### 4. Top 10 restaurants les mieux notés à Rennes

**Requête :**
```cypher
MATCH (r:Restaurant)<-[rating:RATED]-()
WHERE r.city = 'Rennes'
WITH r, 
     AVG(rating.score) as note_moyenne,
     COUNT(rating) as nb_avis
WHERE nb_avis >= 1
RETURN r.name as Restaurant,
       r.cuisine as Cuisine,
       r.city as Ville,
       ROUND(note_moyenne, 2) as NoteMoyenne,
       nb_avis as NombreAvis
ORDER BY note_moyenne DESC, nb_avis DESC
LIMIT 10
```

**Visualisation graphique du réseau à Rennes :**

![Graphe Rennes](captures/15_graphe_rennes.png)

*9 utilisateurs, 10 restaurants à Rennes*

---

## 🔑 Requêtes Cypher clés

### Statistiques globales

```cypher
// Compter les nœuds par type
MATCH (n)
RETURN labels(n)[0] as Type, COUNT(n) as Nombre;

// Compter les relations
MATCH ()-[r]->()
RETURN type(r) as Relation, COUNT(r) as Nombre;
```

### Recherche avancée

```cypher
// Restaurants d'une cuisine dans une ville avec note minimale
MATCH (r:Restaurant)<-[rating:RATED]-()
WHERE r.city = $ville AND r.cuisine = $cuisine
WITH r, AVG(rating.score) as note, COUNT(rating) as nb_avis
WHERE note >= $note_min AND nb_avis >= 1
RETURN r.name, r.cuisine, r.city, ROUND(note, 2) as Note
ORDER BY note DESC
LIMIT 10;
```

### Visualisation réseau

```cypher
// Réseau utilisateurs-restaurants par critère
MATCH (u:User)-[r:RATED]->(rest:Restaurant)
WHERE rest.city = $ville OR rest.cuisine = $cuisine
RETURN u, r, rest
LIMIT 50;
```

---

## 💡 Insights principaux

1. **Meilleure cuisine française** : "Le Keravilin" à Brest se distingue avec une note de 4.0/5

2. **Restaurants italiens** : Présence de restaurants italiens de qualité (note ≥ 3) dans les 3 départements principaux

3. **Pizzerias populaires** : 33 pizzerias notées par 25 utilisateurs différents, montrant l'attractivité de ce type de cuisine

4. **Concentration à Rennes** : La capitale bretonne concentre de nombreux restaurants bien notés avec un réseau actif d'utilisateurs

---

## 🛠️ Technologies utilisées

- **Neo4j Desktop** : Base de données orientée graphe
- **Cypher** : Langage de requête pour Neo4j
- **Python** : Nettoyage et préparation des données (pandas)
- **OpenStreetMap** : Source des données restaurants

---

## 📝 Limites et améliorations possibles

### Limites actuelles
- Données de notes générées aléatoirement (pas de recommandations collaboratives possibles)
- Aucun chevauchement entre utilisateurs (chaque utilisateur note des restaurants différents)
- Absence de données temporelles (dates des visites)

### Améliorations futures
- Intégrer des vraies données de notes (API TripAdvisor, Google Places)
- Ajouter des propriétés : horaires, prix moyen, photos
- Implémenter un système de recommandation basé sur les graphes
- Ajouter des relations : restaurants similaires, utilisateurs amis
- Analyse temporelle : évolution des notes, tendances saisonnières

---

## 📚 Conclusion

Ce projet démontre la puissance de **Neo4j** pour :
- Modéliser des relations complexes (utilisateurs ↔ restaurants)
- Effectuer des recherches multi-critères rapides
- Visualiser des réseaux de données
- Analyser des données géographiques et catégorielles

Les **graphes orientés** sont particulièrement adaptés pour les systèmes de recommandation, l'analyse de réseaux sociaux et les données interconnectées.

---

**Auteur** : Projet académique - Master 2 Data Science  
**Date** : Décembre 2025  
**Technologies** : Neo4j, Cypher, Python, OpenStreetMap
