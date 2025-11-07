"""
Módulo de gestión de alarmas inteligentes
Sistema central para manejar múltiples alarmas con recurrencia y validación
"""

import json
import os
import logging
from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from croniter import croniter
from kivy.clock import Clock
from plyer import notification
import threading
import uuid

logger = logging.getLogger(__name__)

class Alarm:
    """
    Clase que representa una alarma individual
    """
    
    def __init__(self, alarm_id: str = None):
        """
        Inicializa una alarma
        
        Args:
            alarm_id: Identificador único de la alarma
        """
        self.id = alarm_id or str(uuid.uuid4())
        self.title = ""
        self.description = ""
        self.time = "08:00"
        self.recurrence = "none"  # none, daily, weekly, custom
        self.recurrence_data = {}  # Datos específicos de recurrencia
        self.enabled = True
        self.video_url = ""  # URL de video motivacional
        self.browser_preference = "brave"  # brave, chrome, default
        self.sound_file = ""
        self.volume = 80
        self.vibrate = True
        self.snooze_interval = 5
        self.max_snoozes = 3
        self.snooze_count = 0
        self.created_at = datetime.now().isoformat()
        self.last_triggered = None
        self.next_trigger = None
        self.days_of_week = []  # Para recurrencia semanal
        self.custom_schedule = []  # Para recurrencia personalizada
        self.is_active = False
        
        # Validación de datos
        self._validate_time_format()
    
    def _validate_time_format(self):
        """
        Valida que el formato de tiempo sea correcto
        """
        try:
            datetime.strptime(self.time, "%H:%M")
        except ValueError:
            # Si no es válido, usar hora por defecto
            self.time = "08:00"
    
    def get_formatted_time(self) -> str:
        """
        Retorna el tiempo en formato legible
        
        Returns:
            Tiempo formateado como HH:MM
        """
        return self.time
    
    def get_next_trigger_time(self) -> Optional[datetime]:
        """
        Calcula la próxima fecha y hora de activación
        
        Returns:
            Próxima fecha y hora de activación o None
        """
        try:
            now = datetime.now()
            alarm_time = datetime.strptime(self.time, "%H:%M").time()
            
            # Crear fecha inicial para hoy con la hora de la alarma
            next_trigger = datetime.combine(now.date(), alarm_time)
            
            if self.recurrence == "none":
                # Alarma única
                if next_trigger > now:
                    return next_trigger
                else:
                    return None
                    
            elif self.recurrence == "daily":
                # Recurrencia diaria
                if next_trigger <= now:
                    next_trigger += timedelta(days=1)
                return next_trigger
                
            elif self.recurrence == "weekly":
                # Recurrencia semanal
                current_weekday = now.weekday()
                target_weekdays = [int(day) for day in self.days_of_week]
                
                if not target_weekdays:
                    # Si no hay días específicos, usar el día actual
                    target_weekdays = [current_weekday]
                
                # Buscar el próximo día de la semana
                days_ahead = 0
                while True:
                    check_day = (current_weekday + days_ahead) % 7
                    if check_day in target_weekdays:
                        if days_ahead == 0 and next_trigger <= now:
                            days_ahead += 7
                            continue
                        break
                    days_ahead += 1
                
                next_trigger += timedelta(days=days_ahead)
                return next_trigger
                
            elif self.recurrence == "custom":
                # Recurrencia personalizada usando cron
                if self.custom_schedule:
                    cron = croniter(self.custom_schedule, now)
                    return cron.get_next(datetime)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculando próxima activación para alarma {self.id}: {e}")
            return None
    
    def should_trigger(self, current_time: datetime) -> bool:
        """
        Determina si la alarma debe activarse en el tiempo dado
        Verifica la hora actual del sistema contra la hora programada
        
        Args:
            current_time: Tiempo actual a verificar
            
        Returns:
            True si la alarma debe activarse
        """
        if not self.enabled or not self.is_active:
            return False
        
        # Obtener hora y minuto programados
        try:
            alarm_hour, alarm_minute = map(int, self.time.split(':'))
        except Exception:
            return False
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_second = current_time.second
        
        # Verificar si coincide la hora y minuto (solo en los primeros 3 segundos)
        if current_hour == alarm_hour and current_minute == alarm_minute and current_second < 3:
            # Verificar si la alarma ya fue disparada hoy
            if self.last_triggered:
                try:
                    last_trigger = datetime.fromisoformat(self.last_triggered)
                    # Si ya se disparó hoy, no disparar de nuevo
                    if last_trigger.date() == current_time.date():
                        return False
                except Exception:
                    pass
            
            # Verificar recurrencia
            if self.recurrence == "none":
                # Alarma única - solo dispara si es hoy o futuro
                return True
            elif self.recurrence == "daily":
                # Alarma diaria - siempre dispara
                return True
            elif self.recurrence == "weekly":
                # Alarma semanal - solo en días específicos
                current_weekday = current_time.weekday()
                return current_weekday in [int(d) for d in self.days_of_week]
            
            return True
        
        return False
    
    def trigger(self) -> Dict[str, Any]:
        """
        Activa la alarma
        
        Returns:
            Diccionario con información del trigger
        """
        trigger_time = datetime.now()
        self.last_triggered = trigger_time.isoformat()
        self.snooze_count = 0  # Resetear contador de snooze
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'triggered_at': trigger_time.isoformat(),
            'video_url': self.video_url,
            'browser_preference': self.browser_preference,
            'sound_file': self.sound_file,
            'volume': self.volume,
            'vibrate': self.vibrate
        }
    
    def snooze(self) -> bool:
        """
        Aplica snooze a la alarma
        
        Returns:
            True si se aplicó snooze correctamente
        """
        if self.snooze_count < self.max_snoozes:
            self.snooze_count += 1
            self.next_trigger = (datetime.now() + timedelta(minutes=self.snooze_interval)).isoformat()
            return True
        return False
    
    def disable(self):
        """
        Desactiva la alarma
        """
        self.enabled = False
        self.is_active = False
    
    def enable(self):
        """
        Activa la alarma
        """
        self.enabled = True
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la alarma a diccionario para serialización
        
        Returns:
            Diccionario con datos de la alarma
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time': self.time,
            'recurrence': self.recurrence,
            'recurrence_data': self.recurrence_data,
            'enabled': self.enabled,
            'video_url': self.video_url,
            'browser_preference': self.browser_preference,
            'sound_file': self.sound_file,
            'volume': self.volume,
            'vibrate': self.vibrate,
            'snooze_interval': self.snooze_interval,
            'max_snoozes': self.max_snoozes,
            'snooze_count': self.snooze_count,
            'created_at': self.created_at,
            'last_triggered': self.last_triggered,
            'next_trigger': self.next_trigger,
            'days_of_week': self.days_of_week,
            'custom_schedule': self.custom_schedule,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alarm':
        """
        Crea una alarma desde un diccionario
        
        Args:
            data: Datos de la alarma
            
        Returns:
            Instancia de Alarm
        """
        alarm = cls(data.get('id'))
        
        alarm.title = data.get('title', '')
        alarm.description = data.get('description', '')
        alarm.time = data.get('time', '08:00')
        alarm.recurrence = data.get('recurrence', 'none')
        alarm.recurrence_data = data.get('recurrence_data', {})
        alarm.enabled = data.get('enabled', True)
        alarm.video_url = data.get('video_url', '')
        alarm.browser_preference = data.get('browser_preference', 'brave')
        alarm.sound_file = data.get('sound_file', '')
        alarm.volume = data.get('volume', 80)
        alarm.vibrate = data.get('vibrate', True)
        alarm.snooze_interval = data.get('snooze_interval', 5)
        alarm.max_snoozes = data.get('max_snoozes', 3)
        alarm.snooze_count = data.get('snooze_count', 0)
        alarm.created_at = data.get('created_at', datetime.now().isoformat())
        alarm.last_triggered = data.get('last_triggered')
        alarm.next_trigger = data.get('next_trigger')
        alarm.days_of_week = data.get('days_of_week', [])
        alarm.custom_schedule = data.get('custom_schedule', [])
        alarm.is_active = data.get('is_active', False)
        
        alarm._validate_time_format()
        return alarm

class AlarmManager:
    """
    Gestor principal del sistema de alarmas
    """
    
    def __init__(self, config_manager):
        """
        Inicializa el gestor de alarmas
        
        Args:
            config_manager: Instancia del gestor de configuraciones
        """
        self.config_manager = config_manager
        self.alarms: List[Alarm] = []
        self.is_running = False
        self.check_interval = 1  # Verificar cada segundo
        self.check_event = None
        self.notification_callback = None
        self.audio_callback = None
        
        # Directorio de almacenamiento
        self.storage_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.alarms_file = os.path.join(self.storage_dir, "alarms.json")
    
    def start(self):
        """
        Inicia el sistema de alarmas con verificación continua
        El sistema verifica cada segundo si alguna alarma debe dispararse
        """
        if self.is_running:
            logger.warning("Sistema de alarmas ya está en ejecución")
            return
        
        self.is_running = True
        self.check_event = threading.Event()
        self.check_thread = threading.Thread(target=self._alarm_check_loop, daemon=True)
        self.check_thread.start()
        
        logger.info("✅ Sistema de alarmas iniciado - Verificación continua activa")
        logger.info(f"📊 Alarmas cargadas: {len(self.alarms)} total, {len(self.get_active_alarms())} activas")
    
    def stop(self):
        """
        Detiene el sistema de alarmas
        """
        self.is_running = False
        if self.check_event:
            self.check_event.set()
        
        logger.info("Sistema de alarmas detenido")
    
    def _alarm_check_loop(self):
        """
        Bucle principal para verificar alarmas continuamente
        Verifica cada segundo si alguna alarma debe dispararse
        """
        logger.info("🔄 Bucle de verificación de alarmas iniciado")
        
        while self.is_running:
            try:
                # Esperar 1 segundo antes de la próxima verificación
                if self.check_event.wait(self.check_interval):
                    break
                
                # Verificar alarmas pendientes
                self._check_pending_alarms()
                
            except Exception as e:
                logger.error(f"❌ Error en bucle de verificación de alarmas: {e}")
                logger.exception("Stack trace completo:")
        
        logger.info("🛑 Bucle de verificación de alarmas detenido")
    
    def _check_pending_alarms(self):
        """
        Verifica y activa alarmas pendientes
        Compara la hora actual del sistema con las alarmas programadas
        """
        current_time = datetime.now()
        triggered_alarms = []
        
        # Verificar cada alarma
        for alarm in self.alarms:
            if alarm.should_trigger(current_time):
                triggered_alarms.append(alarm)
                logger.info(f"⏰ Alarma detectada para activar: {alarm.title} - {alarm.time}")
        
        # Procesar alarmas activadas
        for alarm in triggered_alarms:
            logger.info(f"🔔 Activando alarma: {alarm.title}")
            self._trigger_alarm(alarm)
    
    def _trigger_alarm(self, alarm: Alarm):
        """
        Activa una alarma específica y ejecuta la secuencia completa:
        1. Sonido de alarma
        2. Notificación
        3. Vibración (si está habilitado)
        4. Abrir navegador Brave
        5. Reproducir video motivacional aleatorio
        
        Args:
            alarm: Alarma a activar
        """
        try:
            # Activar la alarma
            trigger_info = alarm.trigger()
            
            logger.info(f"🔔 Iniciando secuencia de alarma: {alarm.title} ({alarm.id})")
            
            # 1. Reproducir sonido de alarma
            if self.config_manager.get('audio', 'alarm_sound'):
                logger.info("🔊 Reproduciendo sonido de alarma...")
                if self.audio_callback:
                    self.audio_callback(trigger_info)
            
            # 2. Enviar notificación del sistema
            if self.config_manager.get('notifications', 'enabled', True):
                logger.info("📬 Enviando notificación...")
                self._send_notification(trigger_info)
            
            # 3. Vibrar si está habilitado
            if alarm.vibrate and self.config_manager.get('notifications', 'vibrate', True):
                logger.info("📳 Activando vibración...")
                self._vibrate()
            
            # 4. Abrir navegador Brave con video motivacional
            logger.info("🌐 Abriendo navegador Brave con video motivacional...")
            self._open_motivational_video(alarm)
            
            # 5. Calcular y actualizar próxima activación
            next_trigger = alarm.get_next_trigger_time()
            if next_trigger:
                alarm.next_trigger = next_trigger.isoformat()
                logger.info(f"⏰ Próxima activación programada: {next_trigger.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                # Si es alarma única, desactivarla
                if alarm.recurrence == "none":
                    alarm.enabled = False
                    logger.info(f"✅ Alarma única completada, desactivada")
            
            # Guardar cambios
            self.save_alarms()
            
            logger.info(f"✅ Secuencia de alarma completada exitosamente: {alarm.title}")
            
            # Notificar callback si existe
            if self.notification_callback:
                self.notification_callback(trigger_info)
                
        except Exception as e:
            logger.error(f"❌ Error activando alarma {alarm.id}: {e}")
            logger.exception("Stack trace completo:")
    
    def _open_motivational_video(self, alarm: Alarm):
        """
        Abre un video motivacional en el navegador Brave
        
        Args:
            alarm: Alarma que dispara el video
        """
        try:
            from browser_integration import BrowserIntegration
            
            # Crear instancia de browser_integration
            browser = BrowserIntegration(self.config_manager)
            
            # Determinar navegador a usar
            preferred_browser = alarm.browser_preference or "brave"
            
            # Si la alarma tiene video_url específico, usarlo
            if alarm.video_url and alarm.video_url.strip():
                logger.info(f"🎥 Abriendo video específico: {alarm.video_url}")
                success = browser.open_url(alarm.video_url, preferred_browser, fullscreen=False)
            else:
                # Usar video motivacional aleatorio
                logger.info(f"🎲 Seleccionando video motivacional aleatorio...")
                success = browser.open_motivational_video(preferred_browser)
            
            if success:
                logger.info(f"✅ Video motivacional abierto correctamente en {preferred_browser}")
            else:
                logger.warning(f"⚠️ No se pudo abrir el video motivacional")
                
        except Exception as e:
            logger.error(f"❌ Error abriendo video motivacional: {e}")
            logger.exception("Stack trace completo:")
    
    def _send_notification(self, trigger_info: Dict[str, Any]):
        """
        Envía una notificación del sistema
        
        Args:
            trigger_info: Información del trigger de la alarma
        """
        try:
            title = trigger_info.get('title', 'Alarma')
            message = trigger_info.get('description', 'Es hora de tu alarma')
            
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
    
    def _vibrate(self):
        """
        Activa la vibración del dispositivo
        """
        try:
            # La vibración se maneja a nivel de plataforma
            # usando plyer.notification con vibrate=True
            pass
        except Exception as e:
            logger.error(f"Error activando vibración: {e}")
    
    def add_alarm(self, alarm_data: Dict[str, Any]) -> Optional[str]:
        """
        Agrega una nueva alarma
        
        Args:
            alarm_data: Datos de la alarma
            
        Returns:
            ID de la alarma creada o None si hay error
        """
        try:
            # Validar datos
            if not self._validate_alarm_data(alarm_data):
                logger.error("Datos de alarma inválidos")
                return None
            
            # Crear alarma
            alarm = Alarm()
            self._update_alarm_from_data(alarm, alarm_data)
            
            # Verificar duplicados
            if self._is_duplicate_alarm(alarm):
                logger.warning(f"Alarma duplicada detectada: {alarm.title}")
                return None
            
            # Calcular próxima activación
            alarm.next_trigger = alarm.get_next_trigger_time()
            if alarm.next_trigger is None:
                logger.error("No se puede calcular próxima activación")
                return None
            
            # Agregar a la lista
            self.alarms.append(alarm)
            self.save_alarms()
            
            logger.info(f"Alarma agregada: {alarm.title} ({alarm.id})")
            return alarm.id
            
        except Exception as e:
            logger.error(f"Error agregando alarma: {e}")
            return None
    
    def update_alarm(self, alarm_id: str, alarm_data: Dict[str, Any]) -> bool:
        """
        Actualiza una alarma existente
        
        Args:
            alarm_id: ID de la alarma
            alarm_data: Nuevos datos
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Buscar alarma
            alarm = self.get_alarm_by_id(alarm_id)
            if alarm is None:
                logger.error(f"Alarma no encontrada: {alarm_id}")
                return False
            
            # Validar datos
            if not self._validate_alarm_data(alarm_data):
                logger.error("Datos de alarma inválidos")
                return False
            
            # Actualizar datos
            old_enabled = alarm.enabled
            self._update_alarm_from_data(alarm, alarm_data)
            
            # Recalcular próxima activación si es necesario
            if alarm.enabled:
                alarm.next_trigger = alarm.get_next_trigger_time()
            
            self.save_alarms()
            
            logger.info(f"Alarma actualizada: {alarm.title} ({alarm_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando alarma: {e}")
            return False
    
    def delete_alarm(self, alarm_id: str) -> bool:
        """
        Elimina una alarma
        
        Args:
            alarm_id: ID de la alarma
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            for i, alarm in enumerate(self.alarms):
                if alarm.id == alarm_id:
                    deleted_alarm = self.alarms.pop(i)
                    self.save_alarms()
                    logger.info(f"Alarma eliminada: {deleted_alarm.title} ({alarm_id})")
                    return True
            
            logger.warning(f"Alarma no encontrada para eliminar: {alarm_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando alarma: {e}")
            return False
    
    def get_alarm_by_id(self, alarm_id: str) -> Optional[Alarm]:
        """
        Obtiene una alarma por su ID
        
        Args:
            alarm_id: ID de la alarma
            
        Returns:
            Alarma o None si no existe
        """
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None
    
    def get_active_alarms(self) -> List[Alarm]:
        """
        Obtiene todas las alarmas activas
        
        Returns:
            Lista de alarmas activas
        """
        return [alarm for alarm in self.alarms if alarm.enabled]
    
    def get_next_alarm(self) -> Optional[Alarm]:
        """
        Obtiene la próxima alarma a activar
        
        Returns:
            Próxima alarma o None si no hay
        """
        active_alarms = self.get_active_alarms()
        next_alarm = None
        next_time = None
        
        for alarm in active_alarms:
            trigger_time = alarm.get_next_trigger_time()
            if trigger_time is not None:
                if next_time is None or trigger_time < next_time:
                    next_time = trigger_time
                    next_alarm = alarm
        
        return next_alarm
    
    def _update_alarm_from_data(self, alarm: Alarm, data: Dict[str, Any]):
        """
        Actualiza una alarma con nuevos datos
        
        Args:
            alarm: Alarma a actualizar
            data: Nuevos datos
        """
        alarm.title = data.get('title', alarm.title)
        alarm.description = data.get('description', alarm.description)
        alarm.time = data.get('time', alarm.time)
        alarm.recurrence = data.get('recurrence', alarm.recurrence)
        alarm.recurrence_data = data.get('recurrence_data', alarm.recurrence_data)
        alarm.enabled = data.get('enabled', alarm.enabled)
        alarm.video_url = data.get('video_url', alarm.video_url)
        alarm.browser_preference = data.get('browser_preference', alarm.browser_preference)
        alarm.sound_file = data.get('sound_file', alarm.sound_file)
        alarm.volume = data.get('volume', alarm.volume)
        alarm.vibrate = data.get('vibrate', alarm.vibrate)
        alarm.snooze_interval = data.get('snooze_interval', alarm.snooze_interval)
        alarm.max_snoozes = data.get('max_snoozes', alarm.max_snoozes)
        alarm.days_of_week = data.get('days_of_week', alarm.days_of_week)
        alarm.custom_schedule = data.get('custom_schedule', alarm.custom_schedule)
        alarm.is_active = data.get('is_active', alarm.is_active)
        
        alarm._validate_time_format()
    
    def _validate_alarm_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos de una alarma
        
        Args:
            data: Datos a validar
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validar tiempo
            time_str = data.get('time', '08:00')
            datetime.strptime(time_str, "%H:%M")
            
            # Validar volumen
            volume = data.get('volume', 80)
            if not (0 <= volume <= 100):
                return False
            
            # Validar intervalo de snooze
            snooze_interval = data.get('snooze_interval', 5)
            if not (1 <= snooze_interval <= 60):
                return False
            
            # Validar máximo de snoozes
            max_snoozes = data.get('max_snoozes', 3)
            if not (1 <= max_snoozes <= 20):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _is_duplicate_alarm(self, alarm: Alarm) -> bool:
        """
        Verifica si una alarma es duplicada
        
        Args:
            alarm: Alarma a verificar
            
        Returns:
            True si es una alarma duplicada
        """
        if not self.config_manager.get('validation', 'prevent_duplicates', True):
            return False
        
        for existing_alarm in self.alarms:
            if (existing_alarm.title == alarm.title and
                existing_alarm.time == alarm.time and
                existing_alarm.recurrence == alarm.recurrence):
                return True
        
        return False
    
    def save_alarms(self):
        """
        Guarda las alarmas al archivo
        """
        try:
            alarms_data = [alarm.to_dict() for alarm in self.alarms]
            
            with open(self.alarms_file, 'w', encoding='utf-8') as f:
                json.dump(alarms_data, f, indent=2, ensure_ascii=False)
                
            logger.info("Alarmas guardadas correctamente")
            
        except Exception as e:
            logger.error(f"Error guardando alarmas: {e}")
    
    def load_alarms(self):
        """
        Carga las alarmas desde el archivo
        """
        try:
            if os.path.exists(self.alarms_file):
                with open(self.alarms_file, 'r', encoding='utf-8') as f:
                    alarms_data = json.load(f)
                
                self.alarms = [Alarm.from_dict(data) for data in alarms_data]
                logger.info(f"Cargadas {len(self.alarms)} alarmas")
                
        except Exception as e:
            logger.error(f"Error cargando alarmas: {e}")
            self.alarms = []
    
    def set_notification_callback(self, callback):
        """
        Establece el callback para notificaciones
        
        Args:
            callback: Función a llamar cuando se active una alarma
        """
        self.notification_callback = callback
    
    def set_audio_callback(self, callback):
        """
        Establece el callback para audio
        
        Args:
            callback: Función a llamar para reproducir audio
        """
        self.audio_callback = callback
    
    def clear_all_alarms(self) -> bool:
        """
        Elimina todas las alarmas
        
        Returns:
            True si se eliminaron correctamente
        """
        try:
            self.alarms.clear()
            self.save_alarms()
            logger.info("Todas las alarmas han sido eliminadas")
            return True
        except Exception as e:
            logger.error(f"Error eliminando todas las alarmas: {e}")
            return False
    
    def get_alarms_count(self) -> int:
        """
        Obtiene el número total de alarmas
        
        Returns:
            Número de alarmas
        """
        return len(self.alarms)
    
    def get_enabled_alarms_count(self) -> int:
        """
        Obtiene el número de alarmas activas
        
        Returns:
            Número de alarmas activas
        """
        return len([a for a in self.alarms if a.enabled])
    
    def export_alarms(self, file_path: str) -> bool:
        """
        Exporta las alarmas a un archivo
        
        Args:
            file_path: Ruta del archivo de exportación
            
        Returns:
            True si se exportó correctamente
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'alarms': [alarm.to_dict() for alarm in self.alarms]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Alarmas exportadas a {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando alarmas: {e}")
            return False
    
    def import_alarms(self, file_path: str, merge: bool = True) -> bool:
        """
        Importa alarmas desde un archivo
        
        Args:
            file_path: Ruta del archivo de importación
            merge: Si debe fusionar con alarmas existentes
            
        Returns:
            True si se importó correctamente
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_alarms = [Alarm.from_dict(data) for data in import_data.get('alarms', [])]
            
            if merge:
                self.alarms.extend(imported_alarms)
            else:
                self.alarms = imported_alarms
            
            self.save_alarms()
            logger.info(f"Importadas {len(imported_alarms)} alarmas")
            return True
            
        except Exception as e:
            logger.error(f"Error importando alarmas: {e}")
            return False