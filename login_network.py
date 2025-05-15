# -*- coding: utf-8 -*-
# @Author  : N10
# @Email   : dp7100@126.com
# @Software: PyCharm

import msvcrt
import requests
import json
import os

# 使cmd能够正确输出颜色
if os.name == "nt":
    os.system("")

# 切换工作目录到系统临时文件区域
os.chdir(os.getenv('TMP'))
# 文件名称
file_name = "user_account.json"


# md6加密函数 - 根据前端crypt.js实现
def md6(s: str) -> str:
    """完全匹配前端crypt.js的md6函数实现"""

    def mc(a: int) -> str:
        a = a & 0xFF  # 确保a是无符号8位整数
        b = "0123456789ABCDEF"
        if a == ord(' '):
            return '+'
        elif (a < ord('0') and a != ord('-') and a != ord('.')) or \
                (a < ord('A') and a > ord('9')) or \
                (a > ord('Z') and a < ord('a') and a != ord('_')) or \
                (a > ord('z')):
            return f"%{b[(a >> 4) & 0xF]}{b[a & 0xF]}"
        else:
            return chr(a)

    def m(a: int) -> int:
        return (
                ((a & 1) << 7) |
                ((a & 0x2) << 5) |
                ((a & 0x4) << 3) |
                ((a & 0x8) << 1) |
                ((a & 0x10) >> 1) |
                ((a & 0x20) >> 3) |
                ((a & 0x40) >> 5) |
                ((a & 0x80) >> 7)
        ) & 0xFF  # 确保结果在0-255范围内

    result = ""
    c = 0xbb
    for i in range(len(s)):
        a = ord(s[i])
        ma = m(a)
        mask = i & 0xff
        xor = 0x35 ^ mask
        c = (ma ^ xor) & 0xFF  # 关键：确保c是无符号8位整数
        result += mc(c)
    return result


# 检查是否需要输入账号密码，如果不存在临时文件，根据输入新建临时文件保存账号密码。
if not os.path.exists(file_name):
    # 输入账号密码
    account = input("请输入你的账号: ")
    password = input("请输入你的密码: ")

    # 对密码进行哈希处理
    hashed_password = md6(password)

    # 保存账号和哈希后的密码
    res = {
        'account': account,
        'password': hashed_password
    }
    print("已安全保存账号信息", res)
    # 写入json
    with open(file_name, "w+") as fp:
        fp.write(json.dumps(res))
# 如果存在，说明之前已经写入
else:
    # 读取账号和哈希后的密码
    with open(file_name, "r") as fp:
        res = json.loads(fp.read())
        account = res['account']
        hashed_password = res['password']  # 明确这是哈希后的密码
        print(f"已读取保存的账号: {account}")

# 请求网址
url = "http://10.54.216.100:90/login"
# 请求头
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", # 必须指定，否则报404
}

print("\n正在尝试互联网登录认证...")

while True:
    try:
        # 直接使用从文件中读取的哈希值
        encrypted_pwd = hashed_password

        # 打印发送的加密密码（调试用）
        # print(f"发送的加密密码: {encrypted_pwd}")

        # 构建登录请求参数
        payload = f"page_version=10.0&username={account}&password={encrypted_pwd}&login_type=login&page_language=zh&terminal=pc&uri=MTAuNTQuMjE2LjEwMDo5MC9sb2dpbj9oYXNfb3JpX3VyaQ=="

        # 发送登录请求
        res = requests.post(url, data=payload, headers=headers)

        # 打印响应内容（调试用）
        # print(f"响应状态码: {res.status_code}")
        # print(f"响应内容: {res.text}\n")

        # 判断登录是否成功
        failed_keywords = ["登录失败", "error", "账号或密码错误", "认证失败", "账号或者密码错误"]
        success_keywords = ["success", "欢迎", "认证成功", "登录成功"]

        has_failed = any(keyword in res.text for keyword in failed_keywords)
        has_success = any(keyword in res.text for keyword in success_keywords)

        is_success = res.status_code == 200 and (has_success or "location.href" in res.text) and not has_failed

        if is_success:
            print(f"\033[7;32;47m登录成功! \033[0m")
        else:
            print(f"\033[7;31;47m登录失败! {res.content.decode('utf-8')} \033[0m")
            print("\033[7;31;47m", "请检查账号密码是否正确!", "\033[0m")
            os.remove(file_name)
            print("\033[7;36;47m", "已清除保存的账号信息。\n请重新启动程序并输入正确的账号密码。", "\033[0m")

        print("按任意键退出...")
        if ord(msvcrt.getch()):
            break
    except Exception as err:
        print("\033[7;31;47m", "登录错误！\t可能需要先连接WiFi？", "\033[0m")
        print("\033[7;33;40m", f"错误详情: {err}", "\033[0m")
        print("按 'R' 键重新尝试，或按任意键退出...")
        if ord(msvcrt.getch()) != 114:
            break