"""
Service for running SAM2 inference
"""
import os
import cv2
import numpy as np
from ultralytics import SAM
from ultralytics.data.loaders import LoadImagesAndVideos, SourceTypes
from ultralytics.models.sam import SAM2VideoPredictor
from typing import List, Tuple, Dict, Any


class SAMRunner:
    def __init__(self, model_name="sam2.1_l.pt"):
        """Initialize SAM2 model for interactive annotation."""
        self.model_name = model_name
        self.sam_model = None
        self.predictor = None
        self.original_loader_next = LoadImagesAndVideos.__next__  # Store original method
        self.load_model()
    
    def load_model(self):
        """Load the SAM2 model."""
        try:
            self.sam_model = SAM(self.model_name)
            print(f"SAM2 model {self.model_name} loaded successfully")
        except Exception as e:
            print(f"Error loading SAM2 model: {e}")
            raise
    
    def run_interactive_segmentation(self, image_path: str, points: List[List[Tuple[int, int]]], 
                                   labels: List[List[int]]) -> Any:
        """
        Run SAM2 segmentation with interactive points using regular SAM model.
        
        Args:
            image_path: Path to the image
            points: List of point lists for each object
            labels: List of label lists (1 for positive, 0 for negative)
        
        Returns:
            SAM2 results object
        """
        if not self.sam_model:
            print("Error: SAM2 model not loaded")
            raise RuntimeError("SAM2 model not loaded")
        
        if not points or not labels:
            print("Error: Empty points or labels")
            return None
            
        # CRITICAL: Restore original LoadImagesAndVideos method before single image processing
        LoadImagesAndVideos.__next__ = self.original_loader_next
            
        # Filter out empty point lists
        filtered_points = []
        filtered_labels = []
        for i, (p, l) in enumerate(zip(points, labels)):
            if p and l:
                filtered_points.append(p)
                filtered_labels.append(l)
        
        if not filtered_points:
            print("Error: No valid points after filtering")
            return None
            
        try:
            # Use regular SAM model like in notebook: sam_model(init_frame, points=all_points, labels=all_labels)[0]
            results = self.sam_model(image_path, points=filtered_points, labels=filtered_labels)[0]
            return results
        except Exception as e:
            print(f"Error during SAM2 inference: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def balance_annotation_points(self, objects: List[Dict]) -> Tuple[List[List[Tuple[int, int]]], List[List[int]]]:
        """
        Balance annotation points by duplicating points from smaller samples.
        
        Args:
            objects: List of objects with 'positive' and 'negative' point lists
            
        Returns:
            Tuple of (balanced_points, balanced_labels)
        """
        if not objects:
            return [], []
        
        # Calculate total points for each object
        point_counts = []
        all_points = []
        all_labels = []
        
        for obj in objects:
            positive_points = obj.get("positive", [])
            negative_points = obj.get("negative", [])
            points = positive_points + negative_points
            labels = [1] * len(positive_points) + [0] * len(negative_points)
            
            if points:  # Only include objects with points
                all_points.append(points)
                all_labels.append(labels)
                point_counts.append(len(points))
        
        if not point_counts:
            return [], []
        
        # Find maximum number of points
        max_points = max(point_counts)
        
        # Balance by duplicating points
        balanced_points = []
        balanced_labels = []
        
        for points, labels in zip(all_points, all_labels):
            if len(points) < max_points:
                # Duplicate points to match max_points
                while len(points) < max_points:
                    points.extend(points[:min(len(points), max_points - len(points))])
                    labels.extend(labels[:min(len(labels), max_points - len(labels))])
            
            balanced_points.append(points[:max_points])
            balanced_labels.append(labels[:max_points])
        
        return balanced_points, balanced_labels
    
    def create_video_predictor(self, conf=0.88, imgsz=1024):
        """Create SAM2VideoPredictor for batch processing."""
        overrides = dict(
            conf=conf,
            task="segment",
            mode="predict",
            imgsz=imgsz,
            model=self.model_name,
            save=False,
        )
        self.predictor = SAM2VideoPredictor(overrides=overrides)
        return self.predictor
    
    def create_image_loader(self, folder_path: str):
        """Create image loader for batch processing."""
        # Simple monkey patch like in the notebook
        load_next = LoadImagesAndVideos.__next__
        def new_next(self):
            r = load_next(self)
            self.frame += 1
            self.mode = "video"
            return r
        LoadImagesAndVideos.__next__ = new_next
        
        # Create loader exactly like notebook
        folder = folder_path + "/*"
        loader = LoadImagesAndVideos(folder)
        loader.source_type = SourceTypes(from_img=True)
        loader.frames = loader.ni
        loader.frame = 0
        loader.mode = "video"
        loader.fps = 10
        
        return loader
    
    def process_image_sequence(self, folder_path: str, points: List[List[Tuple[int, int]]], 
                             labels: List[List[int]], save_dir: str = None):
        """
        Process a sequence of images with SAM2VideoPredictor.
        
        Args:
            folder_path: Path to folder containing images
            points: Balanced points for all objects
            labels: Balanced labels for all objects
            save_dir: Directory to save results
            
        Returns:
            Generator of results
        """
        if not self.predictor:
            self.create_video_predictor()
        
        loader = self.create_image_loader(folder_path)
        
        results = self.predictor(
            source=loader,
            points=points,
            labels=labels,
        )
        
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        for result in results:
            if save_dir:
                result.save(os.path.join(save_dir, result.path.split('/')[-1]))
            yield result

    # Legacy methods for backward compatibility
    def run_segmentation(self, frame, points, labels):
        """Legacy method - use run_interactive_segmentation instead."""
        return self.run_interactive_segmentation(frame, points, labels)

    def get_contours_and_classes(self, results):
        """Extract contours and classes from results."""
        if results and hasattr(results, 'masks') and results.masks:
            cnts = results.masks.xy
            cls = list(results.boxes.cls.cpu().numpy()) if results.boxes else []
            return cnts, cls
        return [], []

    def save_results(self, results, save_dir):
        """Save results to directory."""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for result in results:
            result.save(os.path.join(save_dir, result.path.split('/')[-1]))