"""
#_______________________________________________________________________________________________
#                               INFORMACJE WSTĘPNE
równoległy filt detekcji i zapis jako paczka JSON
"""
#DO ROWNOLEGLENIA
import multiprocessing
from multiprocessing import Lock, Process, Queue, current_process,Pool,Manager
import time
import queue # imported for using queue.Empty exception

#BIBLIOTEKI DO OBLICZEŃ
#BIBLIOTEKI PODSTAWOWE
import io
import json
import os
from os import listdir
from os.path import isfile, join,isdir
from datetime import datetime
import time
import shutil#do usuwania folderu

#BIBLIOTEKI ANALIZY GRAFICZNEJ
import base64
from PIL import Image
Image.LOAD_TRUNCATED_IMAGES = True
import numpy as np
import matplotlib.pyplot as plt


"""
DEKLARUJEMY ŚCIEŻKI i CZAS START/KONIEC
"""
#SCIEZKI
sciezka='/media/slawekstu/CREDO1/Api/II edycja/credo-data-export/' #sciezka do plików po pobraniu (detections,pings)
mypath = sciezka+'detections/'#sciezka do detekcji
userID = 10069
#onlyfiles = [f for f in listdir(sciezka2) if isfile(join(sciezka2, f))]#tablica nazw plikow z detekcjami

ilosc = 1 #jak chcesz wiecej to zrob liste plik=[] i dodawaj te co chcesz, potem ilosc to len(plik)
plik=[]
plik.append("export_1570262508355_1570263580239.json")
ilosc = len(plik)

paths0=sciezka+'credo-analysis-image/007/filtr/'


if os.path.exists(paths0):#ja sobie zawsze czyscilem pliki - usun jak nie chcesz
    try:
        shutil.rmtree(paths0)#usun stare pliki
    except Exception as e:
        #print(e)
        raise

pngdir=paths0+"Images/"
os.makedirs(paths0, exist_ok=True)

"""
CZEŚĆ I
CZYTANIE DETEKCJI URZYTKOWNIKA WRAZ ICH POSORTOWANIEM
"""
class Detekcja:
    def __init__(self, index,urzadzenie,id,czasT,czasUTC,image):
        self.index = index
        self.urzadzenie = urzadzenie
        self.id = id
        self.czasT = czasT
        self.czasUTC = czasUTC
        self.image = image

    def __str__(self):
        return str.format("Index: {}, Urzadzenie: {}, Id: {},CzasT: {}, CzasUTC: {}, Image: {},Typ: {}, Rodzaj: {}",self.index, self.urzadzenie, self.id,self.czasT, self.czasUTC, self.image, self.typ, self.rodzaj)

#LISTY w sposób multiprocessing
manager = Manager()
tablica_sort=manager.list()#tworzenie listy  do równoleglego dodawania
urzadzonka=manager.list()#tablica urządzen
dobre_po_filtrze=manager.list()
zle_po_filtrze=manager.list()


def czytaj_plik_json(ktory):
    nazwa_pliku=plik[ktory]#nazwa pliku zawiera czas start/koniec
    tablica_slow = nazwa_pliku.split("_")
    OD=int(tablica_slow[1])#w milisekundach
    ODa=int(tablica_slow[1])/1000
    DO=tablica_slow[2]
    DO=DO.split(".")
    DO=int(DO[0])
    DOa=DO/1000#w milisekundach
    print("OD: ",OD)
    print("DO: ",DOa)
        #print(datetime.utcfromtimestamp(int(ODa)).strftime('%Y-%m-%d %H:%M:%S'))
        #print(datetime.utcfromtimestamp(int(DOa)).strftime('%Y-%m-%d %H:%M:%S'))
    name = mypath+plik[ktory]
    print(name)
    with open(name) as f:
        json_from_file = json.load(f)

    for detection in json_from_file['detections']:
        czas= int(detection['timestamp'])
            #POMINIECIE DETEKCJI Z BLYSKAMI (NASZYMI TESTAMI)
            #latwiej sprawdzic czy czas jest w zakazanym czasie niz pozanim (mniej ifow)
        stan = 'True'#czy widzialny na stronie api
        index=int(detection['user_id'])

        if str(detection['visible'])==stan:# and index == userID:
            nazwa=str(index)+'.txt'
            image=detection['frame_content']#.encode('ascii')
            device=detection['device_id']
            ID=int(detection['id'])
            czas2=czas/1000
            czas2r=czas%1000
            czasUTC= datetime.fromtimestamp(czas2)

                        #ze wzgledu na planowane rownoleglenie nie zapiszemy detekcji w tym etapie

                        #tablica_sort.append(0)
            dodaj=Detekcja(index,device,ID,czas,czasUTC,image)#zdefiniowana detekcja
            tablica_sort.append(dodaj)
            urzadzonka.append((index,device))

#ZRÓWNOLEGLANIE
liczba_procesorow = multiprocessing.cpu_count()

def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            task = tasks_to_accomplish.get_nowait()
        except queue.Empty:

            break
        else:
            zadanie=int(task)
            czytaj_plik_json(zadanie)#odpalamy czytanie pliku json o numerze zadania
            tasks_that_are_done.put('task no '+task + ' is done by ' + current_process().name)
            time.sleep(.5)
    return True


def main():
    number_of_task = ilosc#zadań tyle ile mamy plików z detekcjami
    number_of_processes = liczba_procesorow
    tasks_to_accomplish = Queue()#kolejkowanie/lista
    tasks_that_are_done = Queue()
    processes = []

    for i in range(number_of_task):#tworzenie tasków
        tasks_to_accomplish.put(str(i))#dodamy numer pliku

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

    return True



#funkcje do sortowania listy, podział -> sort-> łączenie
def merge(array, left_index, right_index, middle, comparison_function):
    left_copy = array[left_index:middle + 1]
    right_copy = array[middle+1:right_index+1]

    left_copy_index = 0
    right_copy_index = 0
    sorted_index = left_index

    while left_copy_index < len(left_copy) and right_copy_index < len(right_copy):

        # We use the comparison_function instead of a simple comparison operator
        if comparison_function(left_copy[left_copy_index], right_copy[right_copy_index]):
            array[sorted_index] = left_copy[left_copy_index]
            left_copy_index = left_copy_index + 1
        else:
            array[sorted_index] = right_copy[right_copy_index]
            right_copy_index = right_copy_index + 1

        sorted_index = sorted_index + 1

    while left_copy_index < len(left_copy):
        array[sorted_index] = left_copy[left_copy_index]
        left_copy_index = left_copy_index + 1
        sorted_index = sorted_index + 1

    while right_copy_index < len(right_copy):
        array[sorted_index] = right_copy[right_copy_index]
        right_copy_index = right_copy_index + 1
        sorted_index = sorted_index + 1


def merge_sort(array, left_index, right_index, comparison_function):
    if left_index >= right_index:
        return
        #print("zamieniam")

    middle = (left_index + right_index)//2
    merge_sort(array, left_index, middle, comparison_function)
    merge_sort(array, middle + 1, right_index, comparison_function)
    merge(array, left_index, right_index, middle, comparison_function)


def analyze_detection(plik):
    ilosc_detekcji=len(tablica_sort)
    orginal=set(urzadzonka)
    Device_ID = list(orginal)
    ktory=int(plik)-1
    urzadzonko=Device_ID[ktory][1]
    pomocnicza=[]
    for ktora in range (ilosc_detekcji):
        if int(urzadzonko)==int(tablica_sort[ktora].urzadzenie):#czy detekcja nalezy do tego urzadzenia?
            pomocnicza.append(tablica_sort[ktora])
    filtr_antyartefaktowy(urzadzonko,pomocnicza)


def filtr_antyartefaktowy(urzadzenie,lista_detekcji):
    ile_czasow=len(lista_detekcji)#ilosc czasow usera
    ile_czasow2=ile_czasow+1#ilosc czasow usera +1 -> by moc zapisac all wlasciwe czasy do pliku
    dobre=0
    zle=0
    onlyfilesdobre = []
    ilosciowe=0
    zleczasowo=0
    onlyfilesdobre=[]
    dobew=[]
    start=0
    lista_detekcji.append(lista_detekcji[len(lista_detekcji)-1])
    #10 Analiza czasowa
    for pierwszy in range(ile_czasow):#petla roznic miedzy elementem w a pozostalymi;
        if pierwszy==start:
            for drugi in range(pierwszy+1,ile_czasow2):
                a=lista_detekcji[pierwszy].czasT
                #print(lista_detekcji[drugi].czasT)
                b=lista_detekcji[drugi].czasT
                roznica = abs(int(a)-int(b))
                if roznica <60001:#roznica<=1 min
                    ilosciowe+=1
                if roznica>60000 or drugi==(ile_czasow):
                    if ilosciowe >10:#max na minute 9
                        start=pierwszy+ilosciowe#jesli wiecej pomijamy, przesuwajac start o tyle ile bylo w minucie
                        ilosciowe=0#okreslenie ile na minute wystapilo
                        break
                    else:
                        onlyfilesdobre.append(lista_detekcji[pierwszy])#jesli ify nie zadzialaly dodaj do dobrej tablicy
                        dobew.append(pierwszy)
                        ilosciowe=0
                        start+=1
                        break
    ilosci=len(dobew)#ilosc detekcji dobrych czasowo
    for z in range (ilosci):#ilosc dobrych w urzadzeniu
        obrazek=onlyfilesdobre[z].image
        obrazek = obrazek.encode('ascii')
        adres=sciezka+"filtr/"+str(z)+".png"
        os.makedirs(sciezka+"filtr/", exist_ok=True)
        with open(adres, "wb") as fh:
            fh.write(base64.decodebytes(obrazek))
        try:
            im = Image.open(adres).convert('LA')
            pixelMap = im.load()

            pixelMap = im.load()
            img = Image.new( im.mode, im.size)
            pixelsNew = img.load()
            progtla=70
            jasnychpixeli=71
            jasnypunkt=0
            suma_tla=0
            najjasniejszypunkt=0
            najjasniejszypunkt2=0
            for w in range(img.size[0]):
                 for j in range(img.size[1]):
                    a=pixelMap[w,j]#a -tablica pixela ((p),(t)) interesuje nas tylko p; t zawsze ==255
                    a0=a[0]
                    suma_tla+=a0
                    if najjasniejszypunkt<a0:
                        najjasniejszypunkt2=najjasniejszypunkt
                        najjasniejszypunkt=a0
                    if progtla <a0:
                        jasnypunkt+=1

            if (jasnypunkt>0 and jasnypunkt<jasnychpixeli):
                dobre_po_filtrze.append(onlyfilesdobre[z])
            else:
                zle+=1#moje filtry
                zle_po_filtrze.append(onlyfilesdobre[z])
            if os.path.isfile(adres) :
                os.remove(adres)
        except IOError:
            pass

def do_job2(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            task = tasks_to_accomplish.get_nowait()
        except queue.Empty:

            break
        else:
            zadanie=int(task)
            analyze_detection(task)#odpalamy czytanie pliku json o numerze zadania
            tasks_that_are_done.put('task no '+task + ' is done by ' + current_process().name)
            time.sleep(.5)
    return True


def filtrowanie():
    orginal=set(urzadzonka)
    Device_ID = list(orginal)
    ile=len(Device_ID)
    number_of_task = ile+1#zadań tyle ile mamy urzadzen+1
    number_of_processes = liczba_procesorow
    tasks_to_accomplish = Queue()#kolejkowanie/lista
    tasks_that_are_done = Queue()
    processes = []

    for i in range(number_of_task):#tworzenie tasków
        tasks_to_accomplish.put(str(i))#dodamy numer pliku

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=do_job2, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

    #sortowanie po czasie i dodanie do tablicy
    print("zapisane")
    return True

def json_save():
    data = {}
    data['detections'] = []

    for w in range(len(dobre_po_filtrze)):
        data['detections'].append({
            'id': dobre_po_filtrze[w].id,
            'frame_content': dobre_po_filtrze[w].image,
            'timestamp': dobre_po_filtrze[w].czasT,
            'device_id': dobre_po_filtrze[w].urzadzenie,
            'user_id': dobre_po_filtrze[w].index
        })

    with open(paths0+'po_filtrze.json', 'w') as json_file:
        json.dump(data, json_file)

    data2 = {}
    data2['detections'] = []

    for w in range(len(zle_po_filtrze)):
        data2['detections'].append({
            'id': zle_po_filtrze[w].id,
            'frame_content': zle_po_filtrze[w].image,
            'timestamp': zle_po_filtrze[w].czasT,
            'device_id': zle_po_filtrze[w].urzadzenie,
            'user_id': zle_po_filtrze[w].index
        })

    with open(paths0+'zle.json', 'w') as json_file:
        json.dump(data2, json_file)

if __name__ == '__main__':
    os.makedirs(paths0, exist_ok=True)
    main()
    print(len(tablica_sort))
    merge_sort(tablica_sort, 0, len(tablica_sort) -1, lambda detA, detB: detA.czasT < detB.czasT)

    #analyze_detection(paths0+'czas.txt')#zapisz wszystkie
    filtrowanie()
    merge_sort(dobre_po_filtrze, 0, len(dobre_po_filtrze) -1, lambda detA, detB: detA.czasT < detB.czasT)
    json_save()
