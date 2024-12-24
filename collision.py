import tkinter as tk           # 导入 Tkinter 库
from tkinter import *
import math
import random
import matplotlib.pyplot as plt
import numpy as np

'''
此碰撞实验程序源代码由Yanbin Zhang根据
浙江大学2023冬学期普通物理学II课程碰撞实验拓展小组的程序修改而来

'''

class Pair():
    # 数据组
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __lt__(self, b):
        if isinstance(b, Pair):
            return self.x < b.x
        else:
            return NotImplemented

class Group(Pair):
    # 浮点数据组类
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = float(self.x)
        self.y = float(self.y)
    def __add__(self, b):
        if isinstance(b, Group):
            return type(self)(self.x + b.x, self.y + b.y)
        else:
            return NotImplemented
    def __sub__(self, b):
        if isinstance(b, Group):
            return type(self)(self.x - b.x, self.y - b.y)
        else:
            return NotImplemented
    def mod(self):
        return math.sqrt(self.x*self.x+self.y*self.y)
    def __lt__(self, b):
        if isinstance(b, Group):
            return self.x < b.x
        else:
            return NotImplemented

class Vect(Group):
    # 向量 子类
    def __init__(self, x, y):
        super().__init__(x, y)
    def __mul__(self, b):
        if isinstance(b, Group):
            return self.x*b.x+self.y*b.y
        else:
            return type(self)(self.x * b, self.y * b)
    def __rmul__(self, a):
        return type(self)(self.x * a, self.y * a)

class Pos(Group):
    # 坐标 子类
    def __init__(self, x, y):
        super().__init__(x, y)

class Vel(Vect):
    # 速度 子类
    def __init__(self, x, y):
        super().__init__(x, y)

class Ball():
    def __init__(self, ID, pos, r=10, v = Vel(0,0), m = 100, fill = "", locked = False,sticky = 0):
        self.ID=ID
        self.pos=pos
        self.r=r
        self.v=v
        self.m=m
        self.fill = fill
        self.locked=locked
        self.poslb=tk.Label(root,text="("+str(round(pos.x,2))+","+str(round(pos.y,2))+")",fg='black',font=("黑体",10))
        self.poslb.place(x=self.pos.x,y=self.pos.y)
        self.mvlb=tk.Label(root,text="v:("+str(round(self.v.x,2))+","+str(round(self.v.y,2))+") m:"+str(round(self.m)),fg='black',font=("黑体",10))
        self.mvlb.place(x=self.pos.x,y=self.pos.y-20)
        self.IDlb=tk.Label(root,text="id: "+str(self.ID),fg='black',font=("黑体",10))
        self.IDlb.place(x=self.pos.x,y=self.pos.y-40)
        self.history=[]
        self.sticky = sticky
        

        self.momentum_history = []  # 记录动量的变化
        self.velocity_history = []  # 记录速度的变化

    def moveto(self, pos):
        self.pos=pos
    def move(self):
        self.pos += self.v
        self.history.append(math.sqrt(self.v.x**2+self.v.x**2))

        momentum = self.m * self.v.mod()  # 动量 = 质量 * 速度的模
        self.momentum_history.append(momentum)

        self.poslb.configure(text="("+str(round(self.pos.x,2))+","+str(round(self.pos.y,2))+")")
        self.mvlb.configure(text="v:("+str(round(self.v.x,2))+","+str(round(self.v.y,2))+") m:"+str(round(self.m)))
        self.poslb.place(x=self.pos.x,y=self.pos.y)
        self.mvlb.place(x=self.pos.x,y=self.pos.y-20)
        self.IDlb.place(x=self.pos.x,y=self.pos.y-40)


class Timer():
    # 计时器
    def __init__(self, root, func, time, enabled):
        self.rt = root
        self.func = func
        self.t=int(time)
        self.enabled=enabled
        if enabled:
            self.enable()
    def timeup(self):
        self.func()
        self.ti = self.rt.after(self.t, self.timeup)
    def enable(self):
        self.enabled = True
        self.timeup()
    def unable(self):
        self.enabled = False
        self.rt.after_cancel(self.ti)
    def reset_time(self, t):
        self.unable()
        self.t=int(t)
        self.enable()

class ID_Pool():
    # ID池
    def __init__(self):
        self.pool=[]
        self.topid=0
    def getid(self):
        if len(self.pool) == 0:
            self.topid+=1
            return self.topid
        else:
            return self.pool.pop()
    def back(self, p):
        self.pool.append(p)

Balls = []
id_pool = ID_Pool()
FPS = 60
DeadTime = 1e9
CountNum = 0

def draw_ball(ball):
    if ball.fill != "":
        cv.create_oval(ball.pos.x - ball.r, ball.pos.y - ball.r, ball.pos.x + ball.r, ball.pos.y + ball.r, fill = ball.fill)
    else:
        cv.create_oval(ball.pos.x - ball.r, ball.pos.y - ball.r, ball.pos.x + ball.r, ball.pos.y + ball.r)

def creat_ball(p, r=3, v=Vel(0,0), m=500, fill = "", locked = False):
    ball_t = Ball(id_pool.getid(), p, r, v, m, fill, locked)
    Balls.append(ball_t)
    draw_ball(ball_t)

def del_ball(ball):
    ball.poslb.destroy()
    ball.mvlb.destroy()
    ball.IDlb.destroy()
    Balls.remove(ball)



def update(cv):
    #更新整个画布
    cv.delete("all")
    for ball in Balls:
        draw_ball(ball)

def solvefunc(a, b, c):
    delta = math.sqrt(b*b-4*a*c)
    return [(-b+delta)/(2*a), (-b-delta)/(2*a)]


def fiction(ball):
    en = en_fict.get()
    if en:
        try:
            # 获取用户输入的摩擦系数并转换为浮点数
            miu = float(miu_entry.get())
        except ValueError:
            miu = 0.01  # 默认值，当输入无效时使用
        fx = 0
        fy = 0
        if ball.v.x:
            fx = -miu * ball.m * ball.v.x / abs(ball.v.x)
        if ball.v.y:
            fy = -miu * ball.m * ball.v.y / abs(ball.v.y)
        return Vect(fx, fy)
    else:
        return Vect(0, 0)


def hit(b1, b2):
    global CountNum
    e = 1  # 默认完全弹性碰撞

    # 获取弹性系数 e 的值
    try:
        e = float(e_scale.get())  # 从输入框中获取弹性系数//读取进度条内容
        e = min(max(e, 0), 1)  # 保证弹性系数在0到1之间
    except ValueError:
        e = 1  # 如果输入无效，使用默认值 1

    # 碰撞计算
    CountNum += 100
    dv = b1.v - b2.v
    if dv.mod() == 0:
        return
    if hited(b1, b2) == False:
        return
    dp = b2.pos - b1.pos
    dt = 0
    if dp.mod() < b1.r + b2.r:
        a = dv.x ** 2 + dv.y ** 2
        b = -2 * (dv.x * dp.x + dv.y * dp.y)
        c = dp.x ** 2 + dp.y ** 2 - (b1.r + b2.r) ** 2
        dt = solvefunc(a, b, c)[1]
        b1.pos += dt * b1.v
        b2.pos += dt * b2.v

    # 根据弹性系数更新速度
    v1 = ((b1.m - e * b2.m) * b1.v.x + (1 + e) * b2.m * b2.v.x) / (b1.m + b2.m)
    v2 = ((b2.m - e * b1.m) * b2.v.x + (1 + e) * b1.m * b1.v.x) / (b1.m + b2.m)
    b1.v.x = v1
    b2.v.x = v2
    v1 = ((b1.m - e * b2.m) * b1.v.y + (1 + e) * b2.m * b2.v.y) / (b1.m + b2.m)
    v2 = ((b2.m - e * b1.m) * b2.v.y + (1 + e) * b1.m * b1.v.y) / (b1.m + b2.m)
    b1.v.y = v1
    b2.v.y = v2

    dt = -dt
    b1.pos += dt * b1.v
    b2.pos += dt * b2.v



def hited(b1, b2):
    # 是否碰撞
    return (b1.v-b2.v).mod() != 0 and dis(b1.pos, b2.pos) <= b1.r + b2.r - 0.00001

def count_hit():
    global CountNum
    stp = len(Balls)
    hits = []
    for i in range(0, stp - 1):
        for j in range(i + 1, stp):
            CountNum += 2
            if hited(Balls[i], Balls[j]):
                hits.append(Pair(Balls[i].r + Balls[j].r - dis(Balls[i].pos, Balls[j].pos), [Balls[i], Balls[j]]))
    hits.sort()
    #if len(hits):
    #    print(str(len(hits)))
    return hits

def dis(p1, p2):
    return (p1-p2).mod()

def move():
    # 初次计算
    energy=0
    for ball in Balls:
        energy+=ball.v*ball.v*ball.m
        global CountNum
        CountNum += 1
        ball.move()
        if ball.pos.x <= 0:
            ball.v.x *= -1
            ball.pos.x = 1
        if ball.pos.x >= WIDTH:
            ball.v.x *= -1
            ball.pos.x = WIDTH - 1
        if ball.pos.y <= 0:
            ball.v.y *= -1
            ball.pos.y = 1
        if ball.pos.y >= HEIGHT:
            ball.v.y *= -1
            ball.pos.y = HEIGHT - 1

def main_loop():
    # 主循环
    global CountNum
    CountNum = 0
    move()
    while CountNum < DeadTime:
        hitlist = count_hit()
        if len(hitlist) == 0:
            break
        for hits in hitlist:
            hit((hits.y)[0], (hits.y)[1])
    for ball in Balls:
        if abs(ball.v.x)<=abs(fiction(ball).x):
            ball.v.x = 0
        else:
            ball.v.x += 1/ball.m * fiction(ball).x
        if abs(ball.v.y)<=abs(fiction(ball).y):
            ball.v.y = 0
        else:
            ball.v.y += 1/ball.m * fiction(ball).y
    global t
    t+=1
    time.configure(text=str(t))
    update(cv)

def mouse_press(event):
    global mouseball
    if vxin.get()=='' or vyin.get()=='' or m_in.get()=='':
        mouseball = creat_ball(Pos(event.x,event.y), 20, Vel(1,1), 5,  fill = "yellow")
        print("Default v m location is used, please input v(m/s) m(kg) and location(x,y)")
    else:
        mouseball = creat_ball(Pos(event.x,event.y), 20, Vel(float(vxin.get()),float(vyin.get())), float(m_in.get()),  fill = "yellow")

def mouse_up(event):
    global mouseball
    del_ball(mouseball)

def cmd_click():
    if timer.enabled:
        timer.unable()
        cmd.configure(text="Start")
    else:
        timer.enable()
        cmd.configure(text="Stop")

def clear():
    if select_id.get()=='':
        del_ball(Balls[len(Balls)-1])
    else:
        for ball in Balls:
            if ball.ID == int(select_id.get()):
                del_ball(ball) 
    update(cv)

def creat_ball_button():
    if vxin.get()=='' or vyin.get()=='' or m_in.get()=='' or locx.get()=='' or locy.get()=='':
        mouseball = creat_ball(Pos(100,100), 20, Vel(1,1), 5,  fill = "yellow")
        print("Default v m location is used, please input v(m/s) m(kg) and location(x,y)")
    else:
        creat_ball(Pos(float(locx.get()),float(locy.get())), 20, Vel(float(vxin.get()),float(vyin.get())), float(m_in.get()),  fill = "yellow")

def set_ball():
    for ball in Balls:
            if ball.ID == int(select_id.get()):
                if locx.get() !='' and locy.get() !='':
                    ball.pos = Pos(float(locx.get()),float(locy.get()))
                if vxin.get() !='' and vyin.get() !='':
                    ball.v = Vel(float(vxin.get()),float(vyin.get()))
                if m_in.get() !='':
                    ball.m = float(m_in.get())
    update(cv)

def ec_all_f():
    global e_flag
    e_flag=0
    creat_ball(Pos(100,100), 20, Vel(10*random.random()+1,0), 10*random.random()+1,  fill = "green")
    creat_ball(Pos(300,100), 20, Vel(1*random.random()+1,0), 1*random.random()+1,  fill = "green")
    update(cv)


def iec_all_f():
    global e_flag
    e_flag=1
    creat_ball(Pos(100,100), 20, Vel(5,0), 10,  fill = "red")
    creat_ball(Pos(300,100), 20, Vel(0,0), 5,  fill = "red")

import matplotlib.pyplot as plt

def plot_momentum():
    if len(Balls) < 2:
        print("Not enough balls!")
        return

    ball1 = Balls[0]
    ball2 = Balls[1]

    # 创建动量变化的折线图
    plt.figure(figsize=(8, 6))
    plt.plot(ball1.momentum_history, label=f"Ball {ball1.ID} Momentum")
    plt.plot(ball2.momentum_history, label=f"Ball {ball2.ID} Momentum")
    plt.xlabel("Time Step")
    plt.ylabel("Momentum (kg·m/s)")
    plt.title("Momentum Change Over Time")
    plt.legend()
    plt.show()



WIDTH = 500
HEIGHT = 500

root = tk.Tk()                 
root.title("Test")
root.geometry('630x700')


t=0
timer = Timer(root, main_loop, 1000/FPS, False)
tlb = tk.Label(root,text='time:    ',fg='black',font=("黑体",10))
time = tk.Label(root,text='0',fg='black',font=("黑体",10))
idlb = tk.Label(root,text='select id:    ',fg='black',font=("黑体",10))
alllb = tk.Label(root,text='Quick setup:    ',fg='black',font=("黑体",10))


cv = tk.Canvas(root, bg='skyblue', height=HEIGHT, width=WIDTH)
cmd = tk.Button(root, text="Start", width=int(100/7), height=int(20/17), command=cmd_click)
tst = tk.Button(root, text="Remove ball", width=int(100/7), height=int(20/17), command=clear)
create = tk.Button(root, text="Create ball", width=int(100/7), height=int(20/17), command=creat_ball_button)
set = tk.Button(root, text="Set arguments", width=int(100/7), height=int(20/17), command=set_ball)
ec_all = tk.Button(root, text="collision", width=int(100/7), height=int(20/17), command=ec_all_f)
plot_button = tk.Button(root, text="Momentum Plot",width=int(100/7), height=int(20/17), command=plot_momentum)
en_fict = IntVar()
fict = Checkbutton(root,text='Fiction',variable = en_fict,onvalue=1,offvalue=0,fg='black',font=("黑体",10))

# inputs
xl=0
xl+=5
vinlb = tk.Label(root,text='v(x,y):',fg='black',font=("黑体",10))
vinlb.place(x=xl, y=520)
xl+=55
vxin = Entry(root)
vxin.place(x=xl, y=520, width=50, relheight=0.04)
xl+=50
vxulb = tk.Label(root,text='m/s',fg='black',font=("黑体",10))
vxulb.place(x=xl, y=520)
xl+=30
vyin = Entry(root)
vyin.place(x=xl, y=520, width=50, relheight=0.04)
xl+=50
vyulb = tk.Label(root,text='m/s',fg='black',font=("黑体",10))
vyulb.place(x=xl, y=520)

xl+=50
minlb = tk.Label(root,text='m:',fg='black',font=("黑体",10))
minlb.place(x=xl, y=520)
xl+=20
m_in = Entry(root)
m_in.place(x=xl, y=520, width=100, relheight=0.04)
xl+=100
mulb = tk.Label(root,text='kg',fg='black',font=("黑体",10))
mulb.place(x=xl, y=520)

loclb = tk.Label(root,text='location:',fg='black',font=("黑体",10))
loclb.place(x=5, y=560)
locx = Entry(root)
locx.place(x=70, y=560, width=100, relheight=0.04)
locy = Entry(root)
locy.place(x=180, y=560, width=100, relheight=0.04)


miulb = tk.Label(root, text="Friction coefficient (miu):", fg='black', font=("黑体", 10))
miulb.place(x=5, y=603)
miu_entry = Entry(root)
miu_entry.place(x=200, y=600, width=100, relheight=0.04)
miu_entry.insert(0, "0.01")  # 设置默认值

# 添加输入框以控制弹性系数
e_label = tk.Label(root, text="Elastic Coefficient (e):", fg="black", font=("黑体", 10))
e_label.place(x=5, y=650)  # 放置标签
e_scale = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", length=150, font=("黑体", 10))
e_scale.place(x=185, y=633)  # 放置进度条
e_scale.set(1.0)  # 默认值为 1.0


cv.bind("<ButtonRelease-1>", mouse_press)
cv.bind("<Double-Button-1>", mouse_up)

yl=5
cv.place(x=5, y=5)
cmd.place(x=505+10, y=yl)
# yl+=30
# plot.place(x=505+10, y=yl)
yl+=45
tlb.place(x=505+10,y=yl)
time.place(x=505+50,y=yl)
yl+=30
tst.place(x=505+10, y=yl)
yl+=30
create.place(x=505+10, y=yl)
yl+=35
idlb.place(x=505+10, y=yl)
select_id = Entry(root)
select_id.place(x=505+85, y=yl, width=20, height=20)
yl+=25
set.place(x=505+10, y=yl)

yl+=35
alllb.place(x=505+10, y=yl)
yl+=30
ec_all.place(x=505+10, y=yl)
yl+=30

fict.place(x=505+10, y=yl)
yl += 30

plot_button.place(x=505 + 10, y=yl)  # 你可以根据你的界面布局调整位置

root.mainloop()
