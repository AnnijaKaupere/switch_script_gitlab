from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import SSHException
from netmiko.exceptions import AuthenticationException
import time

# here is list of switch ip address
ip_list = []
# '10.70.100.51'
addresses = str(input("Введите адреса через запятую без пробела: "))
split_addresses = addresses.split(",")
for i in split_addresses:
    ip_list.append(i)
print(ip_list)

while True:
    time.sleep(1)
    print('Working...')
    break

# clearing the old data from the CSV file and writing the headers
f = open("login_issues.csv", "w+")
f.write("IP Address, Status")
f.write("\n")
f.close()

f = open("conf.txt", 'w').close()


def error_mes(mes):
    o = open("conf.txt", "a")
    o.write("\n\n----------------------IP_ADDRESS: ", )
    o.write(ip)
    o.write("----------------------")
    o.write("\n")
    o.write(mes)
    o.write("\n\n")
    o.close()


# loop all ip addresses in ip_list
for ip in ip_list:
    eltex = {
        'device_type': 'eltex',
        'ip': ip,
        'username': 'admin',  # ssh username
        'password': 'admin',  # ssh password
        'secret': 'password',  # ssh_enable_password
        'ssh_strict': False,
        'fast_cli': False,
    }

    # handling exceptions errors

    try:
        net_connect = ConnectHandler(**eltex)

    except NetMikoTimeoutException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Device Unreachable/SSH not enabled")
        f.write("\n")
        f.close()
        error_mes("Device Unreachable/SSH not enabled")
        continue

    except AuthenticationException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Authentication Failure")
        f.write("\n")
        f.close()
        error_mes("Authentication Failure")
        continue
    except SSHException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "SSH not enabled")
        f.write("\n")
        f.close()
        error_mes("SSH not enabled")
        continue

    try:
        net_connect.enable()
        f = open("login_issues.csv", "a")
        f.write(ip + "," + " Connected")
        f.write("\n")
        f.close()

    # handling exceptions errors
    except ValueError:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Could be SSH Enable Password issue")
        f.write("\n")
        f.close()
        error_mes("Could be SSH Enable Password issue")
        continue

    sh_run_output = net_connect.send_command('show run')
    # print(sh_run_output)

    sh_tr7_output = net_connect.send_command('show interfaces counters gi1/0/7')
    sh_tr8_output = net_connect.send_command('show interfaces counters gi1/0/8')
    sh_lldp_output = net_connect.send_command('show lldp neighbors')

    config = net_connect.send_command(
        command_string="configure",
        expect_string=r"#",
        strip_prompt=False,
        strip_command=False
    )
    sh_ver_output = net_connect.send_command('do show version')
    # print(sh_ver_output)

    f = open("conf.txt", "a")
    f.write("\n\n----------------------IP_ADDRESS: ", )
    f.write(ip)
    f.write("----------------------")
    f.write("\n\n")
    f.write("-----version info-----")
    f.write(sh_ver_output)
    f.write("\n\n")
    f.write("-----interfaces counters info-----")
    f.write(sh_tr7_output)
    f.write(sh_tr8_output)
    f.write("\n\n")
    f.write("-----lldp neighbors info-----")
    f.write(sh_lldp_output)
    f.write("\n\n")
    f.write("-----configuration info-----")
    f.write(sh_run_output)


f = open("conf.txt", "r")
content = f.read()
# print(content)

import os
import subprocess


def push_to_gitlab(file_path, repository_url, branch_name, commit_message):
    # Переходим в директорию с файлом
    os.chdir(os.path.dirname(file_path))

    # Инициализируем Git-репозиторий, если он еще не существует
    subprocess.run(['git', 'init'])

    # Добавляем файл в индекс
    subprocess.run(['git', 'add', file_path])

    # Создаем коммит
    subprocess.run(['git', 'commit', '-m', commit_message])

    # Добавляем удаленный репозиторий GitLab
    subprocess.run(['git', 'remote', 'add', 'origin', repository_url])

    # Отправляем коммит в репозиторий на указанную ветку
    subprocess.run(['git', 'push', '-u', 'origin', branch_name])


# Пример использования функции
file_path = 'C:\\Users\\student1\\PycharmProjects\\switch_script_gitlab\\conf.txt'
repository_url = 'https://git.ict29.ru/student1/switch_script'
branch_name = 'master'
commit_message = 'committing conf.txt'

push_to_gitlab(file_path, repository_url, branch_name, commit_message)


input('Press <ENTER> to exit')
