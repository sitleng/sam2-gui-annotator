import unittest
from src.app.gui import MainApp
from src.controllers.annotation_controller import AnnotationController

class TestMainApp(unittest.TestCase):
    def setUp(self):
        self.app = MainApp()
        self.controller = AnnotationController()

    def test_app_initialization(self):
        self.assertIsNotNone(self.app)
        self.assertIsInstance(self.app, MainApp)

    def test_controller_initialization(self):
        self.assertIsNotNone(self.controller)
        self.assertIsInstance(self.controller, AnnotationController)

    def test_gui_elements(self):
        self.assertTrue(hasattr(self.app, 'canvas'))
        self.assertTrue(hasattr(self.app, 'reset_button'))

    def test_annotation_functionality(self):
        # Assuming the controller has a method to add annotations
        self.controller.add_annotation((100, 150), label='test')
        self.assertEqual(len(self.controller.annotations), 1)

if __name__ == '__main__':
    unittest.main()