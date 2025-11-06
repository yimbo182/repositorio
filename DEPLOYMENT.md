# Guía de Compilación para Android APK y iOS IPA

## 📱 Compilación Multiplataforma con Buildozer

Esta guía detallada cubre la compilación de la aplicación de Alarmas Inteligente para Android (APK) e iOS (IPA) usando Buildozer y Python-for-Android.

## 🚀 Preparación del Entorno

### Requisitos Generales
- **Python**: 3.8+ 
- **Git**: Para clonar repositorios
- **Espacio en Disco**: Mínimo 5GB libres
- **RAM**: Mínimo 8GB recomendado

### Instalación de Buildozer

```bash
# Instalar buildozer globalmente
pip install buildozer

# Verificar instalación
buildozer --version

# Instalar dependencias adicionales para Android
pip install --upgrade buildozer

# Para Linux: Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3-dev \
    libc6-dev-i386 \
    libgcc-s1 \
    libltdl-dev \
    libffi-dev \
    libssl-dev \
    libbz2-dev \
    zlib1g-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-turbo8-dev \
    openjdk-8-jdk
```

### Verificación de Buildozer

```bash
# Inicializar proyecto (solo la primera vez)
buildozer init

# Verificar configuración
buildozer target list

# Hacer buildozer ejecutable
chmod +x ~/.local/bin/buildozer
```

## 🤖 Compilación para Android (APK)

### Paso 1: Configuración Inicial

```bash
# Asegurar que buildozer.spec esté configurado correctamente
# El archivo ya debe estar configurado con:
# - Título: Alarmas Inteligente
# - Paquete: com.alarmas.inteligente
# - Permisos apropiados
# - Dependencias necesarias
```

### Paso 2: Compilación Básica

```bash
# Compilación completa para Android
buildozer android debug

# Este comando realizará:
# 1. Descarga del toolchain de Android
# 2. Compilación de dependencias Python
# 3. Creación del APK de debug
# 4. Instalación en dispositivo conectado (opcional)

# Para compilación de release
buildozer android release

# El APK se generará en: ./bin/
```

### Paso 3: Compilación Avanzada

```bash
# Limpiar compilación anterior
buildozer android clean

# Compilación con logs detallados
buildozer android debug -v

# Compilación con diferentes APIs de Android
buildozer android debug --android.api=30

# Compilación con arquitectura específica
buildozer android debug --android.archs=arm64-v8a

# Compilación para Play Store (AAB)
buildozer android release --android.release_artifact=aab
```

### Paso 4: Instalación y Testing

```bash
# Instalar en dispositivo conectado
buildozer android debug deploy run

# Instalar solo APK
buildozer android debug deploy

# Ejecutar en dispositivo
buildozer android debug run

# Verificar logs en el dispositivo
adb logcat | grep -i "alarm"

# Listar aplicaciones instaladas
adb shell pm list packages | grep alarmas
```

### Configuración Avanzada de Android

#### Configuración en buildozer.spec

```ini
[app]
# Configuración específica para Android
android.permissions = INTERNET,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,USE_FULL_SCREEN_INTENT,SHOW_WHEN_LOCKED,TURN_SCREEN_ON,SET_ALARM

# Versiones de API
android.api = 33
android.minapi = 21

# Arquitectura
android.archs = arm64-v8a, armeabi-v7a

# Habilitar AndroidX
android.enable_androidx = True

# Storage privado
android.private_storage = True

# Tema de Android
android.theme = "@android:style/Theme.NoTitleBar"

# Backup automático
android.allow_backup = True

# Formato de release
android.release_artifact = apk
```

#### Permisos Especiales

```xml
<!-- En android/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT" />
<uses-permission android:name="android.permission.SHOW_WHEN_LOCKED" />
<uses-permission android:name="android.permission.TURN_SCREEN_ON" />
<uses-permission android:name="android.permission.SET_ALARM" />
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

### Solución de Problemas Android

#### Error: "ANDROID_HOME not set"
```bash
# Instalar Android SDK
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools

# O usar Android Studio para configurarlo automáticamente
```

#### Error: "Failed to install apk on device"
```bash
# Verificar dispositivo conectado
adb devices

# Habilitar depuración USB en el dispositivo
# Configuración > Opciones de desarrollador > Depuración USB

# Reinstalar drivers en Windows
# Descargar drivers desde el fabricante del dispositivo
```

#### Error: "Unable to build with gradle"
```bash
# Actualizar Gradle
buildozer android clean

# Usar versión específica de Gradle
# Editar buildozer.spec
android.gradle_version = 7.5

# Limpiar cache de Gradle
rm -rf ~/.gradle/caches/
```

## 🍎 Compilación para iOS (IPA)

### Paso 1: Preparación del Entorno macOS

```bash
# Verificar versión de macOS (debe ser 10.15+)
sw_vers

# Instalar Xcode desde App Store
# o descargar desde developer.apple.com

# Instalar Command Line Tools
xcode-select --install

# Verificar instalación
xcode-select -p

# Instalar Homebrew (si no está instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 2: Configuración de iOS Buildozer

```bash
# Instalar toolchain de iOS
buildozer target list

# Instalar dependencias específicas para iOS
pip install cython==0.29.33
pip install kivy-ios

# Verificar toolchain
toolchain pip install kivy
```

### Paso 3: Configuración del Proyecto iOS

#### Configuración en buildozer.spec para iOS

```ini
[buildozer.ios]
# Configuración específica para iOS
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# Deploy tools
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

# Bundle identifier
ios.bundle_id = com.alarmas.inteligente

# Display name
ios.display_name = Alarmas Inteligente

# Icon filename
ios.icon_filename = icon.png

# Launch image
ios.launch_image = launch_image.png

# Orientation
ios.orientation = portrait

# Status bar
ios.statusbar_hidden = False

# Deployment target
ios.deployment_target = 11.0
```

### Paso 4: Compilación iOS

```bash
# Compilación completa para iOS
buildozer ios debug

# Este comando realizará:
# 1. Configuración del toolchain iOS
# 2. Compilación de dependencias
# 3. Creación del proyecto Xcode
# 4. Compilación del IPA

# Abrir proyecto en Xcode
open buildozer.ios/AlarmasInteligente.xcodeproj
```

### Paso 5: Compilación desde Xcode

```bash
# Alternativamente, compilar desde línea de comandos
cd buildozer.ios
python toolchain.py build ipa

# O usar xcodebuild
xcodebuild -project AlarmasInteligente.xcodeproj \
           -scheme AlarmasInteligente \
           -configuration Release \
           -sdk iphoneos \
           archive \
           -archivePath build/AlarmasInteligente.xcarchive

# Exportar IPA
xcodebuild -exportArchive \
           -archivePath build/AlarmasInteligente.xcarchive \
           -exportPath build/ \
           -exportOptionsPlist ExportOptions.plist
```

### Configuración de Xcode

#### Configuración del Proyecto

1. **Abrir Xcode Project**: `open buildozer.ios/AlarmasInteligente.xcodeproj`

2. **Configurar Bundle Identifier**:
   ```
   General > Identity > Bundle Identifier: com.alarmas.inteligente
   ```

3. **Configurar Team**:
   ```
   General > Identity > Team: [Tu Apple Developer Team]
   ```

4. **Configurar Capabilities**:
   - Background Modes > Audio, AirPlay, and Picture in Picture
   - Push Notifications (opcional)
   - Background App Refresh

5. **Configurar Info.plist**:
   ```xml
   <key>NSLocalNetworkUsageDescription</key>
   <string>Esta aplicación necesita acceso a la red local para integrar con navegadores.</string>
   
   <key>NSUserNotificationAlertStyle</key>
   <string>alert</string>
   
   <key>UIBackgroundModes</key>
   <array>
       <string>audio</string>
       <string>background-processing</string>
   </array>
   ```

#### Configuración de Build Settings

```xml
<!-- En el archivo .xcconfig -->
CODE_SIGN_IDENTITY = iPhone Distribution
DEVELOPMENT_TEAM = YOUR_TEAM_ID
PROVISIONING_PROFILE = YOUR_PROVISIONING_PROFILE_UUID
CODE_SIGN_STYLE = Manual
```

### Distribución en App Store

#### Preparación para App Store

```bash
# Crear IPA para App Store
buildozer ios release

# O desde Xcode:
# Product > Archive > Distribute App > App Store Connect
```

#### Configuración en App Store Connect

1. **Crear App en App Store Connect**:
   ```
   My Apps > + > New App
   Name: Alarmas Inteligente
   Bundle ID: com.alarmas.inteligente
   SKU: alarmas-inteligente-001
   ```

2. **Subir Metadata**:
   - Descripción
   - Palabras clave
   - Categoría: Productivity
   - Contenido de la aplicación

3. **Subir Screenshots**:
   - iPhone: 6.7", 6.5", 5.5"
   - iPad: 12.9"

4. **Configurar Pricing**:
   - Gratuita o precio fijo

## 🔧 Comandos de Construcción Avanzados

### Scripts de Automatización

#### build_android.sh
```bash
#!/bin/bash
# Script para compilación automatizada de Android

echo "Iniciando compilación para Android..."

# Limpiar compilación anterior
buildozer android clean

# Compilar APK de debug
echo "Compilando APK de debug..."
buildozer android debug

# Verificar si se generó el APK
if [ -f "./bin/alarmasinteligente-1.0.0-debug.apk" ]; then
    echo "✅ APK generado exitosamente"
    echo "📱 Ubicación: ./bin/alarmasinteligente-1.0.0-debug.apk"
    
    # Instalar en dispositivo conectado (opcional)
    read -p "¿Instalar APK en dispositivo conectado? (y/n): " install_choice
    if [ "$install_choice" = "y" ]; then
        adb install ./bin/alarmasinteligente-1.0.0-debug.apk
    fi
else
    echo "❌ Error: No se pudo generar el APK"
    exit 1
fi

echo "🎉 Compilación de Android completada"
```

#### build_ios.sh
```bash
#!/bin/bash
# Script para compilación automatizada de iOS

echo "Iniciando compilación para iOS..."

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: La compilación de iOS solo funciona en macOS"
    exit 1
fi

# Compilar proyecto iOS
echo "Compilando proyecto iOS..."
buildozer ios debug

# Verificar si se generó el proyecto Xcode
if [ -d "./buildozer.ios/AlarmasInteligente.xcodeproj" ]; then
    echo "✅ Proyecto Xcode generado exitosamente"
    echo "📱 Ubicación: ./buildozer.ios/"
    
    # Abrir proyecto en Xcode (opcional)
    read -p "¿Abrir proyecto en Xcode? (y/n): " open_choice
    if [ "$open_choice" = "y" ]; then
        open ./buildozer.ios/AlarmasInteligente.xcodeproj
    fi
else
    echo "❌ Error: No se pudo generar el proyecto Xcode"
    exit 1
fi

echo "🎉 Compilación de iOS completada"
echo "💡 Abre el proyecto en Xcode para finalizar la compilación del IPA"
```

### Optimización de Build

#### Optimización de Tamaño

```bash
# Usar iconos optimizados
# Colocar iconos en diferentes tamaños:
# icon-20.png, icon-40.png, icon-60.png, icon-80.png, icon-120.png, icon-180.png

# Minimizar assets
find . -name "*.png" -exec optipng {} \\;
find . -name "*.jpg" -exec jpegoptim {} \\;

# Usar buildozer con optimizaciones
buildozer android debug --android.minapi=21 --android.archs=arm64-v8a
```

#### Configuración de Release

```bash
# Para Android Release
buildozer android release --android.release_artifact=apk

# Para iOS Release
buildozer ios release

# Configuración optimizada para producción
buildozer android clean
buildozer android release -v
```

## 🧪 Testing en Dispositivos

### Testing en Android

#### Preparación del Dispositivo
```bash
# Habilitar Opciones de Desarrollador
# Configuración > Acerca del teléfono > Tocar 7 veces "Número de compilación"

# Habilitar Depuración USB
# Opciones de desarrollador > Depuración USB

# Instalar APK
adb install ./bin/alarmasinteligente-1.0.0-debug.apk

# Verificar instalación
adb shell pm list packages | grep alarmas
```

#### Testing de Funcionalidades
```bash
# Verificar logs de la aplicación
adb logcat | grep -E "(Alarmas|Python)"

# Verificar permisos
adb shell dumpsys package com.alarmas.inteligente | grep permission

# Testing de notificaciones
adb shell dumpsys notification | grep alarmas

# Testing de audio
# Verificar que la aplicación puede reproducir audio
```

### Testing en iOS

#### Preparación del Dispositivo
```bash
# Para testing sin App Store (Development):
# 1. Abrir Xcode > Window > Devices and Simulators
# 2. Conectar dispositivo via USB
# 3. Seleccionar dispositivo
# 4. Click "Install" en la sección "Installed Apps"

# Para testing con TestFlight:
# 1. Subir IPA a App Store Connect
# 2. Configurar TestFlight
# 3. Enviar invitación para testing interno/externo
```

#### Configuración de Dispositivo para Desarrollo
```xml
<!-- En iOS Device -->
1. Ir a Configuración > General > VPN y Gestión de Dispositivos
2. Confiar en el certificado de desarrollador
3. Permitir apps de desarrolladores no verificados
```

## 📊 Monitoreo y Logs

### Android Monitoring
```bash
# Logs en tiempo real
adb logcat -s Python

# Logs específicos de la aplicación
adb logcat | grep -i "alarm"

# Información del sistema
adb shell dumpsys | grep -i "alarms"

# Estado de la aplicación
adb shell dumpsys package com.alarmas.inteligente
```

### iOS Monitoring
```bash
# Desde Xcode > Window > Devices and Simulators
# 1. Seleccionar dispositivo
# 2. Click "View Device Logs"

# O usar lldb para debugging
# Desde Xcode: Debug > Attach to Process
```

## 🚨 Solución de Problemas Comunes

### Android

#### Error: "SDK location not found"
```bash
# Configurar ANDROID_HOME
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# O crear archivo local.properties
echo "sdk.dir=$HOME/Android/Sdk" > android/local.properties
```

#### Error: "Unable to merge dex"
```bash
# Habilitar multidex en buildozer.spec
android.multiarch = True

# O aumentar memoria de compilación
export GRADLE_OPTS="-Xmx2g -XX:MaxPermSize=512m"
```

#### Error: "INSTALL_FAILED_INSUFFICIENT_STORAGE"
```bash
# Limpiar espacio en dispositivo
adb shell pm clear com.alarmas.inteligente
adb shell pm uninstall com.alarmas.inteligente

# Reinstalar
adb install -r ./bin/alarmasinteligente-1.0.0-debug.apk
```

### iOS

#### Error: "Code signing failed"
```bash
# Verificar certificados en Keychain
# Xcode > Preferences > Accounts > Apple ID > Manage Certificates

# Limpiar build
cd buildozer.ios
rm -rf build/
python toolchain.py clean

# Re-compilar
python toolchain.py build ipa
```

#### Error: "provisioning profile not found"
```bash
# En Xcode:
# 1. Seleccionar proyecto
# 2. General > Signing & Capabilities
# 3. Seleccionar Team
# 4. Xcode creará automáticamente el profile
```

#### Error: "Architecture not supported"
```bash
# Verificar architectures en buildozer.spec
android.archs = arm64-v8a, armeabi-v7a, x86_64

# En Xcode:
# Build Settings > Architectures > arm64
```

## 📈 Optimización de Rendimiento

### Android Optimization
```ini
[app]
# Habilitar compilación optimizada
android.release_artifact = apk
android.enable_androidx = true

# Minimizar tamaño del APK
android.whitelist = 

# Optimizar código
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"
```

### iOS Optimization
```ini
[buildozer.ios]
# Configuración optimizada
ios.deployment_target = 11.0
ios.codesign_identity = iPhone Distribution

# Minimizar tamaño del IPA
ios.enable_bitcode = True
```

## 📝 Checklist Pre-Release

### Android Checklist
- [ ] APK firmado para release
- [ ] Permisos configurados correctamente
- [ ] Icono y splash screen configurados
- [ ] Version code incrementada
- [ ] Tested en múltiples dispositivos
- [ ] Performance testing completado
- [ ] Google Play Store assets preparados

### iOS Checklist
- [ ] Certificado de distribución configurado
- [ ] Provisioning profile válido
- [ ] Bundle identifier único
- [ ] Iconos en todos los tamaños requeridos
- [ ] Screenshots para App Store preparados
- [ ] Metadata de App Store completado
- [ ] Tested en dispositivos físicos
- [ ] App Store review guidelines compliance

---

**Nota**: Esta guía cubre las funcionalidades específicas de la aplicación de Alarmas Inteligente. Para problemas específicos de Buildozer o Kivy, consulte la documentación oficial en https://buildozer.readthedocs.io/

**Última Actualización**: Noviembre 2025