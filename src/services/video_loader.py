class VideoLoader:
    def __init__(self, video_path):
        self.video_path = video_path
        self.frames = []
        self.current_frame_index = 0

    def load_video(self):
        import cv2
        cap = cv2.VideoCapture(self.video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            self.frames.append(frame)
        cap.release()

    def get_next_frame(self):
        if self.current_frame_index < len(self.frames):
            frame = self.frames[self.current_frame_index]
            self.current_frame_index += 1
            return frame
        return None

    def reset(self):
        self.current_frame_index = 0