"""
Módulo de integración con navegadores y deep linking
Gestiona la apertura automática de navegadores y videos de YouTube
"""

import os
import logging
import webbrowser
import subprocess
import platform
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import json

logger = logging.getLogger(__name__)

class BrowserIntegration:
    """
    Gestor de integración con navegadores y deep linking
    """
    
    def __init__(self, config_manager):
        """
        Inicializa la integración con navegadores
        
        Args:
            config_manager: Instancia del gestor de configuraciones
        """
        self.config_manager = config_manager
        self.browser_commands = self._detect_browsers()
        self.deep_link_protocols = self._setup_deep_link_protocols()
    
    def _detect_browsers(self) -> Dict[str, str]:
        """Detecta navegadores disponibles en el sistema"""
        browsers = {}
        system = platform.system()
        
        if system == "Android":
            browsers.update({
                "brave": "com.brave.browser",
                "chrome": "com.android.chrome",
                "firefox": "org.mozilla.firefox"
            })
        elif system == "Darwin":  # macOS
            browsers.update({
                "brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "safari": "open -a Safari"
            })
        elif system == "Windows":
            browsers.update({
                "brave": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            })
        else:  # Linux
            browsers.update({
                "brave": "brave-browser",
                "chrome": "google-chrome",
                "firefox": "firefox"
            })
        
        return browsers
    
    def _setup_deep_link_protocols(self) -> Dict[str, str]:
        """Configura los protocolos de deep linking"""
        return {
            "brave": "brave://",
            "chrome": "googlechrome://",
            "firefox": "firefox://",
            "youtube": "yt://"
        }
    
    def open_url(self, url: str, browser: str = None, fullscreen: bool = False) -> bool:
        """Abre una URL en el navegador especificado"""
        try:
            if not browser:
                browser = self.config_manager.get('browser', 'default_browser', 'brave')
            
            if not self._is_valid_url(url):
                logger.error(f"URL inválida: {url}")
                return False
            
            browser_type = self._determine_browser_type(url, browser)
            
            if self._open_specific_browser(url, browser_type, fullscreen):
                logger.info(f"URL abierta en {browser_type}: {url}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error abriendo URL {url}: {e}")
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Valida si una URL es válida"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _determine_browser_type(self, url: str, preferred_browser: str) -> str:
        """Determina el tipo de navegador a usar"""
        if "youtube.com" in url or "youtu.be" in url:
            if preferred_browser == "brave" and "brave" in self.browser_commands:
                return "brave"
            elif "chrome" in self.browser_commands:
                return "chrome"
        
        if preferred_browser in self.browser_commands:
            return preferred_browser
        
        for browser in ["brave", "chrome", "firefox"]:
            if browser in self.browser_commands:
                return browser
        
        return "default"
    
    def _open_specific_browser(self, url: str, browser: str, fullscreen: bool) -> bool:
        """Abre URL en un navegador específico"""
        try:
            system = platform.system()
            
            if system == "Android":
                return self._open_android_browser(url, browser)
            elif system == "Darwin":
                return self._open_macos_browser(url, browser)
            elif system == "Windows":
                return self._open_windows_browser(url, browser)
            else:
                return self._open_linux_browser(url, browser)
                
        except Exception as e:
            logger.error(f"Error abriendo navegador específico {browser}: {e}")
            return False
    
    def _open_android_browser(self, url: str, browser: str) -> bool:
        """Abre URL en navegador Android"""
        try:
            if browser == "brave":
                intent_url = f"intent://open?url={url}#Intent;scheme=https;package=com.brave.browser;end"
                os.system(f"am start -a android.intent.action.VIEW -d '{intent_url}'")
                return True
            else:
                os.system(f"am start -a android.intent.action.VIEW -d '{url}'")
                return True
        except Exception:
            return False
    
    def _open_macos_browser(self, url: str, browser: str) -> bool:
        """Abre URL en navegador macOS"""
        try:
            command = self.browser_commands[browser]
            if browser in ["brave", "chrome"]:
                subprocess.run([command, url], check=True)
                return True
            else:
                subprocess.run([command, url], check=True)
                return True
        except Exception:
            return False
    
    def _open_windows_browser(self, url: str, browser: str) -> bool:
        """Abre URL en navegador Windows"""
        try:
            command = self.browser_commands[browser]
            if browser in ["brave", "chrome"]:
                subprocess.run([command, url], check=True)
                return True
            else:
                os.system(f'start "" "{url}"')
                return True
        except Exception:
            return False
    
    def _open_linux_browser(self, url: str, browser: str) -> bool:
        """Abre URL en navegador Linux"""
        try:
            command = self.browser_commands[browser]
            if browser in ["brave", "chrome"]:
                subprocess.run([command, url], check=True)
                return True
            else:
                os.system(f"xdg-open '{url}'")
                return True
        except Exception:
            return False
    
    def open_youtube_video(self, video_id: str, browser: str = None, autoplay: bool = True) -> bool:
        """Abre un video de YouTube específico"""
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            if autoplay:
                youtube_url += "&autoplay=1"
            
            return self.open_url(youtube_url, browser, fullscreen=True)
            
        except Exception as e:
            logger.error(f"Error abriendo video de YouTube {video_id}: {e}")
            return False
    
    def extract_youtube_video_id(self, youtube_url: str) -> Optional[str]:
        """Extrae el ID de video de una URL de YouTube"""
        try:
            parsed_url = urlparse(youtube_url)
            
            if "youtube.com" in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if "v" in query_params:
                    return query_params["v"][0]
            
            if "youtu.be" in parsed_url.netloc:
                video_id = parsed_url.path.lstrip("/")
                if video_id:
                    return video_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo video ID de {youtube_url}: {e}")
            return None

class AudioManager:
    """
    Gestor de audio para reproducir sonidos de alarmas y música de fondo
    """
    
    def __init__(self, config_manager):
        """Inicializa el gestor de audio"""
        self.config_manager = config_manager
        self.current_volume = 80
        self.is_playing = False
        self.sound_files = self._scan_sound_files()
    
    def _scan_sound_files(self) -> Dict[str, str]:
        """Escanea archivos de sonido disponibles"""
        sound_dir = os.path.join(os.getcwd(), "sounds")
        sound_files = {}
        
        if os.path.exists(sound_dir):
            for file in os.listdir(sound_dir):
                if file.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                    file_path = os.path.join(sound_dir, file)
                    sound_files[file[:-4]] = file_path
        
        sound_files.update({
            "default": "default_alarm",
            "gentle": "gentle_chime",
            "energetic": "energetic_beep",
            "nature": "nature_sounds"
        })
        
        return sound_files
    
    def play_alarm_sound(self, sound_name: str = None, volume: int = None) -> bool:
        """Reproduce el sonido de alarma"""
        try:
            if sound_name is None:
                sound_name = self.config_manager.get('audio', 'alarm_sound', 'default')
            
            if volume is None:
                volume = self.config_manager.get('audio', 'alarm_volume', 80)
            
            if not self._has_audio_support():
                return False
            
            sound_file = self._get_sound_file_path(sound_name)
            if not sound_file:
                logger.error(f"Archivo de sonido no encontrado: {sound_name}")
                return False
            
            success = self._play_sound_file(sound_file, volume)
            
            if success:
                self.is_playing = True
                self.current_volume = volume
            
            return success
            
        except Exception as e:
            logger.error(f"Error reproduciendo sonido de alarma: {e}")
            return False
    
    def stop_audio(self):
        """Detiene la reproducción de audio"""
        try:
            if self.is_playing:
                system = platform.system()
                
                if system == "Darwin":
                    subprocess.run(["pkill", "afplay"], check=False)
                elif system == "Windows":
                    import winsound
                    winsound.PlaySound(None, winsound.SND_PURGE)
                else:
                    subprocess.run(["pkill", "-f", "aplay"], check=False)
                    subprocess.run(["pkill", "-f", "ffplay"], check=False)
                
                self.is_playing = False
                
        except Exception as e:
            logger.error(f"Error deteniendo audio: {e}")
    
    def _has_audio_support(self) -> bool:
        """Verifica si el sistema soporta audio"""
        try:
            system = platform.system()
            
            if system == "Android":
                return os.path.exists("/system/bin/mediaserver")
            elif system == "Darwin":
                return os.path.exists("/usr/bin/afplay")
            elif system == "Windows":
                return os.path.exists("C:\\Windows\\System32\\WindowsMediaPlayer.dll")
            else:
                return os.path.exists("/usr/bin/aplay") or os.path.exists("/usr/bin/ffplay")
                
        except Exception:
            return False
    
    def _get_sound_file_path(self, sound_name: str) -> Optional[str]:
        """Obtiene la ruta del archivo de sonido"""
        if sound_name in self.sound_files:
            return self.sound_files[sound_name]
        
        sound_dir = os.path.join(os.getcwd(), "sounds")
        for extension in ['.mp3', '.wav', '.ogg', '.m4a']:
            file_path = os.path.join(sound_dir, f"{sound_name}{extension}")
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def _play_sound_file(self, file_path: str, volume: int) -> bool:
        """Reproduce un archivo de sonido específico"""
        try:
            if not os.path.exists(file_path):
                return False
            
            system = platform.system()
            
            if system == "Android":
                return self._play_android_audio(file_path, volume)
            elif system == "Darwin":
                return self._play_macos_audio(file_path, volume)
            elif system == "Windows":
                return self._play_windows_audio(file_path, volume)
            else:
                return self._play_linux_audio(file_path, volume)
                
        except Exception as e:
            logger.error(f"Error reproduciendo archivo {file_path}: {e}")
            return False
    
    def _play_android_audio(self, file_path: str, volume: int) -> bool:
        """Reproduce audio en Android"""
        try:
            from plyer import audio
            if hasattr(audio, 'play'):
                audio.play(file_path)
                return True
            return False
        except Exception:
            return False
    
    def _play_macos_audio(self, file_path: str, volume: int) -> bool:
        """Reproduce audio en macOS"""
        try:
            import subprocess
            subprocess.run(["afplay", file_path], check=True, timeout=30)
            return True
        except Exception:
            return False
    
    def _play_windows_audio(self, file_path: str, volume: int) -> bool:
        """Reproduce audio en Windows"""
        try:
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception:
            return False
    
    def _play_linux_audio(self, file_path: str, volume: int) -> bool:
        """Reproduce audio en Linux"""
        try:
            import subprocess
            subprocess.run(["aplay", file_path], check=True, timeout=30)
            return True
        except Exception:
            try:
                subprocess.run(["ffplay", "-autoexit", file_path], check=True, timeout=30)
                return True
            except Exception:
                return False