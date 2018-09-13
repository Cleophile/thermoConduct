#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Hikari Software
# Y-Enterprise

import json
import pandas as pd
import matplotlib.pyplot as plt

dta = pd.read_csv('/Users/wangtianmin/Downloads/ABCD题/2018-A-Chinese/2_dta.csv')

# 环境温度
Ambience_Hot = 75           # 环境高温
Ambience_Cold = 37          # 环境低温

# 空列表
rho = [300,862,74.2,1.18]   # 材料密度
c = [1377,2100,1726,1005]   # 比热容
k = [0.082,0.37,0.045,0.028]# 热导率
thick = [0.6,6,3.6,5]       # 材料厚度

# 材料系数
thick[1] = 6                # 第2层厚度
thick[3] = 5                # 第4层厚度

# 问题广度设定
total_time = 5400

# 算法精确度设定
time_interval = 0.001
length_interval = 0.5

# 对流系数
h_left= 20                   # 最左材料和空气
h_right= h_left                  # 最右材料和皮肤

# 单位统一
for i in range(len(thick)):
    thick[i] = thick[i]/1000
length_interval = length_interval / 1000
time_inv = int(1/time_interval)

# 设定运算函数，返回值统一为新的温度
def Left_Amb(t1,t2):
    '''
    高温热源和材料的第一次交互
    t1为当前温度
    '''
    heat = (-k[0])*(t1-t2)/length_interval - h_left*(t1-Ambience_Hot)
    delta = heat/(rho[0]*length_interval*c[0])
    return t1 + time_interval*delta

def Right_Amb(tn,t_Left):
    '''
    材料和低温热源的热传导，最后一次热传导
    ***如果考虑热对流，这个函数应该被修改***
    '''
    heat = (-k[-1])*(tn-t_Left)/length_interval - h_right*(tn-Ambience_Cold)
    delta = heat/(rho[-1]*length_interval*c[-1])
    return tn + time_interval*delta

def Border(t_left,ti,t_right,material_left,material_right):
    '''
    跨材料热交互
    '''
    heat = (-k[material_left])*(ti-t_left)/length_interval - k[material_right]*(ti-t_right)/length_interval
    delta = heat/(length_interval*rho[material_left]*c[material_left])
    return ti+time_interval*delta

# 长度和材料决定
def Material_Deter(length):
    if length<thick[0]:
        return 0
    if length<(thick[0] + thick[1]):
        return 1
    if length<(thick[0] + thick[1] + thick[2]):
        return 2
    return 3

def main():
    '''
    计算总运算次数，并设定材料交互的flag
    以及和环境交互的flag
    规定，x=0为0-0.001mm的一段柱状材料（0.001随参数设定而改变）
    所以x=总长度的部分不应该被考虑
    如第一段长度为6mm，x=6的时候应当被认为是一段新材料的开始
    二维数组，二维数组的子数组表示同一时间的不同位置的温度
    另一个维度为时间
    结果保存在JSON中，用Echarts绘制热力图
    '''
    iter_times = int(sum(thick)/length_interval)
    t_series = []
    t_distribute = []
    t_new = []
    time_gaps = int(total_time/time_interval)
    skin_temp = []
    for i in range(iter_times):
        t_distribute.append(37)
        
    for time_series_turing_times in range(time_gaps):
        # range 0
        t_new.append(Left_Amb(t_distribute[0],t_distribute[1]))
        for i in range(1,iter_times - 1):
            material_left = Material_Deter(i*length_interval)
            material_right = Material_Deter((i+1)*length_interval)
            t_new.append(Border(t_distribute[i-1],t_distribute[i],t_distribute[i+1],material_left,material_right))
        # range iter_times-1
        t_new.append(Right_Amb(t_distribute[-1],t_distribute[-2]))
        if time_series_turing_times % time_inv == 0: # or time_series_turing_times < 10:
            # print(t_new[:10],'...',t_new[-10:-1])
            skin_temp.append(t_new[-1])
        t_series.append(t_new)
        t_distribute = t_new
        t_new = []
    
    with open('result.json','w') as f:
        content = json.dumps(skin_temp)
        f.write(content)

    gen_dta = pd.DataFrame(dict(time=list(range(len(skin_temp))),temp=skin_temp))
    dta.plot(x='time',y='temp')
    gen_dta.plot(x='time',y='temp')
    plt.show()
    

if __name__ == "__main__":
    '''
    整体优化：
    1. 去掉温度不变时候的无意义数据
    2. h的取值5-25不能超过范围
    3. 时间和长度的取值, 可以先期检测, 如果温度波动过大应当警示
    '''
    main()


