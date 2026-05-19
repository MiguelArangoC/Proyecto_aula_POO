import unittest
import tkinter as tk
from GUIClaude import RPGApp

class TestGUIInicio(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible en entorno headless: {exc}")
        self.app = RPGApp(self.root)
        
    def tearDown(self):
        self.root.destroy()
        
    def test_pantalla_inicio_configuracion(self):
        # Verifica que la pantalla activa inicial sea 'start'
        self.assertEqual(self.app._active, "start")
        
        start_screen = self.app._screens["start"]
        
        # Verifica que existan las variables de Tkinter para configurar nombre y criatura inicial
        self.assertIsInstance(start_screen.name_var, tk.StringVar)
        self.assertIsInstance(start_screen.starter_var, tk.StringVar)
        
        # Simula configuración por parte del usuario
        start_screen.name_var.set("Ash Ketchum")
        start_screen.starter_var.set("Rocafer")
        
        # Verifica que los valores se configuraron en la GUI correctamente
        self.assertEqual(start_screen.name_var.get(), "Ash Ketchum")
        self.assertEqual(start_screen.starter_var.get(), "Rocafer")

if __name__ == '__main__':
    unittest.main()
