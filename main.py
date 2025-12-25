import cv2
import mediapipe as mp
import math
import numpy as np
import random

# Import 3 file vẽ hình
from cay_thong import ChristmasTree
from hinh_lap_phuong import Cube
from so_67 import Number67

# --- CLASS HIỆU ỨNG TUYẾT ---
class SnowFall:
    def __init__(self, width, height, num_flakes=150):
        self.width = width
        self.height = height
        self.flakes = []
        for _ in range(num_flakes):
            self.flakes.append([
                random.randint(0, width),  # x
                random.randint(0, height), # y
                random.randint(1, 3),      # size
                random.uniform(0.5, 2.5)   # speed
            ])

    def update_and_draw(self, img):
        for flake in self.flakes:
            flake[1] += flake[3] # Rơi xuống
            flake[0] += math.sin(flake[1] * 0.05) * 0.5 # Gió thổi
            
            # Reset khi chạm đáy
            if flake[1] > self.height:
                flake[1] = random.randint(-20, -5)
                flake[0] = random.randint(0, self.width)
            
            cv2.circle(img, (int(flake[0]), int(flake[1])), flake[2], (255, 255, 255), -1)

# --- CẤU HÌNH ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# --- KHỞI TẠO ĐỐI TƯỢNG ---
obj_tree = ChristmasTree()
obj_67 = Number67()
obj_cube = Cube()
snow = None # Sẽ khởi tạo khi biết kích thước video

current_mode = 1
mode_names = {1: "Cay Thong", 2: "So 67", 3: "Hinh Lap Phuong"}

cap = cv2.VideoCapture(0)
current_angle_y = 0
current_angle_x = 0
current_scale = 1.0

print("DA KHOI DONG!")
print("Nhan phim 1: Cay Thong | 2: So 67 | 3: Lap Phuong")

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    h, w, c = img.shape
    
    # Khởi tạo tuyết 1 lần
    if snow is None:
        snow = SnowFall(w, h)

    # 1. Vẽ tuyết (Lớp nền)
    snow.update_and_draw(img)
    
    # 2. Xử lý phím bấm (Instant Switch)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    elif key == ord('1'): current_mode = 1
    elif key == ord('2'): current_mode = 2
    elif key == ord('3'): current_mode = 3

    # 3. Xử lý AR
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    cv2.putText(img, f"Mode: {mode_names[current_mode]}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            if len(lm_list) != 0:

                x4, y4 = lm_list[4][1], lm_list[4][2]
                x8, y8 = lm_list[8][1], lm_list[8][2]
                center_pos = ((x4 + x8) // 2, (y4 + y8) // 2)
                
                length = math.hypot(x8 - x4, y8 - y4)
                target_scale = np.interp(length, [30, 300], [0.5, 3.0])
                current_scale = current_scale * 0.7 + target_scale * 0.3
                
                x0, y0 = lm_list[0][1], lm_list[0][2]
                x9, y9 = lm_list[9][1], lm_list[9][2]
                dx, dy = x9 - x0, y9 - y0
                current_angle_y = math.atan2(dx, -dy) * 2.0
                
                rel_y = center_pos[1]
                target_angle_x = np.interp(rel_y, [0, h], [-0.8, 0.8])
                current_angle_x = current_angle_x * 0.8 + target_angle_x * 0.2
                
                draw_center = (center_pos[0], center_pos[1] - int(50*current_scale))
                
                try:
                    if current_mode == 1:
                        obj_tree.draw(img, current_angle_y, current_angle_x, current_scale, draw_center)
                    elif current_mode == 2:
                        obj_67.draw(img, current_angle_y, current_angle_x, current_scale, draw_center)
                    elif current_mode == 3:
                        obj_cube.draw(img, current_angle_y, current_angle_x, current_scale, draw_center)
                except TypeError:
                     pass

    cv2.imshow("Christmas AR 2025", img)

cap.release()
cv2.destroyAllWindows()