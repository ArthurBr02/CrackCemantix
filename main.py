from datetime import datetime
import json
import os
from time import sleep
import requests
from gensim.models import KeyedVectors
import dictionnaire

model: KeyedVectors = KeyedVectors.load_word2vec_format("frWac_postag_no_phrase_700_skip_cut50.bin", binary=True, unicode_errors="ignore")

data = {"max": {"mot": "", "score": 0}}
mots = []

data["positive"] = []
data["negative"] = []
data['errors'] = []
data["mots"] = {}

print(len(mots))

NB_MOTS = 4000
DATE_DEBUT = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

mots = dictionnaire.get_mots(nombre_mots=NB_MOTS)

print(str(len(mots)) + " mots à traiter")
if NB_MOTS < 100:
    print(str(mots))

if not os.path.exists(f"./Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json"):
    f = open(f"Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json", "w", encoding="utf_8")
    f.write("{}")
    f.close()

data_file = open(f"Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json", "r", encoding="utf_8")
data_json = json.load(data_file)
data_file.close()

index = 1

for key in data_json.keys():
    if key not in mots:
        mots.append(key)

for mot_final in mots:
    mot = mot_final.split('_')[0]

    if mot_final in data_json.keys():
        data['mots'][mot] = data_json[mot_final]
        # print(data_json[mot_final])
        # if data['mots'][mot]['score'] > 0:
        #     data['positive'].append(mot)
        # else:
        #     data['negative'].append(mot)
    else:    
        payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"word\"\r\n\r\n{mot}\r\n-----011000010111000001101001--\r\n"
        headers = {"Content-Type": "multipart/form-data; boundary=---011000010111000001101001"}

        data['mots'][mot] = requests.post("https://cemantix.herokuapp.com/score", data=payload, headers=headers).json()
        sleep(0.6)
        
    if "score" in data['mots'][mot].keys():

        #mot_final = definition_mot.get_formatted_mot(mot)
        if mot_final is not None:
            if data['mots'][mot]["score"] > 0:
                data["positive"].append(mot_final)
                if data['mots'][mot]["score"] > data["max"]["score"]:
                    data["max"]["score"] = data['mots'][mot]["score"]
                    data["max"]["mot"] = mot_final
            else:
                data["negative"].append(mot_final)
        data_json[mot_final] = data['mots'][mot]
        print(str(index) + " - " + mot + " " + str(data['mots'][mot]))
    else:
        if mot in data["mots"]:
            del data["mots"][mot]
        if mot_final in data["positive"]:
            data["positive"].remove(mot_final)
        if mot_final in data["negative"]:
            data["negative"].remove(mot_final)
        data["errors"].append(mot_final)
    
    index += 1

data_file = open(f"Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json", "w", encoding="utf_8")
data_file.write(json.dumps(data_json, indent=4))
data_file.close()

print(str(len(data["positive"]) + len(data["negative"])) + " mots conservés")

index = 1

pos_old = -1
neg_old = -1
m_facteur = 0.8
moyenne = 0

while data["max"]["score"] != 1.0:

        data_file = open(f"Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json", "r", encoding="utf_8")
        data_json = json.load(data_file)
        data_file.close()

        for mot_pos in data["positive"]:
            #mot_final = definition_mot.get_formatted_mot(mot_pos)
            mot_final = mot_pos
            # print("debug 1.1")
            if mot_final is not None:
                index_mot = model.get_index(mot_final)
                if index_mot is None:
                    print("Mot non trouvé: " + mot_final)
                    data["positive"].remove(mot_pos)
        
        # print("debug 2")
        for mot_neg in data["negative"]:
            # mot_final = definition_mot.get_formatted_mot(mot_pos)
            mot_final = mot_neg
            # print("debug 2.1")
            if mot_final is not None:
                index_mot = model.get_index(mot_final)
                if index_mot is None:
                    data["negative"].remove(mot_pos)
        # print("debug 3")
        most_similar_list = model.most_similar(positive=data["positive"], negative=data["negative"], topn=150)
        # print(most_similar_list)
        # print("debug 4")
        for mot in most_similar_list:

            if mot[0] in data["errors"]:
                continue

            if mot[0].split("_")[0] not in data['mots'].keys():

                if mot[0] in data_json.keys():
                    data['mots'][mot[0].split("_")[0]] = data_json[mot[0]]
                else:
                    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"word\"\r\n\r\n{mot[0].split('_')[0]}\r\n-----011000010111000001101001--\r\n"
                    headers = {"Content-Type": "multipart/form-data; boundary=---011000010111000001101001"}
                    data['mots'][mot[0].split("_")[0]] = requests.post("https://cemantix.herokuapp.com/score", data=payload, headers=headers).json()
                    sleep(0.6)
                
                if "score" in data['mots'][mot[0].split('_')[0]].keys():
                    data_json[mot[0]] = data['mots'][mot[0].split('_')[0]]
                    if data['mots'][mot[0].split('_')[0]]["score"] > moyenne:
                        data["positive"].append(mot[0])
                    else:
                        data["negative"].append(mot[0])
                    if data["max"]["score"] < data['mots'][mot[0].split('_')[0]]["score"]:
                        data["max"]["score"] = data['mots'][mot[0].split('_')[0]]["score"]
                        data["max"]["mot"] = mot[0].split('_')[0]
                    #data[mot[0]] = {}
                    #data[mot[0]]["score"] = data[mot[0].split('_')[0]]["score"]
                else:
                    if mot[0].split('_')[0] in data["mots"]:
                        del data["mots"][mot[0].split('_')[0]]
                    if mot[0] in data["positive"]:
                        data["positive"].remove(mot[0])
                    if mot[0] in data["negative"]:
                        data["negative"].remove(mot[0])
                    data["errors"].append(mot[0])
        print(str(index)  + " - " + data["max"]["mot"] + " " + str(data["max"]["score"]))

        positifs = data["positive"]
        negatifs = data["negative"]

        pos_len = len(positifs)
        neg_len = len(negatifs)
        
        print("Pos len: " + str(pos_len) + " Neg len: " + str(neg_len))
        print("Pos old: " + str(pos_old) + " Neg old: " + str(neg_old))

        if neg_len == neg_old and pos_len == pos_old:
            print("neg_len == neg_old and pos_len == pos_old")
            #m_facteur = m_facteur - 0.1
            negatifs = []
        else:
            if pos_len != pos_old:
                pos_old = pos_len

            if neg_len != neg_old:
                neg_old = neg_len

        moyenne = 0

        for valeur in positifs:
            moyenne += data['mots'][valeur.split("_")[0]]["score"]
        for valeur in negatifs:
            moyenne += data['mots'][valeur.split("_")[0]]["score"]
        moyenne = moyenne / (len(positifs) + len(negatifs))

        data["positive"] = []
        data["negative"] = []

        for valeur in positifs:
            if data['mots'][valeur.split("_")[0]]["score"] >= moyenne:# * m_facteur:
                data["positive"].append(valeur)
            else:
                data["negative"].append(valeur)
        for valeur in negatifs:
            if data['mots'][valeur.split("_")[0]]["score"] >= moyenne:# * m_facteur:
                data["positive"].append(valeur)
            else:
                data["negative"].append(valeur)

        data_file = open(f"Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json", "w", encoding="utf_8")
        data_file.write(json.dumps(data_json, indent=4))
        data_file.close()

        index += 1

DATE_FIN = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

print("Fin")
print("Le mot est le suivant: " + data["max"]["mot"].split("_")[0] + " " + str(data["max"]["score"]))
print("Date de début: " + DATE_DEBUT)
print("Date de fin: " + DATE_FIN)



# Prendre une liste de mots, et récupérer celui avec la valeur la plus haute. Faire model.most_similar(positive=mot, topn=50), et faire une requête par mot. 
# Ensuite séparer chaque mot en positif et négatif selon si le score est > à celui du mot ou pas.