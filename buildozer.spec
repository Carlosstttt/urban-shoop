[app]

# (str) Title of your application
title = Urban Shoop

# (str) Package name
package.name = urbanshoop

# (str) Package domain (needed for android/ios packaging)
package.domain = org.urbanshoop

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
# Incluimos kv y json para tus interfaces y la base de datos de compras
source.include_exts = py,png,jpg,kv,json,atlas

# (list) List of inclusions using pattern matching
# Súper importante: forzamos la inclusión de las carpetas assets y kv
source.include_patterns = assets/*, kv/*

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Agregamos plyer para las alertas/notificaciones y pillow para el procesamiento del banner/prendas
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,plyer

# (str) Presplash of the application
# Puedes dejar el banner como pantalla de carga provisional o cambiarlo por tu logo
presplash.filename = %(source.dir)s/assets/banner.jpg

# (str) Icon of the application
# Icono de la app en el teléfono (apunta al banner o a tu archivo personalizado)
icon.filename = %(source.dir)s/assets/banner.jpg

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android NDK API to use.
android.ndk_api = 24

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX support.
android.enable_androidx = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
