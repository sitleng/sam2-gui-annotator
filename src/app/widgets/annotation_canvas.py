"""
Enhanced annotation canvas with SAM2 integration and multi-object support
"""
import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QProgressBar, QMessageBox,
                           QGroupBox, QTextEdit, QSplitter, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Add src to path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from controllers.annotation_controller import AnnotationController


class BatchProcessingThread(QThread):
    """Thread for batch processing to avoid blocking the UI."""
    progress_updated = pyqtSignal(int, int)  # current, total
    processing_finished = pyqtSignal(list)   # results
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self, controller, runs_dir, labels_dir):
        super().__init__()
        self.controller = controller
        self.runs_dir = runs_dir
        self.labels_dir = labels_dir
        
    def run(self):
        try:
            def progress_callback(current, total):
                # Emit progress signal - this should work from thread
                self.progress_updated.emit(current, total)
                print(f"Progress: {current}/{total}")  # Debug print
            
            results = self.controller.process_image_sequence(
                self.runs_dir, self.labels_dir, progress_callback
            )
            self.processing_finished.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AnnotationCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = None
        self.current_image = None
        self.current_results = None
        self.init_ui()
        self.init_controller()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SAM2 Multi-Object Annotation Tool")
        
        # Main layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel for controls
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # Right panel for visualization
        viz_panel = self.create_visualization_panel()
        splitter.addWidget(viz_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 700])
        
    def create_control_panel(self):
        """Create the control panel widget."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        file_group.setLayout(file_layout)
        
        self.load_folder_btn = QPushButton("Load Image Folder")
        self.load_folder_btn.clicked.connect(self.load_image_folder)
        file_layout.addWidget(self.load_folder_btn)
        
        self.folder_info_label = QLabel("No folder loaded")
        file_layout.addWidget(self.folder_info_label)
        
        layout.addWidget(file_group)
        
        # Object management group
        object_group = QGroupBox("Object Management")
        object_layout = QVBoxLayout()
        object_group.setLayout(object_layout)
        
        # Current object info
        self.object_info_label = QLabel("No objects")
        object_layout.addWidget(self.object_info_label)
        
        # Object control buttons
        obj_btn_layout = QHBoxLayout()
        self.new_object_btn = QPushButton("New Object (N)")
        self.new_object_btn.clicked.connect(self.add_new_object)
        obj_btn_layout.addWidget(self.new_object_btn)
        
        self.next_object_btn = QPushButton("Next Object (Tab)")
        self.next_object_btn.clicked.connect(self.switch_to_next_object)
        obj_btn_layout.addWidget(self.next_object_btn)
        
        object_layout.addLayout(obj_btn_layout)
        
        # Clear buttons
        clear_btn_layout = QHBoxLayout()
        self.clear_current_btn = QPushButton("Clear Current")
        self.clear_current_btn.clicked.connect(self.clear_current_object)
        clear_btn_layout.addWidget(self.clear_current_btn)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all_annotations)
        clear_btn_layout.addWidget(self.clear_all_btn)
        
        object_layout.addLayout(clear_btn_layout)
        
        layout.addWidget(object_group)
        
        # Annotation controls group
        annotation_group = QGroupBox("Annotation Controls")
        annotation_layout = QVBoxLayout()
        annotation_group.setLayout(annotation_layout)
        
        instruction_text = """
Instructions:
• Left Click: Add positive point
• Right Click: Add negative point
• 'N' Key: Create new object
• 'Tab' Key: Switch between objects
• Update Segmentation: Run SAM2
        """
        self.instruction_label = QLabel(instruction_text)
        self.instruction_label.setWordWrap(True)
        annotation_layout.addWidget(self.instruction_label)
        
        self.update_segmentation_btn = QPushButton("Update Segmentation")
        self.update_segmentation_btn.clicked.connect(self.update_segmentation)
        annotation_layout.addWidget(self.update_segmentation_btn)
        
        layout.addWidget(annotation_group)
        
        # Batch processing group
        batch_group = QGroupBox("Batch Processing")
        batch_layout = QVBoxLayout()
        batch_group.setLayout(batch_layout)
        
        self.batch_info_label = QLabel("Ready for batch processing")
        batch_layout.addWidget(self.batch_info_label)
        
        self.process_batch_btn = QPushButton("Process All Images")
        self.process_batch_btn.clicked.connect(self.start_batch_processing)
        batch_layout.addWidget(self.process_batch_btn)
        
        self.progress_bar = QProgressBar()
        batch_layout.addWidget(self.progress_bar)
        
        layout.addWidget(batch_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def create_visualization_panel(self):
        """Create the visualization panel with matplotlib."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Make canvas focusable for key events
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        
        layout.addWidget(self.canvas)
        
        # Add image info label
        self.image_info_label = QLabel("No image loaded")
        layout.addWidget(self.image_info_label)
        
        return panel
    
    def init_controller(self):
        """Initialize the annotation controller."""
        try:
            self.controller = AnnotationController()
            self.log_status("Annotation controller initialized successfully")
        except Exception as e:
            self.log_status(f"Error initializing controller: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize SAM2: {e}")
    
    def load_image_folder(self):
        """Load images from a selected folder."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Use Qt dialog instead of native
        dialog.setWindowTitle("Select Image Folder - Click on folder name, then click 'Open'")
        dialog.setLabelText(QFileDialog.Accept, "Select Folder")  # Change button text
        if dialog.exec_():
            folder = dialog.selectedFiles()[0]
            if folder:
                if not os.path.isdir(folder):
                    QMessageBox.warning(self, "Invalid Selection", "Please select a folder, not a file.")
                    self.log_status("Invalid selection: selected a file instead of a folder")
                    return
                if not self.controller:
                    return
                # Clear previous annotations and results when loading new folder
                self.controller.clear_all_annotations()
                self.current_results = None
                self.log_status(f"Cleared previous annotations for new folder")
                
                success = self.controller.load_image_folder(folder)
                if success:
                    info = self.controller.get_image_info()
                    self.folder_info_label.setText(
                        f"Loaded {self.controller.get_image_count()} images\n"
                        f"From: {info.get('folder', 'Unknown')}"
                    )
                    self.load_and_display_first_image()
                    self.update_object_info()  # Update UI to reflect cleared state
                    self.log_status(f"Loaded {self.controller.get_image_count()} images from {folder}")
                else:
                    QMessageBox.warning(self, "Warning", "No images found in the selected folder")
                    self.log_status("Failed to load images from folder")
    
    def load_and_display_first_image(self):
        """Load and display the first image."""
        if not self.controller:
            return
            
        try:
            image_info = self.controller.get_image_info()
            if image_info:
                # Load image with OpenCV and convert to RGB
                import cv2
                image_path = image_info['path']
                
                # IMPORTANT: Set the image path in the annotation state
                self.controller.annotation_state.set_image_path(image_path)
                self.log_status(f"Set annotation image path: {image_path}")
                
                self.current_image = cv2.imread(image_path)
                if self.current_image is not None:
                    self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                    self.display_image()
                    self.update_image_info(image_info)
                    self.log_status(f"Loaded image: {image_info['filename']}")
                else:
                    self.log_status(f"Failed to load image: {image_path}")
        except Exception as e:
            self.log_status(f"Error loading image: {e}")
            import traceback
            traceback.print_exc()
    
    def display_image(self):
        """Display the current image on the canvas."""
        if self.current_image is None:
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.imshow(self.current_image)
        ax.set_title("Click: Left=Positive, Right=Negative | 'N'=New Object, 'Tab'=Switch")
        ax.axis('off')
        
        # Draw existing points
        self.draw_annotation_points(ax)
        
        # Draw segmentation results if available
        if self.current_results:
            self.draw_segmentation_results(ax)
        
        self.canvas.draw()
    
    def draw_annotation_points(self, ax):
        """Draw annotation points on the image."""
        if not self.controller:
            return
            
        objects = self.controller.annotation_state.get_all_objects()
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        
        for i, obj in enumerate(objects):
            color = colors[i % len(colors)]
            
            # Draw positive points
            if obj['positive']:
                pos_points = list(zip(*obj['positive']))
                ax.scatter(pos_points[0], pos_points[1], 
                          c=color, marker='o', s=100, 
                          label=f"Object {i+1} (+)", alpha=0.8)
            
            # Draw negative points
            if obj['negative']:
                neg_points = list(zip(*obj['negative']))
                ax.scatter(neg_points[0], neg_points[1], 
                          c=color, marker='x', s=100, 
                          label=f"Object {i+1} (-)", alpha=0.8)
        
        if objects:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    def draw_segmentation_results(self, ax):
        """Draw segmentation results on the image."""
        if not self.current_results or not hasattr(self.current_results, 'masks'):
            return
            
        try:
            if self.current_results.masks:
                cnts = self.current_results.masks.xy
                colors = ['blue', 'green', 'red', 'yellow', 'purple', 'orange']
                
                for i, cnt in enumerate(cnts):
                    if len(cnt) > 0:
                        color = colors[i % len(colors)]
                        ax.scatter(cnt[:, 0], cnt[:, 1], color=color, s=1, alpha=0.6)
        except Exception as e:
            self.log_status(f"Error drawing segmentation: {e}")
    
    def on_canvas_click(self, event):
        """Handle mouse clicks on the canvas."""
        if event.xdata is None or event.ydata is None or not self.controller:
            return
        
        point = (int(event.xdata), int(event.ydata))
        
        if event.button == 1:  # Left click: positive point
            self.controller.add_positive_point(point)
            self.log_status(f"Added positive point: {point}")
        elif event.button == 3:  # Right click: negative point
            self.controller.add_negative_point(point)
            self.log_status(f"Added negative point: {point}")
        
        self.update_object_info()
        self.display_image()
    
    def on_key_press(self, event):
        """Handle key press events."""
        if not self.controller:
            return
            
        if event.key == 'n':  # New object
            self.add_new_object()
        elif event.key == 'tab':  # Switch object
            self.switch_to_next_object()
    
    def add_new_object(self):
        """Add a new object."""
        if self.controller:
            new_index = self.controller.add_new_object()
            self.log_status(f"Added new object {new_index + 1}")
            self.update_object_info()
            self.display_image()
    
    def switch_to_next_object(self):
        """Switch to the next object."""
        if self.controller:
            self.controller.switch_to_next_object()
            self.update_object_info()
            self.display_image()
            current = self.controller.get_current_object_info()
            self.log_status(f"Switched to object {current['object_index'] + 1}")
    
    def clear_current_object(self):
        """Clear annotations for the current object."""
        if self.controller:
            self.controller.clear_current_object()
            self.log_status("Cleared current object")
            self.update_object_info()
            self.display_image()
    
    def clear_all_annotations(self):
        """Clear all annotations."""
        if self.controller:
            self.controller.clear_all_annotations()
            self.current_results = None
            self.log_status("Cleared all annotations")
            self.update_object_info()
            self.display_image()
    
    def update_segmentation(self):
        """Update segmentation with current annotations."""
        if not self.controller or not self.controller.has_annotations():
            QMessageBox.warning(self, "Warning", "No annotations available")
            return
        
        # Check if SAM model is loaded
        if not self.controller.sam_runner or not self.controller.sam_runner.sam_model:
            error_msg = "SAM2 model not loaded. Please restart the application."
            self.log_status(error_msg)
            QMessageBox.critical(self, "Model Error", error_msg)
            return
        
        try:
            self.log_status("Running SAM2 segmentation...")
            
            # Debug: Check controller state
            image_path = self.controller.annotation_state.get_image_path()
            self.log_status(f"Image path: {image_path}")
            
            # Debug: Check annotations
            points, labels = self.controller.annotation_state.get_points_and_labels()
            self.log_status(f"Points: {len(points)} objects, Labels: {len(labels)} objects")
            
            for i, (pts, lbls) in enumerate(zip(points, labels)):
                self.log_status(f"Object {i+1}: {len(pts)} points, {len(lbls)} labels")
            
            results = self.controller.run_interactive_segmentation()
            if results:
                self.current_results = results
                self.display_image()
                self.log_status("Segmentation updated successfully")
            else:
                self.log_status("Segmentation failed - check error details above")
                
        except Exception as e:
            error_msg = f"Error during segmentation: {e}"
            self.log_status(error_msg)
            print(f"Full error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Segmentation failed: {e}")
    
    def get_yolo_directory_structure(self, current_folder):
        """
        Generate YOLO directory structure from current folder path.
        
        Args:
            current_folder: Path like "../datasets/images/C_3/split_0"
            
        Returns:
            tuple: (runs_dir, labels_dir) like ("../datasets/runs/C_3/split_0", "../datasets/labels/C_3/split_0")
        """
        path_parts = current_folder.split(os.sep)
        try:
            images_index = path_parts.index("images")
            dataset_root = os.sep.join(path_parts[:images_index])
            subdirs_after_images = os.sep.join(path_parts[images_index + 1:])
            
            # Create YOLO directory structure preserving subdirectories
            runs_dir = os.path.join(dataset_root, "runs", subdirs_after_images)
            labels_dir = os.path.join(dataset_root, "labels", subdirs_after_images)
            
        except ValueError:
            # Fallback: if "images" not found in path, use the old method
            folder_name = os.path.basename(current_folder)
            parent_path = os.path.dirname(current_folder)
            grandparent_path = os.path.dirname(parent_path)
            runs_dir = os.path.join(grandparent_path, "runs", folder_name)
            labels_dir = os.path.join(grandparent_path, "labels", folder_name)
            
        return runs_dir, labels_dir
    
    def start_batch_processing(self):
        """Start batch processing of all images."""
        if not self.controller or not self.controller.is_ready_for_batch_processing():
            QMessageBox.warning(self, "Warning", 
                              "Not ready for batch processing. Make sure you have:\n"
                              "1. Loaded images\n"
                              "2. Added annotations\n"
                              "3. No processing in progress")
            return
        
        # Get the current image folder path to determine YOLO structure
        current_folder = self.controller.image_loader.current_folder
        if not current_folder:
            QMessageBox.warning(self, "Warning", "No image folder loaded")
            return
            
        # Get YOLO directory structure
        runs_dir, labels_dir = self.get_yolo_directory_structure(current_folder)
        
        # Show user the directory structure that will be created
        info_msg = (f"YOLO Format Structure:\n"
                   f"Images (predictions): {runs_dir}\n"
                   f"Labels (annotations): {labels_dir}\n\n"
                   f"Process {self.controller.get_image_count()} images?")
        
        reply = QMessageBox.question(self, "Confirm Batch Processing",
                                   info_msg,
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Create directories if they don't exist
            os.makedirs(runs_dir, exist_ok=True)
            os.makedirs(labels_dir, exist_ok=True)
            
            self.start_batch_thread(runs_dir, labels_dir)
    
    def start_batch_thread(self, runs_dir, labels_dir):
        """Start the batch processing thread."""
        self.process_batch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_status("Starting batch processing...")
        self.log_status(f"Saving images to: {runs_dir}")
        self.log_status(f"Saving labels to: {labels_dir}")
        
        self.batch_thread = BatchProcessingThread(self.controller, runs_dir, labels_dir)
        self.batch_thread.progress_updated.connect(self.update_progress, Qt.QueuedConnection)
        self.batch_thread.processing_finished.connect(self.batch_processing_finished, Qt.QueuedConnection)
        self.batch_thread.error_occurred.connect(self.batch_processing_error, Qt.QueuedConnection)
        self.batch_thread.start()
    
    def update_progress(self, current, total):
        """Update the progress bar."""
        progress = int((current / total) * 100)
        print(f"GUI: update_progress called - {current}/{total} = {progress}%")
        self.progress_bar.setValue(progress)
        self.log_status(f"Processing image {current}/{total} ({progress}%)")
        # Force GUI update
        QApplication.processEvents()
    
    def batch_processing_finished(self, results):
        """Handle batch processing completion."""
        self.process_batch_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        self.log_status(f"Batch processing completed! Processed {len(results)} images")
        
        # Get the directory structure info for display
        current_folder = self.controller.image_loader.current_folder
        runs_dir, labels_dir = self.get_yolo_directory_structure(current_folder)
        
        QMessageBox.information(self, "Batch Processing Complete",
                              f"Successfully processed {len(results)} images\n\n"
                              f"Results saved in YOLO format:\n"
                              f"• Images: {runs_dir}\n"
                              f"• Labels: {labels_dir}")
    
    def batch_processing_error(self, error_msg):
        """Handle batch processing error."""
        self.process_batch_btn.setEnabled(True)
        self.log_status(f"Batch processing error: {error_msg}")
        QMessageBox.critical(self, "Batch Processing Error", error_msg)
    
    def update_object_info(self):
        """Update the object information display."""
        if self.controller:
            info = self.controller.get_current_object_info()
            summary = self.controller.get_annotation_summary()
            
            self.object_info_label.setText(
                f"Current Object: {info['object_index'] + 1}/{info['object_count']}\n"
                f"Points: +{info['positive_points']}, -{info['negative_points']}\n"
                f"{summary}"
            )
            
            # Update batch processing readiness
            if self.controller.is_ready_for_batch_processing():
                self.batch_info_label.setText("✓ Ready for batch processing")
                self.process_batch_btn.setEnabled(True)
            else:
                self.batch_info_label.setText("Need annotations to process")
                self.process_batch_btn.setEnabled(False)
    
    def update_image_info(self, info):
        """Update the image information display."""
        self.image_info_label.setText(
            f"Image: {info['filename']} ({info['index']+1}/{info['total']})\n"
            f"Size: {info['width']}x{info['height']}"
        )
    
    def log_status(self, message):
        """Log a status message."""
        self.status_text.append(message)
        # Auto-scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.End)
        self.status_text.setTextCursor(cursor)

    # Legacy methods for backward compatibility
    def load_image(self, image_path):
        """Legacy method."""
        pass

    def reset_annotations(self):
        """Legacy method."""
        self.clear_all_annotations()

    def mousePressEvent(self, event):
        """Legacy mouse event handling."""
        pass