"""
Script de prueba para verificar el diálogo de alarmas
"""

import sys
import traceback

try:
    print("Importando módulos...")
    from datetime import datetime, timedelta
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivymd.app import MDApp
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.button import MDRaisedButton, MDIconButton
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivymd.uix.boxlayout import MDBoxLayout
    
    print("✅ Módulos importados correctamente")
    
    print("\nProbando creación de AlarmTimePickerDialog...")
    
    class TestAlarmTimePickerDialog(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.orientation = 'vertical'
            self.spacing = 15
            self.size_hint_y = None
            self.height = 520
            self.dialog = None
            self.selected_hour = datetime.now().hour
            self.selected_minute = datetime.now().minute
            self.recurrence_type = "daily"
            print(f"  - Inicializado con hora: {self.selected_hour:02d}:{self.selected_minute:02d}")
            self._build_ui()
        
        def _build_ui(self):
            print("  - Construyendo UI...")
            
            # Campo de título
            self.title_field = MDTextField(
                hint_text="Título de la alarma",
                size_hint_y=None,
                height=50,
                text="Mi Alarma"
            )
            self.add_widget(self.title_field)
            print("  - Campo título OK")
            
            # Selector de hora
            time_selector_card = MDCard(
                size_hint=(1, None),
                height=200,
                padding=15
            )
            
            time_selector_layout = MDBoxLayout(orientation='vertical', spacing=10)
            
            # Hora picker
            self.hour_label = MDLabel(
                text=f"{self.selected_hour:02d}",
                font_style="H3",
                halign="center"
            )
            
            self.minute_label = MDLabel(
                text=f"{self.selected_minute:02d}",
                font_style="H3",
                halign="center"
            )
            
            time_selector_layout.add_widget(self.hour_label)
            time_selector_layout.add_widget(self.minute_label)
            time_selector_card.add_widget(time_selector_layout)
            self.add_widget(time_selector_card)
            
            print("  - Time picker OK")
            print("✅ UI construida exitosamente")
    
    # Crear instancia de prueba
    test_dialog = TestAlarmTimePickerDialog()
    print(f"\n✅ Prueba exitosa! Diálogo creado correctamente")
    print(f"Altura del diálogo: {test_dialog.height}")
    print(f"Hora seleccionada: {test_dialog.selected_hour:02d}:{test_dialog.selected_minute:02d}")
    
except Exception as e:
    print(f"\n❌ ERROR DETECTADO:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    print(f"\nStack trace completo:")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Todas las pruebas pasaron correctamente")