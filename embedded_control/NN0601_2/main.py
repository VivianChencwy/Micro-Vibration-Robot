import socket
from pynput import keyboard

# 机器人的IP地址和端口号
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip_port = ('172.20.10.4', 1234)

# 发送命令到机器人
def send_command(power1, power2):
    command = f"M1:{power1},M2:{power2}"
    client.sendto(command.encode('utf-8'), ip_port)
    print(f"Sent: {command}")

# 按键响应函数
def on_key_press(key):
    try:
        if key.char == 'w':  # 前进
            send_command(110, 200)
        elif key.char == 's':  # 后退
            send_command(0, 0)
        elif key.char == 'a':  # 左转
            send_command(0, 125)
        elif key.char == 'd':  # 右转
            send_command(255, 0)

    except AttributeError:
        pass

# 创建键盘监听器
listener = keyboard.Listener(on_press=on_key_press)
listener.start()
listener.join()

client.close()
