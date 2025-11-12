[app]
# --- Основная информация о приложении ---
title = Manga Guide
package.name = mangaguide
package.domain = org.example.mangaguide
version = 1.0.0
source.dir = .

# --- Исходники ---
source.include_exts = py,png,jpg,atlas,ttf,otf,json,txt
source.include_patterns = images/*

# --- Требования (оптимизированы) ---
requirements = python3,
    kivy==2.1.0,
    requests,
    openssl,
    sqlite3,
    pillow,
    android

# Ориентация
orientation = portrait

# --- Android настройки ---
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 26
android.ndk = 25b
android.ndk_api = 21
android.arch = arm64-v8a

# Разрешить бэкапы
android.allow_backup = True

# Бутстрап
p4a.bootstrap = sdl2

# --- Иконка и заставка  ---
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/presplash.jpg
android.presplash_color = #1E3A8A

# --- Дополнительные настройки ---
android.private_storage = True
android.accept_sdk_license = True

# --- Логи ---
log_level = 2

[buildozer]
# --- Общие настройки ---
warn_on_root = 1
