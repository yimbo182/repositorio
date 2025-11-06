# Aplicación de Alarmas Inteligente

## 📱 Sistema de Alarms Multiplataforma con Python y Kivy

Una aplicación móvil avanzada de sistema de alarmas inteligente desarrollada con Python y el framework Kivy, diseñada para funcionar como un sistema completo de gestión de alarmas con integración de navegadores, reproducción de audio y configuración persistente.

## 🚀 Características Principales

### ✨ Funcionalidades Core
- **Sistema de Alarmas Inteligente**: Gestión completa de múltiples alarmas con opciones de recurrencia
- **Interfaz Intuitiva**: Diseño moderno y responsive con Material Design
- **Recurrencia Flexible**: Diaria, semanal y personalizada con expresiones cron
- **Integración con Navegadores**: Deep linking automático con Brave Browser y YouTube
- **Audio Avanzado**: Reproducción de sonidos personalizables y música de fondo
- **Configuración Persistente**: Sistema de almacenamiento seguro con cifrado
- **Temas Personalizados**: Modo claro/oscuro con paleta de colores adaptativa
- **Snooze Inteligente**: Intervalos configurables con límite personalizable
- **Validación Avanzada**: Prevención de duplicados y configuración de límites

### 🔧 Características Técnicas
- **Multiplataforma**: Android, iOS, Windows, macOS y Linux
- **Arquitectura Modular**: Código organizado en módulos especializados
- **Sistema de Configuración**: Gestión avanzada con cifrado de datos sensibles
- **Responsive Design**: Adaptación automática a diferentes tamaños de pantalla
- **Gestión de Permisos**: Solicitud automática de permisos necesarios
- **Logging Completo**: Sistema de registro detallado para debugging
- **Audio Background**: Reproducción continua incluso en segundo plano

## 📋 Requisitos del Sistema

### Desarrollo
- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB)
- **Espacio en Disco**: 2GB libres para dependencias
- **Python Package Manager**: pip

### Compilación Android
- **Java Development Kit**: JDK 11 o superior
- **Android SDK**: API Level 21+ (Android 5.0)
- **Android NDK**: Versión compatible con Python-for-Android
- **Build Tools**: Gradle y Android Build Tools
- **Sistema de Compilación**: Buildozer

### Compilación iOS
- **macOS**: 10.15 (Catalina) o superior
- **Xcode**: 12.0 o superior
- **iOS SDK**: iOS 11.0 o superior
- **Apple Developer Account**: Para distribución
- **CocoaPods**: Para gestión de dependencias iOS

## 🛠️ Instalación y Configuración

### 1. Instalación de Dependencias Python

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Verificación de Instalación

```bash
# Verificar instalación de Kivy
python -c "import kivy; print('Kivy version:', kivy.__version__)"

# Verificar instalación de KivyMD
python -c "from kivymd import __version__; print('KivyMD version:', __version__)"

# Verificar plyer para funcionalidades nativas
python -c "import plyer; print('Plyer version:', plyer.__version__)"
```

### 3. Configuración Inicial

```bash
# Ejecutar la aplicación en modo desarrollo
python main.py

# La aplicación creará automáticamente:
# - Directorio 'config/' con configuraciones encriptadas
# - Directorio 'data/' para almacenamiento de alarmas
# - Directorio 'sounds/' para archivos de audio
# - Archivo 'alarm_system.log' para logging
```

## 🏗️ Estructura del Proyecto

```
alarmas-inteligente/
├── main.py                      # Punto de entrada principal
├── requirements.txt             # Dependencias Python
├── buildozer.spec              # Configuración para compilación móvil
├── config_manager.py           # Gestión de configuraciones persistentes
├── alarm_manager.py            # Sistema de gestión de alarmas
├── browser_integration.py      # Integración con navegadores y audio
├── responsive_manager.py       # Gestión responsive para diferentes pantallas
├── config/                     # Configuraciones encriptadas
│   ├── alarm_config.json      # Configuraciones principales
│   └── .config_key            # Clave de cifrado
├── data/                       # Datos de la aplicación
│   └── alarms.json            # Alarmas guardadas
├── sounds/                     # Archivos de audio
│   ├── default_alarm.mp3      # Sonido por defecto
│   ├── gentle_chime.wav       # Sonido suave
│   ├── energetic_beep.mp3     # Sonido energético
│   └── nature_sounds.ogg      # Sonidos de naturaleza
├── docs/                       # Documentación
│   ├── API_REFERENCE.md       # Referencia de la API
│   ├── DEPLOYMENT.md          # Guía de despliegue
│   └── TROUBLESHOOTING.md     # Solución de problemas
└── tests/                      # Pruebas unitarias
    ├── test_config_manager.py # Pruebas de configuración
    ├── test_alarm_manager.py  # Pruebas de alarmas
    └── test_integration.py    # Pruebas de integración
```

## 🎨 Arquitectura del Sistema

### Componentes Principales

#### 1. **AlarmApp** (main.py)
- **Responsabilidad**: Inicialización y gestión principal de la aplicación
- **Funciones**: 
  - Configuración inicial de Kivy/KivyMD
  - Gestión del ScreenManager
  - Solicitud de permisos del sistema
  - Manejo de eventos de aplicación

#### 2. **ConfigManager** (config_manager.py)
- **Responsabilidad**: Gestión de configuraciones persistentes
- **Funciones**:
  - Almacenamiento cifrado de configuraciones
  - Gestión de temas y preferencias
  - Importación/exportación de configuraciones
  - Sistema de backup automático

#### 3. **AlarmManager** (alarm_manager.py)
- **Responsabilidad**: Sistema central de gestión de alarmas
- **Funciones**:
  - Creación y gestión de objetos Alarm
  - Sistema de verificación temporal
  - Manejo de recurrencias (diaria, semanal, personalizada)
  - Validación y prevención de duplicados
  - Integración con notificaciones del sistema

#### 4. **BrowserIntegration** (browser_integration.py)
- **Responsabilidad**: Integración con navegadores y deep linking
- **Funciones**:
  - Detección automática de navegadores disponibles
  - Apertura de URLs en navegadores específicos
  - Extracción de IDs de videos de YouTube
  - Soporte para deep linking de Brave Browser
  - Gestión de protocolos personalizados

#### 5. **AudioManager** (browser_integration.py)
- **Responsabilidad**: Gestión de audio y reproducción
- **Funciones**:
  - Reproducción de sonidos de alarma
  - Gestión de música de fondo
  - Control de volumen adaptativo
  - Soporte multiplataforma para audio
  - Reproducción en segundo plano

#### 6. **ResponsiveManager** (responsive_manager.py)
- **Responsabilidad**: Adaptación responsive de la interfaz
- **Funciones**:
  - Detección de tamaño y densidad de pantalla
  - Ajuste automático de tamaños de widget
  - Adaptación de fuentes y espaciado
  - Optimización para tablets vs móviles

### Flujo de Datos

```
Usuario Interacción
        ↓
    AlarmApp (UI Principal)
        ↓
    ScreenManager (Gestión de Pantallas)
        ↓
┌─────────────┬─────────────┬─────────────┐
│ ConfigScreen│ AlarmScreen │  MainScreen │
└─────────────┴─────────────┴─────────────┘
        ↓            ↓            ↓
┌─────────────┬─────────────┬─────────────┐
│ConfigManager│AlarmManager │ Responsive  │
└─────────────┴─────────────┴─────────────┘
        ↓            ↓            ↓
┌─────────────┬─────────────┬─────────────┐
│BrowserInteg │ AudioManager│ Window Sizing│
└─────────────┴─────────────┴─────────────┘
```

## 🎯 Configuración Detallada

### Sistema de Configuraciones

El sistema utiliza un enfoque jerárquico con cifrado para configuraciones sensibles:

#### Configuraciones Principales

```json
{
  "theme": {
    "theme_style": "Light",
    "primary_color": "Blue",
    "accent_color": "Amber",
    "custom_colors": {}
  },
  "audio": {
    "alarm_volume": 80,
    "snooze_volume": 60,
    "background_play": true,
    "alarm_sound": "default",
    "custom_sounds": {}
  },
  "notifications": {
    "enabled": true,
    "vibrate": true,
    "sound": true,
    "preview_text": true,
    "priority": "normal"
  },
  "snooze": {
    "default_interval": 5,
    "max_snoozes": 3,
    "progressive_volume": true
  },
  "browser": {
    "default_browser": "brave",
    "auto_open": true,
    "open_fullscreen": false,
    "custom_protocols": {}
  },
  "validation": {
    "prevent_duplicates": true,
    "max_alarms": 50,
    "min_interval": 1,
    "max_interval": 1440
  }
}
```

### Configuración de Audio

#### Archivos de Sonido Soportados
- **Formatos**: MP3, WAV, OGG, M4A
- **Ubicación**: Directorio `sounds/`
- **Nomenclatura**: `nombre_sonido.extension`
- **Reproducción**: Automática según configuración de alarma

#### Configuración de Volumen
- **Rango**: 0-100%
- **Por Alarma**: Configuración individual de volumen
- **Progresivo**: Incremento gradual en snoozes múltiples
- **Sistema**: Ajuste del volumen del sistema

### Configuración de Navegadores

#### Soporte Multiplataforma
- **Android**: Brave Browser, Chrome, Firefox
- **Windows**: Brave Browser, Chrome, Edge
- **macOS**: Brave Browser, Chrome, Safari
- **Linux**: Brave Browser, Chrome, Firefox

#### Deep Linking
```python
# URLs de YouTube con reproducción automática
https://www.youtube.com/watch?v=VIDEO_ID&autoplay=1

# Deep linking específico para Brave
brave://open?url=https://www.youtube.com/watch?v=VIDEO_ID

# Protocolos personalizados
custom://action?param=value
```

## 🔧 API y Uso Programático

### Gestión de Configuraciones

```python
from config_manager import ConfigManager

# Inicializar gestor
config = ConfigManager()

# Obtener configuración
theme_style = config.get('theme', 'theme_style', 'Light')

# Establecer configuración
config.set('audio', 'alarm_volume', 90)

# Exportar configuración
config.export_config('backup_config.json', encrypt=True)

# Importar configuración
config.import_config('backup_config.json', decrypt=True)
```

### Gestión de Alarmas

```python
from alarm_manager import AlarmManager, Alarm

# Inicializar gestor
alarm_manager = AlarmManager(config_manager)

# Crear nueva alarma
alarm_data = {
    'title': 'Gimnasio Matutino',
    'description': 'Hora del entrenamiento',
    'time': '06:00',
    'recurrence': 'daily',
    'video_url': 'https://www.youtube.com/watch?v=example',
    'volume': 85,
    'snooze_interval': 10
}

alarm_id = alarm_manager.add_alarm(alarm_data)

# Obtener alarmas activas
active_alarms = alarm_manager.get_active_alarms()

# Obtener próxima alarma
next_alarm = alarm_manager.get_next_alarm()

# Actualizar alarma
alarm_manager.update_alarm(alarm_id, {'title': 'Nuevo Título'})

# Eliminar alarma
alarm_manager.delete_alarm(alarm_id)
```

### Integración con Navegadores

```python
from browser_integration import BrowserIntegration

# Inicializar integración
browser_integration = BrowserIntegration(config_manager)

# Abrir URL específica
browser_integration.open_url(
    'https://www.youtube.com/watch?v=example',
    browser='brave',
    fullscreen=True
)

# Abrir video de YouTube
browser_integration.open_youtube_video(
    'dQw4w9WgXcQ',
    browser='brave',
    autoplay=True
)

# Extraer ID de video
video_id = browser_integration.extract_youtube_video_id(
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
)
```

### Gestión de Audio

```python
from browser_integration import AudioManager

# Inicializar gestor de audio
audio_manager = AudioManager(config_manager)

# Reproducir sonido de alarma
audio_manager.play_alarm_sound('gentle', volume=90)

# Reproducir música de fondo
audio_manager.play_background_music(
    'https://example.com/background-music.mp3',
    volume=30
)

# Detener audio
audio_manager.stop_audio()

# Establecer volumen
audio_manager.set_volume(75)
```

## 📱 Interfaz de Usuario

### Pantallas Principales

#### 1. **MainScreen** (Pantalla Principal)
- **Funciones**: Vista general de alarmas activas y estadísticas
- **Elementos**: 
  - Toolbar con navegación
  - Tarjeta de estadísticas (próxima alarma, total, estado)
  - Lista de alarmas activas
  - Botón de acción rápida

#### 2. **AlarmScreen** (Gestión de Alarmas)
- **Funciones**: Crear, editar y eliminar alarmas
- **Elementos**:
  - Lista completa de alarmas
  - Formularios de creación/edición
  - Validación en tiempo real
  - Opciones de recurrencia

#### 3. **ConfigScreen** (Configuración)
- **Funciones**: Configuración global de la aplicación
- **Elementos**:
  - Configuración de tema
  - Configuración de audio
  - Configuración de snooze
  - Configuración de notificaciones

### Componentes Adaptativos

#### Responsive Design
- **Pantallas Pequeñas**: Vista compacta con elementos esenciales
- **Tablets**: Layout en dos columnas con navegación lateral
- **Orientación**: Adaptación automática retrato/paisaje
- **Densidad**: Ajuste según DPI de la pantalla

#### Temas Personalizables
- **Modo Claro**: Colores claros con alto contraste
- **Modo Oscuro**: Colores oscuros para uso nocturno
- **Paletas**: Azul, Púrpura, Verde, Naranja
- **Personalización**: Colores completamente personalizables

## 🧪 Testing y Validación

### Pruebas Unitarias

#### ConfigManager Tests
```python
def test_config_save_load():
    config = ConfigManager()
    config.set('test', 'value', 'test_data')
    assert config.get('test', 'value') == 'test_data'

def test_encryption():
    config = ConfigManager()
    # Verificar cifrado de datos sensibles
```

#### AlarmManager Tests
```python
def test_alarm_creation():
    alarm_data = {
        'title': 'Test Alarm',
        'time': '12:00',
        'recurrence': 'daily'
    }
    alarm_id = alarm_manager.add_alarm(alarm_data)
    assert alarm_id is not None

def test_recurrence_calculation():
    # Verificar cálculo de próximas activaciones
```

### Pruebas de Integración

#### Navegador Integration Tests
```python
def test_brave_opening():
    # Verificar apertura de Brave Browser
    result = browser_integration.open_url('https://example.com', 'brave')
    assert result == True

def test_youtube_video():
    # Verificar extracción de ID de video
    video_id = browser_integration.extract_youtube_video_id(
        'https://www.youtube.com/watch?v=test123'
    )
    assert video_id == 'test123'
```

#### Audio Tests
```python
def test_audio_playback():
    # Verificar reproducción de audio
    result = audio_manager.play_alarm_sound('test')
    # Resultado depende de la plataforma

def test_volume_control():
    # Verificar control de volumen
    audio_manager.set_volume(50)
    assert audio_manager.current_volume == 50
```

### Pruebas de UI

#### Responsive Tests
```python
def test_mobile_layout():
    # Simular pantalla móvil
    assert responsive_manager.should_show_compact_view() == True

def test_tablet_layout():
    # Simular pantalla de tablet
    assert responsive_manager.is_tablet_layout() == True
```

## 🔍 Logging y Debugging

### Sistema de Logging

La aplicación implementa un sistema completo de logging:

```python
import logging

# Configuración en main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alarm_system.log'),
        logging.StreamHandler()
    ]
)
```

#### Niveles de Log
- **ERROR**: Errores críticos del sistema
- **WARNING**: Advertencias y estados inesperados
- **INFO**: Información general de funcionamiento
- **DEBUG**: Información detallada para desarrollo

#### Archivos de Log
- **alarm_system.log**: Log principal de la aplicación
- **Configuraciones**: Operaciones de configuración
- **Alarmas**: Activaciones y cambios de alarmas
- **Navegadores**: Operaciones de integración con navegadores

### Debugging

#### Herramientas de Debug
```bash
# Habilitar logging de debug
export KIVY_LOG_LEVEL=debug
python main.py

# Verificar permisos en Android
adb logcat | grep -i "alarm"

# Monitorear notificaciones
adb logcat | grep -i "notification"
```

#### Problemas Comunes
1. **Audio no funciona**: Verificar permisos de audio del sistema
2. **Notificaciones no aparecen**: Verificar configuración de notificaciones
3. **Navegador no abre**: Verificar instalación del navegador preferido
4. **Alarmas no suenan**: Verificar configuración de volumen del sistema

## 📦 Distribución y Deployment

### Preparación para Producción

#### Configuración de Release
```python
# En main.py, cambiar para producción
if __name__ == '__main__':
    # Configurar para producción
    from kivy.config import Config
    Config.set('graphics', 'debug', False)
    Config.set('kivy', 'log_level', 'error')
    
    AlarmApp().run()
```

#### Optimización de Assets
```bash
# Comprimir imágenes
find . -name "*.png" -exec optipng {} \\;

# Optimizar audio
find . -name "*.mp3" -exec mp3gain {} \\;

# Minificar archivos de configuración
```

## 🛡️ Seguridad

### Cifrado de Datos
- **Configuraciones**: Cifrado con Fernet (AES 128)
- **Clave de Cifrado**: Almacenada localmente con permisos restringidos
- **Alarmas**: Datos serializados sin información sensible

### Permisos del Sistema
- **Android**: 
  - `WAKE_LOCK`: Mantener dispositivo despierto para alarmas
  - `RECEIVE_BOOT_COMPLETED`: Reiniciar alarmas después del reinicio
  - `FOREGROUND_SERVICE`: Servicio de audio en segundo plano
  - `SET_ALARM`: Crear alarmas del sistema Android

- **iOS**:
  - `NSLocalNetworkUsageDescription`: Para comunicación con navegadores
  - `NSUserNotificationAlertStyle`: Para notificaciones enriquecidas

### Validación de Entrada
- **URLs**: Validación completa de formato y protocolo
- **Timestamps**: Validación de formato y rangos válidos
- **Configuraciones**: Validación de rangos y tipos de datos
- **Archivos**: Validación de existencia y permisos

## 🔄 Actualizaciones y Mantenimiento

### Sistema de Backup
```python
# Backup automático de configuraciones
config_manager.backup_config()

# Limpieza de backups antiguos
config_manager.cleanup_old_backups(keep_count=5)

# Exportación para migración
config_manager.export_config('migration_backup.json', encrypt=True)
```

### Actualización de Dependencias
```bash
# Verificar dependencias desactualizadas
pip list --outdated

# Actualizar dependencias principales
pip install --upgrade kivy kivymd plyer

# Verificar compatibilidad
python -m pytest tests/
```

### Monitoreo de Rendimiento
- **Memoria**: Uso de memoria por módulo
- **CPU**: Carga durante verificaciones de alarmas
- **Batería**: Impacto en dispositivos móviles
- **Almacenamiento**: Crecimiento de archivos de datos

## 📞 Soporte y Contacto

### Documentación Adicional
- **API Reference**: `docs/API_REFERENCE.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

### Problemas Conocidos
1. **Audio en iOS**: Limitaciones del sandbox de iOS
2. **Notificaciones en Android 13+**: Cambios en permisos de notificaciones
3. **Brave Browser**: Compatibilidad específica por versión

### Roadmap Futuro
- [ ] Integración con calendarios
- [ ] Alertas de clima
- [ ] Compartir alarmas entre dispositivos
- [ ] Integración con asistentes de voz
- [ ] Modo offline para contenido local

---

**Versión**: 1.0.0  
**Última Actualización**: Noviembre 2025  
**Autor**: Sistema de Desarrollo Automatizado  
**Licencia**: MIT License