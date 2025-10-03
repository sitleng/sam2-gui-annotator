"""
Model for managing annotation state with multiple objects and points
"""
from typing import List, Dict, Tuple, Optional


class AnnotationState:
    def __init__(self):
        """Initialize annotation state for multi-object annotation."""
        self.objects = []  # List of objects, each with positive and negative points
        self.current_object = 0  # Index of the object being annotated
        self.image_path = None  # Path to the current image being annotated
        self.segmentation_results = None  # Latest SAM2 results

    def add_object(self) -> int:
        """
        Add a new object to the annotation state.
        
        Returns:
            Index of the newly added object
        """
        new_object = {"positive": [], "negative": []}
        self.objects.append(new_object)
        return len(self.objects) - 1

    def ensure_current_object_exists(self):
        """Ensure that the current object exists."""
        if not self.objects:
            self.add_object()
        elif self.current_object >= len(self.objects):
            self.current_object = len(self.objects) - 1

    def add_positive_point(self, point: Tuple[int, int], object_index: Optional[int] = None):
        """
        Add a positive point to an object.
        
        Args:
            point: (x, y) coordinates
            object_index: Index of object (uses current_object if None)
        """
        if object_index is None:
            object_index = self.current_object
        
        self.ensure_current_object_exists()
        
        if 0 <= object_index < len(self.objects):
            self.objects[object_index]["positive"].append(point)
        else:
            print(f"Invalid object index: {object_index}")

    def add_negative_point(self, point: Tuple[int, int], object_index: Optional[int] = None):
        """
        Add a negative point to an object.
        
        Args:
            point: (x, y) coordinates
            object_index: Index of object (uses current_object if None)
        """
        if object_index is None:
            object_index = self.current_object
        
        self.ensure_current_object_exists()
        
        if 0 <= object_index < len(self.objects):
            self.objects[object_index]["negative"].append(point)
        else:
            print(f"Invalid object index: {object_index}")

    def switch_to_next_object(self):
        """Switch to the next object (creates new one if at the end)."""
        if self.current_object >= len(self.objects) - 1:
            self.add_object()
        self.current_object = (self.current_object + 1) % len(self.objects)

    def switch_to_object(self, object_index: int):
        """
        Switch to a specific object.
        
        Args:
            object_index: Index of the object to switch to
        """
        if 0 <= object_index < len(self.objects):
            self.current_object = object_index
        else:
            print(f"Invalid object index: {object_index}")

    def get_current_object_points(self) -> Dict[str, List[Tuple[int, int]]]:
        """Get points for the current object."""
        self.ensure_current_object_exists()
        if 0 <= self.current_object < len(self.objects):
            return self.objects[self.current_object]
        return {"positive": [], "negative": []}

    def get_all_objects(self) -> List[Dict[str, List[Tuple[int, int]]]]:
        """Get all objects with their points."""
        return self.objects

    def get_points_and_labels(self) -> Tuple[List[List[Tuple[int, int]]], List[List[int]]]:
        """
        Get formatted points and labels for SAM2.
        
        Returns:
            Tuple of (points_list, labels_list) where each entry corresponds to an object
        """
        points_list = []
        labels_list = []
        
        for obj in self.objects:
            positive_points = obj["positive"]
            negative_points = obj["negative"]
            points = positive_points + negative_points
            labels = [1] * len(positive_points) + [0] * len(negative_points)
            
            if points:  # Only include objects with points
                points_list.append(points)
                labels_list.append(labels)
        
        return points_list, labels_list

    def clear_current_object(self):
        """Clear all points for the current object."""
        self.ensure_current_object_exists()
        if 0 <= self.current_object < len(self.objects):
            self.objects[self.current_object] = {"positive": [], "negative": []}

    def clear_all_objects(self):
        """Clear all objects and reset state."""
        self.objects.clear()
        self.current_object = 0
        self.segmentation_results = None

    def remove_current_object(self):
        """Remove the current object."""
        if 0 <= self.current_object < len(self.objects):
            self.objects.pop(self.current_object)
            if self.current_object >= len(self.objects) and self.objects:
                self.current_object = len(self.objects) - 1
            elif not self.objects:
                self.current_object = 0

    def get_object_count(self) -> int:
        """Get the number of objects."""
        return len(self.objects)

    def get_current_object_index(self) -> int:
        """Get the current object index."""
        return self.current_object

    def has_annotations(self) -> bool:
        """Check if there are any annotations."""
        for obj in self.objects:
            if obj["positive"] or obj["negative"]:
                return True
        return False

    def set_image_path(self, path: str):
        """Set the current image path."""
        self.image_path = path

    def get_image_path(self) -> Optional[str]:
        """Get the current image path."""
        return self.image_path

    def set_segmentation_results(self, results):
        """Set the latest segmentation results."""
        self.segmentation_results = results

    def get_segmentation_results(self):
        """Get the latest segmentation results."""
        return self.segmentation_results

    def get_summary(self) -> str:
        """Get a summary of the current annotation state."""
        total_positive = sum(len(obj["positive"]) for obj in self.objects)
        total_negative = sum(len(obj["negative"]) for obj in self.objects)
        
        return (f"Objects: {len(self.objects)}, "
                f"Current: {self.current_object + 1}, "
                f"Total points: {total_positive + total_negative} "
                f"(+{total_positive}, -{total_negative})")

    # Legacy methods for backward compatibility
    def add_annotation(self, points, label):
        """Legacy method - adds points as positive points to current object."""
        if isinstance(points, list) and len(points) == 2:
            self.add_positive_point(tuple(points))
        elif isinstance(points, tuple):
            self.add_positive_point(points)

    def get_annotations(self):
        """Legacy method - returns objects in old format."""
        return [{'points': obj["positive"] + obj["negative"], 
                'label': [1] * len(obj["positive"]) + [0] * len(obj["negative"])}
                for obj in self.objects if obj["positive"] or obj["negative"]]

    def clear_annotations(self):
        """Legacy method - clears all objects."""
        self.clear_all_objects()

    def set_current_object(self, index):
        """Legacy method - switches to object."""
        self.switch_to_object(index)

    def get_current_object(self):
        """Legacy method - returns current object index."""
        return self.get_current_object_index()