#!/usr/bin/env python3

import argparse
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

## GESTION DES ARGUMENTS ## 

# Création du parser
parser = argparse.ArgumentParser('Mise à jour des adresses de la BDNI')
# Nom du fichier BDNI à corriger
parser.add_argument(
    "BDNI_in",
    help="nom du fichier BDNI à corriger",
    type=str
)
# Nom du fichier à écrire en sortie
parser.add_argument(
    "BDNI_out",
    help="nom du fichier à écrire en sortie",
    type=str
)
# Fraction sur laquelle exécuter le code
parser.add_argument(
    "--fraction",
    help="fraction de la BDNI sur laquelle exécuter le script",
    required=False,
    type=float,
    default=1
)
# Table INSEE
parser.add_argument(
    "--insee", "-i",
    help="nom du fichier INSEE à utiliser. défaut: 'insee.csv'",
    required=False,
    type=str,
    default='entrees-bdni/insee.csv'
)
# Table laposte
parser.add_argument(
    "--laposte", "-lp",
    help="nom du fichier La Poste à utiliser. défaut: 'laposte_hexasmal.csv'",
    required=False,
    type=str,
    default='entrees-bdni/laposte_hexasmal.csv'
)
# 
args = parser.parse_args()

### SCRIPT DE REMPLACEMENT DE DONNEES DANS LA BDNI ###

# Pour lancer le script : 
# python3 fix_bdni.py fichier_entree fichier_sortie --fraction --insee --laposte
# fichier_entree : Fichier BDN.EXPLOITATION à passer au script.
# fichier_sortie : Fichier corrigé qui sera exporté par le script.
# --fraction : fraction de la BDNI sur laquelle travailler. Utile uniquement le temps de coder le script, on pourra s'en passer après.
# --insee : nom du tableau des mouvements de commune INSEE à utiliser. insee.csv par défaut
# --laposte : nom du tableau de la poste à utiliser. laposte_hexasmal.csv par défaut

# On utilise la fonction 'apply' de pandas qui nous permet d'appliquer une fonction à chaque ligne d'un DataFrame.
# La fonction en question sera 'fix_code', chargée de trouver quelle modification doit être faite et de la faire.

# On ajoute des colonnes à la BDNI :
#   - Le code INSEE avant  
#   - Le code INSEE après    
#   - Le nom actuel de la commune   
#   - Le code postal actuel de la commune  
#   - La transformation qui a été faite: 
#       - 0 si pas de changement
#       - 1 si correction via historique des codes INSEE
#       - 2 si correction via le nom de commune et le code postal
#       - 3 si on a retrouvé les informations via le code INSEE 
#       - X si l'erreur n'a pas pu être corrigée

## FONCTIONS ##

# Barre de progression
# Crédits : https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
    
# Fonction de récupération des arguments
def get_args():
    # Lecture des arguments passés au script
    # Argument 1 : nom de la BDNI à mettre à jour
    # Argument 2 : nom du fichier de sortie
    str_in = args.BDNI_in
    str_out = args.BDNI_out
    str_insee = args.insee
    str_laposte = args.laposte

    return(str_in, str_out, str_insee, str_laposte)

# Fonction corrigeant la BDNI
def fix_code(row, df_bdni, df_laposte, df_valide, df_move_code, df_move_cp):

    # Cas 0 : la combinaison code insee et nom de commune est déjà bonne
    if row['CC_NOM'] in df_valide.values:
        row['TRANSFO'] = "0"
    
    # Cas 1 : CORRECTION VIA INSEE 
    # Le code commune extrait ne correspond pas à un code commune existant
    # Il pourra alors être présent dans move_code, qui recense les anciens codes communes 
    # On utilise le tableau move_code afin de n'appliquer la méthode qu'à des codes qu'il est possible de corriger ainsi
    elif row['OLD_CC'] in df_move_code['COM_AV'].values:
        # On attribue à NV_CC le nouveau code commune            
        row['NV_CC'] = df_move_code['COM_AP'].loc[df_move_code['COM_AV']==row['OLD_CC']].values[0]
        # On attribue à NV_COMMUNE le nouveau nom de commune                            
        row['NV_COMMUNE'] = df_move_code['NCC_AP'].loc[df_move_code['COM_AP']==row['NV_CC']].values[0]                        
        # On va chercher le nouveau code postal dans le tableau de la poste    
        new_CP = df_laposte['Code_postal'].loc[df_laposte['Code_commune_INSEE']==row['NV_CC']].values
        # On est obligé de vérifier s'il y a plusieurs éléments dans new_CP                   
        if len(new_CP) == 0:
           # On attribue à NV_CP le nouveau code postal                                                                                            
           row['NV_CP'] = new_CP                                                                                                                                                       
        else:
            row['NV_CP'] = new_CP[0]                                                                    
        # On attribue à TRANSFO le code correspondant à une correction via l'INSEE    
        row['TRANSFO'] = "1"                                                                                            
        
    # Cas 2 : CORRECTION VIA CODE POSTAL ET NOM DE COMMUNE
    # Le code commune extrait ne correspond à rien que l'on retrouve dans la table INSEE
    # On utilise alors le code postal et le nom de commune pour trouver un code commune y correspondant
    elif row['CP_NOM'] in df_move_cp['CP_NOM'].values:
        # On attribue à NV_CC le nouveau code commune
        row['NV_CC'] = df_move_cp['Code_commune_INSEE'].loc[df_move_cp['CP_NOM']==row['CP_NOM']].values[0]    
        # On attribue à NV_COMMUNE le nouveau nom de commune                
        row['NV_COMMUNE'] = df_move_cp['Nom_commune'].loc[df_move_cp['CP_NOM']==row['CP_NOM']].values[0]
        # On attribue à NV_CP le nouveau code postal                      
        row['NV_CP'] = df_move_cp['Code_postal'].loc[df_move_cp['CP_NOM']==row['CP_NOM']].values[0]                           
        # On attribue à TRANSFO le code correspondant à une correction via Code postal
        row['TRANSFO'] = "2"

    # Cas 3 : On ne peut apporter aucun changement car le code INSEE extrait ne correspond pas à un vrai code INSEE ou bien il est déjà correct
    # C'est un cas où la correction à suivre sera simple si le code INSEE est correct mais que certaines informations de la ligne ont changé
    # Mais c'est un cas à priori incorrigible si le code ne correspond à rien que l'on connaisse
    else:       
        # Cas 3.1 : Le code INSEE est bon, il s'agit juste de mettre à jour les autres informations
        if row['OLD_CC'] in df_laposte['Code_commune_INSEE'].values:
            # Le code commune reste inchangé    
            row['NV_CC'] = row['OLD_CC']
            # On attribue à NV_COMMUNE le nouveau nom de commune                                                                                
            row['NV_COMMUNE'] = df_laposte['Nom_commune'].loc[df_laposte['Code_commune_INSEE']==row['NV_CC']].values[0]
            # On attribue à NV_CP le nouveau code postal 
            row['NV_CP'] = df_laposte['Code_postal'].loc[df_laposte['Code_commune_INSEE']==row['NV_CC']].values[0]      
            # On attribue à TRANSFO le code correspondant à cette correction
            row['TRANSFO'] = "3"                                                                                        

        # Cas 3.2 : Le code INSEE n'est pas un code INSEE existant et toutes les méthodes précédentes n'ont pas permis de trouver le bon
        else:
            # On attribue à TRANSFO la valeur 'X'
            row['TRANSFO'] = "X" 

    
    i_bar_pos = row.name    
    print_progress_bar(i_bar_pos, len(df_bdni)-1, length = 38)

    return row
   
# Fonction d'importation des données
def import_data(str_in, str_insee, str_laposte):
    # Affichage
    print("[- \t Importation des données \t -]")
    # Barre de progression
    i_bar_length = 5
    print_progress_bar(0, i_bar_length, length=38)

    # Déclaration des noms pour les colonnes de la BDNI
    l_bdni_names = ["COD_PAYS", "NUM_EXP", "TYP_EXP", "NOM_EXP", "COD_SIT", "ADR1", "ADR2", "COD_POST", "COMMUNE",
                  "SIRET", "COD_PAYS_DET", "NUM_DET", "X_L_ADR", "Y_L_ADR", "REF_L_ADR", "DAT_VSE", "APP", "DAT_CRE", "STATUT"]
    print_progress_bar(1, i_bar_length, length=38)
    # Importation de la BDNI
    df_bdni = pd.read_csv(str_in, sep=';', encoding="iso-8859-1",
                       names=l_bdni_names, dtype=object)
    # /!\ On travaille sur le fichier BDN.EXPLOITATION tel que modifié dans le Jupyter Lab 'explore.ipynb'
    print_progress_bar(2, i_bar_length, length=38)
    # Importation de la table des changements de communes de l'INSEE
    df_insee = pd.read_csv(str_insee, dtype=object)
    print_progress_bar(3, i_bar_length, length=38)
    # Importation de la table de corresponde code INSEE/CP de la Poste
    df_laposte = pd.read_csv(str_laposte, sep=';', dtype=object)
    print_progress_bar(4, i_bar_length, length=38)

    # Ajout des nouvelles colonnes à la BDNI

    # Code commune extrait du numéro d'exploitation
    df_bdni['OLD_CC'] = df_bdni['NUM_EXP'].str[:5]
    # Nouveau code commune, inchangé par défaut
    df_bdni['NV_CC'] = df_bdni['OLD_CC']
    # Nouveau nom de commune, inchangé par défaut
    df_bdni['NV_COMMUNE'] = df_bdni['COMMUNE']
    # Nouveau code postal, inchangé par défaut
    df_bdni['NV_CP'] = df_bdni['COD_POST']
    # Type de transformation effectuée, aucune par défaut
    df_bdni['TRANSFO'] = "0"
    print_progress_bar(5, i_bar_length, length=38)

    print("> Données importées \n")

    return(df_bdni, df_insee, df_laposte)

# Fonction créant les DataFrames secondaires utiles à l'exécution du script
def create_dataframes(df_bdni, df_insee, df_laposte):
    # CAS NUL
    # Initialisations servant à identifier les cas où la combinaison code commune et nom de commune est déjà la bonne
    # On crée la combinaison en question
    df_bdni['CC_NOM'] = df_bdni['OLD_CC'] + df_bdni['COMMUNE']
    df_val = df_laposte['Code_commune_INSEE'] + df_laposte['Nom_commune']

    # INSEE
    # Initialisations servant à corriger la BDNI grâce à l'historique des mouvements de l'INSEE
    # On crée un DataFrame contenant tous les codes communes extraits de la BDNI :
    # Récupère les codes
    df_codes_communes = pd.DataFrame(df_bdni['OLD_CC'])
    df_codes_communes = df_codes_communes.rename(
        columns={'OLD_CC': 'COD_COM'})  #  Renomme la colonne
    # Ne garde qu'une ligne par code commune
    df_codes_communes = df_codes_communes.drop_duplicates()
    # On construit un DataFrame contenant tous les codes communes à changer :
    codes_to_change = df_codes_communes.query('COD_COM not in @df_laposte["Code_commune_INSEE"]')
    # Qui est utilisé pour créer un DataFrame contenant les mouvements des communes qui nous intéressent :
    # Récupère les lignes qui nous intéressent
    df_move_cc = df_insee.query('COM_AV in @codes_to_change["COD_COM"]')
    # Supprime les lignes où il n'y a pas de changement de code
    df_move_cc = df_move_cc.loc[df_move_cc['COM_AV'] != df_move_cc['COM_AP']]
    # Supprime les mouvements en double
    df_move_cc.drop_duplicates(['COM_AV', 'COM_AP'])

    # CODE POSTAL ET NOM DE COMMUNE
    # Initialisations servant à corriger la BDNI grâce à la combinaison code postal et nom de commune
    # Combinaison des noms de commune et code postaux permettant de retrouver des codes INSEE
    df_bdni['CP_NOM'] = df_bdni['COD_POST'] + df_bdni['COMMUNE']
    # Création du DataFrame qui permettra de travailler sur cette combinaison
    df_move_cpo = df_laposte.drop_duplicates(['Nom_commune', 'Code_postal'])
    df_move_cpo['CP_NOM'] = df_move_cpo['Code_postal'] + df_move_cpo['Nom_commune']
    df_move_cpo = df_move_cpo.query('CP_NOM in @df_bdni["CP_NOM"]')

    return(df_bdni,df_val, df_move_cc, df_move_cpo)

# Fonction de sortie du nouveau fichier
def write_file(str_filename,dataframe):
    print("[- \t Ecriture du nouveau fichier \t -]")
    print_progress_bar(0, 1, length=38)
    # On écrit le tableau de sortie
    dataframe.to_csv(str_filename, index=False)
    print_progress_bar(1, 1, length=38)
    print(">", str_filename, "écrit \n")

## MAIN ##
def main():

    try:
        
        # Ces variables sont nécessaires à la bonne exécution du script
        #global df_bdni, df_insee, df_laposte, df_valide, df_move_code, df_move_cp

        # Affichage de départ
        print("\t  CORRECTION DE LA BDNI")
        print("############################################\n")

        # Récupération des arguments
        str_input, str_output, str_insee, str_laposte = get_args()
        # Importation des données
        df_bdni, df_insee, df_laposte = import_data(str_input, str_insee, str_laposte)        
        # Création des DataFrames utiles
        df_bdni, df_valide, df_move_code, df_move_cp = create_dataframes(df_bdni,df_insee,df_laposte)

        # Travail sur une fraction des données
        df_bdni = df_bdni.sample(frac=args.fraction, ignore_index=True) 

        ## CORRECTION DE LA BDNI ##

        # Affichage et barre de progression
        print("[- \t Mise à jour de la base \t -]")
        print_progress_bar(0, len(df_bdni)-1, length = 38)

        # Tri de la base qui sert pour la barre de progression (basée sur l'index)
        df_bdni.sort_index(inplace=True)

        # Correction de la BDNI
        df_bdni.apply(fix_code, axis=1, args=(df_bdni,df_laposte,df_valide,df_move_code,df_move_cp))

        # Suppression des colonnes temporaires
        df_bdni.drop(['CC_NOM','CP_NOM'], inplace= True, axis=1)

        # Affichage de correction
        print("> Base mise à jour \n")

        ## SORTIE ##

        # Ecriture du fichier de sortie  
        write_file(str_output,df_bdni)

    ## GESTION DE POTENTIELLES ERREURS ##

    # Interruption du script
    except KeyboardInterrupt:
        print("\n")
        print("Ctrl-C : Arrêt du programme")

    # Nom de fichier introuvable
    except FileNotFoundError:
        print("\n")
        print("Erreur : Fichier introuvable")

if __name__ == "__main__":
    main()