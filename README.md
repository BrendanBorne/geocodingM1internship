# Améliorer la géolocalisation des exploitations pour prédire la circulation d’agents pathogènes dans les troupeaux bovins en Loire-Atlantique

Ce dépôt git a pour objectif de mettre à disposition les scripts de correction de la Base Nationale d'Identification animale et de modélisation de la propagation d'un agent pathogène sur réseau de contact qui ont été produits au cours du stage de M1 MODE au sein de l'INRAE par Brendan Borne.

> Dépôt est en cours de construction !

## Correction de la BDNI

Le script de correction de la BDNI est `fix_bdni.py`.

Le script n'est pas exécutable sans fichier BDNI à corriger. Les données contenues dans la BDNI sont des données considérées comme sensibles. C'est pourquoi il n'est pas possible de donner accès à ce fichier de données pour tester l'exécution du script.

### Exécution du script

Ce script peut être exécuté à partir d'un terminal grâce à la commande `python3`.

L'exécution de ce script doit recevoir deux arguments positionnels (à fournir dans le bon ordre) :

* Le premier argument est le nom du fichier BDNI à corriger
* Le deuxième argument est le nom du fichier corriger à écrire. Ces deux arguments sont obligatoires.

La commande minimale pour lancer le script est donc :

`python3 fix_bdni.py 'BDNI_ENTREE' 'BDNI_SORTIE'`

Additionnellement, trois arguments facultatifs peuvent être passés au script :

* --fraction : fraction de la BDNI sur laquelle travailler. Utile pour le débuggage.
* --insee : nom du tableau des mouvements de commune INSEE à utiliser. "insee.csv" par défaut
* --laposte : nom du tableau de la poste à utiliser. "laposte_hexasmal.csv" par défaut

Voilà un exemple de la commande permettant de lancer avec tous ses arguments :

`python3 fix_bdni.py 'BDNI_ENTREE' 'BDNI_SORTIE' --fraction 0.5 --insee 'insee.csv' --laposte 'laposte_hexasmal.csv'`

### Sorties

Ce script ajoute des colonnes à la BDNI :

* Le code INSEE avant correction
* Le code INSEE après correction
* Le nom actuel de la commune
* Le code postal actuel de la commune  
* La transformation qui a été faite:
  * 0 si pas de changement
  * 1 si correction via historique des codes INSEE
  * 2 si correction via le nom de commune et le code postal
  * 3 si on a retrouvé les informations via le code INSEE
  * X si l'erreur n'a pas pu être corrigée

### Dépendances

Pour s'exécuter, le script a besoin que python et sa librairie [pandas](https://pandas.pydata.org/) soit installés sur votre environnement de travail.

### Crédits

Le script utilise une fonction de barre de progression trouvée [ici](https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters).

## Modélisation de la propagation d'un agent pathogène sur réseau de contact

Le script de modélisation de la propagation d'un agent pathogène sur réseau de contact est `model.py`.

### Exécution du script

Ce script peut également être exécuté a partir d'un terminal avec la commande `python3`.

Ce script ne prend pas d'arguments en entrée à l'heure actuelle, mais un travail est en cours afin de permettre de lui passer en arguments un nombre de répétitions à effectuer, sur quel réseau et pour quel scénario.

Afin de s'exécuter, le script a besoin que le dossier `networks` soit dans le même répertoire.

### Sorties

Ce script produit trois fichiers .csv reprenant la dynamique épidémiologique pour chaque état (S,I,R) par pas de temps.

### Dépendances

Pour s'exécuter, le script a besoin que python soit installé sur votre environnement de travail. Il a également besoin des librairies suivantes :

* [numpy](https://numpy.org/doc/stable/user/index.html)
* [pandas](https://pandas.pydata.org/)
* [rich](https://rich.readthedocs.io/en/stable/introduction.html)
* [tqdm](https://github.com/tqdm/tqdm)

