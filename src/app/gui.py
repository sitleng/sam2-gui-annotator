"""
Main GUI window for SAM2 GUI Annotator
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMenuBar, QAction, QMessageBox
from PyQt5.QtCore import Qt
from .widgets.annotation_canvas import AnnotationCanvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAM2 GUI Annotator - Multi-Object Annotation Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create main layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create and add the annotation canvas
        self.canvas = AnnotationCanvas()
        self.layout.addWidget(self.canvas)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Set window properties
        self.setMinimumSize(800, 600)
        
    def create_menu_bar(self):
        """Create the menu bar with file and help menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        load_action = QAction('Load Image Folder', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.canvas.load_image_folder)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        new_object_action = QAction('New Object', self)
        new_object_action.setShortcut('N')
        new_object_action.triggered.connect(self.canvas.add_new_object)
        edit_menu.addAction(new_object_action)
        
        next_object_action = QAction('Next Object', self)
        next_object_action.setShortcut('Tab')
        next_object_action.triggered.connect(self.canvas.switch_to_next_object)
        edit_menu.addAction(next_object_action)
        
        edit_menu.addSeparator()
        
        clear_current_action = QAction('Clear Current Object', self)
        clear_current_action.triggered.connect(self.canvas.clear_current_object)
        edit_menu.addAction(clear_current_action)
        
        clear_all_action = QAction('Clear All Annotations', self)
        clear_all_action.setShortcut('Ctrl+Delete')
        clear_all_action.triggered.connect(self.canvas.clear_all_annotations)
        edit_menu.addAction(clear_all_action)
        
        # Process menu
        process_menu = menubar.addMenu('Process')
        
        update_seg_action = QAction('Update Segmentation', self)
        update_seg_action.setShortcut('Space')
        update_seg_action.triggered.connect(self.canvas.update_segmentation)
        process_menu.addAction(update_seg_action)
        
        process_menu.addSeparator()
        
        batch_process_action = QAction('Process All Images', self)
        batch_process_action.setShortcut('Ctrl+P')
        batch_process_action.triggered.connect(self.canvas.start_batch_processing)
        process_menu.addAction(batch_process_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        instructions_action = QAction('Instructions', self)
        instructions_action.triggered.connect(self.show_instructions)
        help_menu.addAction(instructions_action)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About SAM2 GUI Annotator",
                         "SAM2 GUI Annotator v1.0\n\n"
                         "A multi-object annotation tool using SAM2 (Segment Anything Model 2)\n"
                         "for interactive image segmentation and batch processing.\n\n"
                         "Built with PyQt5 and Ultralytics SAM2")
    
    def show_instructions(self):
        """Show instructions dialog."""
        instructions = """
SAM2 GUI Annotator Instructions:

1. LOADING IMAGES:
   - Use File → Load Image Folder to select a folder containing images
   - The first image will be displayed for annotation

2. ANNOTATION:
   - Left Click: Add positive points (inside object)
   - Right Click: Add negative points (outside object)
   - 'N' Key or Menu: Create new object
   - 'Tab' Key or Menu: Switch between objects

3. SEGMENTATION:
   - Click "Update Segmentation" to run SAM2 on current annotations
   - Segmentation results will overlay on the image

4. BATCH PROCESSING:
   - Once satisfied with first image annotations, click "Process All Images"
   - Choose save directory for results
   - All images in the folder will be processed with the same annotation points

5. POINT MANAGEMENT:
   - The tool automatically balances annotation points between objects
   - Smaller point sets are duplicated to match the largest set
   - This ensures SAM2VideoPredictor runs without errors

6. TIPS:
   - Add both positive and negative points for better segmentation
   - Use multiple objects for different items in the image
   - Test segmentation on first image before batch processing
        """
        QMessageBox.information(self, "Instructions", instructions)
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(self, 'Exit Application',
                                   'Are you sure you want to exit?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())