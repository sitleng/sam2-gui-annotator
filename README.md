# SAM2 GUI Annotator

A powerful GUI application for interactive image segmentation and annotation using Meta's Segment Anything Model 2 (SAM2). This tool provides an intuitive interface for multi-object annotation with point-based interaction and batch processing capabilities.

## Features

### 🎯 Interactive Segmentation
- **Point-based annotation**: Click to add positive/negative points for precise segmentation control
- **Multi-object support**: Annotate multiple objects in a single image with different labels
- **Real-time preview**: Instant visual feedback as you add annotation point
- **Object switching**: Easy navigation between different objects using keyboard shortcuts

### 🖼️ Image Management
- **Folder-based loading**: Load entire directories of images for batch annotation
- **Image navigation**: Navigate through images with keyboard shortcuts
- **Format support**: Supports common image formats (PNG, JPG, JPEG, etc.)
- **Progress tracking**: Visual progress indicators for batch operations

### ⚡ Advanced Processing
- **SAM2 integration**: Leverages the latest SAM2 model for high-quality segmentation
- **Batch processing**: Process entire image sequences automatically
- **Export functionality**: Save annotations and segmentation masks
- **Multi-threading**: Non-blocking UI during intensive processing operations

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt5
- OpenCV
- SAM2 model weights

### Method 1: Using pip (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd sam2-gui-annotator

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies
The application requires the following Python packages:
- `numpy` - Numerical computing
- `opencv-python-headless` - Computer vision operations
- `matplotlib` - Visualization and plotting
- `tqdm` - Progress bars
- `ultralytics` - YOLOv8/SAM2 model integration
- `pyqt5` - GUI framework
- `Pillow` - Image processing
- `glob2` - File pattern matching
- `pathlib` - Path operations
- `typing` - Type hints

### SAM2 Model Setup
The application will automatically download the SAM2 model weights on first run. The default model is `sam2.1_l.pt`, but you can specify different models:
- `sam2.1_l.pt` (Large model - best accuracy)
- `sam2.1_b.pt` (Base model - balanced)
- `sam2.1_s.pt` (Small model - fastest)

## Usage

### Starting the Application
```bash
# Navigate to the project directory
cd sam2-gui-annotator

# Run the application
python src/main.py
```

### Basic Workflow

#### 1. Load Images
- **Menu**: File → Load Image Folder
- **Shortcut**: `Ctrl+O`
- Select a folder containing your images to annotate

#### 2. Annotate Objects
- **Left Click**: Add positive points (include this area)
- **Right Click**: Add negative points (exclude this area)
- **New Object**: Press `N` to start annotating a new object
- **Switch Objects**: Press `Tab` to cycle between objects

#### 3. Update Segmentation
- **Menu**: Process → Update Segmentation
- **Shortcut**: `Space`
- Apply SAM2 segmentation based on your points

#### 4. Batch Processing
- **Menu**: Process → Process All Images
- **Shortcut**: `Ctrl+P`
- Automatically process all loaded images

#### 5. Clear Annotations
- **Current Object**: Edit → Clear Current Object
- **All Objects**: Edit → Clear All Annotations (`Ctrl+Delete`)

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Load image folder |
| `Ctrl+Q` | Exit application |
| `N` | Create new object |
| `Tab` | Switch to next object |
| `Space` | Update segmentation |
| `Ctrl+P` | Process all images |
| `Ctrl+Delete` | Clear all annotations |


## Configuration

### Model Configuration
You can customize the SAM2 model by modifying the controller initialization:

```python
# In annotation_controller.py
controller = AnnotationController(model_name="sam2.1_b.pt")
```

### UI Configuration
The interface can be customized through the configuration files in `utils/config.py`.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Meta AI for the Segment Anything Model 2 (SAM2)
- Ultralytics for the SAM integration
- PyQt5 team for the GUI framework

## Citation

If you use this tool in your research, please cite:

```bibtex
@INPROCEEDINGS{koh2024crcd,
  author={Oh, Ki-Hwan and Borgioli, Leonardo and Mangano, Alberto and Valle, Valentina and Di Pangrazio, Marco and Toti, Francesco and Pozza, Gioia and Ambrosini, Luciano and Ducas, Alvaro and Žefran, Miloš and Chen, Liaohai and Giulianotti, Pier Cristoforo},
  booktitle={2024 International Symposium on Medical Robotics (ISMR)}, 
  title={Comprehensive Robotic Cholecystectomy Dataset (CRCD): Integrating Kinematics, Pedal Signals, and Endoscopic Videos}, 
  year={2024},
  pages={1-7},
  keywords={Medical robotics;Automation;Robot vision systems;Liver;Kinematics;Predictive models;Cameras},
  doi={10.1109/ISMR63436.2024.10585836}
}

@article{doi:10.1142/S2424905X25500060,
  author = {Oh, Ki-Hwan and Borgioli, Leonardo and Mangano, Alberto and Valle, Valentina and Pangrazio, Marco Di and Toti, Francesco and Pozza, Gioia and Ambrosini, Luciano and Ducas, Alvaro and \v{Z}efran, Milo\v{s} and Chen, Liaohai and Giulianotti, Pier Cristoforo},
  title = {Expanded Comprehensive Robotic Cholecystectomy Dataset},
  journal = {Journal of Medical Robotics Research},
  doi = {10.1142/S2424905X25500060},
  URL = {https://doi.org/10.1142/S2424905X25500060}
}
```
