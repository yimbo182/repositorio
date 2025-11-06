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
from kivymd.material_resources import get_default_theme
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.switch import MDSwitch
from kivymd.uix.slider import MDSlider
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout

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
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        self.title = "Alarmas Inteligente"
        
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
            
            # Configurar colores personalizados
            if theme_style == "Dark":
                self.theme_cls.bg_normal = [0.1, 0.1, 0.1, 1]
                self.theme_cls.bg_light = [0.15, 0.15, 0.15, 1]
                self.theme_cls.bg_dark = [0.05, 0.05, 0.05, 1]
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
        layout = MDBoxLayout(orientation='vertical', spacing=10)
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Alarmas Inteligente",
            elevation=2,
            right_action_items=[
                ["cog", lambda x: self._open_config()],
                ["plus", lambda x: self._add_alarm()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Contenido principal
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20
        )
        
        # Estadísticas rápidas
        stats_card = self._create_stats_card()
        self.content_layout.add_widget(stats_card)
        
        # Lista de alarmas activas
        self.alarm_list = MDList()
        self.content_layout.add_widget(self.alarm_list)
        
        # Botón de acción rápida
        quick_action_button = MDRaisedButton(
            text="Agregar Alarma Rápida",
            size_hint=(1, None),
            height=50,
            on_release=self._quick_add_alarm
        )
        self.content_layout.add_widget(quick_action_button)
        
        layout.add_widget(self.content_layout)
        self.add_widget(layout)
        
        # Programar actualización de estadísticas
        Clock.schedule_interval(self._update_stats, 60)  # Cada minuto
    
    def _create_stats_card(self):
        """
        Crea la tarjeta de estadísticas
        """
        card = MDCard(
            size_hint=(1, None),
            height=120,
            padding=15,
            spacing=10
        )
        
        stats_layout = MDGridLayout(
            cols=3,
            spacing=15,
            size_hint_y=None,
            height=90
        )
        
        # Alarma activa más cercana
        next_alarm_layout = MDBoxLayout(orientation='vertical', spacing=5)
        next_alarm_layout.add_widget(MDLabel(text="Próxima", font_style="Caption"))
        self.next_alarm_label = MDLabel(text="--:--", font_style="H6")
        next_alarm_layout.add_widget(self.next_alarm_label)
        stats_layout.add_widget(next_alarm_layout)
        
        # Total de alarmas
        total_layout = MDBoxLayout(orientation='vertical', spacing=5)
        total_layout.add_widget(MDLabel(text="Total", font_style="Caption"))
        self.total_label = MDLabel(text="0", font_style="H6")
        total_layout.add_widget(self.total_label)
        stats_layout.add_widget(total_layout)
        
        # Estado del sistema
        status_layout = MDBoxLayout(orientation='vertical', spacing=5)
        status_layout.add_widget(MDLabel(text="Estado", font_style="Caption"))
        self.status_label = MDLabel(text="Activo", font_style="H6")
        status_layout.add_widget(self.status_label)
        stats_layout.add_widget(status_layout)
        
        card.add_widget(stats_layout)
        return card
    
    def _open_config(self):
        """
        Abre la pantalla de configuración
        """
        app = App.get_running_app()
        app.screen_manager.current = 'config'
    
    def _add_alarm(self):
        """
        Abre la pantalla para agregar alarma
        """
        app = App.get_running_app()
        app.screen_manager.current = 'alarms'
    
    def _quick_add_alarm(self, instance):
        """
        Agrega una alarma rápida
        """
        dialog = MDDialog(
            title="Alarma Rápida",
            type="custom",
            content_cls=QuickAlarmDialog(),
            auto_dismiss=False
        )
        dialog.open()
    
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
        self.spacing = 10
        self.size_hint_y = None
        self.height = 200
        self._build_ui()
    
    def _build_ui(self):
        """
        Construye la interfaz del diálogo
        """
        # Campo de título
        self.title_field = MDTextField(
            hint_text="Título de la alarma",
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.title_field)
        
        # Campo de URL del video motivacional
        self.video_field = MDTextField(
            hint_text="URL del video motivacional (opcional)",
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.video_field)
        
        # Selector de tiempo rápido
        time_buttons = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=40
        )
        
        for minutes in [5, 10, 15, 30]:
            btn = MDRaisedButton(
                text=f"{minutes}m",
                size_hint_x=0.25,
                on_release=lambda x, m=minutes: self._set_quick_time(m)
            )
            time_buttons.add_widget(btn)
        
        self.add_widget(time_buttons)
    
    def _set_quick_time(self, minutes):
        """
        Establece un tiempo rápido
        """
        # Esta funcionalidad se implementaría para configurar la alarma rápidamente

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
        Construye la interfaz de gestión de alarmas
        """
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Gestionar Alarmas",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            elevation=2
        )
        layout.add_widget(toolbar)
        
        # Lista de alarmas
        scroll = ScrollView()
        self.alarm_list = MDList()
        scroll.add_widget(self.alarm_list)
        
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _go_back(self):
        """
        Regresa a la pantalla principal
        """
        app = App.get_running_app()
        app.screen_manager.current = 'main'

if __name__ == '__main__':
    try:
        AlarmApp().run()
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        print(f"Error fatal: {e}")
        sys.exit(1)