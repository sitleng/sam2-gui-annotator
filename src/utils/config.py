# Configuration settings for the SAM2 GUI Annotator application

# File paths
VIDEO_SOURCE_PATH = "/home/leo/sitl_dvrk_rec/CRCD/*/*/left.mp4"
SAVE_DIR = "/home/leo/yolo/crcd/datasets/runs"

# Model parameters
MODEL_PATH = "sam2.1_l.pt"
CONFIDENCE_THRESHOLD = 0.88
IMG_SIZE = 1024

# Annotation settings
INITIAL_FRAME_INDEX = 0
SEGMENTATION_MODE = "predict"