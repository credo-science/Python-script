'''
MAIN - TO JEDYNY PLIK KTORY TRZEBA URUCHAMIAC w części filtru czasowego

POZOSTALE SA WYWOLYWANE WEWNATRZ TEGO I SĄ POTRZEBNE:
1) filtrowanie_czasowe_script_01.py
2) filtrowanie_czasowe_scripy_02.py
3) right_detections.py

'''
from filtrowanie_czasowe_script_01 import *
from filtrowanie_czasowe_script_02 import *
from filtrowanie_czasowe_right_detections import *
import datetime

import os
import math


home = os.path.dirname(os.path.abspath(__file__))+'/'
sciezka_analizy=home+'dobre_czasowo/'
sciezka_detekcji='/media/slawekstu/CREDO1/Api/credo-data-export/detections/'
step = 10


def main():
    '''
    TWORZE KATALOGI DZIENNE DLA DEVICE_ID
    '''
    os.makedirs(sciezka_analizy+'temp', exist_ok=True)

    lista_poczatkowych_plikow_json = os.listdir(sciezka_detekcji)
    lista_poczatkowych_plikow_json.sort()

    all_ids = len(lista_poczatkowych_plikow_json)

    try:
        with open('info_start_czasowe.txt', 'r') as info_file:
            start_file_name = info_file.readline().strip()
    except:
        start_file_name=lista_poczatkowych_plikow_json[0]

    if start_file_name != 'brak nowych danych':
        # file name na przypadek awarii przechowany w osobnym pliku
        with open('info_start_czasowe_temp.txt', 'w') as info_file:
            info_file.write(start_file_name)

        try:
            od = lista_poczatkowych_plikow_json.index(start_file_name)

            do = od + step

            if do > all_ids:
                do = all_ids

            part_of_list = lista_poczatkowych_plikow_json[od:do]

            print('od:%d do:%d,filename1:%s, filename2:%s'%(od,do,lista_poczatkowych_plikow_json[od],lista_poczatkowych_plikow_json[do-1]))

            if do == all_ids:
                #jesli to byl ostatni plik
                next_time_file = 'brak nowych danych'
                #return False
            else:
                next_time_file = lista_poczatkowych_plikow_json[do]

            with open('info_start_czasowe.txt', 'w') as info_file:
                info_file.write(lista_poczatkowych_plikow_json[od])





            '''
            --------------------------------------------------------------------------------------------
            script_01.py
            --------------------------------------------------------------------------------------------
            '''
            print('***DODAWANIE ELEMENTOW DO SLOWNIKA I TWORZENIE STRUKTURY KATALOGOW***')
            for plik in part_of_list:
                if_visible_rewrite_to_new_localization(plik)
                utworz_foldery(plik)

            '''
            --------------------------------------------------------------------------------------------
            script_02.py
            --------------------------------------------------------------------------------------------
            '''

            lista_plikow_z_folderu = os.listdir(sciezka_analizy+'temp')
            lista_plikow_z_folderu.sort()


            for plik in lista_plikow_z_folderu:
                try:
                    zarzadzaj_dodawaniem_elementow(plik)
                except Exception as e:
                    print('PLIK PRAWDOPODOBNIE USZKODZONY: %s'%plik)

            #print('***ZAPISYWANIE DO PLIKOW***')


            detections = get_detections_dict()
            rodziel_to_na_device_id_file(detections)

            zapisz_podsumowanie_do_pliku()

            '''
            --------------------------------------------------------------------------------------------
            wyzerowanie zmiennych
            --------------------------------------------------------------------------------------------
            '''

            clear_temp()

        except Exception as e:
            print('brak nowych danych!')

        with open('info_start_czasowe.txt', 'w') as info_file:
            info_file.write(next_time_file)

if __name__ == '__main__':

    #petla - ustawienie ile razy ! nie zawsze! ogolnie to trzeba okreslic ile razy ma sie wykonac!
    lista_poczatkowych_plikow_json = os.listdir(sciezka_detekcji)
    ile = len(lista_poczatkowych_plikow_json)
    ile /= step
    ile = math.ceil(ile)
    for i in range(ile):
        print(datetime.datetime.now().time(),"\n")
        main()
