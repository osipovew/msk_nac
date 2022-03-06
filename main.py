import os
import shutil
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


def print_hi(name):
    print(f'Hi, {name}')
    try:
        session = requests.Session()

        r = session.get(
            'https://core.nsdigital.ru/getClientData.php?request=getLinks&stationID=C052'
        )
        print(f"getStationCode: {r.status_code}")

        if r.status_code == 200:
            station_list = type(r.json())
            if isinstance(station_list, list):
                    #todo jbujh
                    xxx




                for type_l in station_list:
                    if type_l["type"] == "file":
                        if type_l["path"].endswith('.mp4'):
                            file_path = os.path.dirname(type_l["path"])
                            file_name_for_path = os.path.basename(type_l["path"])
                            full_path = f"{file_path}/{file_name_for_path}"
                            if check_file(full_path) == False:
                                file_name = wget.download(url + type_l["path"])
                                make_sure_path_exists((os.path.dirname(type_l["path"])))
                                if check_file(file_name):
                                    shutil.move(file_name, full_path)
                                    md5_hash = getmd5(full_path)
                                    if type_l["md5sum"] == md5_hash:
                                        print("1")
                                        logger.info(f"server hash::{type_l['md5sum']}=local hash::{md5_hash}")
                                    else:
                                        remove_file(full_path)
                                        file_name = wget.download(url + type_l["path"])
                                        shutil.move(file_name, full_path)
                            else:
                                md5_hash = getmd5(full_path)

                                if type_l["md5sum"] == md5_hash:
                                    print(f"заебок2")
                                else:
                                    print("не совпадает хеш")
                                    remove_file(full_path)
                                    file_name = wget.download(url + type_l["path"])
                                    shutil.move(file_name, full_path)



    except requests.exceptions.RequestException as e:
        print(f"MAIN NETWORK ERROR: {e}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
