"""
Aplicación de Alarms Inteligente - Sistema Multiplataforma
Versión: 1.0
Desarrollado con Kivy para Android e iOS
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from kivy.config import Config
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.slider import MDSlider
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout

# Importar componentes que pueden tener ubicaciones diferentes
try:
    from kivy.uix.switch import Switch as MDSwitch
except ImportError:
    MDSwitch = None

# Verificar e importar componentes con nombres alternativos
try:
    from kivymd.uix.widget import MDSwitch
except ImportError:
    try:
        from kivy.uix.switch import Switch as MDSwitch
    except ImportError:
        MDSwitch = None

# Importar módulos auxiliares de la aplicación
try:
    from config_manager import ConfigManager
    from alarm_manager import AlarmManager
    from browser_integration import BrowserIntegration, AudioManager
    from responsive_manager import ResponsiveManager
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Error importando módulos auxiliares: {e}")
    print(f"Error: No se pudieron importar los módulos auxiliares: {e}")
    print("Asegúrate de que todos los archivos estén en el directorio correcto:")
    print("- config_manager.py")
    print("- alarm_manager.py")
    print("- browser_integration.py")
    print("- responsive_manager.py")
    sys.exit(1)

# Configuración inicial de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alarm_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración de Kivy
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'window_title', 'Alarmas Inteligente')

class AlarmApp(MDApp):
    """
    Clase principal de la aplicación de alarmas inteligente
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Paleta de colores moderna mejorada
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_hue = "A400"
        self.title = "🔔 Alarmas Inteligente"
        
        # Manager de pantallas
        self.screen_manager = ScreenManager()
        
        # Cargar configuraciones
        self.config_manager = ConfigManager()
        self.alarm_manager = AlarmManager(self.config_manager)
        
    def build(self):
        """
        Construye la interfaz principal de la aplicación
        """
        try:
            # Cargar tema personalizado
            self._load_custom_theme()
            
            # Crear pantalla principal
            main_screen = MainScreen(name='main')
            self.screen_manager.add_widget(main_screen)
            
            # Crear pantalla de configuración
            config_screen = ConfigScreen(name='config')
            self.screen_manager.add_widget(config_screen)
            
            # Crear pantalla de alarmas
            alarm_screen = AlarmScreen(name='alarms')
            self.screen_manager.add_widget(alarm_screen)
            
            return self.screen_manager
            
        except Exception as e:
            logger.error(f"Error construyendo la aplicación: {e}")
            return self._create_error_screen(str(e))
    
    def _load_custom_theme(self):
        """
        Carga el tema personalizado basado en las configuraciones
        """
        try:
            theme_style = self.config_manager.get('theme', 'theme_style', 'Light')
            self.theme_cls.theme_style = theme_style
            
            logger.info(f"Tema cargado: {theme_style}")
            
        except Exception as e:
            logger.error(f"Error cargando tema: {e}")
    
    def _create_error_screen(self, error_message):
        """
        Crea una pantalla de error cuando falla la inicialización
        """
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        
        error_label = MDLabel(
            text="Error de Inicialización",
            theme_text_color="Error",
            font_style="H5",
            halign="center"
        )
        
        message_label = MDLabel(
            text=f"Error: {error_message}",
            theme_text_color="Error",
            halign="center",
            size_hint_y=None,
            height=100
        )
        
        retry_button = MDRaisedButton(
            text="Reintentar",
            size_hint=(0.8, None),
            height=50,
            pos_hint={"center_x": 0.5}
        )
        
        retry_button.bind(on_release=self._retry_build)
        
        layout.add_widget(error_label)
        layout.add_widget(message_label)
        layout.add_widget(retry_button)
        
        return layout
    
    def _retry_build(self, instance):
        """
        Reintenta construir la aplicación
        """
        self.stop()
        Clock.schedule_once(lambda dt: self.build(), 0.1)
    
    def on_start(self):
        """
        Se ejecuta cuando la aplicación inicia
        """
        try:
            logger.info("Iniciando aplicación de alarmas inteligente")
            
            # Solicitar permisos necesarios
            self._request_permissions()
            
            # Iniciar el manager de alarmas
            self.alarm_manager.start()
            
            # Cargar alarmas existentes
            self.alarm_manager.load_alarms()
            
            logger.info("Aplicación iniciada correctamente")
            
        except Exception as e:
            logger.error(f"Error durante la inicialización: {e}")
            self._show_error_snackbar(f"Error de inicialización: {e}")
    
    def _request_permissions(self):
        """
        Solicita los permisos necesarios para la aplicación
        """
        try:
            from plyer import permission, storagepath
            
            # Solicitar permisos de notificación
            if permission.has_permission('notifications') is None:
                permission.request_permission('notifications')
            
            # Verificar permisos de audio
            if permission.has_permission('storage') is None:
                permission.request_permission('storage')
                
        except Exception as e:
            logger.warning(f"No se pudieron solicitar permisos: {e}")
    
    def _show_error_snackbar(self, message):
        """
        Muestra un snackbar de error
        """
        snackbar = Snackbar(
            text=message,
            bg_color=(1, 0, 0, 0.8)
        )
        snackbar.open()

class MainScreen(MDScreen):
    """
    Pantalla principal de la aplicación
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
    
    def _build_ui(self):
        """
        Construye la interfaz de la pantalla principal
        """
        layout = MDBoxLayout(orientation='vertical', spacing=15)
        
        # Toolbar mejorado con diseño moderno
        toolbar = MDTopAppBar(
            title="🔔 Alarmas Inteligente",
            elevation=10,
            left_action_items=[["menu", lambda x: self._show_menu()]],
            right_action_items=[
                ["plus-circle", lambda x: self._quick_add_alarm(x)],
                ["cog", lambda x: self._open_config()]
            ]
        )
        # Gradiente moderno púrpura-azulado
        toolbar.md_bg_color = (0.4, 0.2, 0.8, 1)
        layout.add_widget(toolbar)
        
        # Contenido principal con mejor padding
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            padding=[25, 15, 25, 15]
        )
        
        # Reloj digital - Hora actual del sistema
        clock_card = MDCard(
            size_hint=(1, None),
            height=100,
            padding=15,
            radius=[15, 15, 15, 15],
            elevation=6
        )
        clock_card.md_bg_color = (0.4, 0.2, 0.8, 1)  # Púrpura
        
        clock_layout = MDBoxLayout(orientation='vertical', spacing=5)
        
        self.current_time_label = MDLabel(
            text=datetime.now().strftime("%H:%M:%S"),
            font_style="H3",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Blanco puro para máximo contraste
        )
        clock_layout.add_widget(self.current_time_label)
        
        self.current_date_label = MDLabel(
            text=datetime.now().strftime("%A, %d de %B de %Y"),
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.95, 0.95, 1, 1)  # Blanco azulado para mejor contraste
        )
        clock_layout.add_widget(self.current_date_label)
        
        clock_card.add_widget(clock_layout)
        self.content_layout.add_widget(clock_card)
        
        # Actualizar reloj cada segundo
        Clock.schedule_interval(self._update_clock, 1)
        
        # Estadísticas rápidas con mejor diseño
        stats_card = self._create_stats_card()
        self.content_layout.add_widget(stats_card)
        
        # Lista de alarmas activas
        alarm_section = MDBoxLayout(orientation='vertical', spacing=10)
        alarm_section.add_widget(MDLabel(
            text="📅 Mis Alarmas Activas",
            font_style="H6",
            theme_text_color="Primary"
        ))
        self.alarm_list = MDList()
        self.alarm_list.size_hint_y = None
        self.alarm_list.height = 200
        alarm_section.add_widget(self.alarm_list)
        self.content_layout.add_widget(alarm_section)
        
        # Botones de acción mejorados
        buttons_section = self._create_buttons_section()
        self.content_layout.add_widget(buttons_section)
        
        # Contador de estado
        status_card = self._create_status_card()
        self.content_layout.add_widget(status_card)
        
        layout.add_widget(self.content_layout)
        self.add_widget(layout)
        
        # Programar actualización de estadísticas
        Clock.schedule_interval(self._update_stats, 5)  # Cada 5 segundos
    
    def _update_clock(self, dt):
        """
        Actualiza el reloj digital con la hora actual
        """
        try:
            now = datetime.now()
            self.current_time_label.text = now.strftime("%H:%M:%S")
            self.current_date_label.text = now.strftime("%A, %d de %B de %Y")
        except Exception as e:
            logger.error(f"Error actualizando reloj: {e}")
    
    def _create_stats_card(self):
        """
        Crea la tarjeta de estadísticas con diseño mejorado
        """
        card = MDCard(
            size_hint=(1, None),
            height=130,
            padding=20,
            spacing=10,
            radius=[15, 15, 15, 15],
            elevation=4
        )
        card.md_bg_color = (0.95, 0.95, 1.0, 1)
        
        stats_layout = MDGridLayout(
            cols=3,
            spacing=15,
            size_hint_y=None,
            height=90
        )
        
        # Alarma activa más cercana
        next_alarm_layout = MDBoxLayout(orientation='vertical', spacing=5)
        next_alarm_layout.add_widget(MDLabel(
            text="Próxima",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro para títulos
        ))
        self.next_alarm_label = MDLabel(
            text="--:--",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)  # Negro para valores
        )
        next_alarm_layout.add_widget(self.next_alarm_label)
        stats_layout.add_widget(next_alarm_layout)
        
        # Total de alarmas
        total_layout = MDBoxLayout(orientation='vertical', spacing=5)
        total_layout.add_widget(MDLabel(
            text="Total",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro para títulos
        ))
        self.total_label = MDLabel(
            text="0",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)  # Negro para valores
        )
        total_layout.add_widget(self.total_label)
        stats_layout.add_widget(total_layout)
        
        # Estado del sistema
        status_layout = MDBoxLayout(orientation='vertical', spacing=5)
        status_layout.add_widget(MDLabel(
            text="Estado",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro para títulos
        ))
        self.status_label = MDLabel(
            text="Activo",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)  # Negro para valores
        )
        status_layout.add_widget(self.status_label)
        stats_layout.add_widget(status_layout)
        
        card.add_widget(stats_layout)
        return card
    
    def _create_buttons_section(self):
        """
        Crea la sección de botones mejorada
        """
        section = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=200)
        
        # Título de sección
        section.add_widget(MDLabel(
            text="⚡ Acciones Rápidas",
            font_style="H6",
            theme_text_color="Primary",
            halign="center"
        ))
        
        # Grid de botones
        buttons_grid = GridLayout(
            cols=2,
            spacing=15,
            size_hint_y=None,
            height=120
        )
        
        # Botón principal: Alarma Rápida - Gradiente verde moderno
        quick_button = MDRaisedButton(
            text="🚀 Crear Alarma\nRápida",
            size_hint=(0.5, 1),
            font_size="16sp",
            elevation=8,
            on_release=self._quick_add_alarm,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco para máximo contraste
        )
        quick_button.md_bg_color = (0.0, 0.75, 0.5, 1)  # Verde azulado moderno
        buttons_grid.add_widget(quick_button)
        
        # Botón secundario: Gestionar Alarmas - Azul índigo
        full_button = MDRaisedButton(
            text="📋 Gestionar\nAlarmas",
            size_hint=(0.5, 1),
            font_size="16sp",
            elevation=8,
            on_release=self._add_alarm,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco para máximo contraste
        )
        full_button.md_bg_color = (0.3, 0.4, 0.9, 1)  # Azul índigo
        buttons_grid.add_widget(full_button)
        
        # Botón terciario: Configuración - Púrpura profundo
        config_button = MDRaisedButton(
            text="⚙️ Configuración",
            size_hint=(1, None),
            height=45,
            font_size="16sp",
            elevation=6,
            on_release=self._open_config,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco para máximo contraste
        )
        config_button.md_bg_color = (0.5, 0.2, 0.8, 1)  # Púrpura profundo
        buttons_grid.add_widget(config_button)
        
        section.add_widget(buttons_grid)
        return section
    
    def _open_config(self):
        """
        Abre la pantalla de configuración
        """
        app = App.get_running_app()
        app.screen_manager.current = 'config'
    
    def _create_status_card(self):
        """
        Crea la tarjeta de estado del sistema
        """
        card = MDCard(
            size_hint=(1, None),
            height=100,
            padding=15,
            radius=[20, 20, 20, 20],
            elevation=4
        )
        card.md_bg_color = (0.9, 0.9, 0.9, 1)  # Gris claro
        
        status_layout = MDBoxLayout(orientation='horizontal', spacing=15)
        
        # Indicador de estado
        status_indicator = MDLabel(
            text="🟢",
            font_style="H4",
            size_hint_x=0.2
        )
        status_layout.add_widget(status_indicator)
        
        # Texto de estado
        status_text = MDBoxLayout(orientation='vertical', spacing=5)
        status_text.add_widget(MDLabel(
            text="Sistema Activo",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro para mejor contraste
        ))
        status_text.add_widget(MDLabel(
            text="✅ Todas las funciones operativas",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1)  # Gris medio para texto secundario
        ))
        status_layout.add_widget(status_text)
        
        card.add_widget(status_layout)
        return card
    
    def _show_menu(self):
        """
        Muestra el menú lateral mejorado
        """
        from kivymd.uix.list import OneLineIconListItem
        
        menu_items = []
        
        class MenuItemWithIcon(OneLineIconListItem):
            def __init__(self, text, icon, callback, **kwargs):
                super().__init__(**kwargs)
                self.text = text
                self._icon = icon
                self._callback = callback
                
                # Añadir icono
                icon_widget = IconLeftWidget(icon=icon)
                self.add_widget(icon_widget)
            
            def on_release(self):
                if self._callback:
                    self._callback()
                # Cerrar el diálogo
                if hasattr(self, 'parent_dialog'):
                    self.parent_dialog.dismiss()
        
        # Crear elementos del menú
        items_data = [
            ("🏠 Inicio", "home", self._go_home),
            ("📋 Gestionar Alarmas", "clipboard-list", self._add_alarm),
            ("⚙️ Configuración", "cog", self._open_config),
            ("🗑️ Limpiar Alarmas", "delete-sweep", self._clear_alarms),
            ("📱 Sobre la App", "information", self._show_about),
            ("❓ Ayuda", "help-circle", self._show_help),
            ("🚪 Salir", "exit-to-app", self._show_exit_dialog)
        ]
        
        for text, icon, callback in items_data:
            item = MenuItemWithIcon(text=text, icon=icon, callback=callback)
            menu_items.append(item)
        
        dialog = MDDialog(
            title="🔔 Menú Principal",
            type="simple",
            items=menu_items,
            md_bg_color=(0.98, 0.98, 1.0, 1)
        )
        
        # Guardar referencia al diálogo en cada item
        for item in menu_items:
            item.parent_dialog = dialog
        
        dialog.open()
    
    def _go_home(self):
        """
        Regresa a la pantalla principal
        """
        pass  # Ya estamos en home
    
    def _clear_alarms(self):
        """
        Limpia todas las alarmas
        """
        try:
            app = App.get_running_app()
            app.alarm_manager.clear_all_alarms()
            self._show_success("✅ Todas las alarmas han sido eliminadas")
        except Exception as e:
            logger.error(f"Error limpiando alarmas: {e}")
            self._show_error(f"Error: {str(e)}")
    
    def _show_about(self):
        """
        Muestra información sobre la aplicación
        """
        dialog = MDDialog(
            title="📱 Sobre Alarmas Inteligente",
            text="🔔 Versión 1.0\n\n⭐ Sistema inteligente de alarmas\n🎥 Integración con videos motivacionales\n🌙 Temas claro y oscuro\n🔔 Notificaciones avanzadas\n📱 Optimizado para móviles\n\n💻 Desarrollado con ❤️ usando Kivy + KivyMD",
            buttons=[
                MDRaisedButton(text="👍 Genial!", elevation=0)
            ]
        )
        dialog.open()
    
    def _show_help(self):
        """
        Muestra la ayuda
        """
        dialog = MDDialog(
            title="❓ Ayuda",
            text="🚀 Crear Alarma Rápida: Botón verde para alarmas de 5-60 minutos\n⏰ Alarma Completa: Para configuración avanzada\n🎥 URL de Video: Enlace a YouTube (opcional)\n🔔 Snooze: Función de postergación disponible\n💡 Tip: Prueba el tema oscuro en configuración",
            buttons=[
                MDRaisedButton(text="✅ Entendido", elevation=0)
            ]
        )
        dialog.open()
    
    def _show_exit_dialog(self):
        """
        Muestra diálogo de confirmación para salir
        """
        dialog = MDDialog(
            title="🚪 Salir de la Aplicación",
            text="¿Estás seguro de que quieres salir de Alarmas Inteligente?\n\nTodas las alarmas activas se mantendrán.",
            buttons=[
                MDRaisedButton(
                    text="❌ Cancelar",
                    md_bg_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="🚪 Salir",
                    md_bg_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x: self._exit_app()
                )
            ]
        )
        dialog.open()
    
    def _exit_app(self):
        """
        Sale de la aplicación
        """
        import sys
        app = App.get_running_app()
        app.stop()
        sys.exit(0)
    
    def _show_success(self, message):
        """
        Muestra mensaje de éxito
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=message,
            bg_color=(0, 0.6, 0, 0.9)
        )
        snackbar.open()
    
    def _show_error(self, message):
        """
        Muestra mensaje de error
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=message,
            bg_color=(0.8, 0, 0, 0.9)
        )
        snackbar.open()
    
    def _add_alarm(self):
        """
        Abre la pantalla para agregar alarma
        """
        app = App.get_running_app()
        app.screen_manager.current = 'alarms'
    
    def _quick_add_alarm(self, instance=None):
        """
        Agrega una alarma con hora específica
        """
        try:
            dialog = MDDialog(
                title="⏰ Nueva Alarma",
                type="custom",
                content_cls=AlarmTimePickerDialog(),
                auto_dismiss=False
            )
            # Guardar referencia del diálogo
            content = dialog.content_cls
            content.dialog = dialog
            dialog.open()
        except Exception as e:
            logger.error(f"Error abriendo diálogo de alarma: {e}")
            logger.exception("Stack trace completo:")
            self._show_error(f"Error abriendo diálogo: {str(e)}")
    
    def _update_stats(self, dt):
        """
        Actualiza las estadísticas en tiempo real
        """
        try:
            app = App.get_running_app()
            alarms = app.alarm_manager.get_active_alarms()
            
            # Actualizar total de alarmas
            self.total_label.text = str(len(alarms))
            
            # Actualizar próxima alarma
            next_alarm = app.alarm_manager.get_next_alarm()
            if next_alarm:
                self.next_alarm_label.text = next_alarm.get_formatted_time()
            else:
                self.next_alarm_label.text = "--:--"
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")

class QuickAlarmDialog(BoxLayout):
    """
    Diálogo para crear una alarma rápida
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 15
        self.size_hint_y = None
        self.height = 280
        self.selected_minutes = 5
        self.dialog = None
        self._build_ui()
    
    def _build_ui(self):
        """
        Construye la interfaz del diálogo
        """
        # Campo de título
        self.title_field = MDTextField(
            hint_text="Título de la alarma",
            size_hint_y=None,
            height=50,
            text="Mi Alarma"
        )
        self.add_widget(self.title_field)
        
        # Campo de URL del video motivacional
        self.video_field = MDTextField(
            hint_text="URL del video motivacional (opcional)",
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.video_field)
        
        # Selector de tiempo rápido
        time_layout = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=100)
        time_layout.add_widget(MDLabel(text="Tiempo rápido:", font_style="Caption"))
        
        time_buttons = BoxLayout(
            orientation='horizontal',
            spacing=5,
            size_hint_y=None,
            height=40
        )
        
        self.selected_time_label = MDLabel(
            text="Seleccionado: 5 minutos",
            font_style="Caption",
            theme_text_color="Primary"
        )
        
        for minutes in [5, 10, 15, 30, 60]:
            btn = MDRaisedButton(
                text=f"{minutes}m",
                size_hint_x=0.2,
                on_release=lambda x, m=minutes: self._set_quick_time(m)
            )
            time_buttons.add_widget(btn)
        
        time_layout.add_widget(self.selected_time_label)
        time_layout.add_widget(time_buttons)
        self.add_widget(time_layout)
        
        # Botones de acción
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50
        )
        
        cancel_button = MDRaisedButton(
            text="❌ Cancelar",
            size_hint_x=0.5,
            md_bg_color=(0.7, 0.3, 0.3, 1),
            elevation=4
        )
        cancel_button.bind(on_release=self._cancel_alarm)
        
        save_button = MDRaisedButton(
            text="✅ Guardar Alarma",
            size_hint_x=0.5,
            md_bg_color=(0.0, 0.75, 0.5, 1),
            elevation=6
        )
        save_button.bind(on_release=self._save_alarm)
        
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)
        self.add_widget(button_layout)
    
    def _set_quick_time(self, minutes):
        """
        Establece un tiempo rápido
        """
        self.selected_minutes = minutes
        self.selected_time_label.text = f"Seleccionado: {minutes} minutos"
        self.selected_time_label.theme_text_color = "Primary"
    
    def _save_alarm(self, instance):
        """
        Guarda la alarma creada
        """
        try:
            title = self.title_field.text.strip()
            video_url = self.video_field.text.strip()
            
            # Validaciones
            if not title:
                self._show_error("El título de la alarma es requerido")
                return
            
            # Obtener la aplicación actual
            app = App.get_running_app()
            
            # Calcular tiempo de activación
            from datetime import datetime, timedelta
            activation_time = datetime.now() + timedelta(minutes=self.selected_minutes)
            
            # Crear alarma usando el manager
            alarm_data = {
                'title': title,
                'time': activation_time.strftime('%H:%M'),
                'video_url': video_url if video_url else None,
                'recurrence': 'once',  # Alarmas rápidas son únicas
                'snooze_enabled': True,
                'snooze_interval': 5,
                'snooze_limit': 3,
                'volume': 80,
                'vibration': True,
                'background_audio': True,
                'active': True
            }
            
            # Guardar alarma
            app.alarm_manager.add_alarm(alarm_data)
            
            # Mostrar confirmación
            self._show_success(f"Alarma '{title}' programada para {activation_time.strftime('%H:%M')}")
            
            # Cerrar diálogo
            if self.dialog:
                self.dialog.dismiss()
            
        except Exception as e:
            logger.error(f"Error guardando alarma: {e}")
            self._show_error(f"Error al guardar la alarma: {str(e)}")
    
    def _cancel_alarm(self, instance):
        """
        Cancela la creación de la alarma
        """
        if self.dialog:
            self.dialog.dismiss()
    
    def _show_error(self, message):
        """
        Muestra mensaje de error
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=message,
            bg_color=(1, 0, 0, 0.8)
        )
        snackbar.open()
    
    def _show_success(self, message):
        """
        Muestra mensaje de éxito
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=message,
            bg_color=(0, 1, 0, 0.8)
        )
        snackbar.open()

class ConfigScreen(MDScreen):
    """
    Pantalla de configuración de la aplicación
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
    
    def _build_ui(self):
        """
        Construye la interfaz de configuración
        """
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Configuración",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            elevation=2
        )
        layout.add_widget(toolbar)
        
        # Scroll de configuraciones
        scroll = ScrollView()
        
        config_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            size_hint_y=None
        )
        config_layout.bind(minimum_height=config_layout.setter('height'))
        
        # Configuración de tema
        theme_card = self._create_theme_config()
        config_layout.add_widget(theme_card)
        
        # Configuración de audio
        audio_card = self._create_audio_config()
        config_layout.add_widget(audio_card)
        
        # Configuración de snooze
        snooze_card = self._create_snooze_config()
        config_layout.add_widget(snooze_card)
        
        # Configuración de notificaciones
        notification_card = self._create_notification_config()
        config_layout.add_widget(notification_card)
        
        scroll.add_widget(config_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _create_theme_config(self):
        """
        Crea la sección de configuración de tema
        """
        card = MDCard(padding=15)
        layout = MDBoxLayout(orientation='vertical', spacing=10)
        
        layout.add_widget(MDLabel(text="Tema", font_style="H6"))
        
        # Switch para tema oscuro
        switch_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=48
        )
        switch_layout.add_widget(MDLabel(text="Tema Oscuro"))
        
        self.theme_switch = MDSwitch(
            active=False,
            pos_hint={"center_y": 0.5}
        )
        self.theme_switch.bind(active=self._on_theme_switch)
        switch_layout.add_widget(self.theme_switch)
        
        layout.add_widget(switch_layout)
        card.add_widget(layout)
        
        return card
    
    def _create_audio_config(self):
        """
        Crea la sección de configuración de audio
        """
        card = MDCard(padding=15)
        layout = MDBoxLayout(orientation='vertical', spacing=15)
        
        layout.add_widget(MDLabel(text="Audio", font_style="H6"))
        
        # Volumen de alarma
        volume_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=80
        )
        volume_layout.add_widget(MDLabel(text="Volumen de Alarma"))
        
        self.volume_slider = MDSlider(
            min=0,
            max=100,
            value=80,
            hint=True
        )
        volume_layout.add_widget(self.volume_slider)
        layout.add_widget(volume_layout)
        
        # Audio de fondo
        background_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=48
        )
        background_layout.add_widget(MDLabel(text="Reproducir en segundo plano"))
        
        self.background_switch = MDSwitch(
            active=True,
            pos_hint={"center_y": 0.5}
        )
        background_layout.add_widget(self.background_switch)
        
        layout.add_widget(background_layout)
        card.add_widget(layout)
        
        return card
    
    def _create_snooze_config(self):
        """
        Crea la sección de configuración de snooze
        """
        card = MDCard(padding=15)
        layout = MDBoxLayout(orientation='vertical', spacing=15)
        
        layout.add_widget(MDLabel(text="Snooze", font_style="H6"))
        
        # Intervalo de snooze
        snooze_interval_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=80
        )
        snooze_interval_layout.add_widget(MDLabel(text="Intervalo de Snooze (minutos)"))
        
        self.snooze_slider = MDSlider(
            min=1,
            max=30,
            value=5,
            step=1,
            hint=True
        )
        snooze_interval_layout.add_widget(self.snooze_slider)
        layout.add_widget(snooze_interval_layout)
        
        # Límite de snooze
        limit_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=48
        )
        limit_layout.add_widget(MDLabel(text="Límite de snoozes"))
        
        self.snooze_limit_slider = MDSlider(
            min=1,
            max=10,
            value=3,
            step=1,
            size_hint_x=0.5
        )
        limit_layout.add_widget(self.snooze_limit_slider)
        
        layout.add_widget(limit_layout)
        card.add_widget(layout)
        
        return card
    
    def _create_notification_config(self):
        """
        Crea la sección de configuración de notificaciones
        """
        card = MDCard(padding=15)
        layout = MDBoxLayout(orientation='vertical', spacing=15)
        
        layout.add_widget(MDLabel(text="Notificaciones", font_style="H6"))
        
        # Notificaciones activas
        notif_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=48
        )
        notif_layout.add_widget(MDLabel(text="Notificaciones activas"))
        
        self.notifications_switch = MDSwitch(
            active=True,
            pos_hint={"center_y": 0.5}
        )
        notif_layout.add_widget(self.notifications_switch)
        
        layout.add_widget(notif_layout)
        
        # Vibración
        vibrate_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=48
        )
        vibrate_layout.add_widget(MDLabel(text="Vibración"))
        
        self.vibrate_switch = MDSwitch(
            active=True,
            pos_hint={"center_y": 0.5}
        )
        vibrate_layout.add_widget(self.vibrate_switch)
        
        layout.add_widget(vibrate_layout)
        card.add_widget(layout)
        
        return card
    
    def _on_theme_switch(self, instance, value):
        """
        Callback para cambio de tema
        """
        app = App.get_running_app()
        app.config_manager.set('theme', 'theme_style', 'Dark' if value else 'Light')
        app.theme_cls.theme_style = 'Dark' if value else 'Light'
    
    def _go_back(self):
        """
        Regresa a la pantalla principal
        """
        app = App.get_running_app()
        app.screen_manager.current = 'main'

class AlarmScreen(MDScreen):
    """
    Pantalla para gestionar alarmas
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
    
    def _build_ui(self):
        """
        Construye la interfaz de gestión de alarmas mejorada
        """
        layout = MDBoxLayout(orientation='vertical', spacing=0)
        
        # Toolbar con diseño moderno
        toolbar = MDTopAppBar(
            title="📋 Gestionar Alarmas",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            right_action_items=[
                ["plus", lambda x: self._add_new_alarm()],
                ["refresh", lambda x: self._refresh_alarms()]
            ],
            elevation=10
        )
        toolbar.md_bg_color = (0.4, 0.2, 0.8, 1)
        layout.add_widget(toolbar)
        
        # Contenedor con padding
        content = MDBoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Mensaje de bienvenida
        welcome_card = MDCard(
            size_hint=(1, None),
            height=80,
            padding=15,
            radius=[12, 12, 12, 12],
            elevation=3
        )
        welcome_card.md_bg_color = (0.95, 0.95, 1.0, 1)
        
        welcome_layout = MDBoxLayout(orientation='vertical', spacing=5)
        welcome_layout.add_widget(MDLabel(
            text="🎯 Tus Alarmas Programadas",
            font_style="H6",
            theme_text_color="Primary",
            halign="center"
        ))
        welcome_layout.add_widget(MDLabel(
            text="Toca una alarma para editarla o desliza para eliminar",
            font_style="Caption",
            halign="center"
        ))
        welcome_card.add_widget(welcome_layout)
        content.add_widget(welcome_card)
        
        # Lista de alarmas con scroll
        scroll = ScrollView()
        self.alarm_list = MDList()
        scroll.add_widget(self.alarm_list)
        
        content.add_widget(scroll)
        layout.add_widget(content)
        
        self.add_widget(layout)
        
        # Cargar alarmas al iniciar
        Clock.schedule_once(lambda dt: self._refresh_alarms(), 0.5)
    
    def _add_new_alarm(self, *args):
        """
        Muestra diálogo para agregar nueva alarma
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text="💡 Usa el botón '🚀 Crear Alarma Rápida' desde la pantalla principal",
            bg_color=(0.3, 0.4, 0.9, 0.9)
        )
        snackbar.open()
    
    def _refresh_alarms(self, *args):
        """
        Actualiza la lista de alarmas
        """
        try:
            app = App.get_running_app()
            alarms = app.alarm_manager.get_active_alarms()
            
            # Limpiar lista actual
            self.alarm_list.clear_widgets()
            
            if not alarms:
                # Mostrar mensaje si no hay alarmas
                no_alarms_card = MDCard(
                    size_hint=(1, None),
                    height=150,
                    padding=20,
                    radius=[12, 12, 12, 12],
                    elevation=2
                )
                no_alarms_card.md_bg_color = (0.98, 0.98, 1.0, 1)
                
                no_alarms_layout = MDBoxLayout(orientation='vertical', spacing=10)
                no_alarms_layout.add_widget(MDLabel(
                    text="📭",
                    font_style="H3",
                    halign="center"
                ))
                no_alarms_layout.add_widget(MDLabel(
                    text="No tienes alarmas activas",
                    font_style="H6",
                    halign="center",
                    theme_text_color="Primary"
                ))
                no_alarms_layout.add_widget(MDLabel(
                    text="¡Crea tu primera alarma!",
                    font_style="Caption",
                    halign="center"
                ))
                no_alarms_card.add_widget(no_alarms_layout)
                self.alarm_list.add_widget(no_alarms_card)
            else:
                # Mostrar alarmas
                for alarm in alarms:
                    alarm_item = self._create_alarm_item(alarm)
                    self.alarm_list.add_widget(alarm_item)
            
            logger.info(f"Lista de alarmas actualizada: {len(alarms)} alarmas")
            
        except Exception as e:
            logger.error(f"Error actualizando lista de alarmas: {e}")
    
    def _create_alarm_item(self, alarm):
        """
        Crea un elemento de lista para una alarma
        """
        # Formatear información de la alarma
        time_str = alarm.get_formatted_time()
        title = alarm.title or "Sin título"
        
        # Determinar icono según recurrencia
        if alarm.recurrence == "daily":
            recurrence_icon = "🔁"
            recurrence_text = "Diaria"
        elif alarm.recurrence == "weekly":
            recurrence_icon = "📅"
            recurrence_text = "Semanal"
        else:
            recurrence_icon = "⏰"
            recurrence_text = "Una vez"
        
        # Crear item de lista
        item = ThreeLineAvatarIconListItem(
            text=f"⏰ {title}",
            secondary_text=f"🕐 Hora: {time_str}",
            tertiary_text=f"{recurrence_icon} {recurrence_text} | Volumen: {alarm.volume}%"
        )
        
        # Icono izquierdo
        icon_widget = IconLeftWidget(
            icon="alarm" if alarm.enabled else "alarm-off"
        )
        item.add_widget(icon_widget)
        
        # Botón de editar/eliminar
        from kivymd.uix.button import MDIconButton
        
        delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            on_release=lambda x: self._confirm_delete_alarm(alarm)
        )
        item.add_widget(delete_btn)
        
        # Acción al tocar el item
        item.bind(on_release=lambda x: self._edit_alarm(alarm))
        
        return item
    
    def _edit_alarm(self, alarm):
        """
        Edita una alarma
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=f"📝 Editando: {alarm.title}",
            bg_color=(0.3, 0.4, 0.9, 0.9)
        )
        snackbar.open()
    
    def _confirm_delete_alarm(self, alarm):
        """
        Confirma la eliminación de una alarma
        """
        dialog = MDDialog(
            title="🗑️ Eliminar Alarma",
            text=f"¿Estás seguro de que quieres eliminar la alarma '{alarm.title}'?",
            buttons=[
                MDRaisedButton(
                    text="Cancelar",
                    md_bg_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Eliminar",
                    md_bg_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x: self._delete_alarm(alarm, dialog)
                )
            ]
        )
        dialog.open()
    
    def _delete_alarm(self, alarm, dialog):
        """
        Elimina una alarma
        """
        try:
            app = App.get_running_app()
            if app.alarm_manager.delete_alarm(alarm.id):
                from kivymd.uix.snackbar import Snackbar
                snackbar = Snackbar(
                    text=f"✅ Alarma '{alarm.title}' eliminada",
                    bg_color=(0.0, 0.6, 0.0, 0.9)
                )
                snackbar.open()
                self._refresh_alarms()
            dialog.dismiss()
        except Exception as e:
            logger.error(f"Error eliminando alarma: {e}")
    
    def _go_back(self):
        """
        Regresa a la pantalla principal
        """
        app = App.get_running_app()
        app.screen_manager.current = 'main'
class AlarmTimePickerDialog(BoxLayout):
    """
    Diálogo para configurar alarma con hora específica del día
    """
    
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
        self._build_ui()
    
    def _build_ui(self):
        """
        Construye la interfaz del diálogo con time picker
        """
        # Campo de título
        self.title_field = MDTextField(
            hint_text="Título de la alarma (ej: Despertar, Gym, Reunión)",
            size_hint_y=None,
            height=50,
            text="Mi Alarma",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)  # Texto negro para mejor contraste
        )
        self.add_widget(self.title_field)
        
        # Selector de hora
        time_selector_card = MDCard(
            size_hint=(1, None),
            height=200,
            padding=15,
            radius=[12, 12, 12, 12],
            elevation=2
        )
        time_selector_card.md_bg_color = (0.95, 0.95, 1.0, 1)
        
        time_selector_layout = MDBoxLayout(orientation='vertical', spacing=10)
        
        time_selector_layout.add_widget(MDLabel(
            text="⏰ Hora de la Alarma",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),  # Negro para mejor contraste
            halign="center"
        ))
        
        # Selectores de hora y minuto
        pickers_layout = MDBoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=90)
        
        # Hora
        hour_layout = MDBoxLayout(orientation='vertical', spacing=5)
        hour_layout.add_widget(MDLabel(
            text="Hora",
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro
        ))
        
        hour_picker_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=60)
        
        dec_hour_btn = MDIconButton(
            icon="minus-circle",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),  # Icono negro
            on_release=self._decrease_hour
        )
        hour_picker_layout.add_widget(dec_hour_btn)
        
        self.hour_label = MDLabel(
            text=f"{self.selected_hour:02d}",
            font_style="H3",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.05, 0.05, 0.05, 1)  # Negro intenso para números
        )
        hour_picker_layout.add_widget(self.hour_label)
        
        inc_hour_btn = MDIconButton(
            icon="plus-circle",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),  # Icono negro
            on_release=self._increase_hour
        )
        hour_picker_layout.add_widget(inc_hour_btn)
        
        hour_layout.add_widget(hour_picker_layout)
        pickers_layout.add_widget(hour_layout)
        
        # Separador
        pickers_layout.add_widget(MDLabel(
            text=":",
            font_style="H2",
            halign="center",
            size_hint_x=0.2,
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)  # Negro para separador
        ))
        
        # Minuto
        minute_layout = MDBoxLayout(orientation='vertical', spacing=5)
        minute_layout.add_widget(MDLabel(
            text="Minuto",
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro
        ))
        
        minute_picker_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=60)
        
        dec_minute_btn = MDIconButton(
            icon="minus-circle",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),  # Icono negro
            on_release=self._decrease_minute
        )
        minute_picker_layout.add_widget(dec_minute_btn)
        
        self.minute_label = MDLabel(
            text=f"{self.selected_minute:02d}",
            font_style="H3",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.05, 0.05, 0.05, 1)  # Negro intenso para números
        )
        minute_picker_layout.add_widget(self.minute_label)
        
        inc_minute_btn = MDIconButton(
            icon="plus-circle",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),  # Icono negro
            on_release=self._increase_minute
        )
        minute_picker_layout.add_widget(inc_minute_btn)
        
        minute_layout.add_widget(minute_picker_layout)
        pickers_layout.add_widget(minute_layout)
        
        time_selector_layout.add_widget(pickers_layout)
        
        # Mostrar tiempo hasta alarma
        self.time_until_label = MDLabel(
            text=self._calculate_time_until(),
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1)  # Gris medio para tiempo restante
        )
        time_selector_layout.add_widget(self.time_until_label)
        
        time_selector_card.add_widget(time_selector_layout)
        self.add_widget(time_selector_card)
        
        # Selector de recurrencia
        recurrence_layout = MDBoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=80)
        recurrence_layout.add_widget(MDLabel(
            text="🔁 Repetición",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)  # Gris oscuro
        ))
        
        recurrence_buttons = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=40)
        
        once_btn = MDRaisedButton(
            text="Una vez",
            size_hint_x=0.33,
            on_release=lambda x: self._set_recurrence("none", once_btn),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco
        )
        recurrence_buttons.add_widget(once_btn)
        
        daily_btn = MDRaisedButton(
            text="Diaria",
            size_hint_x=0.33,
            on_release=lambda x: self._set_recurrence("daily", daily_btn),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco
        )
        daily_btn.md_bg_color = (0.0, 0.75, 0.5, 1)
        recurrence_buttons.add_widget(daily_btn)
        
        weekly_btn = MDRaisedButton(
            text="Semanal",
            size_hint_x=0.33,
            on_release=lambda x: self._set_recurrence("weekly", weekly_btn),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco
        )
        recurrence_buttons.add_widget(weekly_btn)
        
        self.recurrence_buttons = [once_btn, daily_btn, weekly_btn]
        recurrence_layout.add_widget(recurrence_buttons)
        self.add_widget(recurrence_layout)
        
        # Campo de URL del video motivacional
        self.video_field = MDTextField(
            hint_text="URL del video (opcional - se usa aleatorio si está vacío)",
            size_hint_y=None,
            height=50,
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)  # Texto negro
        )
        self.add_widget(self.video_field)
        
        # Botones de acción
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50
        )
        
        cancel_button = MDRaisedButton(
            text="❌ Cancelar",
            size_hint_x=0.5,
            md_bg_color=(0.7, 0.3, 0.3, 1),
            elevation=4,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco para contraste
        )
        cancel_button.bind(on_release=self._cancel_alarm)
        
        save_button = MDRaisedButton(
            text="✅ Guardar Alarma",
            size_hint_x=0.5,
            md_bg_color=(0.0, 0.75, 0.5, 1),
            elevation=6,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # Texto blanco para contraste
        )
        save_button.bind(on_release=self._save_alarm)
        
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)
        self.add_widget(button_layout)
    
    def _increase_hour(self, instance):
        """Incrementa la hora"""
        self.selected_hour = (self.selected_hour + 1) % 24
        self.hour_label.text = f"{self.selected_hour:02d}"
        self.time_until_label.text = self._calculate_time_until()
    
    def _decrease_hour(self, instance):
        """Decrementa la hora"""
        self.selected_hour = (self.selected_hour - 1) % 24
        self.hour_label.text = f"{self.selected_hour:02d}"
        self.time_until_label.text = self._calculate_time_until()
    
    def _increase_minute(self, instance):
        """Incrementa el minuto"""
        self.selected_minute = (self.selected_minute + 1) % 60
        self.minute_label.text = f"{self.selected_minute:02d}"
        self.time_until_label.text = self._calculate_time_until()
    
    def _decrease_minute(self, instance):
        """Decrementa el minuto"""
        self.selected_minute = (self.selected_minute - 1) % 60
        self.minute_label.text = f"{self.selected_minute:02d}"
        self.time_until_label.text = self._calculate_time_until()
    
    def _set_recurrence(self, recurrence_type, button):
        """Establece el tipo de recurrencia"""
        self.recurrence_type = recurrence_type
        
        # Resetear colores de todos los botones
        for btn in self.recurrence_buttons:
            btn.md_bg_color = (0.6, 0.6, 0.6, 1)
        
        # Resaltar botón seleccionado
        button.md_bg_color = (0.0, 0.75, 0.5, 1)
    
    def _calculate_time_until(self):
        """Calcula el tiempo hasta que suene la alarma"""
        try:
            now = datetime.now()
            alarm_time = now.replace(hour=self.selected_hour, minute=self.selected_minute, second=0, microsecond=0)
            
            # Si la hora ya pasó hoy, calcular para mañana
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
            
            time_diff = alarm_time - now
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"⏰ Sonará en {hours}h {minutes}m"
            else:
                return f"⏰ Sonará en {minutes} minutos"
        except Exception as e:
            logger.error(f"Error calculando tiempo: {e}")
            return "⏰ Calculando..."
    
    def _save_alarm(self, instance):
        """
        Guarda la alarma con hora específica
        """
        try:
            title = self.title_field.text.strip()
            video_url = self.video_field.text.strip()
            
            # Validaciones
            if not title:
                self._show_error("❌ El título de la alarma es requerido")
                return
            
            # Obtener la aplicación actual
            app = App.get_running_app()
            
            # Formatear hora
            time_str = f"{self.selected_hour:02d}:{self.selected_minute:02d}"
            
            # Crear datos de alarma
            alarm_data = {
                'title': title,
                'time': time_str,
                'video_url': video_url if video_url else "",
                'recurrence': self.recurrence_type,
                'snooze_enabled': True,
                'snooze_interval': 5,
                'max_snoozes': 3,
                'volume': 80,
                'vibrate': True,
                'browser_preference': 'brave',
                'enabled': True,
                'is_active': True,
                'days_of_week': [0, 1, 2, 3, 4, 5, 6] if self.recurrence_type == "weekly" else []
            }
            
            # Guardar alarma
            alarm_id = app.alarm_manager.add_alarm(alarm_data)
            
            if alarm_id:
                # Calcular tiempo hasta alarma
                time_until_text = self._calculate_time_until()
                
                # Mostrar confirmación
                recurrence_text = {
                    "none": "una vez",
                    "daily": "diariamente",
                    "weekly": "semanalmente"
                }.get(self.recurrence_type, "")
                
                self._show_success(f"✅ Alarma '{title}' programada para las {time_str} ({recurrence_text})\n{time_until_text}")
                
                # Cerrar diálogo
                if self.dialog:
                    self.dialog.dismiss()
            else:
                self._show_error("❌ No se pudo crear la alarma. Verifica que no sea duplicada.")
            
        except Exception as e:
            logger.error(f"Error guardando alarma: {e}")
            self._show_error(f"❌ Error al guardar la alarma: {str(e)}")
    
    def _cancel_alarm(self, instance):
        """
        Cancela la creación de la alarma
        """
        if self.dialog:
            self.dialog.dismiss()
    
    def _show_error(self, message):
        """
        Muestra mensaje de error
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=message,
            bg_color=(1, 0, 0, 0.8)
        )
        snackbar.open()
    
    def _show_success(self, message):
        """
        Muestra mensaje de éxito
        """
        from kivymd.uix.snackbar import Snackbar
        snackbar = Snackbar(
            text=message,
            bg_color=(0, 1, 0, 0.8)
        )
        snackbar.open()


if __name__ == '__main__':
    try:
        AlarmApp().run()
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        print(f"Error fatal: {e}")
        sys.exit(1)