# Améliorer la géolocalisation des exploitations pour prédire la circulation d’agents pathogènes dans les troupeaux bovins en Loire-Atlantique

Ce dépôt git a pour objectif de mettre à disposition les scripts de correction de la Base Nationale d'Identification animale et de modélisation de la propagation d'un agent pathogène sur réseau de contact qui ont été produits au cours de mon stage de M1 MODE au sein de l'équipe DYNAMO de l'INRAE.

> Dépôt en cours de construction !

---

## Sommaire

1. [Correction de la BDNI](#bdni)
   * [Exécution](#execscript)
   * [Sorties](#sortiescript)
   * [Dépendances](#depscript)
   * [Crédits](#credits)

2. [Modélisation de la propagation d'un agent pathogène](#model)
   * [Exécution](#execmodel)
   * [Sorties](#sortiemodel)
   * [Dépendances](#depmodel)

3. [Liens utiles](#liens)

---

## Correction de la BDNI <a name="bdni"></a>

Le script de correction de la BDNI est `fix_bdni.py`.

Tous les fichiers nécessaires au script sont contenus dans le dossier `entrees-bdni`.

Le script n'est pas exécutable sans fichier BDNI à corriger. Les données contenues dans la BDNI sont des données considérées comme sensibles. C'est pourquoi il n'est pas possible de donner accès à ce fichier de données pour tester l'exécution du script.

A la place, un fichier BDNI factice a été créé. Il ne contient que 200 entrées pour vous éviter un temps d'exécution trop long. Les colonnes sensibles ont été neutralisées. Ce fichier est `BDN.EXPLOITATION`.

### Exécution du script <a name="execscript"></a>

Ce script peut être exécuté à partir d'un terminal grâce à la commande `python3`.

L'exécution de ce script doit recevoir deux arguments positionnels (à fournir dans le bon ordre) :

* Le premier argument est le nom du fichier BDNI à corriger
* Le deuxième argument est le nom du fichier corriger à écrire. Ces deux arguments sont obligatoires.

La commande minimale pour lancer le script est donc :

`python3 fix_bdni.py BDN.EXPLOITATION BDN.CORRIGE`

> Vous n'êtes pas obligé de nommer le fichier de sortie BDN.CORRIGE et pouvez renommer le fichier BDN.EXPLOITATION avant son utilisation.

Additionnellement, trois arguments facultatifs peuvent être passés au script :

* --fraction : fraction de la BDNI sur laquelle travailler. Utile pour le débuggage.
* --insee : nom du tableau des mouvements de commune INSEE à utiliser. "insee.csv" par défaut
* --laposte : nom du tableau de la poste à utiliser. "laposte_hexasmal.csv" par défaut

Voilà un exemple de la commande permettant de lancer avec tous ses arguments :

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

> L'exécution du modèle sur un nombre élevé de répétitions peut être (très) long. C'est pourquoi le nombre de répétitions par défaut sur la version présente dans ce dépôt est initialisée par défaut à 10 répétitions seulement.

### Sorties du modèle <a name="sortiemodel"></a>

Ce script produit trois fichiers .csv reprenant la dynamique épidémiologique pour chaque état (S,I,R) par pas de temps.

### Dépendances du modèle <a name="depmodel"></a>

Pour s'exécuter, le script a besoin que python soit installé sur votre environnement de travail. Il a également besoin des librairies suivantes :

* [numpy](https://numpy.org/doc/stable/user/index.html)
* [pandas](https://pandas.pydata.org/)
* [rich](https://rich.readthedocs.io/en/stable/introduction.html)
* [tqdm](https://github.com/tqdm/tqdm)

## Liens utiles <a name="liens"></a>
