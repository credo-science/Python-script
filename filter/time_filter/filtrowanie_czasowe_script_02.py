import os
import shutil
import sys
import json
from bson import json_util, ObjectId
import pprint
import datetime

from filtrowanie_czasowe_right_detections import *

home = os.path.dirname(os.path.abspath(__file__))+'/'
sciezka_analizy=home+'dobre_czasowo/'

detections = {}

def get_detections_dict():
    return detections


def clear_temp():
    try:
        shutil.rmtree(sciezka_analizy+'/temp')
        detections.clear()
    except Exception as e:
        print('NIE MOZNA USUNAC PLIKU - USZKODZONY: %s'%plik_json)


def zarzadzaj_dodawaniem_elementow(filename):
    with open(sciezka_analizy+'/temp/'+filename) as json_file:
        # print('trwa przetwarzanie pliku:\t%s'%filename)
        data = json.load(json_file)
        i=1
        for item in data['detections']:
            sys.stdout.write('File: %s\titem:\t%d\r'%(filename,i))
            sys.stdout.flush()
            i+=1
            dodaj_item_do_slownika(sciezka_analizy,item)


def dodaj_item_do_slownika(sciezka_analizy,item):
    value = int(item['timestamp']/1000)
    value = datetime.datetime.fromtimestamp(value)

    device_id = item['device_id']

    # print(value)
    year,month,day =  f'{value:%Y}',f'{value:%m}',f'{value:%d}'

    if year not in detections:
        detections[year] = {}
    if month not in detections[year]:
        detections[year][month] = {}
    if day not in detections[year][month]:
        detections[year][month][day] = {}
    if device_id not in detections[year][month][day]:
        detections[year][month][day][device_id] = []

    detections[year][month][day][device_id].append(item)


def rodziel_to_na_device_id_file(detections):
    # path_to_file = '%s/%s/%s/%s/%s.json'%('detekcje',year,month,day,item['device_id'])
    for year, year_content in detections.items():

        for month,month_content in year_content.items():

            for day,day_content in month_content.items():

                for device_id,device_id_content in day_content.items():

                    path_to_file = sciezka_analizy+'/%s/%s/%s/%s.json'%(year,month,day,device_id)
                    sys.stdout.write('%s\r'%path_to_file)
                    sys.stdout.flush()

                    try:
                        with open(path_to_file) as data_file:
                            data = json.load(data_file)

                        for item in detections[year][month][day][device_id]:
                            data['detections'].append(item)

                        path_to_file2 = path_to_file[:-5] + '_VISIBLE' + path_to_file[-5:]
                        with open(path_to_file2,'w') as f:
                            f.write(json.dumps(data, indent=4, sort_keys=True))

                        right_detections(year,month,path_to_file2)

                        os.remove(path_to_file2)

                    except Exception as e:
                        print('Exception: %s'%e)
