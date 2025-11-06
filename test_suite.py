"""
Suite de testing completo para la aplicación de Alarmas Inteligente
Incluye pruebas unitarias, de integración y funcionales
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
import logging

# Configurar logging para testing
logging.basicConfig(level=logging.WARNING)

# Añadir directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos de la aplicación
try:
    from config_manager import ConfigManager
    from alarm_manager import AlarmManager, Alarm
    from browser_integration import BrowserIntegration, AudioManager
    from responsive_manager import ResponsiveManager
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que todos los archivos estén en el directorio correcto")
    sys.exit(1)

class TestConfigManager(unittest.TestCase):
    """Pruebas para el gestor de configuraciones"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear directorio temporal para testing
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        
        # Mock ConfigManager con directorio de testing
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.test_dir
        self.config_manager.config_path = self.config_file
        self.config_manager.cipher = MagicMock()
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar directorio temporal
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Prueba la creación de configuración por defecto"""
        config_data = self.config_manager._get_default_config()
        
        # Verificar que existen las secciones principales
        required_sections = ['theme', 'audio', 'notifications', 'snooze', 'browser']
        for section in required_sections:
            self.assertIn(section, config_data)
        
        # Verificar configuración específica
        self.assertEqual(config_data['theme']['theme_style'], 'Light')
        self.assertEqual(config_data['audio']['alarm_volume'], 80)
        self.assertEqual(config_data['snooze']['default_interval'], 5)
    
    def test_set_and_get_config(self):
        """Prueba establecer y obtener configuraciones"""
        # Establecer valores
        result1 = self.config_manager.set('theme', 'theme_style', 'Dark')
        result2 = self.config_manager.set('audio', 'alarm_volume', 90)
        
        # Verificar que se establecieron correctamente
        self.assertTrue(result1)
        self.assertTrue(result2)
        
        # Obtener valores
        theme_style = self.config_manager.get('theme', 'theme_style')
        audio_volume = self.config_manager.get('audio', 'alarm_volume')
        
        # Verificar valores
        self.assertEqual(theme_style, 'Dark')
        self.assertEqual(audio_volume, 90)
    
    def test_get_nonexistent_config(self):
        """Prueba obtener configuración que no existe"""
        value = self.config_manager.get('nonexistent', 'key', 'default')
        self.assertEqual(value, 'default')
    
    def test_config_validation(self):
        """Prueba la validación de estructura de configuración"""
        # Configuración válida
        valid_config = {
            'theme': {'theme_style': 'Dark'},
            'audio': {'alarm_volume': 80},
            'notifications': {'enabled': True},
            'snooze': {'default_interval': 5},
            'browser': {'default_browser': 'brave'},
            'validation': {'prevent_duplicates': True},
            'ui': {'responsive': True}
        }
        
        result = self.config_manager._validate_config_structure(valid_config)
        self.assertTrue(result)
        
        # Configuración inválida (falta una sección)
        invalid_config = valid_config.copy()
        del invalid_config['theme']
        
        result = self.config_manager._validate_config_structure(invalid_config)
        self.assertFalse(result)
    
    def test_reset_to_default(self):
        """Prueba resetear configuración a valores por defecto"""
        # Cambiar algunos valores
        self.config_manager.set('theme', 'theme_style', 'Dark')
        self.config_manager.set('audio', 'alarm_volume', 100)
        
        # Resetear
        result = self.config_manager.reset_to_default()
        self.assertTrue(result)
        
        # Verificar que se resetearon
        theme_style = self.config_manager.get('theme', 'theme_style')
        audio_volume = self.config_manager.get('audio', 'alarm_volume')
        
        self.assertEqual(theme_style, 'Light')
        self.assertEqual(audio_volume, 80)

class TestAlarmManager(unittest.TestCase):
    """Pruebas para el gestor de alarmas"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = MagicMock()
        self.config_manager.get.return_value = True  # Configuración por defecto
        
        self.alarm_manager = AlarmManager(self.config_manager)
        self.alarm_manager.storage_dir = self.test_dir
        self.alarm_manager.alarms_file = os.path.join(self.test_dir, "test_alarms.json")
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_alarm_creation(self):
        """Prueba la creación de una alarma"""
        alarm_data = {
            'title': 'Test Alarm',
            'description': 'Alarma de prueba',
            'time': '12:00',
            'recurrence': 'daily',
            'volume': 80,
            'enabled': True
        }
        
        alarm_id = self.alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        self.assertEqual(len(self.alarm_manager.alarms), 1)
    
    def test_alarm_validation(self):
        """Prueba la validación de datos de alarma"""
        # Datos válidos
        valid_data = {
            'title': 'Test',
            'time': '12:00',
            'volume': 50,
            'snooze_interval': 5,
            'max_snoozes': 3
        }
        
        result = self.alarm_manager._validate_alarm_data(valid_data)
        self.assertTrue(result)
        
        # Datos inválidos - tiempo incorrecto
        invalid_data = {
            'title': 'Test',
            'time': '25:00',  # Hora inválida
            'volume': 50
        }
        
        result = self.alarm_manager._validate_alarm_data(invalid_data)
        self.assertFalse(result)
        
        # Datos inválidos - volumen fuera de rango
        invalid_data = {
            'title': 'Test',
            'time': '12:00',
            'volume': 150  # Fuera de rango 0-100
        }
        
        result = self.alarm_manager._validate_alarm_data(invalid_data)
        self.assertFalse(result)
    
    def test_duplicate_alarm_detection(self):
        """Prueba la detección de alarmas duplicadas"""
        # Configurar para prevenir duplicados
        self.config_manager.get.return_value = True
        
        # Crear primera alarma
        alarm_data = {
            'title': 'Test Alarm',
            'time': '12:00',
            'recurrence': 'daily'
        }
        
        self.alarm_manager.add_alarm(alarm_data)
        
        # Intentar crear alarma duplicada
        duplicate_data = {
            'title': 'Test Alarm',  # Mismo título
            'time': '12:00',        # Misma hora
            'recurrence': 'daily'   # Misma recurrencia
        }
        
        result = self.alarm_manager.add_alarm(duplicate_data)
        self.assertIsNone(result)  # Debe retornar None para duplicados
    
    def test_get_next_alarm(self):
        """Prueba obtener la próxima alarma"""
        # Crear alarma para el futuro
        future_alarm = Alarm()
        future_alarm.title = "Future Alarm"
        future_alarm.time = "23:59"
        future_alarm.enabled = True
        future_alarm.recurrence = "none"
        
        # Crear alarma para el pasado
        past_alarm = Alarm()
        past_alarm.title = "Past Alarm"
        past_alarm.time = "00:00"
        past_alarm.enabled = True
        past_alarm.recurrence = "none"
        
        self.alarm_manager.alarms = [past_alarm, future_alarm]
        
        # La próxima alarma debe ser la del futuro
        next_alarm = self.alarm_manager.get_next_alarm()
        self.assertEqual(next_alarm, future_alarm)
    
    def test_alarm_update(self):
        """Prueba actualizar una alarma existente"""
        # Crear alarma inicial
        alarm_data = {
            'title': 'Original Title',
            'time': '12:00',
            'description': 'Original description'
        }
        
        alarm_id = self.alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        
        # Actualizar alarma
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        result = self.alarm_manager.update_alarm(alarm_id, update_data)
        self.assertTrue(result)
        
        # Verificar actualización
        alarm = self.alarm_manager.get_alarm_by_id(alarm_id)
        self.assertEqual(alarm.title, 'Updated Title')
        self.assertEqual(alarm.description, 'Updated description')
        self.assertEqual(alarm.time, '12:00')  # Debe mantenerse
    
    def test_alarm_delete(self):
        """Prueba eliminar una alarma"""
        # Crear alarma
        alarm_data = {
            'title': 'Delete Test',
            'time': '12:00'
        }
        
        alarm_id = self.alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        
        # Verificar que existe
        self.assertEqual(len(self.alarm_manager.alarms), 1)
        
        # Eliminar
        result = self.alarm_manager.delete_alarm(alarm_id)
        self.assertTrue(result)
        
        # Verificar que se eliminó
        self.assertEqual(len(self.alarm_manager.alarms), 0)
        
        # Verificar que no se puede obtener
        alarm = self.alarm_manager.get_alarm_by_id(alarm_id)
        self.assertIsNone(alarm)

class TestAlarmClass(unittest.TestCase):
    """Pruebas para la clase Alarm individual"""
    
    def test_alarm_time_validation(self):
        """Prueba validación de formato de tiempo"""
        # Tiempo válido
        alarm = Alarm()
        alarm.time = "12:30"
        self.assertEqual(alarm.time, "12:30")
        
        # Tiempo inválido debe resetearse
        alarm.time = "25:00"
        self.assertEqual(alarm.time, "08:00")  # Valor por defecto
    
    def test_formatted_time(self):
        """Prueba obtener tiempo formateado"""
        alarm = Alarm()
        alarm.time = "12:30"
        
        formatted_time = alarm.get_formatted_time()
        self.assertEqual(formatted_time, "12:30")
    
    def test_daily_recurrence(self):
        """Prueba recurrencia diaria"""
        alarm = Alarm()
        alarm.time = "09:00"
        alarm.recurrence = "daily"
        alarm.enabled = True
        alarm.is_active = True
        
        next_trigger = alarm.get_next_trigger_time()
        
        # Debe ser para hoy o mañana
        self.assertIsNotNone(next_trigger)
        self.assertGreaterEqual(next_trigger, datetime.now())
        
        # Debe ser a las 09:00
        expected_hour = next_trigger.replace(hour=9, minute=0, second=0, microsecond=0)
        self.assertTrue(
            next_trigger.date() == expected_hour.date() or
            next_trigger.date() == (expected_hour + timedelta(days=1)).date()
        )
    
    def test_no_recurrence(self):
        """Prueba alarma sin recurrencia"""
        alarm = Alarm()
        alarm.time = "12:00"
        alarm.recurrence = "none"
        alarm.enabled = True
        alarm.is_active = True
        
        # Alarma para hoy
        next_trigger = alarm.get_next_trigger_time()
        now = datetime.now()
        
        if next_trigger > now:
            # Debe ser para hoy
            self.assertEqual(next_trigger.date(), now.date())
        else:
            # Debe ser None para alarmas del pasado
            self.assertIsNone(next_trigger)
    
    def test_snooze_functionality(self):
        """Prueba funcionalidad de snooze"""
        alarm = Alarm()
        alarm.max_snoozes = 3
        alarm.snooze_interval = 5
        
        # Snoozes válidos
        for i in range(alarm.max_snoozes):
            result = alarm.snooze()
            self.assertTrue(result)
            self.assertEqual(alarm.snooze_count, i + 1)
        
        # Snooze que excede el límite
        result = alarm.snooze()
        self.assertFalse(result)
        self.assertEqual(alarm.snooze_count, alarm.max_snoozes)
    
    def test_alarm_trigger(self):
        """Prueba activar una alarma"""
        alarm = Alarm()
        alarm.title = "Test Alarm"
        alarm.description = "Test Description"
        alarm.video_url = "https://example.com/video"
        
        trigger_info = alarm.trigger()
        
        # Verificar información del trigger
        self.assertEqual(trigger_info['id'], alarm.id)
        self.assertEqual(trigger_info['title'], alarm.title)
        self.assertEqual(trigger_info['description'], alarm.description)
        self.assertEqual(trigger_info['video_url'], alarm.video_url)
        self.assertIsNotNone(trigger_info['triggered_at'])
        
        # Verificar que se resetó el contador de snooze
        self.assertEqual(alarm.snooze_count, 0)
    
    def test_alarm_serialization(self):
        """Prueba serialización y deserialización de alarma"""
        # Crear alarma con datos
        original_alarm = Alarm()
        original_alarm.title = "Serialization Test"
        original_alarm.time = "14:30"
        original_alarm.recurrence = "weekly"
        original_alarm.volume = 75
        original_alarm.vibrate = True
        
        # Serializar
        alarm_dict = original_alarm.to_dict()
        
        # Deserializar
        restored_alarm = Alarm.from_dict(alarm_dict)
        
        # Verificar que los datos se mantuvieron
        self.assertEqual(restored_alarm.title, original_alarm.title)
        self.assertEqual(restored_alarm.time, original_alarm.time)
        self.assertEqual(restored_alarm.recurrence, original_alarm.recurrence)
        self.assertEqual(restored_alarm.volume, original_alarm.volume)
        self.assertEqual(restored_alarm.vibrate, original_alarm.vibrate)
        self.assertEqual(restored_alarm.id, original_alarm.id)

class TestBrowserIntegration(unittest.TestCase):
    """Pruebas para la integración con navegadores"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.config_manager = MagicMock()
        self.config_manager.get.return_value = 'brave'
        
        self.browser_integration = BrowserIntegration(self.config_manager)
    
    def test_url_validation(self):
        """Prueba validación de URLs"""
        # URLs válidas
        valid_urls = [
            'https://www.youtube.com/watch?v=abc123',
            'http://example.com',
            'brave://open?url=https://example.com'
        ]
        
        for url in valid_urls:
            result = self.browser_integration._is_valid_url(url)
            self.assertTrue(result, f"URL válida falló: {url}")
        
        # URLs inválidas
        invalid_urls = [
            'not_a_url',
            'ftp://',
            '://missing_protocol'
        ]
        
        for url in invalid_urls:
            result = self.browser_integration._is_valid_url(url)
            self.assertFalse(result, f"URL inválida pasó: {url}")
    
    def test_youtube_video_id_extraction(self):
        """Prueba extracción de ID de video de YouTube"""
        test_cases = [
            {
                'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'expected_id': 'dQw4w9WgXcQ'
            },
            {
                'url': 'https://youtu.be/dQw4w9WgXcQ',
                'expected_id': 'dQw4w9WgXcQ'
            },
            {
                'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s',
                'expected_id': 'dQw4w9WgXcQ'
            },
            {
                'url': 'https://youtube.com/watch?v=invalid',
                'expected_id': 'invalid'
            }
        ]
        
        for test_case in test_cases:
            video_id = self.browser_integration.extract_youtube_video_id(test_case['url'])
            self.assertEqual(video_id, test_case['expected_id'], 
                           f"Fallo en URL: {test_case['url']}")
    
    def test_browser_detection(self):
        """Prueba detección de navegadores"""
        # La detección varía según el sistema operativo
        # Solo verificamos que el método funciona sin errores
        
        try:
            browsers = self.browser_integration.browser_commands
            self.assertIsInstance(browsers, dict)
            
            # Verificar que hay al menos algunos navegadores detectados
            self.assertGreater(len(browsers), 0)
            
        except Exception as e:
            self.fail(f"Error en detección de navegadores: {e}")
    
    @patch('os.system')
    @patch('subprocess.run')
    def test_url_opening(self, mock_subprocess, mock_system):
        """Prueba apertura de URLs (mocked)"""
        # Configurar mocks para simular apertura exitosa
        mock_subprocess.return_value = MagicMock()
        mock_system.return_value = 0
        
        # En un entorno real, esto abriría un navegador
        # En testing, solo verificamos que no hay errores
        
        try:
            result = self.browser_integration.open_url('https://example.com')
            # El resultado puede ser True o False dependiendo del sistema
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"Error abriendo URL: {e}")

class TestAudioManager(unittest.TestCase):
    """Pruebas para el gestor de audio"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.config_manager = MagicMock()
        self.config_manager.get.return_value = 80
        
        self.audio_manager = AudioManager(self.config_manager)
        
        # Mock archivos de sonido
        self.test_sound_dir = tempfile.mkdtemp()
        self.test_sound_file = os.path.join(self.test_sound_dir, "test.mp3")
        
        # Crear archivo de sonido de prueba
        with open(self.test_sound_file, 'w') as f:
            f.write("test audio data")
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        shutil.rmtree(self.test_sound_dir, ignore_errors=True)
    
    def test_audio_support_detection(self):
        """Prueba detección de soporte de audio"""
        # Solo verificamos que el método funciona
        try:
            has_support = self.audio_manager._has_audio_support()
            self.assertIsInstance(has_support, bool)
        except Exception as e:
            self.fail(f"Error detectando soporte de audio: {e}")
    
    def test_volume_setting(self):
        """Prueba establecer volumen"""
        # Configurar volumen válido
        self.audio_manager.set_volume(75)
        self.assertEqual(self.audio_manager.current_volume, 75)
        
        # Configurar volumen fuera de rango
        self.audio_manager.set_volume(150)
        self.assertEqual(self.audio_manager.current_volume, 100)  # Debe limitarse a 100
        
        self.audio_manager.set_volume(-10)
        self.assertEqual(self.audio_manager.current_volume, 0)  # Debe limitarse a 0
    
    def test_sound_file_scanning(self):
        """Prueba escaneo de archivos de sonido"""
        # La funcionalidad depende de archivos reales en el directorio sounds/
        # Solo verificamos que el método funciona sin errores
        
        try:
            sound_files = self.audio_manager._scan_sound_files()
            self.assertIsInstance(sound_files, dict)
        except Exception as e:
            self.fail(f"Error escaneando archivos de sonido: {e}")
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_audio_playback_mocked(self, mock_exists, mock_subprocess):
        """Prueba reproducción de audio (mocked)"""
        # Configurar mocks
        mock_exists.return_value = True
        mock_subprocess.return_value = MagicMock()
        
        # En un entorno real, esto reproduciría audio
        # En testing, solo verificamos que no hay errores
        
        try:
            # Esto debería funcionar sin errores aunque no reproduzca audio real
            result = self.audio_manager._play_sound_file('/fake/path/test.mp3', 80)
            # El resultado puede variar según la plataforma
        except Exception as e:
            # Es normal que falle en un entorno de testing sin dependencias reales
            self.assertIn("No such file or directory", str(e) or "not found", str(e))

class TestResponsiveManager(unittest.TestCase):
    """Pruebas para el gestor responsive"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.responsive_manager = ResponsiveManager()
    
    def test_screen_categorization(self):
        """Prueba categorización de tamaños de pantalla"""
        test_cases = [
            {'width': 320, 'height': 568, 'expected': 'small'},  # iPhone SE
            {'width': 375, 'height': 812, 'expected': 'medium'},  # iPhone 11
            {'width': 414, 'height': 896, 'expected': 'large'},   # iPhone 11 Pro Max
            {'width': 768, 'height': 1024, 'expected': 'xlarge'}  # iPad
        ]
        
        for test_case in test_cases:
            category = self.responsive_manager._categorize_screen_size(
                test_case['width'], test_case['height']
            )
            self.assertEqual(category, test_case['expected'])
    
    def test_responsive_values(self):
        """Prueba cálculo de valores responsive"""
        # Solo verificamos que los métodos devuelven valores válidos
        
        try:
            # Testear cálculo de layout sizes
            layout_sizes = self.responsive_manager.layout_sizes
            self.assertIsInstance(layout_sizes, dict)
            self.assertGreater(len(layout_sizes), 0)
            
            # Testear cálculo de font sizes
            font_sizes = self.responsive_manager.font_sizes
            self.assertIsInstance(font_sizes, dict)
            self.assertGreater(len(font_sizes), 0)
            
            # Testear cálculo de spacing
            spacing = self.responsive_manager.spacing_values
            self.assertIsInstance(spacing, dict)
            self.assertGreater(len(spacing), 0)
            
        except Exception as e:
            self.fail(f"Error calculando valores responsive: {e}")
    
    def test_responsive_padding(self):
        """Prueba cálculo de padding responsive"""
        try:
            padding = self.responsive_manager.get_responsive_padding(16)
            self.assertIsInstance(padding, tuple)
            self.assertEqual(len(padding), 2)
            
            # Verificar que son números
            h_padding, v_padding = padding
            self.assertIsInstance(h_padding, (int, float))
            self.assertIsInstance(v_padding, (int, float))
            
        except Exception as e:
            self.fail(f"Error calculando padding responsive: {e}")
    
    def test_layout_detection(self):
        """Prueba detección de layout"""
        try:
            # Verificar detección de vista compacta
            is_compact = self.responsive_manager.should_show_compact_view()
            self.assertIsInstance(is_compact, bool)
            
            # Verificar detección de tablet
            is_tablet = self.responsive_manager.is_tablet_layout()
            self.assertIsInstance(is_tablet, bool)
            
            # Verificar número de columnas
            columns = self.responsive_manager.get_grid_columns()
            self.assertIn(columns, [1, 2])
            
        except Exception as e:
            self.fail(f"Error detectando layout: {e}")

class TestIntegration(unittest.TestCase):
    """Pruebas de integración entre componentes"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.test_dir
        self.config_manager.config_path = os.path.join(self.test_dir, "test_config.json")
        
        self.alarm_manager = AlarmManager(self.config_manager)
        self.browser_integration = BrowserIntegration(self.config_manager)
        self.audio_manager = AudioManager(self.config_manager)
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_alarm_creation_and_storage(self):
        """Prueba crear alarma y verificar persistencia"""
        # Crear alarma
        alarm_data = {
            'title': 'Integration Test',
            'time': '15:30',
            'recurrence': 'daily',
            'video_url': 'https://www.youtube.com/watch?v=test',
            'volume': 85
        }
        
        # Agregar alarma
        alarm_id = self.alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        
        # Guardar alarmas
        self.alarm_manager.save_alarms()
        
        # Verificar que se guardó el archivo
        self.assertTrue(os.path.exists(self.alarm_manager.alarms_file))
        
        # Limpiar alarmas en memoria
        self.alarm_manager.alarms = []
        
        # Cargar alarmas desde archivo
        self.alarm_manager.load_alarms()
        
        # Verificar que se cargó la alarma
        self.assertEqual(len(self.alarm_manager.alarms), 1)
        
        loaded_alarm = self.alarm_manager.alarms[0]
        self.assertEqual(loaded_alarm.title, alarm_data['title'])
        self.assertEqual(loaded_alarm.time, alarm_data['time'])
        self.assertEqual(loaded_alarm.video_url, alarm_data['video_url'])
    
    def test_configuration_across_modules(self):
        """Prueba que la configuración se comparte entre módulos"""
        # Establecer configuración
        self.config_manager.set('theme', 'theme_style', 'Dark')
        self.config_manager.set('audio', 'alarm_volume', 90)
        self.config_manager.set('browser', 'default_browser', 'chrome')
        
        # Verificar que los módulos usan la misma configuración
        audio_volume = self.audio_manager.config_manager.get('audio', 'alarm_volume')
        browser_pref = self.browser_integration.config_manager.get('browser', 'default_browser')
        
        self.assertEqual(audio_volume, 90)
        self.assertEqual(browser_pref, 'chrome')
    
    def test_alarm_with_browser_integration(self):
        """Prueba integración de alarma con navegador"""
        # Crear alarma con URL de video
        alarm_data = {
            'title': 'YouTube Alarm',
            'time': '16:00',
            'recurrence': 'none',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'browser_preference': 'brave'
        }
        
        alarm_id = self.alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        
        # Verificar extracción de ID de video
        video_url = alarm_data['video_url']
        video_id = self.browser_integration.extract_youtube_video_id(video_url)
        self.assertEqual(video_id, 'dQw4w9WgXcQ')
        
        # Simular activación de alarma
        alarm = self.alarm_manager.get_alarm_by_id(alarm_id)
        trigger_info = alarm.trigger()
        
        # Verificar que la información incluye URL y preferencia de navegador
        self.assertEqual(trigger_info['video_url'], video_url)
        self.assertEqual(trigger_info['browser_preference'], 'brave')
    
    @patch('subprocess.run')
    def test_alarm_trigger_with_audio_and_browser(self, mock_subprocess):
        """Prueba activación completa de alarma con audio y navegador"""
        # Configurar mocks
        mock_subprocess.return_value = MagicMock()
        
        # Configurar callback de audio
        audio_played = []
        
        def mock_audio_callback(trigger_info):
            audio_played.append(trigger_info)
        
        self.audio_manager.play_alarm_sound = MagicMock(return_value=True)
        self.alarm_manager.set_audio_callback(mock_audio_callback)
        
        # Crear alarma con URL de video
        alarm_data = {
            'title': 'Complete Test',
            'time': '17:00',
            'recurrence': 'none',
            'video_url': 'https://www.youtube.com/watch?v=complete',
            'volume': 80
        }
        
        alarm_id = self.alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        
        # Simular verificación de alarmas pendientes
        # (En un entorno real, esto sería llamado por el thread de verificación)
        current_time = datetime.now() + timedelta(minutes=1)  # Tiempo futuro
        
        # Verificar si la alarma debe activarse
        alarm = self.alarm_manager.get_alarm_by_id(alarm_id)
        
        # Activar manualmente para testing
        trigger_info = alarm.trigger()
        
        # Verificar información del trigger
        self.assertEqual(trigger_info['title'], alarm_data['title'])
        self.assertEqual(trigger_info['video_url'], alarm_data['video_url'])
        self.assertEqual(trigger_info['volume'], alarm_data['volume'])

class TestPerformance(unittest.TestCase):
    """Pruebas de rendimiento y carga"""
    
    def test_alarm_manager_performance(self):
        """Prueba rendimiento del gestor de alarmas con muchas alarmas"""
        config_manager = MagicMock()
        config_manager.get.return_value = True
        
        alarm_manager = AlarmManager(config_manager)
        
        # Crear 100 alarmas
        num_alarms = 100
        alarm_ids = []
        
        start_time = datetime.now()
        
        for i in range(num_alarms):
            alarm_data = {
                'title': f'Alarm {i}',
                'time': f'{8 + i % 12:02d}:{i % 60:02d}',
                'recurrence': 'daily' if i % 2 == 0 else 'none'
            }
            
            alarm_id = alarm_manager.add_alarm(alarm_data)
            if alarm_id:
                alarm_ids.append(alarm_id)
        
        end_time = datetime.now()
        creation_time = (end_time - start_time).total_seconds()
        
        # La creación no debe tomar más de 5 segundos
        self.assertLess(creation_time, 5.0)
        
        # Verificar que se crearon las alarmas
        self.assertGreater(len(alarm_ids), 0)
        
        # Testear búsqueda de próxima alarma
        start_time = datetime.now()
        next_alarm = alarm_manager.get_next_alarm()
        end_time = datetime.now()
        
        search_time = (end_time - start_time).total_seconds()
        
        # La búsqueda no debe tomar más de 1 segundo
        self.assertLess(search_time, 1.0)
        
        # Verificar que se encontró una alarma
        self.assertIsNotNone(next_alarm)
    
    def test_config_manager_performance(self):
        """Prueba rendimiento del gestor de configuraciones"""
        config_manager = ConfigManager()
        
        # Crear muchas configuraciones
        num_configs = 1000
        
        start_time = datetime.now()
        
        for i in range(num_configs):
            config_manager.set(f'section_{i}', f'key_{i}', f'value_{i}')
        
        end_time = datetime.now()
        setting_time = (end_time - start_time).total_seconds()
        
        # La configuración no debe tomar más de 3 segundos
        self.assertLess(setting_time, 3.0)
        
        # Testear lectura de configuraciones
        start_time = datetime.now()
        
        for i in range(num_configs):
            value = config_manager.get(f'section_{i}', f'key_{i}')
            self.assertEqual(value, f'value_{i}')
        
        end_time = datetime.now()
        reading_time = (end_time - start_time).total_seconds()
        
        # La lectura no debe tomar más de 2 segundos
        self.assertLess(reading_time, 2.0)

class TestEdgeCases(unittest.TestCase):
    """Pruebas de casos extremos y situaciones inusuales"""
    
    def test_empty_alarm_data(self):
        """Prueba crear alarma con datos mínimos"""
        config_manager = MagicMock()
        config_manager.get.return_value = True
        
        alarm_manager = AlarmManager(config_manager)
        
        # Datos mínimos
        alarm_data = {
            'title': '',  # Título vacío
            'time': '00:00'  # Hora válida mínima
        }
        
        alarm_id = alarm_manager.add_alarm(alarm_data)
        self.assertIsNotNone(alarm_id)
        
        alarm = alarm_manager.get_alarm_by_id(alarm_id)
        self.assertIsNotNone(alarm)
        self.assertEqual(alarm.time, '00:00')
    
    def test_invalid_time_formats(self):
        """Prueba diferentes formatos de tiempo inválidos"""
        config_manager = MagicMock()
        config_manager.get.return_value = True
        
        alarm_manager = AlarmManager(config_manager)
        
        invalid_times = [
            '25:00',  # Hora inválida
            '12:60',  # Minuto inválido
            'abc:def',  # Formato inválido
            '12',  # Sin minutos
            '12:',  # Sin segundos
            ':30'  # Sin hora
        ]
        
        for invalid_time in invalid_times:
            alarm_data = {
                'title': 'Test',
                'time': invalid_time
            }
            
            alarm_id = alarm_manager.add_alarm(alarm_data)
            # Debe manejar el tiempo inválido (convertir a valor por defecto o rechazar)
            if alarm_id:
                alarm = alarm_manager.get_alarm_by_id(alarm_id)
                # Si se creó, debe tener un tiempo válido
                self.assertNotEqual(alarm.time, invalid_time)
    
    def test_malformed_config_data(self):
        """Prueba configuración con datos malformados"""
        config_manager = ConfigManager()
        
        # Configuración con tipos incorrectos
        malformed_configs = [
            {'theme': {'theme_style': None}},  # Valor None
            {'audio': {'alarm_volume': 'invalid'}},  # String en lugar de int
            {'snooze': {'max_snoozes': -5}},  # Valor negativo
            {'browser': {'default_browser': 123}}  # Número en lugar de string
        ]
        
        for malformed_config in malformed_configs:
            # Debe manejar graciosamente la configuración malformada
            try:
                config_manager.set_section('test', malformed_config)
                # Si no lanza excepción, debe tener valores válidos
                test_section = config_manager.get_section('test')
                self.assertIsInstance(test_section, dict)
            except Exception:
                # Está bien que lance excepción por datos malformados
                pass
    
    def test_large_configuration_values(self):
        """Prueba con valores de configuración muy grandes"""
        config_manager = ConfigManager()
        
        # Valores muy grandes
        large_configs = {
            'audio': {
                'alarm_volume': 9999,  # Fuera del rango 0-100
                'custom_sounds': {f'sound_{i}': f'path_{i}' * 100 for i in range(1000)}
            },
            'validation': {
                'max_alarms': 999999
            }
        }
        
        # Debe manejar graciosamente valores grandes
        try:
            for section, data in large_configs.items():
                for key, value in data.items():
                    config_manager.set(section, key, value)
            
            # Verificar que los valores se almacenaron
            stored_volume = config_manager.get('audio', 'alarm_volume')
            self.assertEqual(stored_volume, 9999)
            
        except Exception as e:
            # Es aceptable que falle con valores extremos
            self.assertIn('memory', str(e).lower() or 'size', str(e).lower())

def run_all_tests():
    """Ejecuta todas las pruebas y genera un reporte"""
    # Configurar test suite
    test_classes = [
        TestConfigManager,
        TestAlarmManager,
        TestAlarmClass,
        TestBrowserIntegration,
        TestAudioManager,
        TestResponsiveManager,
        TestIntegration,
        TestPerformance,
        TestEdgeCases
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Añadir todas las pruebas
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar pruebas con reporte detallado
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("=" * 70)
    print("🧪 INICIANDO SUITE DE TESTING - APLICACIÓN DE ALARMAS INTELIGENTE")
    print("=" * 70)
    
    start_time = datetime.now()
    result = runner.run(suite)
    end_time = datetime.now()
    
    # Reporte final
    print("\n" + "=" * 70)
    print("📊 REPORTE FINAL DE TESTING")
    print("=" * 70)
    
    total_time = (end_time - start_time).total_seconds()
    print(f"⏱️  Tiempo total de ejecución: {total_time:.2f} segundos")
    print(f"✅ Pruebas ejecutadas: {result.testsRun}")
    print(f"❌ Pruebas fallidas: {len(result.failures)}")
    print(f"⚠️  Pruebas con errores: {len(result.errors)}")
    
    if result.failures:
        print(f"\n🔴 PRUEBAS FALLIDAS ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Error desconocido'}")
    
    if result.errors:
        print(f"\n🟡 ERRORES ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.splitlines()[-1]}")
    
    # Estadísticas de cobertura
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 ¡EXCELENTE! La aplicación pasa la mayoría de las pruebas")
    elif success_rate >= 80:
        print("👍 BIEN: La aplicación funciona correctamente con algunas limitaciones")
    elif success_rate >= 60:
        print("⚠️  REGULAR: La aplicación necesita mejoras antes de producción")
    else:
        print("🚨 CRÍTICO: La aplicación tiene problemas significativos")
    
    print("\n💡 Recomendaciones:")
    if result.failures:
        print("   • Revisar y corregir pruebas fallidas")
    if result.errors:
        print("   • Investigar errores de implementación")
    if success_rate < 95:
        print("   • Añadir pruebas para casos no cubiertos")
    
    print("\n" + "=" * 70)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Ejecutar tests si se llama directamente
    success = run_all_tests()
    sys.exit(0 if success else 1)