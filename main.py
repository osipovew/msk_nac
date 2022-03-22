import os
import shutil
import time
import schedule as schedule
import wget
import logging
import errno
from md5hash import scan
import requests
import datetime
import calendar

logger = logging.getLogger(__name__)

url = "https://core.nsdigital.ru/"
list_file_web = []
list_file_os = []
dict_mark = {
    'marker_status': 0,
    'marker_delete': 0
}

def time_timestamp():
    ts = time.time()
    return ts

def date_time():
    st = datetime.datetime.fromtimestamp(time_timestamp()).strftime('%Y-%m-%d %H:%M:%S')
    return st

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def getmd5(filename):
    md5_hash = scan(filename).lower()
    return md5_hash


def remove_file(file):
    print('Файл удален:' + file)
    os.remove(file)
    return not os.path.exists(file)


def check_file(file):
    file_path_check = os.path.exists(file)
    return file_path_check


def start_job():
    try:
        session = requests.Session()

        r = session.get(
            'https://core.nsdigital.ru/getClientData.php?request=getLinks&stationID=C052'
        )
        print(f"getStationCode: {r.status_code}")

        if r.status_code == 200:
            station_list = r.json()
            # pprint(station_list)
            if isinstance(station_list, list):
                for type_l in station_list:
                    print(
                        "=============================================================================================================")
                    if isinstance(type_l, dict):
                        if type_l["type"]:
                            if type_l["type"] == "file":
                                if type_l["path"]:
                                    where_is_path = os.getcwd()
                                    file_path = os.path.dirname(f"{where_is_path}/local_version/{type_l['path']}")
                                    file_name_for_path = os.path.basename(f"{where_is_path}/{type_l['path']}")
                                    # print(file_name_for_path)
                                    # list_file_web.append(file_name_for_path)
                                    full_path = f"{file_path}/{file_name_for_path}"
                                    make_sure_path_exists(file_path)
                                    if check_file(full_path):
                                        md5_hash = getmd5(full_path)
                                        if type_l["md5sum"]:
                                            if type_l["md5sum"] == md5_hash:
                                                if os.path.getsize(full_path) == int(type_l["size"]):
                                                    print("os.path.abspath ::", os.path.abspath(full_path))
                                                    print(
                                                        f"вес локальный: {os.path.getsize(full_path)} вес серверный {type_l['size']} сходятся ")
                                                    print(
                                                        f"server hash1::{type_l['md5sum']} local hash::{md5_hash} сходятся")
                                                    # logger.info(f"server hash::{type_l['md5sum']}=local hash::{md5_hash}")
                                                    print("заебок")
                                                    dict_mark.update(marker_status=0)
                                                else:
                                                    print(f"вес не сходится, удаляю {full_path}")
                                                    print(
                                                        f"вес локальный: {os.path.getsize(full_path)} вес серверный {type_l['size']} ")
                                                    remove_file(full_path)
                                            else:
                                                print(
                                                    f"server hash1::{type_l['md5sum']} local hash::{md5_hash} не сходятся")
                                                remove_file(full_path)
                                                print("удаляю")
                                        else:
                                            print("нет такого ключа")
                                    else:
                                        file_name = wget.download(url + type_l["path"])
                                        shutil.move(file_name, full_path)
                                        print("файла нет! качаю снова")
                                        print(full_path)
                                else:
                                    print("нет такого ключа")
                            else:
                                print("Значение не file")
                        else:
                            print("проблемы со значением")
                    else:
                        print("другой тип")
            else:
                print("другой тип")
        else:
            print("код не 200")
    except requests.exceptions.RequestException as e:
        print(f"MAIN NETWORK ERROR: {e}")


def delete_old_content():
    # try:
    if dict_mark['marker_status'] == 0:
        session = requests.Session()
        list_file_web = []
        list_file_os = []

        r = session.get(
            'https://core.nsdigital.ru/getClientData.php?request=getLinks&stationID=C052'
        )
        station_list = r.json()
        if r.status_code == 200:
            station_list = r.json()
            if isinstance(station_list, list):
                for type_l in station_list:
                    if isinstance(type_l, dict):
                        if type_l["type"]:
                            if type_l["type"] == "file":
                                if type_l["path"]:
                                    file_name_for_path = os.path.basename(type_l["path"])
                                    if file_name_for_path.endswith("mp4"):
                                        list_file_web.append(file_name_for_path)
        where_is_path = os.getcwd()
        path_for = os.listdir(f"{where_is_path}/local_version/video/templatesVideo")
        path_for_del = (f"{where_is_path}/local_version/video/templatesVideo")
        for path_content in path_for:
            list_file_os.append(path_content)
        result = list(set(list_file_web) ^ set(list_file_os))
        for test in result:
            str1 = ''.join(test)
            date_file = int(os.path.getctime(f"{path_for_del}/{str1}"))
            print(f"debug def {int(time_timestamp())}|||{date_time()}")
            print(f"дата создания файла {date_file}")
            print(f"текущая дата {time_timestamp()}")
            print(f"результат вычитания времени {time_timestamp() - date_file}")
            # print(time_timestamp() - date_file > 10000000)
            # if UTC - date_file > 10000000:
            if time_timestamp() - date_file > 10:
                #todo поправить время с 10 до 10000000
                try:
                    # if os.path.getctime(f"{path_for_del}/{str1}")
                    # os.remove(os.path.join(path_for_del, str1))
                    print("↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓")
                    print(f"обнаружен враждебный файл: удаляю {str1}")
                    print("↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑")
                    print("####################################################################")
                except:
                    print(f"обнаружена разница в списках: {str1} возможно файл еще не скачан")
            list_file_web.clear()
            list_file_os.clear()
    else:
        print("маркер не 0!")
    # except:
    #     print(f"try: brake;  maybe file not exist {path_for_del}/{str1}")


schedule.every(5).seconds.do(delete_old_content)
schedule.every(500).seconds.do(start_job)

# 495 - marker ok
# 500 - marker 0

while True:
    schedule.run_pending()
    time.sleep(10)