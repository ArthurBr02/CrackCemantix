import os
import json
from gensim.models import KeyedVectors

pronoms_cl = ['je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'le', 'lui', 'la', 'les', 'leur', 'moi', 'toi', 'se', 'ta', 'ce', 'ça', 'leur']
pronoms = ['soi', 'eux', 'en', 'y', 'mien', 'mienne', 'miens', 'miennes', 'tien', 'tienne', 'tiens', 'tiennes', 'sien', 'sienne', 'siens', 'siennes', 'nôtre', 'nôtres', 'vôtre', 'vôtres', 'leurs', 'ceci', 'cela', 'celui', 'celui-ci', 'celui-là', 'celle', 'celle-ci', 'celle-là', 'ceux', 'ceux-ci', 'ceux-là', 'celles', 'celles-ci', 'celles-là', 'aucun', 'chacun', 'onpersonne', 'quiconque', 'rien', 'tout', 'aucune', 'chacune', 'certains', 'certaines', 'beaucoup', 'peu', 'plusieurs', 'qui', 'que', 'dont', 'où', 'lequel', 'quoi', 'laquelle', 'lesquels', 'lesquelles', 'auquel', 'auxquels', 'auxquelles', 'desquels', 'desquelles']

def afficher_pronoms():
    """
    Affiche les pronoms
    """

    with open("./Dictionnaire/plover/pronoms.txt", 'r', encoding='utf-8') as fichier_principal:
        lignes = fichier_principal.read().split("\n")
        for mot in lignes:
            if mot not in pronoms_cl:
                pronoms.append(mot)
        print(pronoms)

def ajouter_fichier_fichier_principal(path, denomination):
    """
    Ajoute le fichier spécifié dans le dictionnaire
    """

    if not os.path.exists("./dictionnaire_complet.json"):
            file = open("./dictionnaire_complet.json", 'w')
            file.write("{}")
            file.close()
        
    with open("./dictionnaire_complet.json", 'r', encoding='utf-8') as fichier_principal:
        dictionnaire = json.load(fichier_principal)

    with open(path, 'r', encoding='utf-8') as fichier:
        fichier_a_traiter = json.load(fichier)
        for mot in fichier_a_traiter.values():
            if mot not in dictionnaire.keys() and not (mot.__contains__(" ") or mot.__contains__("'")):
                if mot in pronoms_cl:
                    dictionnaire[mot] = mot + "_cl"
                elif mot in pronoms:
                    dictionnaire[mot] = mot + "_pro"
                else:
                    dictionnaire[mot] = mot + "_" + denomination

    with open("./dictionnaire_complet.json", 'w', encoding='utf-8') as fichier_principal:
        json.dump(dictionnaire, fichier_principal, ensure_ascii=False, indent=4)

def generer_dictionnaire_cemantix():
    model: KeyedVectors = KeyedVectors.load_word2vec_format("frWac_postag_no_phrase_700_skip_cut50.bin", binary=True, unicode_errors="ignore")
    
    dictionnaire_cemantix = []

    keys = []

    result = model.key_to_index.items()
    for key in result:
        keys.append(key[0])

    with open("./dictionnaire_complet.json", 'r', encoding='utf-8') as fichier_principal:
        dictionnaire = json.load(fichier_principal)
        for mot in dictionnaire.values():
            # result = model.key_to_index[mot]
            # print(result)
            if mot in keys:
                dictionnaire_cemantix.append(mot)
                print(mot)

            # if result is not None:
            #     dictionnaire_cemantix.append(mot)
            #     print(mot)
    
    with open("./dictionnaire_cemantix.json", 'w', encoding='utf-8') as fichier_principal:
        json.dump(dictionnaire_cemantix, fichier_principal, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    # FICHIER_SOURCE = [("Dictionnaire/plover/03_French_Adverbes.json", "adv"), ("Dictionnaire/plover/04_French_Adjectifs.json", "a"), ("Dictionnaire/plover/05_French_Noms.json", "n"), ("Dictionnaire/plover/06_French_Verbes.json", "v")]
    # for fichier in FICHIER_SOURCE:
        # ajouter_fichier_fichier_principal(fichier[0], fichier[1])
    # afficher_pronoms()
    generer_dictionnaire_cemantix()