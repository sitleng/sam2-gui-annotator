"""
Enhanced annotation controller integrating SAM2 with multi-object annotation
"""
import os
from typing import Optional, List, Tuple, Any
from services.sam_runner import SAMRunner
from services.image_loader import ImageLoader
from models.annotation_state import AnnotationState


class AnnotationController:
    def __init__(self, model_name: str = "sam2.1_l.pt"):
        """
        Initialize the annotation controller.
        
        Args:
            model_name: Name of the SAM2 model to use
        """
        self.sam_runner = SAMRunner(model_name)
        self.image_loader = ImageLoader()
        self.annotation_state = AnnotationState()
        self.is_batch_processing = False
        
    def load_image_folder(self, folder_path: str) -> bool:
        """
        Load images from a folder.
        
        Args:
            folder_path: Path to the folder containing images
            
        Returns:
            True if images were loaded successfully
        """
        success = self.image_loader.load_folder(folder_path)
        if success:
            first_image_path = self.image_loader.get_first_image_path()
            if first_image_path:
                self.annotation_state.set_image_path(first_image_path)
        return success
    
    def get_image_info(self) -> dict:
        """Get information about the current image."""
        return self.image_loader.get_image_info()
    
    def add_positive_point(self, point: Tuple[int, int]) -> bool:
        """
        Add a positive point for the current object.
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            True if point was added successfully
        """
        try:
            self.annotation_state.add_positive_point(point)
            return True
        except Exception as e:
            print(f"Error adding positive point: {e}")
            return False
    
    def add_negative_point(self, point: Tuple[int, int]) -> bool:
        """
        Add a negative point for the current object.
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            True if point was added successfully
        """
        try:
            self.annotation_state.add_negative_point(point)
            return True
        except Exception as e:
            print(f"Error adding negative point: {e}")
            return False
    
    def switch_to_next_object(self):
        """Switch to the next object for annotation."""
        self.annotation_state.switch_to_next_object()
    
    def add_new_object(self) -> int:
        """
        Add a new object and switch to it.
        
        Returns:
            Index of the new object
        """
        new_index = self.annotation_state.add_object()
        self.annotation_state.switch_to_object(new_index)
        return new_index
    
    def get_current_object_info(self) -> dict:
        """Get information about the current object."""
        current_points = self.annotation_state.get_current_object_points()
        return {
            'object_index': self.annotation_state.get_current_object_index(),
            'object_count': self.annotation_state.get_object_count(),
            'positive_points': len(current_points['positive']),
            'negative_points': len(current_points['negative']),
            'total_points': len(current_points['positive']) + len(current_points['negative'])
        }
    
    def run_interactive_segmentation(self) -> Optional[Any]:
        """
        Run SAM2 segmentation on the current image with current annotations.
        
        Returns:
            SAM2 results or None if failed
        """
        image_path = self.annotation_state.get_image_path()
        if not image_path:
            print("Error: No image path set in annotation state")
            return None
        
        if not os.path.exists(image_path):
            print(f"Error: Image file does not exist: {image_path}")
            return None
        
        points, labels = self.annotation_state.get_points_and_labels()
        if not points:
            print("Error: No annotation points available")
            return None
        
        print(f"Debug: Running segmentation on {image_path}")
        print(f"Debug: Points structure: {points}")
        print(f"Debug: Labels structure: {labels}")
        
        try:
            results = self.sam_runner.run_interactive_segmentation(image_path, points, labels)
            if results:
                self.annotation_state.set_segmentation_results(results)
                print("Debug: Segmentation completed successfully")
            else:
                print("Error: SAM runner returned None")
            return results
        except Exception as e:
            print(f"Error during segmentation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def prepare_for_batch_processing(self) -> Tuple[List[List[Tuple[int, int]]], List[List[int]]]:
        """
        Prepare balanced points and labels for batch processing.
        
        Returns:
            Tuple of (balanced_points, balanced_labels)
        """
        objects = self.annotation_state.get_all_objects()
        balanced_points, balanced_labels = self.sam_runner.balance_annotation_points(objects)
        return balanced_points, balanced_labels
    
    def process_image_sequence(self, runs_dir: str, labels_dir: str,
                             progress_callback=None) -> List[Any]:
        """
        Process the entire image sequence with SAM2VideoPredictor.
        
        Args:
            runs_dir: Directory to save prediction images
            labels_dir: Directory to save label text files
            progress_callback: Callback function to report progress
            
        Returns:
            List of results
        """
        if not self.annotation_state.has_annotations():
            print("No annotations available for batch processing")
            return []
        
        folder_path = self.image_loader.current_folder
        if not folder_path:
            print("No image folder loaded")
            return []
        
        # Get balanced points and labels
        balanced_points, balanced_labels = self.prepare_for_batch_processing()
        
        if not balanced_points:
            print("No valid points for batch processing")
            return []
        
        self.is_batch_processing = True
        results = []
        
        try:
            result_generator = self.sam_runner.process_image_sequence(
                folder_path, balanced_points, balanced_labels, runs_dir
            )
            
            total_images = self.image_loader.get_image_count()
            
            for i, result in enumerate(result_generator):
                results.append(result)
                current = i + 1
                if progress_callback:
                    print(f"Controller: Calling progress_callback({current}, {total_images})")
                    progress_callback(current, total_images)
            
            # Save text annotations in YOLO format
            if results and labels_dir:
                self.save_text_annotations(labels_dir, results)
            
        except Exception as e:
            print(f"Error during batch processing: {e}")
        finally:
            self.is_batch_processing = False
        
        return results
    
    def save_text_annotations(self, save_dir: str, results: List[Any]):
        """
        Save text annotations for the results.
        
        Args:
            save_dir: Directory to save text files
            results: List of SAM2 results
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        for result in results:
            try:
                # Create text file path
                image_name = os.path.basename(result.path)
                txt_name = os.path.splitext(image_name)[0] + '.txt'
                txt_path = os.path.join(save_dir, txt_name)
                
                # Save text annotations
                result.save_txt(txt_path)
            except Exception as e:
                print(f"Error saving text annotation: {e}")
    
    def clear_current_object(self):
        """Clear annotations for the current object."""
        self.annotation_state.clear_current_object()
    
    def clear_all_annotations(self):
        """Clear all annotations."""
        self.annotation_state.clear_all_objects()
    
    def remove_current_object(self):
        """Remove the current object."""
        self.annotation_state.remove_current_object()
    
    def get_annotation_summary(self) -> str:
        """Get a summary of the current annotation state."""
        return self.annotation_state.get_summary()
    
    def has_annotations(self) -> bool:
        """Check if there are any annotations."""
        return self.annotation_state.has_annotations()
    
    def get_image_count(self) -> int:
        """Get the number of loaded images."""
        return self.image_loader.get_image_count()
    
    def is_ready_for_batch_processing(self) -> bool:
        """Check if the controller is ready for batch processing."""
        return (self.annotation_state.has_annotations() and 
                self.image_loader.get_image_count() > 0 and
                not self.is_batch_processing)

    # Legacy methods for backward compatibility  
    def load_video(self, video_path):
        """Legacy method - use load_image_folder instead."""
        return self.load_image_folder(video_path)

    def annotate_frame(self, frame):
        """Legacy method - use run_interactive_segmentation instead."""
        return self.run_interactive_segmentation()

    def save_annotations(self, save_path):
        """Legacy method - use process_image_sequence instead."""
        # For backward compatibility, create both runs and labels directories
        runs_dir = os.path.join(save_path, "runs")
        labels_dir = os.path.join(save_path, "labels")
        os.makedirs(runs_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        return self.process_image_sequence(runs_dir, labels_dir)

    def reset_annotations(self):
        """Legacy method - use clear_all_annotations instead."""
        self.clear_all_annotations()