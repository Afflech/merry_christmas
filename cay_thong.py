import numpy as np
import cv2
import random

class ChristmasTree:
    def __init__(self):
        self.points = []
        
        # --- CẤU HÌNH CÂY ---
        layers = 35           # Số vòng xoắn
        points_per_layer = 20
        height = 250
        radius_max = 120
        
        # 1. TẠO TÁN LÁ VÀ QUẢ CHÂU
        for i in range(layers * points_per_layer):
            progress = i / (layers * points_per_layer) # 0 (đỉnh) -> 1 (đáy)
            
            # Góc xoay + nhiễu ngẫu nhiên
            angle = progress * 15 * np.pi + random.uniform(-0.2, 0.2)
            
            r = progress * radius_max
            
            # Tọa độ 3D (x, y, z)
            y = (progress - 0.5) * height
            x = r * np.cos(angle)
            z = r * np.sin(angle)
            
            # Xác định loại điểm
            if random.random() < 0.1:
                color = random.choice([(0, 0, 255), (0, 255, 255), (255, 0, 0)]) 
                size = 4
                pt_type = 'ornament'
            else:
                g = int(100 + progress * 100 + random.randint(-30, 30))
                g = max(50, min(255, g))
                color = (20, g, 20) 
                size = 2
                pt_type = 'leaf'

            self.points.append({
                'coords': [x, y, z],
                'color': color,
                'size': size,
                'type': pt_type
            })

        # 2. TẠO THÂN CÂY (TRUNK)
        trunk_height = 50
        trunk_radius = 15
        trunk_y_start = height / 2 
        
        for h in range(0, trunk_height, 5):
            for angle_deg in range(0, 360, 45):
                angle_rad = np.deg2rad(angle_deg)
                x = trunk_radius * np.cos(angle_rad)
                z = trunk_radius * np.sin(angle_rad)
                y = trunk_y_start + h
                
                self.points.append({
                    'coords': [x, y, z],
                    'color': (19, 69, 139),
                    'size': 3,
                    'type': 'trunk'
                })

    # --- HÀM DRAW ĐÃ CẬP NHẬT: Thêm rotation_angle_x ---
    def draw(self, img, rotation_angle_y, rotation_angle_x, scale, center_pos):
        cx, cy = center_pos
        
        # Tính toán trước sin/cos cho cả 2 trục
        # Trục Y: Xoay trái/phải
        cos_y = np.cos(rotation_angle_y)
        sin_y = np.sin(rotation_angle_y)
        
        # Trục X: Xoay lên/xuống (Mới thêm)
        cos_x = np.cos(rotation_angle_x)
        sin_x = np.sin(rotation_angle_x)
        
        draw_list = []

        for p in self.points:
            x, y, z = p['coords']
            
            # --- BƯỚC 1: Xoay quanh trục X (Gật gù) ---
            # Công thức: y' = y*cos - z*sin; z' = y*sin + z*cos
            y_rot_x = y * cos_x - z * sin_x
            z_rot_x = y * sin_x + z * cos_x
            
            # --- BƯỚC 2: Xoay quanh trục Y (Xoay tròn) ---
            # Lưu ý: Dùng z_rot_x (đã xoay X) để tính tiếp
            # Công thức: x' = x*cos - z*sin; z'' = x*sin + z*cos
            x_final = x * cos_y - z_rot_x * sin_y
            z_final = x * sin_y + z_rot_x * cos_y
            y_final = y_rot_x # Y chỉ bị ảnh hưởng bởi bước 1
            
            # --- BƯỚC 3: Chiếu 3D -> 2D ---
            screen_x = int(x_final * scale + cx)
            screen_y = int(y_final * scale + cy)
            
            draw_list.append({
                'x': screen_x,
                'y': screen_y,
                'z': z_final, # Dùng z cuối cùng để sắp xếp độ sâu
                'color': p['color'],
                'size': int(p['size'] * scale),
                'type': p['type']
            })
            
        # Sắp xếp để vẽ điểm xa trước (Z nhỏ), điểm gần sau (Z lớn)
        draw_list.sort(key=lambda k: k['z'])

        for p in draw_list:
            if 0 <= p['x'] < img.shape[1] and 0 <= p['y'] < img.shape[0]:
                color = p['color']
                
                if p['type'] == 'ornament':
                    # Hiệu ứng nhấp nháy đèn
                    if random.random() < 0.1: 
                        color = random.choice([(0, 0, 255), (0, 255, 255), (255, 0, 0), (255, 255, 255)])
                
                cv2.circle(img, (p['x'], p['y']), max(1, p['size']), color, -1)

        # --- VẼ NGÔI SAO (Cũng cần xoay theo trục X) ---
        # Đỉnh cây gốc là (0, -125, 0)
        top_x, top_y, top_z = 0, -125, 0
        
        # 1. Xoay X
        top_y_rot = top_y * cos_x - top_z * sin_x
        top_z_rot = top_y * sin_x + top_z * cos_x
        
        # 2. Xoay Y
        top_x_final = top_x * cos_y - top_z_rot * sin_y
        top_y_final = top_y_rot
        
        top_screen_x = int(top_x_final * scale + cx)
        top_screen_y = int(top_y_final * scale + cy)
        
        star_size = int(12 * scale)
        if star_size > 0:
            cv2.circle(img, (top_screen_x, top_screen_y), star_size, (0, 255, 255), -1) 
            cv2.circle(img, (top_screen_x, top_screen_y), int(star_size*0.5), (255, 255, 255), -1)