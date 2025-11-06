"""
Módulo de optimización responsive para diferentes tamaños de pantalla
Adapta la interfaz de usuario según el dispositivo
"""

import logging
from typing import Dict, Any, Tuple
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

logger = logging.getLogger(__name__)

class ResponsiveManager:
    """
    Gestor de diseño responsive para la aplicación
    """
    
    def __init__(self):
        """Inicializa el gestor responsive"""
        self.screen_info = self._get_screen_info()
        self.layout_sizes = self._calculate_layout_sizes()
        self.font_sizes = self._calculate_font_sizes()
        self.spacing_values = self._calculate_spacing()
    
    def _get_screen_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la pantalla actual
        
        Returns:
            Diccionario con información de pantalla
        """
        width, height = Window.size
        density = Window.dpi / 160 if hasattr(Window, 'dpi') else 1
        
        return {
            'width': width,
            'height': height,
            'density': density,
            'aspect_ratio': width / height if height > 0 else 1,
            'is_landscape': width > height,
            'size_category': self._categorize_screen_size(width, height)
        }
    
    def _categorize_screen_size(self, width: int, height: int) -> str:
        """
        Categoriza el tamaño de pantalla
        
        Args:
            width: Ancho de pantalla
            height: Alto de pantalla
            
        Returns:
            Categoría del tamaño de pantalla
        """
        area = width * height
        
        if area < 200000:  # ~300x667 (iPhone SE)
            return 'small'
        elif area < 500000:  # ~375x1334 (iPhone 11)
            return 'medium'
        elif area < 800000:  # ~414x896 (iPhone 11 Pro Max)
            return 'large'
        else:
            return 'xlarge'
    
    def _calculate_layout_sizes(self) -> Dict[str, int]:
        """
        Calcula tamaños de layout según la pantalla
        
        Returns:
            Diccionario con tamaños de layout
        """
        size_cat = self.screen_info['size_category']
        density = self.screen_info['density']
        
        base_sizes = {
            'small': {
                'toolbar_height': 56,
                'card_height': 100,
                'list_item_height': 56,
                'button_height': 40,
                'text_field_height': 44,
                'max_content_width': 320
            },
            'medium': {
                'toolbar_height': 64,
                'card_height': 120,
                'list_item_height': 64,
                'button_height': 48,
                'text_field_height': 56,
                'max_content_width': 400
            },
            'large': {
                'toolbar_height': 72,
                'card_height': 140,
                'list_item_height': 72,
                'button_height': 56,
                'text_field_height': 64,
                'max_content_width': 480
            },
            'xlarge': {
                'toolbar_height': 80,
                'card_height': 160,
                'list_item_height': 80,
                'button_height': 64,
                'text_field_height': 72,
                'max_content_width': 600
            }
        }
        
        # Aplicar densidad
        base = base_sizes[size_cat]
        return {k: int(v * density) for k, v in base.items()}
    
    def _calculate_font_sizes(self) -> Dict[str, float]:
        """
        Calcula tamaños de fuente según la pantalla
        
        Returns:
            Diccionario con tamaños de fuente
        """
        size_cat = self.screen_info['size_category']
        
        font_sizes = {
            'small': {
                'tiny': 10,
                'small': 12,
                'medium': 14,
                'large': 16,
                'title': 18,
                'heading': 20,
                'display': 24
            },
            'medium': {
                'tiny': 11,
                'small': 13,
                'medium': 15,
                'large': 17,
                'title': 19,
                'heading': 21,
                'display': 26
            },
            'large': {
                'tiny': 12,
                'small': 14,
                'medium': 16,
                'large': 18,
                'title': 20,
                'heading': 22,
                'display': 28
            },
            'xlarge': {
                'tiny': 13,
                'small': 15,
                'medium': 17,
                'large': 19,
                'title': 21,
                'heading': 23,
                'display': 30
            }
        }
        
        return font_sizes[size_cat]
    
    def _calculate_spacing(self) -> Dict[str, int]:
        """
        Calcula valores de espaciado según la pantalla
        
        Returns:
            Diccionario con valores de espaciado
        """
        size_cat = self.screen_info['size_category']
        density = self.screen_info['density']
        
        spacing = {
            'small': 8,
            'medium': 12,
            'large': 16,
            'xlarge': 20
        }
        
        base_spacing = spacing[size_cat]
        return {
            'tiny': int(base_spacing * 0.5 * density),
            'small': int(base_spacing * density),
            'medium': int(base_spacing * 1.5 * density),
            'large': int(base_spacing * 2 * density),
            'xlarge': int(base_spacing * 3 * density)
        }
    
    def get_responsive_value(self, category: str, base_value: float) -> float:
        """
        Obtiene un valor responsive basado en la categoría y valor base
        
        Args:
            category: Categoría del tamaño ('small', 'medium', 'large', 'xlarge')
            base_value: Valor base
            
        Returns:
            Valor ajustado según el tamaño de pantalla
        """
        screen_cat = self.screen_info['size_category']
        
        multipliers = {
            'small': 0.8,
            'medium': 1.0,
            'large': 1.2,
            'xlarge': 1.4
        }
        
        multiplier = multipliers.get(screen_cat, 1.0)
        return base_value * multiplier
    
    def adapt_widget_size(self, widget, widget_type: str):
        """
        Adapta el tamaño de un widget según la pantalla
        
        Args:
            widget: Widget a adaptar
            widget_type: Tipo de widget ('toolbar', 'button', 'card', etc.)
        """
        try:
            sizes = self.layout_sizes
            
            if widget_type == 'toolbar':
                widget.height = sizes['toolbar_height']
            elif widget_type == 'button':
                widget.height = sizes['button_height']
            elif widget_type == 'card':
                widget.height = sizes['card_height']
            elif widget_type == 'list_item':
                widget.height = sizes['list_item_height']
            elif widget_type == 'text_field':
                widget.height = sizes['text_field_height']
                
        except Exception as e:
            logger.error(f"Error adaptando widget {widget_type}: {e}")
    
    def adapt_text_size(self, label, text_type: str = 'medium'):
        """
        Adapta el tamaño de texto según la pantalla
        
        Args:
            label: Label a adaptar
            text_type: Tipo de texto ('tiny', 'small', 'medium', etc.)
        """
        try:
            font_sizes = self.font_sizes
            if text_type in font_sizes:
                label.font_size = font_sizes[text_type]
            else:
                label.font_size = font_sizes['medium']
                
        except Exception as e:
            logger.error(f"Error adaptando texto {text_type}: {e}")
    
    def get_responsive_padding(self, base_padding: float) -> Tuple[float, float]:
        """
        Obtiene padding responsive
        
        Args:
            base_padding: Padding base
            
        Returns:
            Tuple con padding horizontal y vertical
        """
        spacing = self.spacing_values
        
        # Determinar spacing apropiado
        screen_cat = self.screen_info['size_category']
        
        if screen_cat == 'small':
            h_padding = spacing['small']
            v_padding = spacing['tiny']
        elif screen_cat == 'medium':
            h_padding = spacing['medium']
            v_padding = spacing['small']
        elif screen_cat == 'large':
            h_padding = spacing['large']
            v_padding = spacing['medium']
        else:  # xlarge
            h_padding = spacing['xlarge']
            v_padding = spacing['large']
        
        return (h_padding, v_padding)
    
    def should_show_compact_view(self) -> bool:
        """
        Determina si se debe mostrar la vista compacta
        
        Returns:
            True si debe usar vista compacta
        """
        return self.screen_info['size_category'] in ['small', 'medium']
    
    def get_max_content_width(self) -> int:
        """
        Obtiene el ancho máximo de contenido
        
        Returns:
            Ancho máximo de contenido en píxeles
        """
        return self.layout_sizes['max_content_width']
    
    def is_tablet_layout(self) -> bool:
        """
        Determina si es un layout de tablet
        
        Returns:
            True si es layout de tablet
        """
        return self.screen_info['size_category'] in ['large', 'xlarge']
    
    def get_grid_columns(self) -> int:
        """
        Obtiene número apropiado de columnas para grid
        
        Returns:
            Número de columnas
        """
        if self.is_tablet_layout():
            return 2
        else:
            return 1
    
    def adapt_screen_layout(self, screen_manager: ScreenManager):
        """
        Adapta el layout de todas las pantallas
        
        Args:
            screen_manager: ScreenManager de la aplicación
        """
        try:
            for screen in screen_manager.screens:
                if hasattr(screen, 'adaptive_layout'):
                    screen.adaptive_layout()
                    
        except Exception as e:
            logger.error(f"Error adaptando layout de pantallas: {e}")
    
    def on_window_resize(self, window, width, height):
        """
        Callback para redimensionamiento de ventana
        
        Args:
            window: Ventana redimensionada
            width: Nuevo ancho
            height: Nuevo alto
        """
        # Actualizar información de pantalla
        self.screen_info = self._get_screen_info()
        self.layout_sizes = self._calculate_layout_sizes()
        self.font_sizes = self._calculate_font_sizes()
        self.spacing_values = self._calculate_spacing()
        
        logger.info(f"Pantalla redimensionada a {width}x{height}")
    
    def create_responsive_card(self, content_widget, card_style: str = 'default'):
        """
        Crea una tarjeta responsive
        
        Args:
            content_widget: Widget contenido
            card_style: Estilo de tarjeta
            
        Returns:
            Tarjeta adaptada
        """
        from kivymd.uix.card import MDCard
        from kivy.uix.boxlayout import BoxLayout
        
        card = MDCard(
            size_hint=(1, None),
            height=self.layout_sizes['card_height'],
            padding=self.get_responsive_padding(16),
            elevation=2 if not self.should_show_compact_view() else 1
        )
        
        content_layout = BoxLayout(
            orientation='vertical' if not self.is_tablet_layout() else 'horizontal',
            spacing=self.spacing_values['small']
        )
        
        content_layout.add_widget(content_widget)
        card.add_widget(content_layout)
        
        return card
    
    def create_responsive_list_item(self, icon: str, primary_text: str, secondary_text: str = "", 
                                  tertiary_text: str = "", on_release=None):
        """
        Crea un elemento de lista responsive
        
        Args:
            icon: Icono del elemento
            primary_text: Texto principal
            secondary_text: Texto secundario
            tertiary_text: Texto terciario
            on_release: Callback al tocar
            
        Returns:
            Elemento de lista adaptado
        """
        from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget
        from kivymd.uix.label import MDLabel
        
        # Crear el elemento
        item = ThreeLineAvatarIconListItem(
            height=self.layout_sizes['list_item_height'],
            on_release=on_release
        )
        
        # Agregar icono si se especifica
        if icon:
            icon_widget = IconLeftWidget(icon=icon)
            item.add_widget(icon_widget)
        
        # El contenido de texto ya está incluido en ThreeLineAvatarIconListItem
        # que tiene primary_text, secondary_text y tertiary_text
        
        return item
    
    def create_responsive_button(self, text: str, button_style: str = 'raised', 
                               on_release=None, icon: str = None):
        """
        Crea un botón responsive
        
        Args:
            text: Texto del botón
            button_style: Estilo del botón ('raised', 'flat', 'outline')
            on_release: Callback al tocar
            icon: Icono opcional
            
        Returns:
            Botón adaptado
        """
        from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDOutlinedButton
        
        button_kwargs = {
            'text': text,
            'size_hint': (1, None),
            'height': self.layout_sizes['button_height'],
            'on_release': on_release
        }
        
        if icon and hasattr(self, 'add_button_icon'):
            button_kwargs['icon'] = icon
        
        if button_style == 'raised':
            return MDRaisedButton(**button_kwargs)
        elif button_style == 'flat':
            return MDFlatButton(**button_kwargs)
        else:
            return MDOutlinedButton(**button_kwargs)
    
    def get_orientation_sensitive_layout(self, portrait_layout, landscape_layout):
        """
        Obtiene layout sensible a la orientación
        
        Args:
            portrait_layout: Layout para modo retrato
            landscape_layout: Layout para modo paisaje
            
        Returns:
            Layout apropiado según orientación
        """
        if self.screen_info['is_landscape'] and landscape_layout:
            return landscape_layout
        else:
            return portrait_layout

# Clase base para pantallas que se adaptan automáticamente
class AdaptiveScreen:
    """
    Clase base para pantallas con adaptación automática
    """
    
    def __init__(self):
        self.responsive_manager = ResponsiveManager()
    
    def adaptive_layout(self):
        """
        Método que debe ser implementado por cada pantalla para adaptarse
        """
        raise NotImplementedError("Las pantallas deben implementar adaptive_layout()")
    
    def on_pre_enter(self):
        """
        Se llama antes de entrar a la pantalla
        """
        self.adaptive_layout()
    
    def adapt_widget(self, widget, widget_type: str):
        """
        Adapta un widget específico
        
        Args:
            widget: Widget a adaptar
            widget_type: Tipo de widget
        """
        self.responsive_manager.adapt_widget_size(widget, widget_type)
    
    def adapt_text(self, label, text_type: str = 'medium'):
        """
        Adapta el texto de un label
        
        Args:
            label: Label a adaptar
            text_type: Tipo de texto
        """
        self.responsive_manager.adapt_text_size(label, text_type)
    
    def get_responsive_padding(self, base_padding: float):
        """
        Obtiene padding responsive
        
        Args:
            base_padding: Padding base
            
        Returns:
            Padding adaptado
        """
        return self.responsive_manager.get_responsive_padding(base_padding)