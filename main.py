# 这是一个示例 Python 脚本。
import json
import traceback

import pywifi

import winreg
import ctypes
from typing import TextIO

import abc

import os
import threading

import subprocess
from subprocess import check_output

import re


class ProxyMode(metaclass=abc.ABCMeta):
    proxy_conf: dict
    check: bool = False
    """
    初始化
    :return:
    """

    def __init__(self, proxy_conf: dict):
        self.proxy_conf = proxy_conf
        self.check_parameter(proxy_conf)

        pass

    def get_check(self):
        return self.check

    pass

    """
    参数校验
    :return:
    """

    @abc.abstractmethod  # 定义抽象方法，无需实现功能
    def check_parameter(self, proxy_dict):
        pass

    @abc.abstractmethod
    def set_proxy(self):
        pass

    # 读取json配置
    @staticmethod
    def read_json() -> dict:
        """
        读取配置文件，正常时返回字典对象，发生异常时返回FALSE
        :return:
        """
        try:
            # 采用with-open 去关闭资源，而不是try-finally,保持代码整洁
            # 配置mode为读取，write时文件指针放在文件末尾，文本编码为UTF-8
            with open('proxy.json', 'r', encoding="UTF-8") as fh:
                data = json.load(fh)
                # print(data.keys())
                return data
        except IOError:
            # 如果捕获异常，记录失败日志
            # traceback.print_exc()
            print("\033[0;33;40m未找到配置文件 proxy.json！\033[0m")
            ProxyMode.if_write_json()
        except json.decoder.JSONDecodeError:
            print("\033[0;33;40m配置文件 proxy.json 损坏！\033[0m")
            ProxyMode.if_write_json()
        pass

    @staticmethod
    def write_json():
        """
        写入默认配置文件
        当选择 auto 模式时，置反系统代理状态
        当选择 name 模式时，根据当前wifi名称，检索 auto 是否有同名配置，并根据配置设置系统代理，如果没有同名配置，则什么都不做
        当选择 manual 模式时，手动设置系统代理状态
        :return:
        """
        try:
            json_str = {
                "mode": "name",
                "localIdentification": "<local>;",
                "auto": {
                    "notLocal": "selected",
                    "ProxyServer": "",
                    "ProxyOverride": ""
                },
                "name": {
                    "wifiName1": {
                        "enable": "open",
                        "notLocal": "selected",
                        "ProxyServer": "",
                        "ProxyOverride": ""
                    },
                    "wifiName2": {
                        "enable": "close",
                        "notLocal": "selected",
                        "ProxyServer": "",
                        "ProxyOverride": ""
                    },
                    "wifiName3": {
                        "enable": "open",
                        "notLocal": "not selected",
                        "ProxyServer": "127.0.0.1:80",
                        "ProxyOverride": ""
                    }
                },
                "manual": {
                    "notLocal": "selected",
                    "ProxyServer": "",
                    "ProxyOverride": ""
                }
            }
            json_dumps = json.dumps(json_str)
            with open('./proxy.json', 'w') as f:
                f.write(json_dumps)
                return True
        except IOError:
            # 如果捕获异常，记录失败日志
            traceback.print_exc()
            return False
        pass

    @staticmethod
    def if_write_json():
        """
        根据用户输入，判断是否重新写入默认配置文件
        :return:
        """
        if input("\033[0;31;40m是否重新生成空配置文件 proxy.json (y/n)？\033[0m").lower() in ["y", "Y", "yes"]:
            ProxyMode.write_json()
            print("\033[0;32;40m已在当前目录重新写入空配置文件(proxy.json)！\033[0m")
            return True
        return False
        pass

    pass


pass


class AutoProxy(ProxyMode):
    def __init__(self, proxy_conf: dict):
        super().__init__(proxy_conf)

    pass

    def check_parameter(self, auto_proxy_dict):
        """
         用于判断手动模式下，json是否符合自定义的Json格式，当存在键为 key 的对象 并且格式正确时，返回TRUE
         :param auto_proxy_dict:
         :return:
         """
        if isinstance(auto_proxy_dict, dict):
            key = "auto"
            if key in auto_proxy_dict:
                set_conf = auto_proxy_dict[key]
                if ('notLocal' in set_conf
                        and 'localIdentification' in auto_proxy_dict and auto_proxy_dict[
                            "localIdentification"] != ""
                        and 'ProxyServer' in set_conf and set_conf["ProxyServer"] != ""
                        and 'ProxyOverride' in set_conf):
                    self.check = True
                    print("\033[0;32;40m 配置校验通过\033[0m")
                    return True
                else:
                    print("\033[0;31;40m 配置校验未通过！\033[0m")
            else:
                print("\033[0;31;40m未找到手动模式的配置！\033[0m")
        else:
            print("\033[0;31;40m配置文件格式不正确！\033[0m")
        pass

    def set_proxy(self):

        local_identification: str = self.proxy_conf["localIdentification"]
        set_conf = proxy_dict["auto"]
        if AutoProxy.is_open_proxy_form_win():
            print("\033[0;32;40m当前系统代理已开启，正在关闭……！\033[0m")
            close_proxy()
            print("\033[0;32;40m已关闭系统代理！\033[0m")
        else:
            print("\033[0;32;40m当前系统代理已关闭，正在开启……！\033[0m")
            if set_conf["notLocal"] == "selected":
                # 设置代理
                start_proxy(set_conf["ProxyServer"],
                            local_identification + set_conf["ProxyOverride"].replace(local_identification, ""))
                print("勾选“请勿将代理服务器用于本地(Intranet)地址”,并开启系统代理！")
            else:
                # 设置代理
                start_proxy(set_conf["ProxyServer"], set_conf["ProxyOverride"])
                print("取消勾选“请勿将代理服务器用于本地(Intranet)地址”,并开启系统代理！")

            print("\033[0;32;40m已开启系统代理！\033[0m")

        pass

    @staticmethod
    def is_open_proxy_form_win():
        """
        判断是否开启了代理，开启状态返回True
        :return:
        """
        try:
            if get_key("ProxyEnable")[0] == 1:
                return True
        except FileNotFoundError as err:
            print("没有找到代理信息：" + str(err))
        except Exception as err:
            print("有其他报错：" + str(err))
        return False

    pass


pass


class NameProxy(ProxyMode):
    wifi_name: str
    """
    当前连接的wifi名称
    """

    def __init__(self, proxy_conf: dict):
        self.wifi_name = get_wifi_name()
        super().__init__(proxy_conf)

    pass

    def check_parameter(self, proxy_dict):
        """
        用于判断wifi名称模式下，json是否符合自定义的Json格式，当存在键为 key 的对象 并且格式正确时，返回TRUE
        :param proxy_dict: dict
        :return:
        """
        if isinstance(proxy_dict, dict):
            # 判断字典中是否存在 name 对象
            if "name" in proxy_dict:
                name_conf = proxy_dict["name"]
                if self.wifi_name in name_conf:
                    set_conf = name_conf[self.wifi_name]
                    if ("enable" in set_conf
                            and ((set_conf["enable"] == "open"
                                  and 'ProxyServer' in set_conf and set_conf["ProxyServer"] != "")
                                 or (set_conf["enable"] != "" and set_conf["enable"] != "open"))
                            and 'notLocal' in set_conf
                            and 'localIdentification' in proxy_dict and proxy_dict["localIdentification"] != ""
                            and 'ProxyOverride' in set_conf):
                        self.check = True
                        print("\033[0;32;40m 配置校验通过\033[0m")
                        return True
                    else:
                        print("\033[0;31;40m wifi: %s 的配置校验未通过！\033[0m" % self.wifi_name)
                else:
                    print("\033[0;31;40m 未找到wifi: %s 的配置！\033[0m" % self.wifi_name)
        else:
            print("\033[0;31;40m 配置文件格式不正确！\033[0m")
        pass

    def set_proxy(self):
        local_identification: str = self.proxy_conf["localIdentification"]
        name_conf = proxy_dict["name"]
        set_conf = name_conf[self.wifi_name]
        if set_conf["enable"] == "open":

            if set_conf["notLocal"] == "selected":
                # 设置代理
                start_proxy(set_conf["ProxyServer"],
                            local_identification + set_conf["ProxyOverride"].replace(local_identification, ""))
                print("勾选“请勿将代理服务器用于本地(Intranet)地址”,并开启系统代理！")
            else:
                # 设置代理
                start_proxy(set_conf["ProxyServer"], set_conf["ProxyOverride"])
                print("取消勾选“请勿将代理服务器用于本地(Intranet)地址”,并开启系统代理！")
        else:
            close_proxy()
            print("\033[0;32;40m已关闭系统代理！\033[0m")
        pass


def get_wifi_name() -> str:
    """
    获取当前连接wifi名称
    :rtype: str
    :return:
    """
    result = check_output(['netsh', 'wlan', 'show', 'interfaces', '|', 'findstr', '/C:"SSID"'])
    # result = subprocess.check_output(['netsh', 'wlan', 'show', 'network'])
    result = result.decode('gbk')
    lst = result.split('\r\n')
    lst = lst[4:]

    ssid = None
    for index in range(len(lst)):
        res = re.search(r'[/\x20]+SSID[/\x20]*:', lst[index], re.I)
        if res:
            wifi_ssid_str: str = lst[index]
            index = wifi_ssid_str.find(':')
            ssid = wifi_ssid_str[index + 2:]
            break

    # scanoutput: bytes = check_output([os.path.abspath(".") + r"\wifi_name.bat"])  # 最好使用完整路径
    # ssidBytes: str = scanoutput.decode()
    # ssid = ssidBytes[0:-2]
    if ssid is None:
        print("\033[0;31;40m请检查wifi是否连接！\033[0m")
        wait_for_input(5)
    elif ssid == "":
        print("\033[0;31;40m当前连接的wifi名称为空:%s，请检查wifi是否连接！\033[0m" % ssid)
    else:
        print("\033[0;37;42m当前连接的wifi名称为:%s\033[0m" % ssid)
    return ssid
    pass


pass


class ManualProxy(ProxyMode):
    def __init__(self, proxy_conf: dict):
        super().__init__(proxy_conf)

    pass

    def check_parameter(self, manual_proxy_dict):
        """
        用于判断手动模式下，json是否符合自定义的Json格式，当存在键为 key 的对象 并且格式正确时，返回TRUE
        :param manual_proxy_dict:
        :return:
        """
        if isinstance(manual_proxy_dict, dict):
            key = "manual"
            if key in manual_proxy_dict:
                set_conf = manual_proxy_dict[key]
                if ('notLocal' in set_conf
                        and 'localIdentification' in manual_proxy_dict and manual_proxy_dict[
                            "localIdentification"] != ""
                        and 'ProxyServer' in set_conf and set_conf["ProxyServer"] != ""
                        and 'ProxyOverride' in set_conf):
                    self.check = True
                    print("\033[0;32;40m 配置校验通过\033[0m")
                else:
                    print("\033[0;31;40m 配置校验未通过！\033[0m")
            else:
                print("\033[0;31;40m 未找到手动模式的配置！\033[0m")
        else:
            print("\033[0;31;40m 配置文件格式不正确！\033[0m")
        pass

    def set_proxy(self):
        """
        当从配置文件中检索到当前wifi的配置时，开启代理，反之关闭代理
        :param proxy_conf:
        :return:
        """
        conf = self.proxy_conf['manual']
        # 获取本地标识
        local_identification: str = self.proxy_conf["localIdentification"]
        print("            \033[0;33;40m请选择要进行的操作，然后按回车！\033[0m")
        print("            \033[0;33;40m执行命令后，系统设置面板未刷新，请刷新或者重新打开系统设置面板！\033[0m")
        print("      ================================================================")
        print("")
        print("            1.修改ip为内网ip，并设置代理")
        print("")
        print("            2.恢复ip为动态ip，并关闭代理")
        print("")
        print("            3.退出")
        # 等待用户输入
        user_input = input("请输入序号：")
        if user_input == "1":
            if conf["notLocal"] == "selected":
                # 设置代理
                start_proxy(conf["ProxyServer"],
                            local_identification + conf["ProxyOverride"].replace(local_identification, ""))
                print("勾选“请勿将代理服务器用于本地(Intranet)地址”,并开启系统代理！")
            else:
                # 设置代理
                start_proxy(conf["ProxyServer"], conf["ProxyOverride"])
                print("取消勾选“请勿将代理服务器用于本地(Intranet)地址”,并开启系统代理！")
        elif user_input == "2":
            # 关闭代理
            close_proxy()
            print("关闭代理！")
        else:
            wait_for_input(5)

        pass


pass


def wait_for_input(timeout):
    """

    :type timeout: int
    """
    print("程序将于 %d 秒后自动退出，或请按任意键立即退出……" % timeout)
    user_input = None

    def input_thread():
        nonlocal user_input
        user_input = input()

    input_thread = threading.Thread(target=input_thread)
    input_thread.start()
    input_thread.join(timeout)

    if input_thread.is_alive():
        # 线程仍在运行，即超时
        # print("等待超时")
        os._exit(1)
        input_thread.join()
    else:
        # 用户已输入
        print(user_input)
    pass


# 如果从来没有开过代理 有可能健不存在 会报错
INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                   0, winreg.KEY_ALL_ACCESS)
# 设置刷新
INTERNET_OPTION_REFRESH = 37
INTERNET_OPTION_SETTINGS_CHANGED = 39
internet_set_option = ctypes.windll.Wininet.InternetSetOptionW


def set_key(name, value):  # 修改键值
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    winreg.SetValueEx(INTERNET_SETTINGS, name, 0, reg_type, value)
    pass


def get_key(name, default=None):
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)

    return winreg.QueryValueEx(INTERNET_SETTINGS, name)

    pass


def start_proxy(proxy_server, proxy_override):
    # 启用代理
    set_key('ProxyEnable', 1)  # 启用
    # 绕过本地
    set_key('ProxyServer', proxy_server)  # 代理IP及端口
    set_key('ProxyOverride', proxy_override)  # 忽略地址
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    pass


def close_proxy():
    # 停用代理
    set_key('ProxyEnable', 0)  # 停用
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    pass


if __name__ == '__main__':
    # 读取获取配置文件
    proxy_dict = ProxyMode.read_json()
    if proxy_dict != False:
        if 'mode' in proxy_dict:
            if proxy_dict['mode'] == 'auto':

                proxy_object = AutoProxy(proxy_dict)
                if proxy_object.check:
                    proxy_object.set_proxy()

            elif proxy_dict['mode'] == 'name':

                proxy_object = NameProxy(proxy_dict)
                if proxy_object.check:
                    proxy_object.set_proxy()

            elif proxy_dict['mode'] == 'manual':

                proxy_object = ManualProxy(proxy_dict)
                if proxy_object.check:
                    proxy_object.set_proxy()

            else:
                print("未检索到对应模式[自动模式：auto "
                      " wifi名称模式: name "
                      "手动模式: manual "
                      "，请检查配置模式是否正确！")

    wait_for_input(5)
