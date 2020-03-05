import base64
from PIL import Image
import io
import json
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import time


mypath = '/media/slawekstu/CREDO1/Api/credo-data-export/detections/'#sciezka do detekcji
home = os.path.dirname(os.path.abspath(__file__))+'/'#sam ustala gdzie aktualnie jestes
paths0=home+"wynik_filtru/"

#NIE CZYTAJ ZBYT DUZYCH ODLEGLOSCI CZASOWYCH BO MOZE SIE ZAPCHAC PAMIEC - BEZPIECZNY CZAS TO <MIESIAC
rok_start=2020
miesiac_start=2
dzien_start=20

rok_koniec=2020
miesiac_koniec=2
dzien_koniec=22#jesli z 1 dnia to daj tu dzien_start+1
# dodatkowe ograncizenie by czytać mniej plikow
#np czytasz tylko dla 23-24.02 z roznica przeczyta sie tylko takie ktorych nazwa czasu jest z zakresu 21-26.02
roznica_czasu=2*86400000#N* 1 dzien

zacznijod=230#podaj jakiś poczatek by nie szukał we wszystkich czasow - oszczednosc czasu
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]#tablica nazw plikow z detekcjami
ilosc_plikow = len(onlyfiles)

start = int(datetime(rok_start, miesiac_start,dzien_start, 0, 0).strftime("%s")) * 1000 #data rozpoczecia pobieranie detekcji
start=str(start)
start=int(start)
stop = int(datetime(rok_koniec, miesiac_koniec,dzien_koniec, 0, 0).strftime("%s")) * 1000 #data zakończenia pobierania
stop=str(stop)
stop=int(stop)

"""
CZEŚĆ I
CZYTANIE DETEKCJI URZYTKOWNIKA WRAZ ICH POSORTOWANIEM
"""
class Detekcja:#czas, dane o userze, dane o hicie, dodatek
    def __init__(self,id,timestamp,czasUTC,time_received,user_id,device_id,team_id,latitude,altitude,longitude,frame_content,height,width,y,x,source,provider,accuracy):

        self.id = id
        self.timestamp = timestamp
        self.czasUTC = czasUTC
        self.time_received = time_received
        self.user_id = user_id
        self.device_id = device_id
        self.team_id = team_id
        self.latitude = latitude
        self.altitude = altitude
        self.longitude = longitude
        self.frame_content = frame_content
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.source = source
        self.provider = provider
        self.accuracy = accuracy

    def __str__(self):
        return str.format("id: {}, timestamp: {}, czasUTC: {}, time_received: {}, user_id: {}, device_id: {}, team_id: {}, latitude: {}, altitude: {}, longitude: {}, frame_content: {}, height: {}, width: {}, y: {}, x: {}, source: {}, provider: {}, accuracy " ,self.id,self.timestamp,self.czasUTC,self.time_received,self.user_id,self.device_id,self.team_id,self.latitude,self.altitude, self.longitude,self.frame_content,self.height,self.width,self.y,self.x,self.source,self.provider,self.accuracy)

#LISTY
tablica_sort=[]
urzadzonka=[]
dobre_po_filtrze=[]
zle_po_filtrze=[]



def czytaj_plik_json(ktory):
    nazwa_pliku=onlyfiles[ktory]#nazwa pliku zawiera czas start/koniec
    tablica_slow = nazwa_pliku.split("_")
    OD=int(tablica_slow[1])#w milisekundach
    ODa=int(tablica_slow[1])/1000
    DO=tablica_slow[2]
    DO=DO.split(".")
    DO=int(DO[0])
    DOa=DO/1000#w milisekundach
    #print("OD: ",OD,"\tDO: ",DOa)
    #wez wszystkie pliki sasiadujace i bedace w tej  dacie
    if OD> start-roznica_czasu  and DO <stop+roznica_czasu and DO>start or OD> start and OD<stop and DO <stop+roznica_czasu:
        print(datetime.utcfromtimestamp(int(ODa)).strftime('OD: %Y-%m-%d %H:%M:%S'),
        datetime.utcfromtimestamp(int(DOa)).strftime('\tDO: %Y-%m-%d %H:%M:%S'))
        name = mypath+onlyfiles[ktory]
        print(name)
        with open(name) as f:
            json_from_file = json.load(f)

        for detection in json_from_file['detections']:
            czas= int(detection['timestamp'])
            stan = 'True'#czy widzialny na stronie api
            index=int(detection['user_id'])
#tu tylko intereusjace nas czasy
            if str(detection['visible'])==stan and czas>start and czas<stop:# and index == userID:
                id = int(detection['id'])
                timestamp = detection['timestamp']
                czas2=czas/1000
                czasUTC= datetime.fromtimestamp(czas2)
                time_received = detection['time_received']
                user_id = int(detection['user_id'])
                device_id = int(detection['device_id'])
                team_id = detection['team_id']
                latitude = detection['latitude']
                altitude = detection['altitude']
                longitude = detection['longitude']
                frame_content = detection['frame_content']
                height = detection['height']
                width = detection['width']
                y = detection['y']
                x = detection['x']
                source = detection['source']
                provider = detection['provider']
                accuracy = detection['accuracy']
                    #tablica_sort.append(0)
                dodaj=Detekcja(id,timestamp,czasUTC,time_received,user_id,device_id,team_id,latitude,altitude,longitude,frame_content,height,width,y,x,source,provider,accuracy)#zdefiniowana detekcja
                tablica_sort.append(dodaj)
                urzadzonka.append((index,device_id))

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
        print("zamieniam")

    middle = (left_index + right_index)//2
    merge_sort(array, left_index, middle, comparison_function)
    merge_sort(array, middle + 1, right_index, comparison_function)
    merge(array, left_index, right_index, middle, comparison_function)


def analyze_detection(plik):
    ilosc_detekcji=len(tablica_sort)
    orginal=set(urzadzonka)
    Device_ID = list(orginal)
    ktory=int(plik)
    urzadzonko=Device_ID[ktory][1]
    pomocnicza=[]
    for ktora in range (ilosc_detekcji):
        if int(urzadzonko)==int(tablica_sort[ktora].device_id):#czy detekcja nalezy do tego urzadzenia?
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
                a=lista_detekcji[pierwszy].timestamp
                #print(lista_detekcji[drugi].timestamp)
                b=lista_detekcji[drugi].timestamp
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
        obrazek=onlyfilesdobre[z].frame_content
        obrazek = obrazek.encode('ascii')
        adres=paths0+str(z)+".png"
        os.makedirs(paths0, exist_ok=True)
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



def json_save():
    print("Zapisywanie detekcji")
    data = {}
    data['detections'] = []

    for w in range(len(dobre_po_filtrze)):
            data['detections'].append({
                'id': dobre_po_filtrze[w].id,
                'timestamp': dobre_po_filtrze[w].timestamp,
                'czasUTC': str(dobre_po_filtrze[w].czasUTC),
                'time_received': dobre_po_filtrze[w].time_received,
                'user_id': dobre_po_filtrze[w].user_id,
                'device_id': dobre_po_filtrze[w].device_id,
                'team_id': dobre_po_filtrze[w].team_id,
                'latitude': dobre_po_filtrze[w].latitude,
                'altitude': dobre_po_filtrze[w].altitude,
                'longitude': dobre_po_filtrze[w].longitude,
                'frame_content': dobre_po_filtrze[w].frame_content,
                'height': dobre_po_filtrze[w].height,
                'width': dobre_po_filtrze[w].width,
                'y': dobre_po_filtrze[w].y,
                'x': dobre_po_filtrze[w].x,
                'source': dobre_po_filtrze[w].source,
                'provider': dobre_po_filtrze[w].provider,
                'accuracy': dobre_po_filtrze[w].accuracy
            })

    with open(paths0+'po_filtrze.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)#zobacz jak fajnie wyglada taki plik

    data2 = {}
    data2['detections'] = []

    for w in range(len(zle_po_filtrze)):
            data2['detections'].append({
                'id': dobre_po_filtrze[w].id,
                'timestamp': dobre_po_filtrze[w].timestamp,
                'czasUTC': str(dobre_po_filtrze[w].czasUTC),
                'time_received': dobre_po_filtrze[w].time_received,
                'user_id': dobre_po_filtrze[w].user_id,
                'device_id': dobre_po_filtrze[w].device_id,
                'team_id': dobre_po_filtrze[w].team_id,
                'latitude': dobre_po_filtrze[w].latitude,
                'altitude': dobre_po_filtrze[w].altitude,
                'longitude': dobre_po_filtrze[w].longitude,
                'frame_content': dobre_po_filtrze[w].frame_content,
                'height': dobre_po_filtrze[w].height,
                'width': dobre_po_filtrze[w].width,
                'y': dobre_po_filtrze[w].y,
                'x': dobre_po_filtrze[w].x,
                'source': dobre_po_filtrze[w].source,
                'provider': dobre_po_filtrze[w].provider,
                'accuracy': dobre_po_filtrze[w].accuracy
            })

    with open(paths0+'zle.json', 'w') as json_file:
        json.dump(data2, json_file)

def main():
    for i in range (zacznijod,ilosc_plikow):
        czytaj_plik_json(i)

    print(len(tablica_sort))
    merge_sort(tablica_sort, 0, len(tablica_sort) -1, lambda detA, detB: detA.timestamp < detB.timestamp)
    # mamy juz posortowane czasy
    orginal=set(urzadzonka)
    Device_ID = list(orginal)
    ile=len(Device_ID)
    for w in range (ile):
        analyze_detection(w)

    merge_sort(dobre_po_filtrze, 0, len(dobre_po_filtrze) -1, lambda detA, detB: detA.timestamp < detB.timestamp)
    merge_sort(zle_po_filtrze, 0, len(dobre_po_filtrze) -1, lambda detA, detB: detA.timestamp < detB.timestamp)

if __name__ == '__main__':
    os.makedirs(paths0, exist_ok=True)
    main()
    json_save()
