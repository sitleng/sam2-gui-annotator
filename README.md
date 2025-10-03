# SAM2 GUI Annotator

A powerful GUI application for interactive image segmentation and annotation using Meta's Segment Anything Model 2 (SAM2). This tool provides an intuitive interface for multi-object annotation with point-based interaction and batch processing capabilities.

## Features

### 🎯 Interactive Segmentation
- **Point-based annotation**: Click to add positive/negative points for precise segmentation control
- **Multi-object support**: Annotate multiple objects in a single image with different labels
- **Real-time preview**: Instant visual feedback as you add annotation points
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

### 🎮 User-Friendly Interface
- **PyQt5-based GUI**: Clean, responsive desktop interface
- **Keyboard shortcuts**: Efficient workflow with customizable hotkeys
- **Menu system**: Organized menu structure for all functions
- **Progress visualization**: Real-time feedback on processing status

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

### Method 2: Using Poetry
```bash
# Clone the repository
git clone <repository-url>
cd sam2-gui-annotator

# Install with Poetry
poetry install
poetry shell
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

## Project Structure

```
sam2-gui-annotator/
├── src/
│   ├── main.py                 # Application entry point
│   ├── app/
│   │   ├── gui.py             # Main window and menu system
│   │   ├── events.py          # Event handling
│   │   └── widgets/
│   │       └── annotation_canvas.py  # Main annotation interface
│   ├── controllers/
│   │   └── annotation_controller.py  # Core annotation logic
│   ├── models/
│   │   └── annotation_state.py       # State management
│   ├── services/
│   │   ├── image_loader.py           # Image loading utilities
│   │   ├── sam_runner.py             # SAM2 model interface
│   │   ├── storage.py                # Data persistence
│   │   └── video_loader.py           # Video processing (future)
│   └── utils/
│       └── config.py                 # Configuration management
├── tests/                            # Unit tests
├── data/
│   └── samples/                      # Sample images
├── requirements.txt                  # Python dependencies
├── pyproject.toml                   # Poetry configuration
└── README.md                        # This file
```

## Architecture

The application follows a Model-View-Controller (MVC) architecture:

- **View Layer** (`app/`): PyQt5-based GUI components
- **Controller Layer** (`controllers/`): Business logic and coordination
- **Model Layer** (`models/`): Data structures and state management
- **Service Layer** (`services/`): External integrations (SAM2, file I/O)

## Configuration

### Model Configuration
You can customize the SAM2 model by modifying the controller initialization:

```python
# In annotation_controller.py
controller = AnnotationController(model_name="sam2.1_b.pt")
```

### UI Configuration
The interface can be customized through the configuration files in `utils/config.py`.

## Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `python -m pytest tests/`
5. Make your changes
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to all public methods
- Include unit tests for new features

## Troubleshooting

### Common Issues

#### Model Loading Errors
```
Error loading SAM2 model: ...
```
**Solution**: Ensure you have sufficient disk space and internet connection for model download.

#### PyQt5 Import Errors
```
ModuleNotFoundError: No module named 'PyQt5'
```
**Solution**: Install PyQt5: `pip install PyQt5`

#### Memory Issues
**Solution**: Use a smaller SAM2 model (`sam2.1_s.pt`) or reduce batch size.

### Performance Tips
- Use GPU acceleration if available
- Close other applications to free up RAM
- Use smaller images for faster processing
- Enable batch processing for multiple images

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Meta AI for the Segment Anything Model 2 (SAM2)
- Ultralytics for the SAM integration
- PyQt5 team for the GUI framework

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{sam2_gui_annotator,
  title={SAM2 GUI Annotator: Interactive Image Segmentation Tool},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/sam2-gui-annotator}
}
```

## Support

For questions, issues, or feature requests, please:
1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include system specifications and error messages

---

**Happy Annotating! 🎨**
