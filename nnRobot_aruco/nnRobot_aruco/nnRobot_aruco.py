import cv2 
import numpy as np 
import socket
import math
import time

BUFSIZE = 1024 # 网络通信中一次可以接收或发送的最大数据量（以字节为单位）
client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # 地址族为IPv4，socket类型为UDP
ip_port_1 = ('172.20.10.9', 1234)  # 输入第一个机器人IP地址以及端口
ip_port_2 = ('172.20.10.10', 1234) # 输入第二个机器人IP地址以及端口

Point = []
sta = True
#构建滑块调节二值图的阀值
n = 199 #设定初始值
def nothing(x):
    pass
def createbars():
    cv2.createTrackbar("n","image",n, 250, nothing) 
# 记录鼠标点击的位置
def setpoint(event,x,y,flags,param):  
    global Point # 指明要修改全局变量Point
    if event==cv2.EVENT_LBUTTONDOWN: # 左键点击增加点的个数
        print("Point is",x,y)
        Point.append((x,y))
        print(Point)
    if event==cv2.EVENT_RBUTTONDOWN: # 右键直接重置Point
        Point = []
#弧度计算
def get_angle_by_cos(p0, p1, p2): 
    """
    使用向量的点乘公式计算角度值
    :param p0:
    :param p1: 角的顶点
    :param p2:
    :return: 弧度
    """
    # print(p0, p1, p2)
    # 将三角形两条边用向量来表示，l1, l2是元胞
    l1 = p0[0] - p1[0], p0[1] - p1[1]
    l2 = p2[0] - p1[0], p2[1] - p1[1]
    # print(l1, l2)
    m = math.sqrt(l1[0]**2 + l1[1]**2) * math.sqrt(l2[0]**2 + l2[1]**2)
    if m == 0:
        return 0
    cos = (l1[0] * l2[0] + l1[1] * l2[1]) / m
    # print(cos)
    
    # 将cos转成角度（弧度值）
    try:
        R = math.acos(cos)
    except:
        R = 180
    return R
# 线段长度计算
def calculate_distance(point1, point2):  
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def send_command_1(power1, power2):
    command = f"M1:{power1},M2:{power2}"
    client.sendto(command.encode('utf-8'), ip_port_1)

def send_command_2(power1, power2):
    command = f"M1:{power1},M2:{power2}"
    client.sendto(command.encode('utf-8'), ip_port_2)

# main
# 创建VideoCapture对象，捕捉第一个摄像头的视频(参数0) 
camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
time.sleep(2.0)

# 判断视频是否打开 
if (camera.isOpened()):
    print('Open') 
else: 
    print('摄像头未打开') 
    
# 创建一个图像窗口，并且这个窗口的大小用户可以自己调整
#cv2.namedWindow("image",cv2.WINDOW_NORMAL)

Nx1_1 = 0 #确定机器人方向的点
Ny1_1 = 0 #确定机器人方向的点
Nx1_2 = 0
Ny1_2 = 0
Nx_1 = 0 #机器人中点
Ny_1 = 0 #机器人中点
Nx_2 = 0 #机器人中点
Ny_2 = 0 #机器人中点
Mx = 0 #下一个机器人要去的位置
My = 0 #下一个机器人要去的位置
key_mode = 0 # 1只控制无壳机器人，2只控制有壳子机器人，3两个一起控制
# 创建ArUco字典和检测参数
cameraMatrix = np.load("calibration_matrix.npy")
distCoeffs = np.load("distortion_coefficients.npy")

while True:
    # 从摄像头读取一帧图像，grabbed布尔值代表是否成功抓取，frame_lwpCV那一帧图像本身
    grabbed, frame_lwpCV = camera.read() 
    if not grabbed:
        continue
    frame_gray = cv2.cvtColor(frame_lwpCV,cv2.COLOR_BGR2GRAY)
    cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters_create()
    
    read_key_mode = cv2.waitKey(1) & 0xFF 
    if read_key_mode == ord('1'):
        key_mode = 1
        print('mode:1')
    elif read_key_mode == ord('2'):
        key_mode = 2
        print('mode:2')
    elif read_key_mode == ord('3'):
        key_mode = 3
        print('mode:3')
    
    corners, ids, rejected_img_points = cv2.aruco.detectMarkers(frame_gray, cv2.aruco_dict, parameters=parameters)
    if len(corners) > 0:
        #暂时先弄1个
        for i in range(0, len(ids)):
            # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, cameraMatrix,
                                                                        distCoeffs)
            # Draw a square around the markers
            cv2.aruco.drawDetectedMarkers(frame_lwpCV, corners) 
            # Draw Axis
            #cv2.aruco.drawAxis(frame_lwpCV, cameraMatrix, distCoeffs, rvec, tvec, 0.01) 
            length = 0.01
            axis = np.float32([[length,0,0], [0,length,0], [0,0,length]]).reshape(-1,3)
        
            # 投影 3D 点到图像平面
            imgpts, _ = cv2.projectPoints(axis, rvec, tvec, cameraMatrix, distCoeffs)
            
            # 获取标记中心点的 2D 坐标
            corner = np.float32([0, 0, 0]).reshape(-1, 3)
            origin, _ = cv2.projectPoints(corner, rvec, tvec, cameraMatrix, distCoeffs)
            origin = tuple(origin.ravel().astype(int))
            if ids[i] == 14:
                Nx_1, Ny_1 = origin
                Nx1_1, Ny1_1 = tuple(imgpts[1].ravel().astype(int)) #红色的轴位方向

                # 绘制轴
                #frame_lwpCV = cv2.line(frame_lwpCV, origin, tuple(imgpts[0].ravel().astype(int)), (0,0,255), 5)  # X 轴：红色
                frame_lwpCV = cv2.line(frame_lwpCV, origin, tuple(imgpts[1].ravel().astype(int)), (0,255,0), 5)  # Y 轴：绿色
                #frame_lwpCV = cv2.line(frame_lwpCV, origin, tuple(imgpts[2].ravel().astype(int)), (255,0,0), 5)  # Z 轴：蓝色
            elif ids[i] == 19:
                Nx_2, Ny_2 = origin
                Nx1_2, Ny1_2 = tuple(imgpts[1].ravel().astype(int)) #红色的轴位方向

                # 绘制轴
                #frame_lwpCV = cv2.line(frame_lwpCV, origin, tuple(imgpts[0].ravel().astype(int)), (0,0,255), 5)  # X 轴：红色
                frame_lwpCV = cv2.line(frame_lwpCV, origin, tuple(imgpts[1].ravel().astype(int)), (0,255,0), 5)  # Y 轴：绿色
                #frame_lwpCV = cv2.line(frame_lwpCV, origin, tuple(imgpts[2].ravel().astype(int)), (255,0,0), 5)  # Z 轴：蓝色
    
    if key_mode == 1:
        #获取Mx,My的值
        if len(Point) != 0:
            cv2.line(frame_lwpCV,(Nx_1, Ny_1),Point[0],(0,0,255),2)
            if(len(Point)) > 1:
                for j in range(len(Point)-1):
                    cv2.line(frame_lwpCV,Point[j],Point[j+1],(0,0,255),2)
            Mx = Point[0][0]
            My = Point[0][1]
        else:
            Mx = 0
            My = 0

        #处理三个点的数据，机器人y轴线两个点line，鼠标单击的点Mx，My。设A为短边的中点，B为长边的中点，C为鼠标单击点点
        if Mx !=0 and My !=0:    
            cv2.line(frame_lwpCV,(Nx_1,Ny_1),(Mx,My),(0,0,255),2)

            # 计算机器人与目标点的弧度与角度ABC
            a_1 = get_angle_by_cos((Nx1_1,Ny1_1),(Nx_1,Ny_1),(Mx,My))  
            angle_1 = round(math.degrees(a_1), 2)
            # 计算机器人方向
            # 原理：AB与AC叉乘，若大于0，则AB应该顺时针旋转；若小于0，则AB应该逆时针旋转
            b_1 = ((Mx-Nx1_1)*(Ny_1-Ny1_1))-((My-Ny1_1)*(Nx_1-Nx1_1))  
            #print(f"弧度：{a}， 角度：{angle} , 方向: {b}")
            #机器人与目标点距离 BC
            N_M_1 = calculate_distance((Nx_1,Ny_1),(Mx,My))   
            # 在图像上绘制文本，显示距离
            font=cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame_lwpCV,str(int(N_M_1)),(Nx_1,Ny_1),font,1,(0,0,255),2)

            # 对轨迹的更新
            #print(angle)
            #无壳
            if angle_1 < 20:
                if N_M_1 > 25 :
                    send_command_1(190, 245)
                    #print(f"M1:{110},M2:{200}")
            else:
                if b_1 < 0: #先假设右转
                    #右边马达顺时针
                    send_command_1(180, 0)
                    #print(f"M1:{50},M2:{0}")
                else:
                    send_command_1(0, 150)
                    #print(f"M1:{0},M2:{125}")
            
            if N_M_1 <= 25:
                    if len(Point) != 0:
                        Point.remove(Point[0])
                        print(Point)
                    else:
                        Mx = 0 
                        My = 0
        else:
            send_command_1(0,0)
    elif key_mode == 2:
        #获取Mx,My的值
        if len(Point) != 0:
            cv2.line(frame_lwpCV,(Nx_2, Ny_2),Point[0],(0,0,255),2)
            if(len(Point)) > 1:
                for j in range(len(Point)-1):
                    cv2.line(frame_lwpCV,Point[j],Point[j+1],(0,0,255),2)
            Mx = Point[0][0]
            My = Point[0][1]
        else:
            Mx = 0
            My = 0

        #处理三个点的数据，机器人y轴线两个点line，鼠标单击的点Mx，My。设A为短边的中点，B为长边的中点，C为鼠标单击点点
        if Mx !=0 and My !=0:    
            cv2.line(frame_lwpCV,(Nx_2,Ny_2),(Mx,My),(0,0,255),2)

            # 计算机器人与目标点的弧度与角度ABC
            a_2 = get_angle_by_cos((Nx1_2,Ny1_2),(Nx_2,Ny_2),(Mx,My))  
            angle_2 = round(math.degrees(a_2), 2)
            # 计算机器人方向
            # 原理：AB与AC叉乘，若大于0，则AB应该顺时针旋转；若小于0，则AB应该逆时针旋转
            b_2 = ((Mx-Nx1_2)*(Ny_2-Ny1_2))-((My-Ny1_2)*(Nx_1-Nx1_2))  
            #print(f"弧度：{a}， 角度：{angle} , 方向: {b}")
            #机器人与目标点距离 BC
            N_M_2 = calculate_distance((Nx_2,Ny_2),(Mx,My))  
            # 在图像上绘制文本，显示距离
            font=cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame_lwpCV,str(int(N_M_2)),(Nx_2,Ny_2),font,1,(0,0,255),2)

            # 对轨迹的更新
            #有壳
            if angle_2 < 20:
                if N_M_2 > 25 :
                    send_command_2(190, 245)
                    #print(f"M1:{110},M2:{200}")
            else:
                if b_2 < 0: #先假设右转
                    #右边马达顺时针
                    send_command_2(180, 0)
                    #print(f"M1:{50},M2:{0}")
                else:
                    send_command_2(0, 150)
                    #print(f"M1:{0},M2:{125}")
                    
            if N_M_2 <= 25:
                send_command_2(0,0)
            
            if N_M_2 <= 25:
                    if len(Point) != 0:
                        Point.remove(Point[0])
                        print(Point)
                    else:
                        Mx = 0 
                        My = 0
        else:
            send_command_2(0,0)
    elif key_mode == 3:
        #获取Mx,My的值
        if len(Point) != 0:
            cv2.line(frame_lwpCV,(Nx_1, Ny_1),Point[0],(0,0,255),2)
            cv2.line(frame_lwpCV,(Nx_2, Ny_2),Point[0],(0,0,255),2)
            if(len(Point)) > 1:
                for j in range(len(Point)-1):
                    cv2.line(frame_lwpCV,Point[j],Point[j+1],(0,0,255),2)
            Mx = Point[0][0]
            My = Point[0][1]
        else:
            Mx = 0
            My = 0

        #处理三个点的数据，机器人y轴线两个点line，鼠标单击的点Mx，My。设A为短边的中点，B为长边的中点，C为鼠标单击点点
        if Mx !=0 and My !=0:    
            cv2.line(frame_lwpCV,(Nx_1,Ny_1),(Mx,My),(0,0,255),2)
            cv2.line(frame_lwpCV,(Nx_2,Ny_2),(Mx,My),(0,0,255),2)

            # 计算机器人与目标点的弧度与角度ABC
            a_1 = get_angle_by_cos((Nx1_1,Ny1_1),(Nx_1,Ny_1),(Mx,My))  
            a_2 = get_angle_by_cos((Nx1_2,Ny1_2),(Nx_2,Ny_2),(Mx,My))  
            angle_1 = round(math.degrees(a_1), 2)
            angle_2 = round(math.degrees(a_2), 2)
            # 计算机器人方向
            # 原理：AB与AC叉乘，若大于0，则AB应该顺时针旋转；若小于0，则AB应该逆时针旋转
            b_1 = ((Mx-Nx1_1)*(Ny_1-Ny1_1))-((My-Ny1_1)*(Nx_1-Nx1_1))  
            b_2 = ((Mx-Nx1_2)*(Ny_2-Ny1_2))-((My-Ny1_2)*(Nx_1-Nx1_2))  
            #print(f"弧度：{a}， 角度：{angle} , 方向: {b}")
            #机器人与目标点距离 BC
            N_M_1 = calculate_distance((Nx_1,Ny_1),(Mx,My))  
            N_M_2 = calculate_distance((Nx_2,Ny_2),(Mx,My))  
            # 在图像上绘制文本，显示距离
            font=cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame_lwpCV,str(int(N_M_1)),(Nx_1,Ny_1),font,1,(0,0,255),2)
            cv2.putText(frame_lwpCV,str(int(N_M_2)),(Nx_2,Ny_2),font,1,(0,0,255),2)

            # 对轨迹的更新
            #print(angle)
            #无壳
            if angle_1 < 20:
                if N_M_1 > 25 :
                    send_command_1(190, 245)
                    #print(f"M1:{110},M2:{200}")
            else:
                if b_1 < 0: #先假设右转
                    #右边马达顺时针
                    send_command_1(180, 0)
                    #print(f"M1:{50},M2:{0}")
                else:
                    send_command_1(0, 150)
                    #print(f"M1:{0},M2:{125}")
            
            #有壳
            if angle_2 < 20:
                if N_M_2 > 25 :
                    send_command_2(190, 245)
                    #print(f"M1:{110},M2:{200}")
            else:
                if b_2 < 0: #先假设右转
                    #右边马达顺时针
                    send_command_2(180, 0)
                    #print(f"M1:{50},M2:{0}")
                else:
                    send_command_2(0, 150)
                    #print(f"M1:{0},M2:{125}")
                    
            if N_M_1 <= 25:
                send_command_1(0,0)
            if N_M_2 <= 25:
                send_command_2(0,0)
            
            if N_M_1 <= 25 and N_M_2 <= 25:
                    if len(Point) != 0:
                        Point.remove(Point[0])
                        print(Point)
                    else:
                        Mx = 0 
                        My = 0
        else:
            send_command_1(0,0)
            send_command_2(0,0)
    
    cv2.imshow('Image', frame_lwpCV)
    cv2.setMouseCallback("Image", setpoint)
    
    key = cv2.waitKey(1) & 0xFF 
    # 按'q'健退出循环 
    if key == ord('q'):
        break 
    '''
    # 按'p'键切换图像的绘制模式
    if key == ord('p'):
        sta = not sta
        print(sta)
    '''
        
camera.release()
cv2.destroyAllWindows()

'''
#处理三个点的数据，机器人y轴线两个点line，鼠标单击的点Mx，My。设A为短边的中点，B为长边的中点，C为鼠标单击点点
    if Mx !=0 and My !=0:    
        cv2.line(frame_lwpCV,(Nx,Ny),(Mx,My),(0,0,255),2)

        # 计算机器人与目标点的弧度与角度ABC
        a = get_angle_by_cos((Nx1,Ny1),(Nx,Ny),(Mx,My))  
        angle = round(math.degrees(a), 2)
        # 计算机器人方向
        # 原理：AB与AC叉乘，若大于0，则AB应该顺时针旋转；若小于0，则AB应该逆时针旋转
        b = ((Mx-Nx1)*(Ny-Ny1))-((My-Ny1)*(Nx-Nx1))  
        #print(f"弧度：{a}， 角度：{angle} , 方向: {b}")
        #机器人与目标点距离 BC
        N_M = calculate_distance((Nx,Ny),(Mx,My))  
        # 在图像上绘制文本，显示距离
        font=cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame_lwpCV,str(int(N_M)),(Nx,Ny),font,1,(0,0,255),2)

        # 对轨迹的更新
        if N_M > 25 :
            msg = "C"+str(int(N_M))+",R"+str(int(angle))+",F"+str(b)
            client.sendto(msg.encode('utf-8'),ip_port)   #UDP发送数据
        if N_M <= 25 :
            if len(Point) != 0:
                Point.remove(Point[0])
                print(Point)
            else:
                Mx = 0 
                My = 0
    else:
        msg = "C0,R180,F1"
        client.sendto(msg.encode('utf-8'),ip_port)   #UDP发送数据
'''
