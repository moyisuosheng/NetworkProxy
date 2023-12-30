# 这是一个示例 Python 脚本。
import json
import traceback
# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


import winreg
import ctypes
from typing import TextIO

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


def start_proxy(proxy_server, proxy_override):
    # 启用代理
    set_key('ProxyEnable', 1)  # 启用
    # 绕过本地
    set_key('ProxyServer', proxy_server)  # 代理IP及端口
    set_key('ProxyOverride', proxy_override)  # 忽略地址
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)


def close_proxy():
    # 停用代理
    set_key('ProxyEnable', 0)  # 停用
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)


# 读取json配置
def read_json():
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
        write_json()
        print("\033[0;33;40m未找到配置文件，已在当前目录重新写入空配置文件(proxy.json)！\033[0m")
        input("\033[0;33;40m请按下任意键退出……\033[0m")
        exit(1)
    except json.decoder.JSONDecodeError:
        write_json()
        print("\033[0;33;40m配置文件损坏，已在当前目录重新写入空配置文件(proxy.json)！\033[0m")
        input("\033[0;33;40m请按下任意键退出……\033[0m")
        exit(1)

def write_json():
    try:
        json_str = {
            "notLocal": "selected",
            "localIdentification": "<local>;",
            "ProxyServer": "",
            "ProxyOverride": ""
        }
        json_dumps = json.dumps(json_str)
        with open('./proxy.json', 'w') as f:
            f.write(json_dumps)
            return True
    except IOError:
        # 如果捕获异常，记录失败日志
        traceback.print_exc()


def check_json_format(proxy_dict):
    """
    用于判断一个字符串是否符合Json格式
    :param proxy_dict:
    :param raw_msg:
    :return:
    """
    if not isinstance(proxy_dict, dict):
        if input("\033[0;31;40m请检查配置文件，notLocal 、localIdentification 和 ProxyServer 为必填项，请检查是否已填写配置！是否重新生成空配置文件("
                 "y/n)？\033[0m").lower() in [
            "y", "yes"]:
            write_json()
            print("\033[0;32;40m已在当前目录重新写入空配置文件(proxy.json)！\033[0m")
            input("\033[0;33;40m请按下任意键退出……\033[0m")
            exit(1)
        else:
            exit(1)
    if ('notLocal' in proxy_dict
            and 'ProxyServer' in proxy_dict
            and 'ProxyOverride' in proxy_dict
            and 'localIdentification' in proxy_dict
            and proxy_dict["ProxyServer"] != ""
            and proxy_dict["localIdentification"] != ""):
        return True
    else:
        if input(
                "\033[0;31;40m配置文件损坏,请检查是否已填写配置！notLocal 和 ProxyServer 为必填项。是否重新生成空配置文件(y/n)？\033[0m").lower() in [
            "y", "yes"]:
            write_json()
            print("\033[0;32;40m已在当前目录重新写入空配置文件(proxy.json)！\033[0m")
            input("\033[0;33;40m请按下任意键退出……\033[0m")
            exit(1)
        else:
            exit(1)


if __name__ == '__main__':
    # 勾选“请勿将代理服务器用于本地(Intranet)地址” ，就追加这段字符串

    proxy_data_dict = read_json()

    localIdentification: str = proxy_data_dict["localIdentification"]

    check_json_format(proxy_data_dict)

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
    userInput = input("请输入序号：")
    if userInput == "1":
        if proxy_data_dict["notLocal"] == "selected":
            # 设置代理
            start_proxy(proxy_data_dict["ProxyServer"],
                        localIdentification + proxy_data_dict["ProxyOverride"].replace(localIdentification, ""))
            print("勾选“请勿将代理服务器用于本地(Intranet)地址”,并设置代理！")
        else:
            # 设置代理
            start_proxy(proxy_data_dict["ProxyServer"], proxy_data_dict["ProxyOverride"])
            print("取消勾选“请勿将代理服务器用于本地(Intranet)地址”,并设置代理！")
    elif userInput == "2":
        # 关闭代理
        close_proxy()
        print("关闭代理！")
    else:
        print()
print("请按任意键退出……")
# 等待用户输入
input()
