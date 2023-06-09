# Improving farm geolocation to predict pathogen circulation in cattle herds in Loire-Atlantique, France

The purpose of this git repository is to provide the scripts for correcting the National Animal Identification Database and for modeling the spread of a pathogen over a contact network, which were produced during my M1 MODE internship with INRAE's DYNAMO team.

You can download the entire contents of this repository for testing on your machine via the `Code` button then `Download ZIP` or by cloning the repository at home.

---

## Contents

1. [BDNI correction](#bdni)
   * Execution](#execscript)
   * [Outputs](#sortiescript)
   * [Dependencies](#depscript)
   * [Credits](#credits)

2. [Pathogen spread model](#model)
   * [Execution](#execmodel)
   * Outputs](#sortiemodel)
   * [Dependencies](#depmodel)

3. [Useful links](#liens)

---

## BDNI correction <a name="bdni"></a>

The BDNI correction script is `fix_bdni.py`.

All files required for the script are contained in the `entrees-bdni` folder.

The script cannot be run without a BDNI file to correct. The data contained in the BDNI is considered sensitive. For this reason, it is not possible to give access to this data file to test the script execution.

Instead, a dummy BDNI file has been created. It contains only 200 entries, to save you a long execution time. Sensitive columns have been neutralized. This file is `BDN.EXPLOITATION`.

### Exécution du script <a name="execscript"></a>

Ce script peut être exécuté à partir d'un terminal grâce à la commande `python3`.

L'exécution de ce script doit recevoir deux arguments positionnels (à fournir dans le bon ordre) :

* Le premier argument est le nom du fichier BDNI à corriger
* Le deuxième argument est le nom du fichier corrigé à écrire.

Ces deux arguments sont obligatoires.

La commande minimale pour lancer le script est donc :

`python3 fix_bdni.py BDN.EXPLOITATION BDN.CORRIGE`

> Vous n'êtes pas obligé de nommer le fichier de sortie BDN.CORRIGE et pouvez renommer le fichier BDN.EXPLOITATION avant son utilisation.

Additionnellement, trois arguments facultatifs peuvent être passés au script :

* --fraction : fraction de la BDNI sur laquelle travailler. Utile pour le débuggage. 1 par défaut.
* --insee : nom du tableau des mouvements de commune INSEE à utiliser. "insee.csv" par défaut.
* --laposte : nom du tableau de la poste à utiliser. "laposte_hexasmal.csv" par défaut.

Voilà un exemple de la commande permettant de lancer le script avec tous ses arguments :

`python3 fix_bdni.py BDN.EXPLOITATION BDN.CORRIGE --fraction 0.5 --insee 'insee.csv' --laposte 'laposte_hexasmal.csv'`

### Sorties du script <a name="sortiescript"></a>

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

Il écrit ensuite un fichier au même format que le fichier passé en entrée, mais contenant les colonnes additionnelles.

### Dépendances du script <a name="depscript"></a>

Pour s'exécuter, le script a besoin que python et sa librairie [pandas](https://pandas.pydata.org/) soit installés sur votre environnement de travail.

### Crédits <a name="credits"></a>

Le script utilise une fonction de barre de progression trouvée [ici](https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters).

---

## Modélisation de la propagation d'un agent pathogène <a name="model"></a>

Le script de modélisation de la propagation d'un agent pathogène sur réseau de contact est `model.py`.

### Exécution du modèle <a name="execmodel"></a>

Ce script est exécuté a partir d'un terminal avec la commande `python3`.

Ce script ne prend pas d'arguments en entrée à l'heure actuelle, mais un travail est en cours afin de permettre de lui passer en arguments un nombre de répétitions à effectuer, sur quel réseau et pour quel scénario.

La commande pour lancer le modèle est donc :

`python3 model.py`

En l'état, il faut aller changer à la main les paramètres du scénario que l'on souhaite tester ainsi que le fichier de réseau à importer. Ces paramètres sont tous à changer au même endroit au début du script.

Afin de s'exécuter, le script a besoin que le dossier `networks` soit dans le même répertoire.

> L'exécution du modèle sur un nombre élevé de répétitions peut être (très) long. C'est pourquoi le nombre de répétitions par défaut sur la version présente dans ce dépôt est initialisée à 10 répétitions seulement.

### Sorties du modèle <a name="sortiemodel"></a>

Ce script produit quatre fichiers :

* dynamique_S.csv : Nombre de noeuds à l'état S pour chaque pas de temps.
* dynamique_I.csv : Nombre de noeuds à l'état I pour chaque pas de temps.
* dynamique_R.csv : Nombre de noeuds à l'état R pour chaque pas de temps.
* epidemy_Size.csv : Nombre cumulé du nombre de noeuds infectés à chaque pas de temps (les noeuds ne sont comptés qu'une fois).

Ces fichiers sont écrits par défaut dans le répertoire `sorties-modele`.

### Dépendances du modèle <a name="depmodel"></a>

Pour s'exécuter, le script a besoin que python soit installé sur votre environnement de travail. Il a également besoin des librairies suivantes :

* [numpy](https://numpy.org/doc/stable/user/index.html)
* [pandas](https://pandas.pydata.org/)
* [rich](https://rich.readthedocs.io/en/stable/introduction.html)
* [tqdm](https://github.com/tqdm/tqdm)

---

## Liens utiles <a name="liens"></a>

Les fichiers fournis dans le git permettent de lancer le script sans problème. Néanmoins ces fichiers sont mis à jour régulièrement. Il est donc possible que ceux que vous trouverez ici ne soient plus complètement à jour.

Vous pouvez récupérer les derniers fichiers ici :

* [La Poste](https://datanova.laposte.fr/explore/dataset/laposte_hexasmal/information/?disjunctive.code_commune_insee&disjunctive.nom_de_la_commune&disjunctive.code_postal&disjunctive.ligne_5)
* [Insee](https://www.insee.fr/fr/information/6051727)

> L'Insee propose de télécharger un ensemble de fichiers. Celui qui nous intéresse pour corriger la BDNI est mvtcommune_202X.csv
