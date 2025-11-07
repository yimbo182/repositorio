# 📱 Instrucciones de Uso - Alarmas Inteligente v2.0

## 🚀 Cómo Iniciar la Aplicación

### Opción 1: Desde la Terminal
```bash
python main.py
```

### Opción 2: Desde VSCode
1. Abre `main.py`
2. Click derecho → "Run Python File in Terminal"
3. O presiona `Ctrl+F5`

---

## ⏰ Cómo Crear una Alarma

### Paso 1: Abrir el Diálogo
1. En la pantalla principal, click el botón verde **"🚀 Crear Alarma Rápida"**
2. Se abrirá el diálogo "⏰ Nueva Alarma"

### Paso 2: Configurar la Alarma

#### A. Título de la Alarma
- Escribe un nombre descriptivo
- Ejemplo: "Despertar", "Ir al Gym", "Tomar Medicina"

#### B. Seleccionar Hora
**Time Picker con botones +/-**:
- **Hora**: Usa los botones circulares para ajustar (00-23)
  - Click ➖ para decrementar
  - Click ➕ para incrementar
- **Minuto**: Igual que la hora (00-59)

**Ejemplo**:
- Para alarma a las 7:30 AM → Ajusta a `07:30`
- Para alarma a las 3:45 PM → Ajusta a `15:45`

#### C. Seleccionar Frecuencia
Elige uno de los tres botones:
- **Una vez**: Suena solo una vez y se desactiva
- **Diaria**: Suena todos los días a la misma hora ✅ (predeterminado)
- **Semanal**: Suena ciertos días de la semana

#### D. Video Motivacional (Opcional)
- **Dejar vacío**: El sistema seleccionará un video aleatorio de los 10 predeterminados
- **Ingresar URL**: Pega una URL de YouTube específica

**Ejemplo de URLs válidas**:
```
https://www.youtube.com/watch?v=ZXsQAXx_ao0
https://youtu.be/mgmVOuLgFB0
```

### Paso 3: Guardar
1. Click botón verde **"✅ Guardar Alarma"**
2. Verás un mensaje: "✅ Alarma 'Despertar' programada para 07:30 (diariamente)"
3. Debajo dirá: "⏰ Sonará en Xh Ym"

---

## 📋 Cómo Gestionar Alarmas

### Ver Todas las Alarmas
1. Click botón azul **"📋 Gestionar Alarmas"**
2. Verás lista completa con:
   - ⏰ Título
   - 🕐 Hora programada
   - 🔁 Tipo de recurrencia
   - 🔊 Nivel de volumen

### Eliminar una Alarma
1. En la lista de alarmas, click el botón rojo **❌** de la alarma
2. Confirma en el diálogo que aparece
3. La alarma será eliminada

### Limpiar Todas las Alarmas
1. Click icono menú ☰ (arriba izquierda)
2. Selecciona **"🗑️ Limpiar Alarmas"**
3. Todas las alarmas serán eliminadas

---

## 🎥 Sistema de Videos Motivacionales

### Videos Predeterminados (10 videos)
El sistema incluye 10 videos motivacionales en español:
1. Motivación Matutina - Empieza Tu Día con Energía
2. Nunca Te Rindas - Video Motivacional
3. Despierta tu Grandeza - Motivación Diaria
4. El Poder de Levantarse Temprano
5. Tu Momento Es Ahora - Motivación Poderosa
6. Despierta Campeón - Rutina Matutina
7. No Tienes Tiempo para el Miedo
8. Empieza Hoy Tu Transformación
9. Disciplina y Consistencia - Claves del Éxito
10. Despierta con Propósito - Motivación Matinal

### Agregar Videos Personalizados
1. Abre el archivo `motivational_videos.json`
2. En la sección `"custom_videos"`, agrega:

```json
"custom_videos": [
  {
    "title": "Mi Video Favorito",
    "url": "https://www.youtube.com/watch?v=TU_VIDEO_ID",
    "duration": "10:00"
  }
]
```

3. Guarda el archivo
4. Reinicia la aplicación

---

## 🔔 Qué Pasa Cuando Suena una Alarma

Secuencia automática completa:

```
⏰ 07:00:00 - Hora programada alcanzada
    ↓
🔔 Sistema detecta coincidencia
    ↓
🔊 Reproduce sonido de alarma
    ↓
📬 Muestra notificación del sistema
    ↓
📳 Activa vibración del dispositivo
    ↓
🦁 Lanza Brave Browser automáticamente
    ↓
🎲 Selecciona video motivacional aleatorio
    ↓
🎥 Abre YouTube con el video
    ↓
▶️ El video comienza a reproducirse automáticamente (autoplay)
    ↓
✅ Actualiza próxima activación según recurrencia
```

---

## ⚙️ Configuración

### Cambiar Tema (Claro/Oscuro)
1. Click botón morado **"⚙️ Configuración"**
2. En la sección "Tema", activa **"Tema Oscuro"**
3. La interfaz cambiará a colores oscuros

### Ajustar Volumen
1. En Configuración → "Audio"
2. Desliza el control de **"Volumen de Alarma"** (0-100)
3. Los cambios se guardan automáticamente

### Configurar Snooze
1. En Configuración → "Snooze"
2. **Intervalo de Snooze**: 1-30 minutos
3. **Límite de snoozes**: 1-10 veces
4. Ajusta según tu preferencia

---

## 🕐 Pantalla Principal

### Elementos Visibles:

1. **Reloj Digital**:
   - Hora actual: `21:04:35`
   - Fecha: `Miércoles, 06 de Noviembre de 2025`
   - Actualización en tiempo real (cada segundo)

2. **Tarjeta de Estadísticas**:
   - **Próxima**: Hora de la próxima alarma
   - **Total**: Número total de alarmas activas
   - **Estado**: Estado del sistema (Activo/Inactivo)

3. **Botones de Acción**:
   - 🚀 **Crear Alarma Rápida** (verde)
   - 📋 **Gestionar Alarmas** (azul)
   - ⚙️ **Configuración** (púrpura)

4. **Tarjeta de Estado**:
   - 🟢 Indicador visual
   - Mensaje de estado del sistema

---

## ❓ Preguntas Frecuentes

### ¿Cuántas alarmas puedo crear?
Hasta 50 alarmas (configurable en `config_manager.py`)

### ¿Las alarmas funcionan si cierro la app?
**En Windows**: No, debes mantener la app abierta
**En Android**: Sí, funcionará en segundo plano (con permisos)

### ¿Puedo usar el mismo video siempre?
Sí, ingresa la URL específica al crear la alarma

### ¿Puedo desactivar el video automático?
Sí, edita `motivational_videos.json`:
```json
"settings": {
  "autoplay": false
}
```

### ¿Qué pasa si no tengo instalado Brave?
El sistema intentará usar Chrome o el navegador predeterminado

### ¿Cómo funciona la recurrencia semanal?
Actualmente suena todos los días de la semana. En futuras versiones podrás elegir días específicos.

---

## 🐛 Solución de Problemas

### La app se cierra al crear alarma
1. Cierra la app completamente
2. Reinicia con: `python main.py`
3. Intenta crear la alarma nuevamente
4. Si persiste, revisa `alarm_system.log`

### El video no se abre
1. Verifica que Brave esté instalado
2. Prueba con Chrome editando `browser_integration.py`
3. Revisa que la URL sea válida

### La alarma no suena
1. Verifica que esté **activada** (icono ⏰ verde)
2. Verifica que `is_active = True`
3. Revisa `alarm_system.log` para errores

### Error de "readonly property"
Reinicia la aplicación, ya está corregido en la última versión.

---

## 📞 Soporte

### Logs del Sistema
Los logs se guardan automáticamente en:
```
alarm_system.log
```

### Archivos de Configuración
```
config/
  ├── alarm_config.json (configuraciones)
  └── .config_key (clave de cifrado)

data/
  └── alarms.json (alarmas guardadas)
```

### Backup de Alarmas
Para hacer backup manual:
```bash
# Copiar archivo de alarmas
copy data\alarms.json data\alarms_backup.json
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Despertar todos los días a las 7:00 AM
```
Título: "Buenos días ☀️"
Hora: 07:00
Recurrencia: Diaria ✅
Video: [vacío] → aleatorio
```

### Caso 2: Recordatorio de Gym (Lun-Mié-Vie)
```
Título: "Hora del Gym 💪"
Hora: 18:00
Recurrencia: Semanal ✅
Video: https://youtube.com/watch?v=xxx (video fitness)
```

### Caso 3: Reunión Importante (una sola vez)
```
Título: "Reunión con el cliente"
Hora: 14:30
Recurrencia: Una vez ✅
Video: [vacío] o video específico
```

---

## 🎨 Características de la Interfaz

### Paleta de Colores:
- **Primario**: DeepPurple (#6633CC)
- **Acento**: Teal (#008080)
- **Éxito**: Verde azulado (#00BF7F)
- **Info**: Azul índigo (#4D66E5)
- **Error**: Rojo coral (#B34D4D)

### Elementos Visuales:
- **Bordes redondeados**: 12-15px en todas las tarjetas
- **Elevación**: 2-10px según importancia
- **Iconos**: Material Design en toda la app
- **Fuentes**: Roboto (KivyMD predeterminado)

---

## 📝 Ejemplo de Uso Paso a Paso

```
1. Abrir app → python main.py
   ✅ Ver reloj: 21:04:35

2. Click "🚀 Crear Alarma Rápida"
   ✅ Diálogo se abre

3. Escribir título: "Despertar"
   ✅ Título ingresado

4. Ajustar hora a 07:00
   - Click ➕ hasta llegar a 07
   - Click ➕ en minutos si necesario
   ✅ Hora configurada

5. Verificar recurrencia: "Diaria" (verde)
   ✅ Recurrencia correcta

6. Campo video: dejar vacío
   ✅ Usará video aleatorio

7. Click "✅ Guardar Alarma"
   ✅ Mensaje: "Alarma programada para 07:00 (diariamente)"
   ✅ Mensaje: "⏰ Sonará en 9h 56m"

8. Ir a "📋 Gestionar Alarmas"
   ✅ Ver alarma en la lista

9. Al día siguiente a las 07:00:00
   ✅ Suena alarma
   ✅ Brave se abre
   ✅ YouTube reproduce video
```

---

## 🔧 Mantenimiento

### Actualizar Videos
Editar `motivational_videos.json`:
- Agregar videos en `custom_videos`
- Modificar configuración en `settings`

### Cambiar Navegador Predeterminado
Editar `browser_integration.py` línea 129:
```python
"default_browser": "brave"  # Cambiar a "chrome" o "firefox"
```

### Ajustar Intervalo de Verificación
Editar `alarm_manager.py` línea 291:
```python
self.check_interval = 1  # Segundos entre verificaciones
```

---

## ✅ Checklist Rápido

Antes de usar la app, verifica:

- [x] Python 3.10+ instalado
- [x] Dependencias instaladas: `pip install -r requirements.txt`
- [x] Brave Browser instalado (o Chrome)
- [x] Permisos de notificación concedidos
- [x] Archivo `motivational_videos.json` presente
- [x] Directorio `data/` creado automáticamente
- [x] Directorio `config/` creado automáticamente

---

## 🎉 ¡Disfruta de tu Aplicación!

Ahora tienes un sistema completo de alarmas con:
- ⏰ Hora específica (no cuenta regresiva)
- 🎲 Videos motivacionales aleatorios
- 🔄 Recurrencia personalizable
- 📊 Estadísticas en tiempo real
- 🎨 Interfaz moderna y atractiva

**¿Algún problema?** Consulta [`SOLUCION_ERRORES.md`](SOLUCION_ERRORES.md:1)

**¿Quieres saber cómo funciona internamente?** Lee [`REESTRUCTURACION_SISTEMA_ALARMAS.md`](REESTRUCTURACION_SISTEMA_ALARMAS.md:1)