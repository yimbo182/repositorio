"""
Módulo de gestión de configuraciones persistentes
Maneja el almacenamiento y recuperación de configuraciones de usuario
"""

import json
import os
from typing import Any, Optional
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Gestor de configuraciones persistentes
    """
    
    def __init__(self, config_file: str = "alarm_config.json"):
        """
        Inicializa el gestor de configuraciones
        
        Args:
            config_file: Nombre del archivo de configuración
        """
        self.config_file = config_file
        self.config_dir = os.path.join(os.getcwd(), "config")
        self.config_path = os.path.join(self.config_dir, config_file)
        
        # Crear directorio de configuración si no existe
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Inicializar clave de cifrado
        self._init_encryption()
        
        # Cargar configuraciones
        self._load_config()
    
    def _init_encryption(self):
        """
        Inicializa el sistema de cifrado para configuraciones sensibles
        """
        key_file = os.path.join(self.config_dir, ".config_key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generar nueva clave de cifrado
            self.encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
        
        self.cipher = Fernet(self.encryption_key)
    
    def _load_config(self):
        """
        Carga las configuraciones desde el archivo
        """
        self.config_data = {}
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read()
                
                # Desencriptar datos
                decrypted_data = self.cipher.decrypt(encrypted_data.encode())
                self.config_data = json.loads(decrypted_data.decode())
                
                logger.info("Configuración cargada correctamente")
                
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
                self.config_data = self._get_default_config()
        else:
            # Crear configuración por defecto
            self.config_data = self._get_default_config()
            self._save_config()
    
    def _save_config(self):
        """
        Guarda las configuraciones al archivo
        """
        try:
            # Encriptar datos
            json_data = json.dumps(self.config_data, indent=2, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_data.decode())
            
            logger.info("Configuración guardada correctamente")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def _get_default_config(self) -> dict:
        """
        Retorna la configuración por defecto
        """
        return {
            "theme": {
                "theme_style": "Light",
                "primary_color": "Blue",
                "accent_color": "Amber",
                "custom_colors": {}
            },
            "audio": {
                "alarm_volume": 80,
                "snooze_volume": 60,
                "background_play": True,
                "alarm_sound": "default",
                "custom_sounds": {}
            },
            "notifications": {
                "enabled": True,
                "vibrate": True,
                "sound": True,
                "preview_text": True,
                "priority": "normal"
            },
            "snooze": {
                "default_interval": 5,
                "max_snoozes": 3,
                "progressive_volume": True
            },
            "browser": {
                "default_browser": "brave",
                "auto_open": True,
                "open_fullscreen": False,
                "custom_protocols": {}
            },
            "validation": {
                "prevent_duplicates": True,
                "max_alarms": 50,
                "min_interval": 1,
                "max_interval": 1440
            },
            "ui": {
                "responsive": True,
                "show_seconds": False,
                "compact_view": False,
                "animations": True
            },
            "security": {
                "lock_settings": False,
                "pin_protection": False,
                "biometric_unlock": False
            },
            "backup": {
                "auto_backup": True,
                "backup_interval": 24,
                "cloud_sync": False,
                "last_backup": None
            }
        }
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración
        
        Args:
            section: Sección de configuración
            key: Clave dentro de la sección
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la configuración o default
        """
        try:
            return self.config_data.get(section, {}).get(key, default)
        except Exception as e:
            logger.error(f"Error obteniendo configuración {section}.{key}: {e}")
            return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """
        Establece un valor de configuración
        
        Args:
            section: Sección de configuración
            key: Clave dentro de la sección
            value: Valor a establecer
            
        Returns:
            True si se estableció correctamente
        """
        try:
            if section not in self.config_data:
                self.config_data[section] = {}
            
            self.config_data[section][key] = value
            self._save_config()
            return True
            
        except Exception as e:
            logger.error(f"Error estableciendo configuración {section}.{key}: {e}")
            return False
    
    def get_section(self, section: str) -> dict:
        """
        Obtiene toda una sección de configuración
        
        Args:
            section: Sección a obtener
            
        Returns:
            Diccionario con la sección completa
        """
        return self.config_data.get(section, {})
    
    def set_section(self, section: str, data: dict) -> bool:
        """
        Establece una sección completa de configuración
        
        Args:
            section: Sección a establecer
            data: Datos de la sección
            
        Returns:
            True si se estableció correctamente
        """
        try:
            self.config_data[section] = data
            self._save_config()
            return True
            
        except Exception as e:
            logger.error(f"Error estableciendo sección {section}: {e}")
            return False
    
    def export_config(self, file_path: str, encrypt: bool = False) -> bool:
        """
        Exporta la configuración a un archivo
        
        Args:
            file_path: Ruta del archivo de exportación
            encrypt: Si debe encriptar el archivo exportado
            
        Returns:
            True si se exportó correctamente
        """
        try:
            json_data = json.dumps(self.config_data, indent=2, ensure_ascii=False)
            
            if encrypt:
                json_data = self.cipher.encrypt(json_data.encode()).decode()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            logger.info(f"Configuración exportada a {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando configuración: {e}")
            return False
    
    def import_config(self, file_path: str, decrypt: bool = False) -> bool:
        """
        Importa configuración desde un archivo
        
        Args:
            file_path: Ruta del archivo de importación
            decrypt: Si el archivo está encriptado
            
        Returns:
            True si se importó correctamente
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            if decrypt:
                json_data = self.cipher.decrypt(json_data.encode()).decode()
            
            imported_data = json.loads(json_data)
            
            # Validar estructura básica
            if self._validate_config_structure(imported_data):
                self.config_data.update(imported_data)
                self._save_config()
                logger.info(f"Configuración importada desde {file_path}")
                return True
            else:
                logger.error("Estructura de configuración inválida")
                return False
                
        except Exception as e:
            logger.error(f"Error importando configuración: {e}")
            return False
    
    def _validate_config_structure(self, config_data: dict) -> bool:
        """
        Valida que la estructura de configuración sea correcta
        
        Args:
            config_data: Datos de configuración a validar
            
        Returns:
            True si la estructura es válida
        """
        required_sections = [
            "theme", "audio", "notifications", 
            "snooze", "browser", "validation", "ui"
        ]
        
        try:
            for section in required_sections:
                if section not in config_data:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def reset_to_default(self) -> bool:
        """
        Resetea la configuración a valores por defecto
        
        Returns:
            True si se reseteó correctamente
        """
        try:
            self.config_data = self._get_default_config()
            self._save_config()
            logger.info("Configuración reseteada a valores por defecto")
            return True
            
        except Exception as e:
            logger.error(f"Error reseteando configuración: {e}")
            return False
    
    def get_all_config(self) -> dict:
        """
        Obtiene toda la configuración
        
        Returns:
            Diccionario completo con todas las configuraciones
        """
        return self.config_data.copy()
    
    def backup_config(self) -> str:
        """
        Crea una copia de seguridad de la configuración
        
        Returns:
            Ruta del archivo de backup
        """
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"config_backup_{timestamp}.json"
        backup_path = os.path.join(self.config_dir, backup_file)
        
        if self.export_config(backup_path, encrypt=True):
            # Actualizar fecha de último backup
            self.set("backup", "last_backup", timestamp)
            return backup_path
        
        return ""
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """
        Limpia backups antiguos manteniendo solo los más recientes
        
        Args:
            keep_count: Número de backups a mantener
        """
        try:
            backup_files = []
            for file in os.listdir(self.config_dir):
                if file.startswith("config_backup_") and file.endswith(".json"):
                    file_path = os.path.join(self.config_dir, file)
                    backup_files.append((file_path, os.path.getctime(file_path)))
            
            # Ordenar por fecha de creación (más recientes primero)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Eliminar backups antiguos
            for file_path, _ in backup_files[keep_count:]:
                os.remove(file_path)
                logger.info(f"Backup antiguo eliminado: {file_path}")
                
        except Exception as e:
            logger.error(f"Error limpiando backups: {e}")