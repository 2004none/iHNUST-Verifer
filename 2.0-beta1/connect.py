import pywifi
import time
import os
import re
import base64
import random
import requests
import platform
from const import *
from pywifi import const, Profile

wifi = pywifi.PyWiFi()
system = platform.platform()


def online(index=blank_int, url=Default_url, timeset=Default_timeset):
    if index > Max_times:
        return Offline
    try:
        a = requests.get(url, timeout=timeset)
        if a.status_code == requests.codes.ok:
            return Online
    except requests.exceptions.ConnectionError:
        return Offline
    except requests.exceptions.ReadTimeout:
        return online(index + 1, url, timeset + time_sp)


def Adapter_Scanner():
    index = blank_int
    out = 'Adapters' + f"\n"
    for i in wifi.interfaces():
        out = out + f"[{index}]     {i}\n"
        index = index + 1
    out = out + f"pls input the number:"
    if index > 1:
        printf(out, fmt_infor, up)
        selected = input()
        printf(down)
        return selected
    elif index == 1:
        return Adapter_only_one
    else:
        return Adapter_not_find


def Adapter_Checker(target_num=blank_int, ssid=Default_ssid, turl=Default_url):
    ifaces = wifi.interfaces()[target_num]

    # print(ifaces.name())
    # if ssid == :  # raise ValueError('"ssid" is NULL')
    #     ssid = input("pls input the legal ssid")

    if ifaces.status() == const.IFACE_CONNECTED:
        if online(url=turl) == Online:
            if str(ifaces.scan_results()[0].ssid) == ssid:
                return Connected_target_online
            else:
                return Connected_other_online
        else:
            if str(ifaces.scan_results()[0].ssid) == ssid:
                return Connected_target_offline
            else:
                return Connected_other_offline
    else:
        return Disconnected


def printf(content=None, fmt=None, margin=center):
    if margin == up:
        print('-' * 50)

    if content is not None:
        if fmt == fmt_infor:
            print(f"[{time.strftime('%H:%M:%S', time.localtime())}]     [INFOR]     {content}")
        elif fmt == fmt_warning:
            print(f"\033[0;33;40m[{time.strftime('%H:%M:%S', time.localtime())}]     [WARNING]   {content}\033[0m")
        elif fmt == fmt_error:
            print(f"\033[0;31;40m[{time.strftime('%H:%M:%S', time.localtime())}]     [ERROR]     {content}\033[0m")
        else:
            print(content)

    if margin == down:
        print('-' * 50)


def modify_profile(target_num=blank_int, typed=None, ssid=Default_ssid, auth=const.AUTH_ALG_OPEN,
                   akm=const.AKM_TYPE_NONE,
                   ciper=const.CIPHER_TYPE_NONE, key=None):
    ifaces = wifi.interfaces()[target_num]

    if typed == mk:
        profile: Profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = auth
        profile.akm = akm
        profile.ciper = ciper
        profile.key = key

        modify_profile(target_num=target_num, typed=rm_c, ssid=ssid)
        ifaces.add_network_profile(profile)
        return OK

    if typed == rm_c:
        profile = pywifi.Profile()
        profile.ssid = ssid
        ifaces.remove_network_profile(profile)
        return OK

    if typed == rm_a:
        ifaces.remove_all_network_profiles()
        return OK

    if typed == find_c:
        profiles = ifaces.network_profiles()
        for i in profiles:
            if ssid == i.ssid:
                return i
        return Not_found


def helper(target_num=blank_int, error_reason=None, ssid=None, exit_code: dict = None, path: str = Default_path,
           file_for=data):
    if error_reason == [profile_error, profile_not_found]:
        modify_profile(target_num=target_num, ssid=ssid, typed=rm_c)
        if input('Connect to Default-ssid (Y/N)') in ['Y', 'y']:
            modify_profile(target_num, mk, ssid=Default_ssid)
            connecter(target_num, Default_ssid)
        else:
            printf("Please forget the wlan ,then connect again", fmt_infor)
            os._exit(0)
    elif error_reason == fx_verify:

        if exit_code.get('result') == '1' or exit_code.get('ret_code') == 2:
            printf("Success", fmt_infor)
        elif exit_code.get('ret_code') == 3:
            printf("Busy , Please try it later", fmt_warning)
        else:
            code = 0
            msg = base64.b64decode(exit_code.get('msg')).decode()
            if msg == 'userid error1':
                printf("USERNAME_ERROR OR ICP_ERROR", fmt_error)
                code = 1
            if msg == 'userid error2':
                printf("PASSWORD_ERROR", fmt_error)
                code = 1
            if 'Rad:Oppp error' in msg:
                printf("Connected devices more than 2", fmt_warning)
                pass

            if code == 1:
                if input("TRY AGAIN? (Y?N)") in ['y', 'Y']:
                    file_save(path, file_for=data)
                    dict_data = file_load(path, file_for=data)
                    verify(i_num, dict_data)
                else:
                    os._exit(0)
            else:
                os._exit(0)


def connecter(target_num=blank_int, ssid=Default_ssid, timeset=Default_timeset * 10, ):
    ifaces = wifi.interfaces()[target_num]
    pf = modify_profile(target_num=target_num, typed=find_c, ssid=ssid)
    if pf is not Not_found:
        printf('Please Wait', fmt_infor)
        index = 6
        while index > 0:
            if index % 2 == 0:
                ifaces.connect(pf)
            time.sleep(timeset)
            if ifaces.status() == const.IFACE_CONNECTED:
                printf(f"Connected! SSID:{ifaces.scan_results()[0].ssid}", fmt_infor)
                return online(blank_int)
            index = index - 1
        else:
            helper(profile_error)
    else:
        helper(profile_not_found, ssid)


def ipv4(target_num=blank_int):
    ifaces = wifi.interfaces()[target_num]
    if 'windows' in system.lower():
        status_list = list(os.popen("ipconfig /all").read().split('\n'))
        for i in status_list:
            if ifaces.name() in i:
                return re.search(r'(\.*\d+){4}', status_list[status_list.index(i) + 5]).group()

    if 'linux' in system.lower():
        exit_code = os.popen(f"echo `ifconfig  wlan{target_num} | head -n2 | grep inet | awk '{{print$2}}'`")
        return exit_code.read()


def file_save(path=None, file_for=None):
    icp_d = {'1': '%40unicom', '2': '%40telecom', '3': '%40cmcc', '4': ''}
    if file_for == data:
        printf("New User Infor:", margin=up)
        f = open(path, 'wb+')
        f.truncate()

        content = 'FUCK' + '{' + f"'username': '{input('[Username]:')}', 'pd': '{input('[Password]:')}', " + \
                  f"'ICP':'{icp_d.get(input('[Icp]([1]:unicom  [2]:telecom  [3]:cmcc  [4]:univer):'))}'}}HOWDAREYOU"
        printf(margin=down)
        f.write(base64.b64encode(content.encode('utf-8')))
        f.close()

    elif file_for == config:
        pass


def verify(target_num=blank_int, dic=None):
    if dic is None:
        raise ValueError('dict not found')
    url = ("http://login.hnust.cn:801/eportal/?c=Portal&a=login&callback=dr1004&login_method=1&user_account=%2C0" +
           f"%2C{dic.get('username')}{dic.get('ICP')}&user_password={dic.get('pd')}" +
           f"&wlan_user_ip={ipv4(target_num)}&wlan_user_ipv6" +
           f"=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=&jsVersion=3.3.3&v={random.randint(1000, 9999)}")
    resp = requests.get(url)

    helper(error_reason=fx_verify, exit_code=dict(eval((resp.text[6:]))))


def file_finder(path=None, file_for=data):
    if path is None:
        raise ValueError('path not found')
    try:
        printf("Finder: Read User Infor", fmt_infor)
        f = open(path, 'r', encoding='utf-8')
        printf("Finder: File Exist", fmt_infor)
        if file_for == data:
            dict(eval(base64.b64decode(f.read()).decode('utf-8')[4:-10]))
            printf("Finder: Data Legal", fmt_infor)
        f.close()
        return OK
    except FileNotFoundError:
        printf("Finder: File Not Exist", fmt_error)

    except SyntaxError or ValueError:
        printf("Finder: File Error", fmt_error)
    file_save(path, data)


def file_load(path=None, file_for=None):
    if path is None:
        raise ValueError('path not found')
    if file_for == data:
        f = open(path, 'rb')
        data_dict = dict(eval(base64.b64decode(f.read()).decode('utf-8')[4:-10]))
        printf("The user infor", margin=up)
        for k, v in data_dict.items():
            print(f"{k} : ***{v[3:]}")
        printf(margin=down)
        f.close()
        return data_dict
    elif file_for == config:
        pass


if __name__ == '__main__':

    i_num = Adapter_Scanner()
    status_code = Adapter_Checker(target_num=i_num)
    power = AACW
    infaces = wifi.interfaces()[i_num]
    """Pre"""
    if status_code == Connected_target_online or (status_code == Connected_other_online and not power):
        printf('Your network is working', fmt_infor)
        os._exit(0)
    elif status_code is not Connected_target_offline:
        infaces.disconnect()
        time.sleep(1)
        if connecter() == Online:
            printf('Your network is working', fmt_infor)
            os._exit(0)
    file_finder(Default_path, data)
    dic_data = file_load(Default_path, data)
    verify(i_num, dic_data)
