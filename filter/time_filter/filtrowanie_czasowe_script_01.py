import os
import shutil
import sys
import json
from bson import json_util, ObjectId
import pprint
import datetime
import time

home = os.path.dirname(os.path.abspath(__file__))+'/'
sciezka_analizy=home+'dobre_czasowo/'
sciezka_detekcji='/media/slawekstu/CREDO1/Api/credo-data-export/detections/'
'''
--------------------------------------------------------------------------------------------
zadania tego skryptu sa realizowane w dwoch krokach
1) wyodrebnienie samych visible
2) utworzenie drzewa katalogow z plikami=device_id w nazwie

w folderze sciezka_analizy znajduja sie detekcje po device_id w katalogach jak dni
w folderze sciezka_analizy sa tez tymczasowe pliki json, te tylko z visible:true
--------------------------------------------------------------------------------------------
'''



list_path_to_folder = []
list_path_to_device_ide_file = []


def if_visible_rewrite_to_new_localization(plik_json):
    zawartosc_json = {'detections':[]}
    try:
        with open(sciezka_detekcji+plik_json) as json_file:
            data = json.load(json_file)
            for item in data['detections']:
                if item['visible'] == True:
                    zawartosc_json['detections'].append(item)


        json_object = json.loads(json_util.dumps(zawartosc_json))

        path_to_file = sciezka_analizy+'temp/'+plik_json
        with open(path_to_file,'w') as visible_file:
            json.dump(json_object, visible_file, indent=4)
    except Exception as e:
        print('Exception: %s'%e)


def utworz_foldery(plik_json):
    try:
        with open(sciezka_analizy+'temp/'+plik_json) as json_file:
            data = json.load(json_file)
            for item in data['detections']:
                sprawdz_i_przygotuj(item)

    except Exception as e:
        print('PLIK PRAWDOPODOBNIE USZKODZONY: %s'%plik_json)


def sprawdz_i_przygotuj(item):
    value = int(item['timestamp']/1000)
    value = datetime.datetime.fromtimestamp(value)
    # print(value)
    year,month,day =  f'{value:%Y}',f'{value:%m}',f'{value:%d}'
    path_to_folder = sciezka_analizy+'/%s/%s/%s'%(year,month,day)


    if path_to_folder not in list_path_to_folder:
        # print(path_to_folder)
        list_path_to_folder.append(path_to_folder)

        if os.path.exists(path_to_folder) == False:
            os.makedirs(path_to_folder, exist_ok=True)

    #czy tworzyc nowy plik?
    filename = '%s.json'%(item['device_id'])
    path_to_device_id_file = path_to_folder+'/'+filename
    if path_to_device_id_file not in list_path_to_device_ide_file:
        # sys.stdout.write('Proba utworzenia pliku: %s\r'%(path_to_device_id_file))
        # sys.stdout.flush()
        list_path_to_device_ide_file.append(path_to_device_id_file)

    if os.path.exists(path_to_device_id_file) == False:
        utworz_nowy_plik(path_to_device_id_file)


def utworz_nowy_plik(path_to_file):
    try:
        dictionary ={'detections':[]}
        json_object = json.dumps(dictionary, indent = 4)
        with open(path_to_file, 'w') as outfile:
            outfile.write(json_object)
    except Exception as e:
        print(e)
