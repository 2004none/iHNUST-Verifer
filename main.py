# Version 1.1
# copyright@Kangwang
# Only for windows
import base64
import os
import random
import requests


def Ver() -> str:
    re = os.popen('netsh wlan show interfaces | findstr /c:"SSID"')
    if 'iHNUST' in re.read():
        exit_code = os.popen('ping www.baidu.com -w 10')
        if exit_code:
            return 'EC1'
        else:
            return 'OK'
    else:
        return 'EC0'


def Ipv4() -> str:
    re = os.popen('netsh interface ipv4 show ipaddress interface="wlan"')
    return re.read()[4:18]


def fw(spath: str) -> bool:
    dicp = {'1': '%40unicom', '2': "%40telecom", '3': '%40cmcc', '0': ''}
    print("[New verify]:")
    fi = open(spath, 'wb+')
    fi.truncate()

    content = '{' + f"'username': '{input('[Username]:')}', 'password': '{input('[Password]:')}', " + \
              f"'ICP': '{dicp.get(input('[Icp]: [1]:unicom  [2]:telecom  [3]:cmcc  [0]:HNUST'))}'" + '}'

    fi.write(base64.b64encode(content.encode('utf-8')))
    fi.close()
    return True


if __name__ == '__main__':
    #   print(Ver())
    #   print(Ipv4())
    inf = Ver()
    if inf == "OK":
        exit(0)
    else:
        if inf == 'EC0':
            print("[Wlan is not connected]")
            exit(0)

        #        dic = {'username': '220504011', 'password': '2004110', 'ICP': '%40unicom'}
        path = 'verify.txt'

        print("[Read User Infor]")
        try:
            f = open(path, 'rb')
            dic = dict(eval(base64.b64decode(f.read()).decode('utf-8')))
            f.close()
            del dic
        except FileNotFoundError:
            print("[Can't Find User Infor]")
            fw(path)
        except SyntaxError:
            print("[The file is ERROR]\n[remake!!!]")
            fw(path)

        f = open(path, 'rb')
        dic = dict(eval(base64.b64decode(f.read()).decode('utf-8')))
        print(dic)
        print("[The user infor]:")
        for k, v in dic.items():
            print(f"{k} : {v}")

        url = ("http://login.hnust.cn:801/eportal/?c=Portal&a=login&callback=dr1004&login_method=1&user_account=%2C0" +
               f"%2C{dic.get('username')}{dic.get('ICP')}&user_password={dic.get('password')}&wlan_user_ip={Ipv4()}" +
               "&wlan_user_ipv6" +
               f"=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=&jsVersion=3.3.3&v={random.randint(1000, 9999)}")
        #  print(url)
        resp = requests.get(url)

        js = dict(eval((resp.text[6:])))
        # print(js)
        msg = js.get('msg', '')
        if msg != '认证成功':
            msg = base64.b64decode(msg).decode()
        print(msg)

        if js.get('ret_code') == 3:
            print("[BUSY!!!!]")
            print("[pls connect iHNUST once more ]")
            exit(0)

        if msg == '' or msg == '认证成功':
            print("[SUCCESS!]")
        elif msg == 'userid error2':
            print("[Password Error, pls confirm your password]")
        elif msg == 'userid error1':
            print("[Username Error, pls confirm your username]")
        elif msg == 'Rad:Oppp error: 09026004|109020013|Reject by concurrency control.':
            print("[Connected devices is more than 2 ]")
            print("http://49.123.1.40:8080/Self/login/?302=LI")
