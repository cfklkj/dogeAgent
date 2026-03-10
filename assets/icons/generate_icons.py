#!/usr/bin/env python3
"""生成 dogeAgent 图标文件"""
from PIL import Image, ImageDraw
import math
import os

def create_icon_png():
    """创建 256x256 应用图标"""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size // 2, size // 2
    radius = size // 2 - 10
    
    # 绘制圆形背景 - 金黄色渐变效果
    for i in range(radius, 0, -1):
        ratio = i / radius
        r = int(218 + (255 - 218) * (1 - ratio))
        g = int(165 + (215 - 165) * (1 - ratio))
        b = int(32 + (100 - 32) * (1 - ratio))
        draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=(r, g, b)
        )
    
    # 绘制柴犬脸部
    ear_color = (180, 120, 60)
    # 左耳
    draw.polygon([
        (70, 60),
        (100, 20),
        (130, 70)
    ], fill=ear_color)
    # 右耳
    draw.polygon([
        (126, 70),
        (156, 20),
        (186, 60)
    ], fill=ear_color)
    
    # 脸部主体 - 米白色
    face_color = (255, 245, 220)
    draw.ellipse([60, 60, 196, 200], fill=face_color)
    
    # 眼睛区域 - 深色毛发
    muzzle_color = (200, 150, 80)
    draw.ellipse([80, 100, 115, 140], fill=muzzle_color)
    draw.ellipse([141, 100, 176, 140], fill=muzzle_color)
    
    # 眼睛 - 黑色圆点
    draw.ellipse([92, 110, 108, 130], fill=(30, 30, 30))
    draw.ellipse([148, 110, 164, 130], fill=(30, 30, 30))
    
    # 眼睛高光
    draw.ellipse([96, 113, 102, 120], fill=(255, 255, 255))
    draw.ellipse([152, 113, 158, 120], fill=(255, 255, 255))
    
    # 鼻子
    draw.ellipse([115, 145, 141, 165], fill=(30, 30, 30))
    draw.ellipse([120, 148, 128, 155], fill=(255, 255, 255))
    
    # 嘴巴 - 微笑曲线
    draw.arc([100, 155, 156, 185], 0, 180, fill=(100, 60, 40), width=3)
    
    # 舌头
    draw.ellipse([118, 172, 138, 190], fill=(255, 120, 120))
    
    # 腮红
    draw.ellipse([65, 140, 85, 155], fill=(255, 180, 180))
    draw.ellipse([171, 140, 191, 155], fill=(255, 180, 180))
    
    return img

def create_doge_png():
    """创建 300x300 柴犬主图，透明背景"""
    size = 300
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 耳朵 - 尖三角形
    ear_color = (185, 125, 65)
    draw.polygon([
        (55, 90),
        (90, 20),
        (125, 100)
    ], fill=ear_color)
    draw.polygon([
        (70, 85),
        (92, 40),
        (115, 95)
    ], fill=(220, 180, 120))
    
    draw.polygon([
        (175, 100),
        (210, 20),
        (245, 90)
    ], fill=ear_color)
    draw.polygon([
        (185, 95),
        (208, 40),
        (230, 85)
    ], fill=(220, 180, 120))
    
    # 脸部 - 米白色
    face_color = (255, 248, 230)
    draw.ellipse([50, 80, 250, 260], fill=face_color)
    
    # 脸部两侧深色毛发
    side_color = (190, 140, 80)
    draw.ellipse([50, 100, 100, 200], fill=side_color)
    draw.ellipse([60, 80, 120, 150], fill=side_color)
    draw.ellipse([200, 100, 250, 200], fill=side_color)
    draw.ellipse([180, 80, 240, 150], fill=side_color)
    
    # 重新覆盖脸部中间白色区域
    draw.ellipse([80, 100, 220, 250], fill=face_color)
    
    # 眼睛周围深色区域
    eye_patch = (170, 120, 70)
    draw.ellipse([85, 120, 135, 175], fill=eye_patch)
    draw.ellipse([165, 120, 215, 175], fill=eye_patch)
    
    # 眼睛 - 大黑眼珠
    draw.ellipse([100, 135, 130, 170], fill=(25, 25, 25))
    draw.ellipse([170, 135, 200, 170], fill=(25, 25, 25))
    
    # 眼睛高光
    draw.ellipse([105, 140, 118, 153], fill=(255, 255, 255))
    draw.ellipse([175, 140, 188, 153], fill=(255, 255, 255))
    draw.ellipse([118, 158, 124, 165], fill=(255, 255, 255))
    draw.ellipse([188, 158, 194, 165], fill=(255, 255, 255))
    
    # 眉毛区域
    draw.arc([95, 115, 135, 135], 200, 340, fill=eye_patch, width=4)
    draw.arc([165, 115, 205, 135], 200, 340, fill=eye_patch, width=4)
    
    # 鼻子
    draw.ellipse([130, 180, 170, 210], fill=(30, 30, 30))
    draw.ellipse([138, 185, 155, 198], fill=(255, 255, 255))
    
    # 嘴巴
    draw.line([(130, 215), (110, 230)], fill=(80, 50, 40), width=3)
    draw.arc([130, 200, 170, 240], 0, 180, fill=(80, 50, 40), width=3)
    draw.line([(170, 215), (190, 230)], fill=(80, 50, 40), width=3)
    
    # 舌头
    draw.ellipse([140, 220, 160, 245], fill=(255, 130, 130))
    
    # 腮红
    draw.ellipse([60, 175, 90, 195], fill=(255, 190, 190))
    draw.ellipse([210, 175, 240, 195], fill=(255, 190, 190))
    
    # 额头小星星
    star_color = (255, 200, 50)
    star_center = (150, 95)
    points = []
    for i in range(5):
        angle = math.radians(90 + i * 72)
        x = star_center[0] + 8 * math.cos(angle)
        y = star_center[1] - 8 * math.sin(angle)
        points.append((x, y))
        angle2 = math.radians(90 + i * 72 + 36)
        x2 = star_center[0] + 4 * math.cos(angle2)
        y2 = star_center[1] - 4 * math.sin(angle2)
        points.append((x2, y2))
    draw.polygon(points, fill=star_color)
    
    return img

def main():
    output_dir = r"H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent\assets\icons"
    
    print("Generating icons...")
    
    icon = create_icon_png()
    icon_path = os.path.join(output_dir, "icon.png")
    icon.save(icon_path, "PNG")
    print(f"Created: {icon_path}")
    
    doge = create_doge_png()
    doge_path = os.path.join(output_dir, "doge.png")
    doge.save(doge_path, "PNG")
    print(f"Created: {doge_path}")
    
    print("All icons generated successfully!")

if __name__ == "__main__":
    main()
