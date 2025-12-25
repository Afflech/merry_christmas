try:
    import mediapipe.python.solutions
    print("Import thành công (lạ nhỉ?)")
except ImportError as e:
    print("LỖI THẬT SỰ LÀ ĐÂY:")
    print(e)
except Exception as e:
    print("Lỗi khác:")
    print(e)