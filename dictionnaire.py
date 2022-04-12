import json
import random

def get_mots(nombre_mots = None):
    """
    Retourne les mots du dictionnaire
    args: nombre_mots (int) : nombre de mots à retourner (None pour tous)
    """

    with open("dictionnaire_cemantix.json", "r", encoding="utf_8") as fichier:
        
        dict_cemantix = json.load(fichier)

        mots = []

        if nombre_mots is None:
            return dict_cemantix
        else:
            while len(mots) < nombre_mots:
                mot = random.choice(dict_cemantix)
                if mot not in mots:
                    mots.append(mot)
            return mots

if __name__ == "__main__":
    print(get_mots(10))


