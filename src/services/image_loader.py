"""
Service for loading and managing image sequences
"""
import os
import cv2
import numpy as np
from glob import glob
from pathlib import Path
from typing import List, Optional, Tuple


class ImageLoader:
    def __init__(self):
        """Initialize the image loader."""
        self.image_paths = []
        self.current_index = 0
        self.current_folder = None
    
    def load_folder(self, folder_path: str, extensions: List[str] = None) -> bool:
        """
        Load all images from a folder.
        
        Args:
            folder_path: Path to the folder containing images
            extensions: List of file extensions to include (default: common image formats)
            
        Returns:
            True if images were found, False otherwise
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        
        if not os.path.exists(folder_path):
            print(f"Folder does not exist: {folder_path}")
            return False
        
        # Build glob patterns for all extensions
        patterns = []
        for ext in extensions:
            patterns.extend([
                os.path.join(folder_path, f"*{ext}"),
                os.path.join(folder_path, f"*{ext.upper()}")
            ])
        
        # Collect all image files
        self.image_paths = []
        for pattern in patterns:
            self.image_paths.extend(glob(pattern))
        
        # Sort paths for consistent ordering
        self.image_paths.sort()
        
        if not self.image_paths:
            print(f"No images found in folder: {folder_path}")
            return False
        
        self.current_folder = folder_path
        self.current_index = 0
        print(f"Loaded {len(self.image_paths)} images from {folder_path}")
        return True
    
    def get_image_count(self) -> int:
        """Get the total number of loaded images."""
        return len(self.image_paths)
    
    def get_current_image_path(self) -> Optional[str]:
        """Get the path of the current image."""
        if 0 <= self.current_index < len(self.image_paths):
            return self.image_paths[self.current_index]
        return None
    
    def get_first_image_path(self) -> Optional[str]:
        """Get the path of the first image."""
        if self.image_paths:
            return self.image_paths[0]
        return None
    
    def load_current_image(self) -> Optional[np.ndarray]:
        """Load the current image as a numpy array."""
        path = self.get_current_image_path()
        if path:
            try:
                image = cv2.imread(path)
                return image
            except Exception as e:
                print(f"Error loading image {path}: {e}")
        return None
    
    def load_first_image(self) -> Optional[np.ndarray]:
        """Load the first image as a numpy array."""
        if self.image_paths:
            try:
                image = cv2.imread(self.image_paths[0])
                return image
            except Exception as e:
                print(f"Error loading first image {self.image_paths[0]}: {e}")
        return None
    
    def next_image(self) -> bool:
        """Move to the next image."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            return True
        return False
    
    def previous_image(self) -> bool:
        """Move to the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def set_current_index(self, index: int) -> bool:
        """Set the current image index."""
        if 0 <= index < len(self.image_paths):
            self.current_index = index
            return True
        return False
    
    def get_image_info(self) -> dict:
        """Get information about the current image."""
        path = self.get_current_image_path()
        if not path:
            return {}
        
        try:
            image = self.load_current_image()
            if image is not None:
                height, width = image.shape[:2]
                return {
                    'path': path,
                    'filename': os.path.basename(path),
                    'index': self.current_index,
                    'total': len(self.image_paths),
                    'width': width,
                    'height': height,
                    'folder': self.current_folder
                }
        except Exception as e:
            print(f"Error getting image info: {e}")
        
        return {}
    
    def get_remaining_images(self, start_index: int = 1) -> List[str]:
        """
        Get paths of remaining images (excluding the first one by default).
        
        Args:
            start_index: Index to start from (default: 1 to skip first image)
            
        Returns:
            List of image paths
        """
        if start_index < len(self.image_paths):
            return self.image_paths[start_index:]
        return []
    
    def validate_image_sequence(self) -> bool:
        """Validate that all images in the sequence can be loaded."""
        if not self.image_paths:
            return False
        
        for i, path in enumerate(self.image_paths):
            try:
                image = cv2.imread(path)
                if image is None:
                    print(f"Failed to load image {i}: {path}")
                    return False
            except Exception as e:
                print(f"Error validating image {i} ({path}): {e}")
                return False
        
        return True