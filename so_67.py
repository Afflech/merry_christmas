import numpy as np
import cv2

class Number67:
    def __init__(self):
        self.segments = []
        
        # --- CẤU HÌNH KÍCH THƯỚC ---
        w = 40  # Chiều rộng thanh ngang
        h = 45  # Chiều cao thanh dọc
        d = 10  # Độ dày 3D (Depth)
        
        # Hàm tạo một thanh (segment) 3D
        # pos: toạ độ gốc (x, y)
        # orientation: 'H' (Ngang) hoặc 'V' (Dọc)
        def create_segment_3d(x, y, orientation):
            points = []
            if orientation == 'H':
                # Thanh ngang: Dài theo X, mỏng theo Y
                # Mặt trước (Z = -d)
                points.append([-w/2 + x, -2 + y, -d]) # 0: Top-Left
                points.append([ w/2 + x, -2 + y, -d]) # 1: Top-Right
                points.append([ w/2 + x,  2 + y, -d]) # 2: Bottom-Right
                points.append([-w/2 + x,  2 + y, -d]) # 3: Bottom-Left
                # Mặt sau (Z = d)
                points.append([-w/2 + x, -2 + y, d])  # 4
                points.append([ w/2 + x, -2 + y, d])  # 5
                points.append([ w/2 + x,  2 + y, d])  # 6
                points.append([-w/2 + x,  2 + y, d])  # 7
            else:
                # Thanh dọc: Mỏng theo X, dài theo Y
                points.append([-2 + x, -h/2 + y, -d]) 
                points.append([ 2 + x, -h/2 + y, -d])
                points.append([ 2 + x,  h/2 + y, -d])
                points.append([-2 + x,  h/2 + y, -d])
                # Mặt sau
                points.append([-2 + x, -h/2 + y, d])
                points.append([ 2 + x, -h/2 + y, d])
                points.append([ 2 + x,  h/2 + y, d])
                points.append([-2 + x,  h/2 + y, d])
            return points

        # --- ĐỊNH NGHĨA VỊ TRÍ 7 ĐOẠN (A,B,C,D,E,F,G) ---
        # Offset: Để dời vị trí vẽ số 6 và số 7
        def get_segments_coords(offset_x, offset_y):
            # Tọa độ tâm của các thanh dựa trên sơ đồ 7 đoạn chuẩn
            coords = {
                'a': (0 + offset_x, -h - 5 + offset_y, 'H'), # Ngang trên
                'b': (w/2 + 2 + offset_x, -h/2 - 2 + offset_y, 'V'), # Dọc trên phải
                'c': (w/2 + 2 + offset_x, h/2 + 2 + offset_y, 'V'),  # Dọc dưới phải
                'd': (0 + offset_x, h + 5 + offset_y, 'H'),  # Ngang dưới
                'e': (-w/2 - 2 + offset_x, h/2 + 2 + offset_y, 'V'), # Dọc dưới trái
                'f': (-w/2 - 2 + offset_x, -h/2 - 2 + offset_y, 'V'),# Dọc trên trái
                'g': (0 + offset_x, 0 + offset_y, 'H')       # Ngang giữa
            }
            return coords

        # --- TẠO SỐ 6 (Bên trái) ---
        # Số 6 dùng các đoạn: a, c, d, e, f, g (Thiếu b)
        center_6_x = -50
        segs_6 = get_segments_coords(center_6_x, 0)
        active_6 = ['a', 'c', 'd', 'e', 'f', 'g']
        
        for key in active_6:
            x, y, orient = segs_6[key]
            pts = create_segment_3d(x, y, orient)
            self.segments.append({'points': pts, 'color': (0, 255, 0)}) # Xanh lá

        # --- TẠO SỐ 7 (Bên phải) ---
        # Số 7 dùng các đoạn: a, b, c
        center_7_x = 50
        segs_7 = get_segments_coords(center_7_x, 0)
        active_7 = ['a', 'b', 'c']
        
        for key in active_7:
            x, y, orient = segs_7[key]
            pts = create_segment_3d(x, y, orient)
            self.segments.append({'points': pts, 'color': (0, 255, 255)}) # Vàng/Cyan

        # Các cạnh nối để vẽ hộp (Box) từ 8 điểm đỉnh
        self.box_edges = [
            (0,1), (1,2), (2,3), (3,0), # Mặt trước
            (4,5), (5,6), (6,7), (7,4), # Mặt sau
            (0,4), (1,5), (2,6), (3,7)  # Nối trước-sau
        ]

    # Cập nhật hàm draw cho so_67.py
    def draw(self, img, angle_y, angle_x, scale, center_pos):
        cx, cy = center_pos
        cy_cos, cy_sin = np.cos(angle_y), np.sin(angle_y)
        cx_cos, cx_sin = np.cos(angle_x), np.sin(angle_x) # Xoay dọc
        
        def project(pt):
            x, y, z = pt
            # 1. Xoay X
            y_rx = y * cx_cos - z * cx_sin
            z_rx = y * cx_sin + z * cx_cos
            # 2. Xoay Y
            x_final = x * cy_cos - z_rx * cy_sin
            z_final = x * cy_sin + z_rx * cy_cos
            y_final = y_rx
            return (int(x_final * scale + cx), int(y_final * scale + cy))

        # Phần vẽ giữ nguyên, chỉ thay logic chiếu
        for seg in self.segments:
            pts_3d = seg['points']
            color = seg['color']
            pts_2d = [project(p) for p in pts_3d]
            
            thickness = max(1, int(2 * scale))
            for edge in self.box_edges:
                pt1 = pts_2d[edge[0]]
                pt2 = pts_2d[edge[1]]
                if 0 <= pt1[0] < img.shape[1] and 0 <= pt1[1] < img.shape[0]:
                    cv2.line(img, pt1, pt2, color, thickness)
            
            # Tô màu mặt trước
            face_front = np.array([pts_2d[0], pts_2d[1], pts_2d[2], pts_2d[3]], np.int32)
            face_front = face_front.reshape((-1, 1, 2))
            overlay = img.copy()
            cv2.fillPoly(overlay, [face_front], color)
            cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)