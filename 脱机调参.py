import sensor, image, time,screen

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(True)
sensor.set_hmirror(True)
clock = time.clock()    #声明时钟，用于获取帧速

#屏幕初始化。可写入参数：
#screen_baudrate SPI频率，默认80，单位Mhz
#pressure 压力阈值，默认1800，数值越大，需要压力越大
screen.init()

# 创建一个320x240的额外图像缓冲区
img_drawing_board = sensor.alloc_extra_fb(320, 240, sensor.RGB565)
#bin_img=sensor.alloc_extra_fb(320, 240, sensor.RGB565)
# 创建一个新的图像缓冲区，足够容纳两个图像
combined_img = sensor.alloc_extra_fb(320, 240, sensor.RGB565)  # 宽度是两个图像宽度之和
# 将绘图板填充为白色
img_drawing_board.draw_rectangle(0, 0, 320, 240, fill=True, color=(255, 255, 255))
# 滑动条参数
slider_width = 15  # 滑动条宽度
slider_height = 10  # 滑动条高度
slider_color = (255, 0, 0)  # 滑动条颜色
slider_pos_LL = 32  # 初始位置
slider_pos_AL = 32  # 初始位置
slider_pos_BL = 32  # 初始位置
slider_pos_LH = 32+256  # 初始位置
slider_pos_AH = 32+256  # 初始位置
slider_pos_BH = 32+256  # 初始位置

color_L_Mode_L=0
color_L_Mode_H=0
color_A_Mode_L=0
color_A_Mode_H=0
color_B_Mode_L=0
color_B_Mode_H=0

color_L_Mode=0
color_A_Mode=0
color_B_Mode=0
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))
# 创建一个绘制按钮的函数
def draw_button_YES(text):
    # 绘制按钮的外框
    img_drawing_board.draw_rectangle(250, 50, 30, 20, color=(0, 255, 0), fill=False)
    # 绘制按钮内的文本
    img_drawing_board.draw_string(255,55, text, color=(255, 0, 255), scale=1, mono_space=False)

def draw_button_AUTO(text):
    # 绘制按钮的外框
    img_drawing_board.draw_rectangle(250, 85, 30, 20, color=(0, 255, 0), fill=False)
    # 绘制按钮内的文本
    img_drawing_board.draw_string(255,90, text, color=(255, 0, 255), scale=1, mono_space=False)
def draw_interface(img_drawing_board, color_L_Mode_L, color_L_Mode_H, color_A_Mode_L, color_A_Mode_H, color_B_Mode_L, color_B_Mode_H, slider_pos_LL, slider_pos_LH, slider_pos_AL, slider_pos_AH, slider_pos_BL, slider_pos_BH, slider_width, slider_height):
    img_drawing_board.clear()
    img_drawing_board.draw_string(5, 120, 'LL:' + str(color_L_Mode_L), color=(255, 0, 255), mono_space=False)
    img_drawing_board.draw_string(5, 140, 'LH:' + str(color_L_Mode_H), color=(255, 0, 255), mono_space=False)
    img_drawing_board.draw_string(5, 160, 'AL:' + str(color_A_Mode_L), color=(255, 0, 255), mono_space=False)
    img_drawing_board.draw_string(5, 180, 'AH:' + str(color_A_Mode_H), color=(255, 0, 255), mono_space=False)
    img_drawing_board.draw_string(5, 200, 'BL:' + str(color_B_Mode_L), color=(255, 0, 255), mono_space=False)
    img_drawing_board.draw_string(5, 220, 'BH:' + str(color_B_Mode_H), color=(255, 0, 255), mono_space=False)

    img_drawing_board.draw_rectangle(32, 125 - 1, 255, 2, color=(255, 0, 0), fill=True)
    img_drawing_board.draw_rectangle(slider_pos_LL, 125 - (slider_height // 2), slider_width, slider_height, color=(0, 255, 255), fill=True)
    img_drawing_board.draw_rectangle(32, 145 - 1, 255, 2, color=(255, 0, 0), fill=True)
    img_drawing_board.draw_rectangle(slider_pos_LH, 145 - (slider_height // 2), slider_width, slider_height, color=(0, 255, 255), fill=True)
    img_drawing_board.draw_rectangle(32, 165 - 1, 255, 2, color=(255, 0, 0), fill=True)
    img_drawing_board.draw_rectangle(slider_pos_AL, 165 - (slider_height // 2), slider_width, slider_height, color=(0, 255, 255), fill=True)
    img_drawing_board.draw_rectangle(32, 185 - 1, 255, 2, color=(255, 0, 0), fill=True)
    img_drawing_board.draw_rectangle(slider_pos_AH, 185 - (slider_height // 2), slider_width, slider_height, color=(0, 255, 255), fill=True)
    img_drawing_board.draw_rectangle(32, 205 - 1, 255, 2, color=(255, 0, 0), fill=True)
    img_drawing_board.draw_rectangle(slider_pos_BL, 205 - (slider_height // 2), slider_width, slider_height, color=(0, 255, 255), fill=True)
    img_drawing_board.draw_rectangle(32, 225 - 1, 255, 2, color=(255, 0, 0), fill=True)
    img_drawing_board.draw_rectangle(slider_pos_BH, 225 - (slider_height // 2), slider_width, slider_height, color=(0, 255, 255), fill=True)

fps=0   #帧速变量
last_x=0    #上一次x坐标
last_y=0    #上一次y坐标
auto_flag=0 #自适应阈值
cnt=0 #自适应阈值统计
first_time_press=True   #第一次按下（抬笔后线条不连续）
img = sensor.snapshot() #获取感光器画面
while True:
    while True:
        clock.tick()    #时钟记录点，用于获取帧速
        img = sensor.snapshot() #获取感光器画面
    #    # 查找色块，使用阈值
    #    for blob in bin_img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
    #        bin_img.draw_rectangle(blob.rect(), color=(0, 255, 0))  # 画出矩形轮廓
        # 绘制界面
        draw_interface(img_drawing_board, color_L_Mode_L, color_L_Mode_H, color_A_Mode_L, color_A_Mode_H, color_B_Mode_L, color_B_Mode_H, slider_pos_LL, slider_pos_LH, slider_pos_AL, slider_pos_AH, slider_pos_BL, slider_pos_BH, slider_width, slider_height)
        # 绘制正常状态的按钮
        draw_button_YES("YES")
        draw_button_AUTO("AUTO")


        img_drawing_board.draw_string(200,10,'FPS:'+str(fps),color=(255,0,0),scale=2,mono_space=False)    #绘制帧速
        if not auto_flag:
            bin_img = img
            color_L_Mode_L=slider_pos_LL - 160
            color_A_Mode_L=slider_pos_AL - 160
            color_B_Mode_L=slider_pos_BL - 160
            color_L_Mode_H=slider_pos_LH - 160
            color_A_Mode_H=slider_pos_AH - 160
            color_B_Mode_H=slider_pos_BH - 160
            thresholds = [(color_L_Mode_L, color_L_Mode_H, color_A_Mode_L, \
                                         color_A_Mode_H, color_B_Mode_L, color_B_Mode_H)]
            bin_img.binary(thresholds)
            if screen.press:  # 如果触屏被按下
                    # 计算触摸点相对于滑动条的位置
                    touch_x = screen.x
                    touch_y = screen.y
                    if touch_x < 32:
                        touch_x = 32
                    if touch_x > 287:
                        touch_x = 287
                    # 更新滑动条位置
                    if 120 < touch_y < 130:
                        slider_pos_LL = touch_x
                    if 140 < touch_y < 150:
                        slider_pos_LH = touch_x
                    if 160 < touch_y < 170:
                        slider_pos_AL = touch_x
                    if 180 < touch_y < 190:
                        slider_pos_AH = touch_x
                    if 200 < touch_y < 210:
                        slider_pos_BL = touch_x
                    if 220 < touch_y < 230:
                        slider_pos_BH = touch_x

                    if 250<touch_x<280 and 85<touch_y<105:
                        auto_flag=1
        else:
            if cnt <= 100:
                cnt = cnt+1
                img_drawing_board.draw_string(200,55, str(cnt), color=(255, 0, 0), scale=2, mono_space=False)
                img.draw_rectangle((140, 100, 40, 40), color = (255,255,255))#画roi框
                statistics_Data = img.get_statistics(roi = (140, 100, 40, 40) )
            #    print(statistics_Data)
            #    print(statistics_Data.l_mode()) #LAB众数，打印出来看看效果稳定不稳定
            #    print(statistics_Data.a_mode())
            #    print(statistics_Data.b_mode())
                color_L_Mode = statistics_Data.l_mode()     #分别赋值LAB的众数
                color_A_Mode = statistics_Data.a_mode()
                color_B_Mode = statistics_Data.b_mode()
                #计算颜色阈值，这样写的话，颜色阈值是实时变化的，后续想要什么效果可以自己修改
                color_L_Mode_L=color_L_Mode - 30
                color_L_Mode_H=color_L_Mode + 30
                color_A_Mode_L=color_A_Mode - 30
                color_A_Mode_H=color_A_Mode + 30
                color_B_Mode_L=color_B_Mode - 30
                color_B_Mode_H=color_B_Mode + 30
                thresholds = [(color_L_Mode_L, color_L_Mode_H, color_A_Mode_L, \
                                             color_A_Mode_H, color_B_Mode_L, color_B_Mode_H)]
                img.binary(thresholds)
            else:
                cnt=0;
                auto_flag=0;
                slider_pos_LL=color_L_Mode_L+160
                slider_pos_AL=color_A_Mode_L+160
                slider_pos_BL=color_B_Mode_L+160
                slider_pos_LH=color_L_Mode_H+160
                slider_pos_AH=color_A_Mode_H+160
                slider_pos_BH=color_B_Mode_H+160
        # 将第一个图像绘制到新图像
        combined_img.draw_image(img_drawing_board, 0, 0)
        img_resized = img.copy(x_size=160)  # 指定新宽度，自动计算x_scale
        # 将第二个图像绘制到新图像的上方
        combined_img.draw_image(img_resized, 0, 0)
        screen.display(combined_img)
        fps=clock.fps() #获取帧速




