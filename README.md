# NetworkProxy
Windows系统一键配置系统代理

# 一、打包成 exe 文件步骤

1. 通过 `PyCharm Professional` 打开本项目

2. 依次点击 `设置` -> `项目:项目名称 ` -> `Python解释器` -> `+`

3. 在弹出页面中搜索 `pyinstaller` ，并添加

4. 在`终端`执行打包指令

   ```cmd
   pyinstaller -F -i ./ico.ico ./main.py
   ```

   即可在本项目的 `dist` 目录下找到打包好的`exe`文件。

# 二、配置文件

位置：`main.py` 同目录下的 `proxy.json`

```
{
  "notLocal": "selected",
  "localIdentification": "<local>;",
  "ProxyServer": "",
  "ProxyOverride": ""
}
```

解释：

```
notLocal: 非必填项，当值为"selected"时，勾选 “请勿将代理服务器用于本地(Intranet)地址” 选项。

localIdentification: 必填项，勾选 “请勿将代理服务器用于本地(Intranet)地址” 选项 的标识字符串，默认为"<local>;"。

ProxyServer: 必填项，设置代理的地址，格式为 ip:port 。

ProxyServer: 非必填项，忽略的地址列表，字符串格式，地址见以分段号分割 ，若是包含字符串"<local>;" ，则勾选  “请勿将代理服务器用于本地(Intranet)地址” 选项。
```

