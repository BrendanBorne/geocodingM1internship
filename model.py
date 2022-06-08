#!/usr/bin/env python3

# Portion de script qui définit les conditions initiales du modèle de propagation SIRS sur réseau de contacts

# ---------------------------- LIBRAIRIES ----------------------------- #
import numpy as np
import pandas as pd
import math
import os
import click
from rich import print
from tqdm import tqdm
tqdm.pandas() # tqdm intègre pandas 
# --------------------------------------------------------------------- #

# Utilitaire pour l'affichage de lignes sur le terminal
terminal_Size = os.get_terminal_size().columns 

# ---------------------------- FONCTIONS ------------------------------ #
# Fonction d'initialisation de la matrice d'adjacence
def init_Matr(row):
    # Il y a un lien (1) pour chaque couple origine-destination
    matr_Adjacence[row['originID'],row['destID']] = 1
    return row

# Fonction d'initialisation de la metapopulation
def initialize_MetaPopulation(row):
    # On créé un node avec pour id l'ID du point correspondant
    node = Node(row['nodeID']) 
    # On peuple le vecteur contenant toute la metapopulation
    nodes_MetaPopulation.append(node) 
    return row
# --------------------------------------------------------------------- #

# ---------------------------- PARAMETRES ----------------------------- # 
#                                                                       #
# omega : taux de perte d'immunité  (1/omega = durée de l'immunité)     #
# gamma : taux de guérison          (1/gamma = durée de l'infection)    #
# beta : taux d'infection                                               #
# Tmax = durée de la simulation                                         #
# df = pas de temps                                                     #
# nb_Reps = nombre de répétitions                                       #
# --------------------------------------------------------------------- #

beta = 0.02
gamma = 1/20
omega = 1/100         
Tmax = 365
dt = 1
nb_Reps=10

# Importatation des données réseau
df_Links = pd.read_csv('networks/5km/reseau_geocode_5km.csv')
# Chemin pour les sorties
path = '' # Cette variable permet de choisir si l'on veut exporter les dynamiques dans un dossier précis

# --------------------------- CLASSE NODE ----------------------------- #
#                                                                       # 
# Variables :                                                           #
# dict_State : {'S':1, 'I':0, 'R':0}                                    #
#                                                                       #
# Fonctions :                                                           #
# set_State()                                                           #
# update_Infectes()                                                     #
#                                                                       #
# --------------------------------------------------------------------- # 

class Node:

    def __init__(self, id):
        self.id = id
        self.dict_State = {'S':1, 'I':0, 'R':0}

    def get_State(self):
        return self.dict_State

    def set_State(self, state):
        if state == 'S':
            self.dict_State['S'] = 1
            self.dict_State['I'] = 0
            self.dict_State['R'] = 0
        elif state == 'I':
            self.dict_State['S'] = 0
            self.dict_State['I'] = 1
            self.dict_State['R'] = 0
        elif state == 'R':
            self.dict_State['S'] = 0
            self.dict_State['I'] = 0
            self.dict_State['R'] = 1

    def dyn_Epi(self): # TODO : passer vec_VoisInf en paramètre
        # S -> I
        if self.dict_State['S'] == 1:
            # On calcule le taux d'infection en fonction du nombre de voisins
            infection_rate = beta * vec_VoisInf[self.id]
            # On transforme le taux en probabilité
            infection_proba = 1 - math.exp(-infection_rate*dt)
            # On tire dans une loi binomiale avec cette probabilité
            infection = np.random.binomial(self.dict_State['S'], infection_proba)
            # Si on a 0, on n'a pas été infecté
            # Si on a 1, on a été infecté
            self.dict_State['S'] -= infection
            self.dict_State['I'] += infection
        # I -> R
        elif self.dict_State['I'] == 1:
            # On calcule le taux de guérison
            healing_rate = gamma
            # On transforme le taux en probabilité
            healing_proba = 1 - math.exp(-healing_rate*dt)
            # On tire dans une loi binomiale avec cette probabilité
            healing = np.random.binomial(self.dict_State['I'], healing_proba)
            # Si on a 0, on n'a pas guéri
            # Si on a 1, on a guéri
            self.dict_State['I'] -= healing
            self.dict_State['R'] += healing
        # R -> S
        elif self.dict_State['R'] == 1:
            # On calcule le taux de perte d'immunité
            immunity_loss_rate = omega
            # On transforme le taux en probabilité
            immunity_loss_proba = 1 - math.exp(-immunity_loss_rate*dt)
            # On tire dans une loi binomiale avec cette probabilité
            immunity_loss = np.random.binomial(self.dict_State['R'], immunity_loss_proba)
            # Si on a 0, on n'a pas perdu l'immunité
            # Si on a 1, on a perdu l'immunité
            self.dict_State['R'] -= immunity_loss
            self.dict_State['S'] += immunity_loss
        else:
            print('Erreur : pas de statut')

    def update_Infected(self):
        vec_Infectes[self.id] = self.dict_State['I']

# -------------------- IMPORTATION DES DONNEES ------------------------ #

# Le travail du script peut commencer
click.clear()
print('═' * terminal_Size)
print('[bold purple]INITIALISATION')
print('─' * terminal_Size)

# --------------------- CHEMINS RESEAU ET SORTIE --------------------- #


# On créé ensuite un DataFrame contenant les ID de nos nodes
df_nodes = pd.DataFrame(df_Links['originID'])
df_nodes.rename(columns={'originID':'nodeID'},inplace=True) 
df_nodes.drop_duplicates(inplace=True)

# On construit ensuite la métapopulation
print("Construction de la métapopulation...")

# Array qui contiendra les nodes
nodes_MetaPopulation = []

# Peuplement de l'array
df_nodes.progress_apply(initialize_MetaPopulation, axis=1)


# --------------------------------------------------------------------- #

# ---------------------- MATRICES ET VECTEURS ------------------------- #
#                                                                       #
# matr_Adjacence : matrice d'adjacence                  (A)             #
# vec_Infectes : vecteurs des infectes                  (P)             #
# vec_VoinsInf : vecteurs des voisins infectes          (M)             #
#                                                                       #
# --------------------------------------------------------------------- #      

# Construction de la matrice d'adjacence
print("\nConstruction de la matrice d'adjacence...")
# On trouve la taille de la matrice à créer
int_Size = np.max(df_Links['originID']) + 1
# On remplit une matrice de zéros de ladite taille
matr_Adjacence = np.zeros((int_Size,int_Size))
# On applique la fonction d'initialisation de la matrice
# tqdm remplace le apply() de pandas par progress_apply() qui affiche une barre de progression
df_Links.progress_apply(init_Matr,axis=1)

def initialize_Simulation(int_Size):
    # Réinitialisation de la metapop
    for n in nodes_MetaPopulation:
        n.set_State('S')
    # Infection du premier troupeau
    # On génère aléatoirement le numéro du premier troupeau infecté
    int_FirstInfected = np.random.randint(0,int_Size)
    #print("Le troupeau infecté est le troupeau numéro :", int_FirstInfected)
    # On attribue au node concerné le statut infecté
    nodes_MetaPopulation[int_FirstInfected].set_State('I')
    # Construction du vecteur d'infectés
    # Le vecteur de base ne contient que le premier infecté définit précédemment
    vec_Infectes = np.zeros(int_Size)
    vec_Infectes[int_FirstInfected] = 1
    # Construction du vecteur du nombre de voisins infectés
    # Ce vecteur est le résultat de la multiplication mathématique de la matrice d'adjacence par le vecteur des infectés
    vec_VoisInf = np.matmul(matr_Adjacence, vec_Infectes)

    return(vec_Infectes, vec_VoisInf)

print('─' * terminal_Size)
print('[bold purple]CALCULS')
print('─' * terminal_Size)

sortie_Dynamique_S = []
sortie_Dynamique_I = []
sortie_Dynamique_R = []

## ENREGISTRER LA TAILLE DU SET A CHAQUE PAS DE TEMPS
size_overTime = []

print("Propagation du pathogène sur", nb_Reps, "répétitions")

for x in tqdm(range(nb_Reps)):

    vec_Infectes, vec_VoisInf = initialize_Simulation(int_Size)

    total_I = set(())

    for t in tqdm(range(0, Tmax, dt),position=1,leave=False):

        # On va compter le nombre de S, I, R pour le pas de temps
        nb_S = 0
        nb_I = 0
        nb_R = 0

        for n in nodes_MetaPopulation:
            n.dyn_Epi()
            n.update_Infected()

            nb_S += n.dict_State['S']
            nb_I += n.dict_State['I']
            nb_R += n.dict_State['R']

            if n.dict_State['I'] == 1:
                total_I.add(n.id)

        vec_VoisInf = np.matmul(matr_Adjacence,vec_Infectes)

        # Sorties
        sortie_Dynamique_S.append([t, nb_S])
        sortie_Dynamique_I.append([t, nb_I])
        sortie_Dynamique_R.append([t, nb_R])

        size_overTime.append([t,len(total_I)])        


# Mise en forme des sorties
sortie_Dynamique_S = pd.DataFrame(sortie_Dynamique_S, columns=['t','S'])
sortie_Dynamique_I = pd.DataFrame(sortie_Dynamique_I, columns=['t','I'])
sortie_Dynamique_R = pd.DataFrame(sortie_Dynamique_R, columns=['t','R'])

size_overTime = pd.DataFrame(size_overTime, columns=['t','count'])

# Ecriture des sorties
print('Ecriture des fichiers...')
sortie_Dynamique_S.to_csv(path+'dynamique_S.csv', index=False)
sortie_Dynamique_I.to_csv(path+'dynamique_I.csv', index=False)
sortie_Dynamique_R.to_csv(path+'dynamique_R.csv', index=False)

size_overTime.to_csv(path+'epidemy_Size.csv',index=False)

print('═' * terminal_Size)