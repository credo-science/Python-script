import os
import sys
import json
from bson import json_util, ObjectId
import pprint
import time
import datetime


podsumowanie = {}
plik_statystyki = 'podsumowanie_czas.json'

def get_list_of_artefacts_timestamp(timestamps):
    N = len(timestamps)
    if N <= 10:
        return []
    else:

        remove_ts_list = []
        id_sprawdzanego = 0

        #waraint gdy sprwadzamy jak pogrupowal
        ts_vector = []

        for i in range(N):
            abs_diff = abs(timestamps[id_sprawdzanego] - timestamps[i])

            if abs_diff < 60000:
                ts_vector.append(timestamps[i])
            else:
                len_time_vector = len(ts_vector)
                if len_time_vector > 10:
                    #waraint gdy sprwadzamy jak pogrupowal
                    remove_ts_list.append(ts_vector)
                    ts_vector = []

                #ustaw id sprawdzanego na nestepne
                id_sprawdzanego = i

        return remove_ts_list


def right_detections(year,month,path_to_file):
    dictionary = {}

    with open(path_to_file) as json_file:
        dictionary = json.load(json_file)

        timestamps = list()
        for item in dictionary['detections']:
            timestamps.append(item['timestamp'])


    remove_ts_list = get_list_of_artefacts_timestamp(timestamps)
    remove_ts_list = [y for x in remove_ts_list for y in x]
    remove_ts_list = list(set(remove_ts_list))


    lista_poprawne = []

    for item in dictionary['detections']:
        ts = item['timestamp']
        if ts not in remove_ts_list:
            # print('right detections: %d'%ts)
            lista_poprawne.append(item)

    path_to_file2 = path_to_file.replace('_VISIBLE.json','.json')

    #uzupelnienie podsumowania o visible
    # print('%s\tALL: %d\tRIGHT: %d'%(path_to_file,len(dictionary['detections']),len(lista_poprawne)))
    zaktualizuj_podsumowanie_dict(year,month,len(dictionary['detections']),len(lista_poprawne),0)

    dictionary = { 'detections':[]}
    dictionary['detections'] = lista_poprawne
    json_object = json.loads(json_util.dumps(dictionary))

    with open(path_to_file2,'w') as json_file:
        json.dump(json_object, json_file, indent=4)


def zaktualizuj_podsumowanie_dict(year,month,visible=0,dobre_czasowo=0,dobre_graficznie=0):
    if year not in podsumowanie:
        podsumowanie[year] = {}
    if month not in podsumowanie[year]:
        podsumowanie[year][month] = {}
    if 'visible' not in podsumowanie[year][month]:
        podsumowanie[year][month]['visible'] = 0
    if 'dobre_czasowo' not in podsumowanie[year][month]:
        podsumowanie[year][month]['dobre_czasowo'] = 0
    if 'dobre_graficznie' not in podsumowanie[year][month]:
        podsumowanie[year][month]['dobre_graficznie'] = 0

    podsumowanie[year][month]['visible'] += visible
    podsumowanie[year][month]['dobre_czasowo'] += dobre_czasowo
    podsumowanie[year][month]['dobre_graficznie'] += dobre_graficznie


def zapisz_podsumowanie_do_pliku():
    try:
        #print(podsumowanie)

        #jesli podsumowanie istnialo to trzeba je zaktualizowac (dodac nowe wartosci)
        if os.path.exists(plik_statystyki):
            with open(plik_statystyki) as podsumowanie_file:
                podsumowanie2 = json.load(podsumowanie_file)
            for year, year_content in podsumowanie2.items():
                for month,month_content in year_content.items():
                    zaktualizuj_podsumowanie_dict(
                        year,
                        month,
                        month_content['visible'],
                        month_content['dobre_czasowo'],
                        month_content['dobre_graficznie'])

        with open(plik_statystyki,'w+') as f:
            f.write(json.dumps(podsumowanie, indent=4, sort_keys=True))

        podsumowanie.clear()

    except Exception as e:
        print('Exception: %s'%e)
    #print(podsumowanie)
