import numpy as np
import cv2

import numpy as np
import cv2

class Cube:
    def __init__(self):
        r = 50
        self.vertices = [
            [-r, -r, -r], [r, -r, -r], [r, r, -r], [-r, r, -r],
            [-r, -r, r],  [r, -r, r],  [r, r, r],  [-r, r, r]
        ]
        self.edges = [
            (0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]

    # THAM SỐ MỚI: angle_x
    def draw(self, img, angle_y, angle_x, scale, center_pos):
        cx, cy = center_pos
        
        # Tính toán trước sin/cos
        cy_cos, cy_sin = np.cos(angle_y), np.sin(angle_y)
        cx_cos, cx_sin = np.cos(angle_x), np.sin(angle_x)

        def project(pt):
            x, y, z = pt
            
            # 1. Xoay X (Vertical Tilt)
            y_rx = y * cx_cos - z * cx_sin
            z_rx = y * cx_sin + z * cx_cos
            
            # 2. Xoay Y (Horizontal Spin)
            x_final = x * cy_cos - z_rx * cy_sin
            z_final = x * cy_sin + z_rx * cy_cos
            y_final = y_rx
            
            return (int(x_final * scale + cx), int(y_final * scale + cy))

        points_2d = [project(v) for v in self.vertices]

        for edge in self.edges:
            pt1 = points_2d[edge[0]]
            pt2 = points_2d[edge[1]]
            cv2.line(img, pt1, pt2, (255, 0, 255), 2)
            cv2.circle(img, pt1, 4, (0, 255, 255), -1)