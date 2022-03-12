import os
import shutil
import time
from pprint import pprint

import schedule as schedule
from apscheduler.schedulers.background import BackgroundScheduler
import wget
import logging
import errno
from md5hash import scan
import requests

logger = logging.getLogger(__name__)

url = "https://core.nsdigital.ru/"


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
                    print("=============================================================================================================")
                    if isinstance(type_l, dict):
                            if type_l["type"]:
                                if type_l["type"] == "file":
                                    if type_l["path"]:
                                        file_path = os.path.dirname(f"local_version/{type_l['path']}")
                                        file_name_for_path = os.path.basename(type_l["path"])
                                        full_path = f"{file_path}/{file_name_for_path}"
                                        make_sure_path_exists(file_path)
                                        if check_file(full_path):
                                                md5_hash = getmd5(full_path)
                                                if type_l["md5sum"]:
                                                    if type_l["md5sum"] == md5_hash:
                                                        if os.path.getsize(full_path) == int(type_l["size"]):
                                                            print("os.path.abspath ::", os.path.abspath(full_path))
                                                            print(f"вес локальный: {os.path.getsize(full_path)} вес серверный {type_l['size']} сходятся ")
                                                            print(
                                                                f"server hash1::{type_l['md5sum']} local hash::{md5_hash} сходятся")
                                                            # logger.info(f"server hash::{type_l['md5sum']}=local hash::{md5_hash}")
                                                            print("заебок")
                                                        else:
                                                            print(f"вес не сходится, удаляю {full_path}")
                                                            print(f"вес локальный: {os.path.getsize(full_path)} вес серверный {type_l['size']} ")
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

schedule.every(60).seconds.do(start_job)

while True:
    schedule.run_pending()
    time.sleep(1)
# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi()


