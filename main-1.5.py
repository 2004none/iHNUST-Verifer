# Version 1.5
# copyright@Kangwang
# Windows Edition
import base64
import os
import random
import requests
import time
import re


def Ver() -> str:  # 获取SSID
    res = os.popen('netsh wlan show interfaces | findstr /c:"SSID"')
    if 'iHNUST' in res.read():
        exit_code = os.popen('ping www.baidu.com -n 1 -w 25')
        txt = exit_code.read()
        #   print(txt)
        if 'Request timed out' in txt or '请求超时' in txt:
            return 'EC1'
        else:
            return 'OK'
    else:
        return 'EC0'


def Ipv4() -> str:  # 获取IPV4地址
    r = os.popen('netsh interface ipv4 show ipaddress interface="wlan"')
    li = re.search(r'(\.*\d+){4}', r.read())
    return li.group()


def test(rpath):
    eprint('Try to read user infor', 'm')
    try:
        fi = open(rpath, 'rb')
        eprint('File is exist', '')
        dict(eval(base64.b64decode(fi.read()).decode('utf-8')[4:-10]))
        eprint('Data is legal', '')
        fi.close()
    except FileNotFoundError:
        #   print("[Can't Find User Infor]")
        eprint('Can not Find User Infor', 'e')
        fw(rpath)
    except SyntaxError or ValueError:
        #   print("[The file is ERROR]\n[remake!!!]")
        eprint('The file is ERROR', 'e')
        fw(rpath)


def fread(readpath):
    f = open(readpath, 'rb')
    dictt = dict(eval(base64.b64decode(f.read()).decode('utf-8')[4:-10]))
    eprint("The user infor", 'ms')
    for k, v in dictt.items():
        print(f"{k} : ***{v[3:]}")
    eprint('', 'me')
    f.close()
    return dictt


def fw(spath: str) -> bool:  # 创建数据文件
    # if input(eprint(''))
    dicp = {'1': '%40unicom', '2': "%40telecom", '3': '%40cmcc', '0': ''}
    eprint("New verify", 'ms')
    fi = open(spath, 'wb+')
    fi.truncate()

    content = 'FUCK' + '{' + f"'username': '{input('[Username]:')}', 'password': '{input('[Password]:')}', " + \
              f"'ICP': '{dicp.get(input('[Icp]([1]:unicom  [2]:telecom  [3]:cmcc  [0]:HNUST):'))}'" + '}' + 'HOWDAREYOU'

    fi.write(base64.b64encode(content.encode('utf-8')))
    fi.close()
    eprint('', 'me')
    return True


def eprint(i=None, s=''):
    if s == 'e':
        print(f"\033[0;31;40m[{time.strftime('%H:%M:%S', time.localtime())}]    [ERROR]     {i}\033[0m")
    elif s == 'i':
        print(f"\033[0;33;40m[{time.strftime('%H:%M:%S', time.localtime())}]    [WARRING]   {i}\033[0m")
    elif s == 'ms':
        print('*' * 50)
        print(i)
    elif s == 'me':
        print('*' * 50)
    else:
        print(f'[{time.strftime("%H:%M:%S", time.localtime())}]    [INFOR]     {i}')


def msdecide(mspath):
    js = pas(fread(mspath))
    #    print(js)
    msg = js.get('msg', '')

    if (msg == '' or msg == '认证成功') and not js.get('ret_code') == 3:
        eprint("Success", 'ms')
        eprint('', 'me')
        os._exit(0)
    else:
        msg = base64.b64decode(msg).decode()
        code = 0
        if js.get('ret_code') == 3:
            eprint("System busy", 'e')
            eprint("pls connect iHNUST once again", 'i')
            code = 1
        elif msg == 'userid error2':
            eprint("Password Error", 'e')
            eprint('pls confirm your password', 'i')
            code = -1
        elif msg == 'userid error1':
            eprint("Username Error", 'e')
            eprint('pls confirm your username', 'i')
            code = -1
        elif 'Rad:Oppp error' in msg:
            eprint("Connected devices is more than 2 ", 'e')
            eprint("http://49.123.1.40:8080/Self/login/?302=LI", 'i')
            code = 1

        if code == 1:
            eprint('Try again?(Y/N)', 'ms')
            if input() in ['y', 'Y']:
                msdecide(mspath)
            else:
                os._exit(0)
        else:
            fw(mspath)
            msdecide(mspath)


def pas(dic: dict):
    url = ("http://login.hnust.cn:801/eportal/?c=Portal&a=login&callback=dr1004&login_method=1&user_account=%2C0" +
           f"%2C{dic.get('username')}{dic.get('ICP')}&user_password={dic.get('password')}" +
           f"&wlan_user_ip={Ipv4()}&wlan_user_ipv6" +
           f"=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=&jsVersion=3.3.3&v={random.randint(1000, 9999)}")
    #  print(url)
    resp = requests.get(url)
    return dict(eval((resp.text[6:])))


if __name__ == '__main__':
    path = 'verify'
    test(path)
    inf = Ver()
    #    print(inf)
    if inf == "OK":
        eprint("Already connected", '')
        os._exit(0)
    else:
        if inf == 'EC0':
            eprint('Wlan is not connected', 'e')
            os._exit(0)
        else:
            eprint('Try to Verify', '')
            msdecide(path)
