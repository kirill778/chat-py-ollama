import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Canvas, font
import requests
import json
import threading
from datetime import datetime
import os
import io
import base64
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import time
import math
import random

class ModernWidget:
    def __init__(self):
        # Премиум цветовая схема
        self.primary = "#3B82F6"          # Синий
        self.primary_light = "#93C5FD"    # Светло-синий
        self.primary_dark = "#1E40AF"     # Темно-синий
        self.secondary = "#10B981"        # Зеленый
        self.accent = "#8B5CF6"           # Фиолетовый
        self.warning = "#F59E0B"          # Оранжевый
        self.danger = "#EF4444"           # Красный
        self.dark = "#1F2937"             # Темный
        self.darker = "#111827"           # Очень темный
        self.text_dark = "#374151"        # Темный текст
        self.text_light = "#F9FAFB"       # Светлый текст
        self.light = "#F3F4F6"            # Светлый
        self.extra_light = "#F9FAFB"      # Очень светлый
        self.gray = "#6B7280"             # Серый
        self.light_gray = "#E5E7EB"       # Светло-серый
        
        # Градиенты (симуляция через цвета)
        self.gradient_primary = ["#3B82F6", "#2563EB", "#1D4ED8", "#1E40AF"]
        self.gradient_secondary = ["#10B981", "#059669", "#047857", "#065F46"]
        
        # Цвета сообщений
        self.user_message_bg = "#EFF6FF"  # Очень светло-синий фон
        self.user_message_border = "#BFDBFE"  # Светло-синяя граница
        self.bot_message_bg = "#FFFFFF"  # Белый фон
        self.bot_message_border = "#E5E7EB"  # Светло-серая граница
        
        # Настройки шрифтов
        self.title_font = ("Segoe UI", 20, "bold")
        self.header_font = ("Segoe UI", 14, "bold")
        self.body_font = ("Segoe UI", 11)
        self.small_font = ("Segoe UI", 9)
        self.tiny_font = ("Segoe UI", 8)
        
        # Размеры и отступы
        self.padding = 20
        self.border_radius = 12
        self.button_radius = 8
        
    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        # Создаем закругленный прямоугольник на canvas
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def create_circle(self, parent, x, y, radius, **kwargs):
        # Создаем круг на parent (canvas)
        return parent.create_oval(x-radius, y-radius, x+radius, y+radius, **kwargs)
    
    def hex_to_rgb(self, hex_color):
        """Конвертирует HEX цвет в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb):
        """Конвертирует RGB цвет в HEX"""
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def adjust_color(self, hex_color, factor):
        """Изменяет яркость цвета в формате HEX"""
        rgb = self.hex_to_rgb(hex_color)
        new_rgb = tuple(min(255, int(c * factor)) for c in rgb)
        return self.rgb_to_hex(new_rgb)
    
    def create_gradient_image(self, width, height, color1, color2, horizontal=True):
        """Создает градиентное изображение между двумя цветами"""
        base = Image.new('RGBA', (width, height), color1)
        top = Image.new('RGBA', (width, height), color2)
        
        mask = Image.new('L', (width, height))
        mask_data = []
        
        for y in range(height):
            for x in range(width):
                if horizontal:
                    mask_data.append(int(255 * (x / width)))
                else:
                    mask_data.append(int(255 * (y / height)))
        
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    
    def create_shadow_image(self, width, height, radius=5, opacity=150):
        """Создает эффект тени для элементов интерфейса"""
        # Создаем изображение с прозрачным фоном
        shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Создаем черный прямоугольник немного меньше основного размера
        shadowDraw = ImageDraw.Draw(shadow)
        shadowDraw.rectangle(
            [radius, radius, width-radius, height-radius],
            fill=(0, 0, 0, opacity)
        )
        
        # Применяем размытие
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
        return shadow

class OllamaChat(ModernWidget):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("Ollama Chat")
        self.root.geometry("1080x800")
        self.root.minsize(900, 650)
        
        # Основной фон приложения
        self.bg_color = self.light
        self.root.configure(bg=self.bg_color)
        
        # Настройки API
        self.api_url = "http://localhost:11434/api/generate"
        self.model = "llama3"  # Модель по умолчанию
        
        # Инициализация анимации
        self.typing_animation_id = None
        self.typing_dots = ""
        
        # Эффекты для элементов
        self.current_animation = None
        self.animation_frames = []
        
        # История сообщений
        self.messages_history = []
        
        # Загрузка ресурсов и изображений
        self.load_resources()
        
        # Создание интерфейса
        self.create_ui()
        
        # Анимируем появление интерфейса
        self.animate_startup()
    
    def load_resources(self):
        """Загрузка всех необходимых ресурсов и изображений"""
        try:
            # Создаем пользовательские изображения и иконки
            self.create_custom_images()
            
            # Загружаем логотипы и иконки
            logo_size = 42
            self.logo_image = self.create_logo(logo_size)
            
            # Иконки для сообщений
            self.bot_icon = self.create_icon("bot")
            self.user_icon = self.create_icon("user")
            
            # Иконки действий
            self.send_icon = self.create_action_icon("send")
            self.settings_icon = self.create_action_icon("settings")
            self.refresh_icon = self.create_action_icon("refresh")
            
            # Создаем шаблон карточки сообщения
            self.create_message_card_template()
            
        except Exception as e:
            print(f"Ошибка загрузки ресурсов: {e}")
            # Создаем пустые изображения, если возникает ошибка
            empty = Image.new('RGBA', (32, 32), color=(255, 255, 255, 0))
            self.bot_icon = ImageTk.PhotoImage(empty)
            self.user_icon = ImageTk.PhotoImage(empty)
            self.logo_image = ImageTk.PhotoImage(empty)
            self.send_icon = ImageTk.PhotoImage(empty)
    
    def create_custom_images(self):
        """Создает все пользовательские изображения"""
        # Фоновые градиенты
        width, height = 300, 70
        gradient = self.create_gradient_image(width, height, self.primary, self.primary_dark, horizontal=False)
        self.header_bg = ImageTk.PhotoImage(gradient)
        
        # Другие элементы (кнопки, разделители и т.д.)
        self.create_custom_button_images()
    
    def create_custom_button_images(self):
        """Создает изображения для кнопок разных состояний"""
        # Основная кнопка
        width, height = 120, 40
        # Обычное состояние
        normal = self.create_gradient_image(width, height, self.primary, self.primary_dark, horizontal=False)
        # Добавляем закругленные углы через маску
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=self.button_radius, fill=255)
        normal.putalpha(mask)
        self.button_normal = ImageTk.PhotoImage(normal)
        
        # Состояние при наведении
        hover = self.create_gradient_image(width, height, self.adjust_color(self.primary, 1.1), 
                                         self.primary, horizontal=False)
        hover.putalpha(mask)
        self.button_hover = ImageTk.PhotoImage(hover)
        
        # Состояние при нажатии
        pressed = self.create_gradient_image(width, height, self.primary_dark, 
                                           self.primary, horizontal=False)
        pressed.putalpha(mask)
        self.button_pressed = ImageTk.PhotoImage(pressed)
    
    def create_message_card_template(self):
        """Создает шаблон для карточки сообщения с тенью"""
        width, height = 400, 150
        
        # Создаем основное изображение с закругленными углами
        card = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle([(0, 0), (width, height)], radius=self.border_radius, 
                             fill=self.extra_light)
        
        # Создаем тень
        shadow = self.create_shadow_image(width+20, height+20, radius=8)
        
        # Объединяем изображения
        final_card = Image.new('RGBA', (width+20, height+20), (0, 0, 0, 0))
        final_card.paste(shadow, (0, 0), shadow)
        final_card.paste(card, (10, 5), card)
        
        # Сохраняем как шаблон
        self.message_card_template = final_card
    
    def create_logo(self, size):
        """Создает логотип приложения"""
        logo = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        
        # Создаем градиентный круг
        draw.ellipse([0, 0, size, size], fill=self.primary)
        
        # Добавляем букву "O" в центре
        if hasattr(draw, 'text'):
            # Для PIL, поддерживающего шрифты
            try:
                font_size = int(size * 0.6)
                font = ImageFont.truetype("arial.ttf", font_size)
                # Центрируем текст
                text_width, text_height = draw.textsize("O", font=font)
                position = ((size - text_width) // 2, (size - text_height) // 2 - int(size * 0.05))
                draw.text(position, "O", fill=self.text_light, font=font)
            except:
                # Если шрифт не найден, рисуем круг
                inner_margin = int(size * 0.3)
                draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                          fill=self.text_light)
        else:
            # Если text не поддерживается, рисуем круг
            inner_margin = int(size * 0.3)
            draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                       fill=self.text_light)
        
        # Добавляем блик
        highlight_size = int(size * 0.2)
        highlight_pos = int(size * 0.15)
        draw.ellipse([highlight_pos, highlight_pos, 
                     highlight_pos+highlight_size, highlight_pos+highlight_size], 
                    fill=(255, 255, 255, 180))
        
        return ImageTk.PhotoImage(logo)
        
    def create_icon(self, icon_type):
        """Создает современные иконки пользователя и бота"""
        size = 64
        icon = Image.new('RGBA', (size, size), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(icon)
        
        if icon_type == "bot":
            # Создаем стильную иконку робота
            # Фон
            draw.ellipse([4, 4, size-4, size-4], fill=self.primary)
            # Лицо робота
            face_margin = int(size * 0.2)
            face_size = size - (face_margin * 2)
            draw.rounded_rectangle([face_margin, face_margin+2, 
                                  size-face_margin, size-face_margin+2], 
                                 radius=int(face_size * 0.2),
                                 fill=self.text_light)
            # Глаза
            eye_size = int(size * 0.12)
            eye_pos_y = int(size * 0.35)
            draw.ellipse([int(size * 0.3), eye_pos_y, 
                         int(size * 0.3) + eye_size, eye_pos_y + eye_size], 
                        fill=self.primary)
            draw.ellipse([int(size * 0.58), eye_pos_y, 
                         int(size * 0.58) + eye_size, eye_pos_y + eye_size], 
                        fill=self.primary)
            # Антенна
            antenna_width = int(size * 0.08)
            draw.rectangle([int(size / 2) - antenna_width/2, int(size * 0.05), 
                          int(size / 2) + antenna_width/2, face_margin],
                         fill=self.primary)
            draw.ellipse([int(size / 2) - antenna_width, 0, 
                         int(size / 2) + antenna_width, antenna_width*2], 
                        fill=self.warning)
            # Улыбка
            smile_y = int(size * 0.55)
            smile_width = int(size * 0.4)
            smile_start_x = int(size / 2) - smile_width/2
            for i in range(3):
                draw.line([smile_start_x, smile_y + i, 
                          smile_start_x + smile_width, smile_y + i], 
                         fill=self.primary, width=1)
        else:
            # Создаем стильную иконку пользователя
            # Фон
            draw.ellipse([4, 4, size-4, size-4], fill=self.accent)
            # Голова
            head_size = int(size * 0.35)
            head_pos_y = int(size * 0.25)
            draw.ellipse([int(size / 2) - head_size/2, head_pos_y,
                        int(size / 2) + head_size/2, head_pos_y + head_size], 
                       fill=self.text_light)
            # Тело
            body_width = int(head_size * 1.2)
            body_height = int(size * 0.3)
            body_top = head_pos_y + head_size - int(size * 0.05)
            draw.rectangle([int(size / 2) - body_width/2, body_top,
                         int(size / 2) + body_width/2, body_top + body_height],
                        fill=self.text_light)
            # Закругление снизу тела
            draw.ellipse([int(size / 2) - body_width/2, body_top + body_height - int(size * 0.08),
                        int(size / 2) + body_width/2, body_top + body_height + int(size * 0.08)],
                       fill=self.text_light)
        
        # Применяем эффект размытия для мягкой тени
        shadow = icon.copy()
        shadow = shadow.filter(ImageFilter.GaussianBlur(2))
        
        # Объединяем с оригиналом
        icon_with_shadow = Image.new('RGBA', icon.size, (0, 0, 0, 0))
        icon_with_shadow.paste(shadow, (2, 2), shadow)
        icon_with_shadow.paste(icon, (0, 0), icon)
        
        return ImageTk.PhotoImage(icon_with_shadow)
    
    def create_action_icon(self, icon_type):
        """Создает иконки для действий пользовательского интерфейса"""
        size = 32
        icon = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        if icon_type == "send":
            # Иконка отправки (бумажный самолетик)
            points = [
                (int(size * 0.2), int(size * 0.2)),  # Верхний левый
                (int(size * 0.8), int(size * 0.5)),  # Правый центр
                (int(size * 0.2), int(size * 0.8)),  # Нижний левый
                (int(size * 0.4), int(size * 0.5)),  # Центральный выступ
            ]
            draw.polygon(points, fill=self.primary)
        
        elif icon_type == "settings":
            # Иконка настроек (шестеренка)
            outer_radius = int(size * 0.4)
            inner_radius = int(size * 0.2)
            center = (int(size / 2), int(size / 2))
            
            # Внешний круг
            draw.ellipse([center[0] - outer_radius, center[1] - outer_radius,
                        center[0] + outer_radius, center[1] + outer_radius], 
                       fill=self.gray)
            
            # Внутренний круг
            draw.ellipse([center[0] - inner_radius, center[1] - inner_radius,
                        center[0] + inner_radius, center[1] + inner_radius], 
                       fill=self.light)
            
            # Зубчики
            for i in range(8):
                angle = math.radians(i * 45)
                tooth_length = int(size * 0.2)
                x1 = center[0] + int(outer_radius * math.cos(angle))
                y1 = center[1] + int(outer_radius * math.sin(angle))
                x2 = center[0] + int((outer_radius + tooth_length) * math.cos(angle))
                y2 = center[1] + int((outer_radius + tooth_length) * math.sin(angle))
                draw.line([(x1, y1), (x2, y2)], fill=self.gray, width=int(size * 0.1))
        
        elif icon_type == "refresh":
            # Иконка обновления (круговая стрелка)
            center = (int(size / 2), int(size / 2))
            radius = int(size * 0.35)
            
            # Рисуем круговую стрелку
            for angle in range(30, 330, 1):
                rad = math.radians(angle)
                x = center[0] + int(radius * math.cos(rad))
                y = center[1] + int(radius * math.sin(rad))
                draw.point((x, y), fill=self.primary)
            
            # Наконечник стрелки
            arrow_size = int(size * 0.15)
            arrow_angle = math.radians(30)
            arrow_x = center[0] + int(radius * math.cos(arrow_angle))
            arrow_y = center[1] + int(radius * math.sin(arrow_angle))
            
            arrow_points = [
                (arrow_x, arrow_y),
                (arrow_x - arrow_size, arrow_y - arrow_size/2),
                (arrow_x - arrow_size/2, arrow_y + arrow_size)
            ]
            draw.polygon(arrow_points, fill=self.primary)
        
        return ImageTk.PhotoImage(icon)
    
    def create_ui(self):
        """Создание современного пользовательского интерфейса"""
        # Создаем основной контейнер с тенью
        self.main_container = tk.Frame(self.root, bg=self.light)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Создание боковой панели (левой)
        self.create_sidebar()
        
        # Создание основного содержимого
        self.main_content = tk.Frame(self.main_container, bg=self.light)
        self.main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем заголовок
        self.create_header()
        
        # Создаем область чата
        self.create_chat_area()
        
        # Создаем нижнюю панель ввода
        self.create_input_area()
        
        # Добавляем приветственное сообщение
        self.add_bot_message("Привет! Я бот, работающий через Ollama. Чем могу помочь сегодня?")
    
    def create_sidebar(self):
        """Создает стильную боковую панель"""
        self.sidebar = tk.Frame(self.main_container, bg=self.darker, width=80)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Логотип в верхней части сайдбара
        logo_frame = tk.Frame(self.sidebar, bg=self.darker, height=80)
        logo_frame.pack(fill=tk.X, pady=(20, 10))
        
        logo_label = tk.Label(logo_frame, image=self.logo_image, 
                             bg=self.darker, bd=0)
        logo_label.image = self.logo_image
        logo_label.pack(pady=5)
        
        # Разделительная линия
        separator = tk.Frame(self.sidebar, height=2, bg=self.dark)
        separator.pack(fill=tk.X, padx=15, pady=10)
        
        # Создаем боковые кнопки меню (иконки)
        self.create_sidebar_buttons()
    
    def create_sidebar_buttons(self):
        """Создает анимированные кнопки в сайдбаре"""
        # Контейнер для кнопок
        button_container = tk.Frame(self.sidebar, bg=self.darker)
        button_container.pack(fill=tk.X, padx=10, pady=5)
        
        # Функция для эффекта при наведении
        def on_enter(e, button, color):
            button.config(bg=color)
            
        def on_leave(e, button):
            button.config(bg=self.darker)
            
        # Функция для создания иконки-кнопки
        def create_sidebar_button(icon, text, command=None):
            btn_frame = tk.Frame(button_container, bg=self.darker, height=60)
            btn_frame.pack(fill=tk.X, pady=5)
            
            btn = tk.Label(btn_frame, image=icon, bg=self.darker, cursor="hand2")
            btn.image = icon
            btn.pack(pady=5)
            
            text_label = tk.Label(btn_frame, text=text, font=self.small_font,
                                bg=self.darker, fg=self.light_gray)
            text_label.pack()
            
            btn.bind("<Enter>", lambda e: on_enter(e, btn_frame, self.dark))
            btn.bind("<Leave>", lambda e: on_leave(e, btn_frame))
            
            if command:
                btn.bind("<Button-1>", command)
        
        # Создаем несколько кнопок меню
        create_sidebar_button(self.bot_icon, "Чат")
        create_sidebar_button(self.settings_icon, "Настройки")
        create_sidebar_button(self.refresh_icon, "Обновить")
    
    def create_header(self):
        """Создает стильную верхнюю панель заголовка"""
        # Создаем контейнер заголовка с градиентным фоном
        self.header = tk.Frame(self.main_content, bg=self.light, height=80)
        self.header.pack(fill=tk.X, pady=(0, 10))
        self.header.pack_propagate(False)
        
        # Левая часть заголовка (название приложения)
        header_left = tk.Frame(self.header, bg=self.light)
        header_left.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        title_label = tk.Label(header_left, text="Ollama Chat", font=self.title_font, 
                              bg=self.light, fg=self.dark)
        title_label.pack(side=tk.LEFT, pady=20)
        
        # Подзаголовок
        subtitle = tk.Label(header_left, text="Общение с AI моделями", 
                          font=self.small_font, bg=self.light, fg=self.gray)
        subtitle.pack(side=tk.LEFT, padx=10, pady=25)
        
        # Правая часть заголовка (выбор модели)
        header_right = tk.Frame(self.header, bg=self.light)
        header_right.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        model_container = tk.Frame(header_right, bg=self.light, pady=5)
        model_container.pack(side=tk.TOP, fill=tk.X, pady=15)
        
        model_label = tk.Label(model_container, text="Модель:", 
                              font=self.body_font, bg=self.light, fg=self.gray)
        model_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Стилизуем выпадающий список моделей
        self.model_var = tk.StringVar(value=self.model)
        models = ["llama3", "llama2", "mistral", "gemma", "phi"]
        
        self.create_custom_combobox(model_container, self.model_var, models)
        
        # Разделитель под заголовком
        separator = tk.Frame(self.main_content, height=2, bg=self.light_gray)
        separator.pack(fill=tk.X, padx=0, pady=(0, 10))
    
    def create_custom_combobox(self, parent, variable, values):
        """Создает стильный выпадающий список"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Настройка стиля Combobox
        style.configure('Custom.TCombobox', 
                      fieldbackground=self.extra_light,
                      background=self.primary,
                      foreground=self.dark,
                      arrowcolor=self.primary,
                      selectbackground=self.primary,
                      selectforeground=self.light,
                      borderwidth=0,
                      font=self.body_font)
        
        style.map('Custom.TCombobox',
                 fieldbackground=[('readonly', self.extra_light)],
                 selectbackground=[('readonly', self.primary_light)],
                 selectforeground=[('readonly', self.dark)])
        
        self.model_dropdown = ttk.Combobox(parent, textvariable=variable, 
                                         values=values, width=12, font=self.body_font,
                                         style='Custom.TCombobox', state="readonly")
        self.model_dropdown.pack(side=tk.LEFT)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.update_model)
        
        # Создаем рамку вокруг выпадающего списка для имитации тени
        frame = tk.Frame(parent, highlightbackground=self.light_gray, 
                        highlightthickness=1, bd=0)
        frame.place(in_=self.model_dropdown, x=-1, y=-1, 
                  width=self.model_dropdown.winfo_reqwidth()+2, 
                  height=self.model_dropdown.winfo_reqheight()+2)
        frame.lower(self.model_dropdown)
    
    def create_chat_area(self):
        """Создает современную область чата с улучшенным дизайном"""
        # Основной контейнер для чата
        self.chat_area = tk.Frame(self.main_content, bg=self.light)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)
        
        # Контейнер сообщений с прокруткой
        self.messages_canvas = tk.Canvas(self.chat_area, bg=self.light, 
                                       highlightthickness=0)
        
        # Стилизация полосы прокрутки
        style = ttk.Style()
        style.configure("Modern.Vertical.TScrollbar", 
                      background=self.light, 
                      troughcolor=self.light,
                      arrowcolor=self.primary,
                      borderwidth=0,
                      relief="flat")
        
        style.map("Modern.Vertical.TScrollbar",
                background=[("active", self.light_gray), ("disabled", self.light)],
                troughcolor=[("active", self.light), ("disabled", self.light)])
        
        self.messages_scrollbar = ttk.Scrollbar(self.chat_area, orient="vertical",
                                              command=self.messages_canvas.yview,
                                              style="Modern.Vertical.TScrollbar")
        
        self.messages_container = tk.Frame(self.messages_canvas, bg=self.light)
        self.messages_container.bind(
            "<Configure>",
            lambda e: self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        )
        
        # Настройка рамки для сообщений
        self.messages_frame = self.messages_canvas.create_window(
            (0, 0), window=self.messages_container, anchor="nw", 
            width=self.messages_canvas.winfo_reqwidth())
        
        # Обновление ширины окна сообщений при изменении размера
        def configure_message_frame(event):
            canvas_width = event.width
            self.messages_canvas.itemconfig(self.messages_frame, width=canvas_width)
        
        self.messages_canvas.bind('<Configure>', configure_message_frame)
        self.messages_canvas.configure(yscrollcommand=self.messages_scrollbar.set)
        
        self.messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_input_area(self):
        """Создает стильную область ввода сообщений"""
        # Статус бар над полем ввода
        self.status_frame = tk.Frame(self.main_content, bg=self.light, height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))
        
        self.status_label = tk.Label(self.status_frame, text="Готов к общению", 
                                   bg=self.light, fg=self.secondary,
                                   font=self.small_font)
        self.status_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Нижняя панель ввода
        self.input_area = tk.Frame(self.main_content, bg=self.light_gray, height=120)
        self.input_area.pack(fill=tk.X, side=tk.BOTTOM, before=self.status_frame, pady=(10, 0))
        
        # Создаем внутренний контейнер с тенью
        input_inner = tk.Frame(self.input_area, bg=self.light_gray)
        input_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Создаем стилизованное поле ввода
        input_frame = tk.Frame(input_inner, bg=self.extra_light, bd=0)
        input_frame.pack(fill=tk.X, pady=0)
        
        # Добавляем тень (имитация)
        input_frame.config(highlightbackground=self.light_gray, 
                         highlightthickness=1, bd=0)
        
        # Текстовое поле
        self.input_field = tk.Text(input_frame, height=3, bg=self.extra_light, 
                                 fg=self.dark, font=self.body_font, bd=0, 
                                 padx=15, pady=10, wrap=tk.WORD,
                                 insertbackground=self.dark)
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Плейсхолдер для текстового поля
        self.input_field.insert("1.0", "Введите сообщение...")
        self.input_field.config(fg=self.gray)
        
        # Обработчики фокуса для плейсхолдера
        def on_focus_in(event):
            if self.input_field.get("1.0", tk.END).strip() == "Введите сообщение...":
                self.input_field.delete("1.0", tk.END)
                self.input_field.config(fg=self.dark)
                
        def on_focus_out(event):
            if not self.input_field.get("1.0", tk.END).strip():
                self.input_field.insert("1.0", "Введите сообщение...")
                self.input_field.config(fg=self.gray)
        
        self.input_field.bind("<FocusIn>", on_focus_in)
        self.input_field.bind("<FocusOut>", on_focus_out)
        self.input_field.bind("<Return>", self.send_message_event)
        self.input_field.bind("<Control-Return>", self.insert_newline)
        
        # Кнопка отправки с иконкой
        self.create_send_button(input_frame)
    
    def create_send_button(self, parent):
        """Создает анимированную кнопку отправки"""
        # Контейнер для кнопки
        send_button_frame = tk.Frame(parent, bg=self.extra_light)
        send_button_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Кнопка отправки с градиентом и тенью
        self.send_button = tk.Label(send_button_frame, text="Отправить", 
                                   bg=self.primary, fg=self.text_light,
                                   font=self.body_font, cursor="hand2",
                                   padx=15, pady=8)
        self.send_button.pack(side=tk.RIGHT)
        
        # Добавляем эффект закругленных углов
        self.send_button.bind("<Enter>", lambda e: self.button_hover_effect(e, True))
        self.send_button.bind("<Leave>", lambda e: self.button_hover_effect(e, False))
        self.send_button.bind("<Button-1>", lambda e: self.button_click_effect(e))
        self.send_button.bind("<ButtonRelease-1>", 
                             lambda e: (self.button_hover_effect(e, True), self.send_message()))
    
    def button_hover_effect(self, event, hovering):
        """Создает эффект при наведении на кнопку"""
        if hovering:
            event.widget.config(bg=self.adjust_color(self.primary, 1.1))
        else:
            event.widget.config(bg=self.primary)
    
    def button_click_effect(self, event):
        """Создает эффект при нажатии на кнопку"""
        event.widget.config(bg=self.primary_dark)
    
    def animate_startup(self):
        """Анимирует появление интерфейса при запуске"""
        # Сначала скрываем все элементы
        self.main_content.pack_forget()
        self.sidebar.pack_forget()
        
        # Функция для плавного появления элементов
        def show_element(element, duration=300):
            element.pack_configure(**element._pack_info)
            self.root.update_idletasks()
            
        # Сохраняем информацию о размещении
        self.sidebar._pack_info = {
            'side': tk.LEFT, 
            'fill': tk.Y
        }
        self.main_content._pack_info = {
            'side': tk.LEFT, 
            'fill': tk.BOTH, 
            'expand': True
        }
        
        # Анимируем появление элементов с задержкой
        self.root.after(100, lambda: show_element(self.sidebar))
        self.root.after(300, lambda: show_element(self.main_content))
    
    def update_model(self, event=None):
        """Обновляет выбранную модель и отображает уведомление"""
        old_model = self.model
        self.model = self.model_var.get()
        
        # Добавляем сообщение только если модель изменилась
        if old_model != self.model:
            # Показываем красивое уведомление о смене модели
            self.show_notification(f"Модель изменена на {self.model}", 
                                  bg_color=self.light_gray, icon="settings")
    
    def show_notification(self, message, bg_color=None, duration=3000, icon=None):
        """Показывает стильное уведомление с анимацией"""
        if bg_color is None:
            bg_color = self.primary_light
            
        # Фрейм уведомления с тенью
        notif_frame = tk.Frame(self.messages_container, bg=self.light)
        notif_frame.pack(fill=tk.X, padx=20, pady=10, anchor=tk.CENTER)
        
        # Внутренний контейнер уведомления
        notif_inner = tk.Frame(notif_frame, bg=bg_color, padx=15, pady=10)
        notif_inner.pack(anchor=tk.CENTER)
        
        # Скругление углов (имитация через внешнюю границу)
        notif_inner.config(highlightbackground=self.light_gray, 
                         highlightthickness=1, bd=0)
        
        # Если есть иконка, добавляем её
        if icon == "settings":
            icon_label = tk.Label(notif_inner, image=self.settings_icon, bg=bg_color)
            icon_label.image = self.settings_icon
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Сообщение уведомления
        notif_text = tk.Label(notif_inner, text=message, font=self.body_font, 
                            bg=bg_color, fg=self.dark)
        notif_text.pack(side=tk.LEFT)
        
        # Прокрутка вниз
        self.root.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
        # Анимация появления и исчезновения
        for i in range(10):
            alpha = i / 10.0
            notif_inner.config(bg=self.blend_colors(self.light, bg_color, alpha))
            self.root.update_idletasks()
            time.sleep(0.02)
        
        # Автоматическое удаление через duration миллисекунд
        self.root.after(duration, lambda: self.fade_out_widget(notif_frame))
    
    def fade_out_widget(self, widget, steps=10, delay=20):
        """Плавное исчезновение виджета"""
        def step(i):
            if i > 0:
                widget.config(bg=self.adjust_color(self.light, 1.0 - i/steps))
                self.root.after(delay, lambda: step(i-1))
            else:
                widget.destroy()
        
        step(steps)
    
    def blend_colors(self, color1, color2, alpha):
        """Смешивает два цвета с коэффициентом alpha"""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        
        blended = tuple(int(c1 * (1 - alpha) + c2 * alpha) for c1, c2 in zip(rgb1, rgb2))
        return self.rgb_to_hex(blended)
    
    def insert_newline(self, event):
        """Вставляет новую строку в поле ввода"""
        self.input_field.insert(tk.INSERT, "\n")
        return "break"
    
    def send_message_event(self, event):
        """Обработчик события нажатия клавиши Enter для отправки сообщения"""
        # Предотвращаем отправку, если в поле только placeholder
        if self.input_field.get("1.0", tk.END).strip() == "Введите сообщение...":
            return "break"
            
        self.send_message()
        return "break"  # Предотвращает стандартное действие клавиши Enter
    
    def send_message(self):
        """Отправляет сообщение пользователя и запрашивает ответ от бота"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        # Проверяем, что сообщение не является плейсхолдером
        if message and message != "Введите сообщение...":
            self.input_field.delete("1.0", tk.END)
            
            # Убираем фокус с поля ввода для активации плейсхолдера
            self.root.focus_set()
            
            # Добавляем сообщение пользователя с эффектом появления
            self.add_user_message(message)
            
            # Запуск запроса в отдельном потоке
            threading.Thread(target=self.get_response, args=(message,), daemon=True).start()
    
    def add_user_message(self, message):
        """Добавляет сообщение пользователя в чат"""
        self.add_message("Вы", message, is_user=True)
    
    def add_bot_message(self, message):
        """Добавляет сообщение бота в чат"""
        # Если есть анимация "typing", останавливаем её
        if self.typing_animation_id:
            self.root.after_cancel(self.typing_animation_id)
            self.typing_animation_id = None
            
            # Найти и удалить сообщение "печатает..."
            for widget in self.messages_container.winfo_children():
                if hasattr(widget, 'typing_indicator') and widget.typing_indicator:
                    self.fade_out_widget(widget, steps=5, delay=10)
                    break
        
        # Добавляем сообщение бота с небольшой задержкой для реалистичности
        self.root.after(300, lambda: self.add_message("Бот", message, is_user=False))
    
    def add_message(self, sender, message, is_user):
        """Добавляет новое сообщение в чат с современным стилем"""
        # Сохраняем сообщение в истории
        self.messages_history.append((sender, message, is_user))
        
        # Создаем карточку сообщения с тенью и закругленными углами
        message_card = tk.Frame(self.messages_container, bg=self.light)
        message_card.pack(fill=tk.X, padx=20, pady=10)
        
        # Анимация появления
        message_card.lower()  # Помещаем под остальные виджеты для анимации
        
        # Рамка сообщения
        message_frame = tk.Frame(message_card, bg=self.light)
        message_frame.pack(side=tk.RIGHT if is_user else tk.LEFT, anchor="e" if is_user else "w", 
                         fill=tk.X, padx=0, pady=0)
        
        # Верхняя часть сообщения (отправитель и время)
        header_frame = tk.Frame(message_frame, bg=self.light)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Иконка с эффектом тени
        icon = self.user_icon if is_user else self.bot_icon
        icon_label = tk.Label(header_frame, image=icon, bg=self.light)
        icon_label.image = icon
        
        # Информация о сообщении
        info_frame = tk.Frame(header_frame, bg=self.light)
        
        sender_label = tk.Label(info_frame, text=sender, font=self.header_font, 
                              bg=self.light, fg=self.dark)
        
        time_label = tk.Label(info_frame, text=datetime.now().strftime("%H:%M"), 
                            font=self.small_font, bg=self.light, fg=self.gray)
        
        # Размещение в зависимости от отправителя (справа или слева)
        if is_user:
            icon_label.pack(side=tk.RIGHT, padx=(10, 0))
            info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))
            sender_label.pack(anchor=tk.E)
            time_label.pack(anchor=tk.E)
        else:
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
            sender_label.pack(anchor=tk.W)
            time_label.pack(anchor=tk.W)
        
        # Контейнер для содержимого сообщения с фоном и тенью
        bg_color = self.user_message_bg if is_user else self.bot_message_bg
        border_color = self.user_message_border if is_user else self.bot_message_border
        
        # Создаем контейнер сообщения с эффектом тени
        text_container = tk.Frame(message_frame, bg=bg_color, bd=0)
        text_container.pack(fill=tk.X, padx=(50 if not is_user else 0, 50 if is_user else 0))
        
        # Эффект закругленных углов и тени
        text_container.config(highlightbackground=border_color, 
                            highlightthickness=1, 
                            relief="flat")
        
        # Стилизованный текст сообщения
        text_label = tk.Label(text_container, text=message, justify=tk.LEFT, 
                           bg=bg_color, fg=self.text_dark, 
                           wraplength=500, font=self.body_font,
                           padx=20, pady=15)
        text_label.pack(fill=tk.X, expand=True)
        
        # Анимируем появление сообщения
        self.animate_message_appear(message_card)
        
        # Прокрутка вниз до нового сообщения
        self.root.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
    
    def animate_message_appear(self, widget, steps=10, delay=20):
        """Анимирует появление нового сообщения"""
        # Сохраняем оригинальный фон
        original_bg = widget.cget('bg')
        
        # Начинаем со скрытого сообщения (бледного)
        widget.config(bg=self.light)
        
        def step(i):
            if i <= steps:
                # Постепенно меняем прозрачность
                alpha = i / steps
                blended = self.blend_colors(self.light, original_bg, alpha)
                widget.config(bg=blended)
                self.root.after(delay, lambda: step(i+1))
        
        # Запускаем анимацию
        step(1)
    
    def show_typing_indicator(self):
        """Показывает индикатор печати с анимацией"""
        # Создаем новый frame для индикатора
        typing_frame = tk.Frame(self.messages_container, bg=self.light)
        typing_frame.typing_indicator = True  # Метка для идентификации
        typing_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Рамка для индикатора
        indicator_frame = tk.Frame(typing_frame, bg=self.light)
        indicator_frame.pack(side=tk.LEFT, anchor="w", padx=0, pady=0)
        
        # Иконка бота
        icon_label = tk.Label(indicator_frame, image=self.bot_icon, bg=self.light)
        icon_label.image = self.bot_icon
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Стилизованный индикатор печати
        typing_container = tk.Frame(indicator_frame, bg=self.light_gray, 
                                  padx=10, pady=8)
        typing_container.pack(side=tk.LEFT, padx=5)
        
        # Эффект закругленных углов
        typing_container.config(highlightbackground=self.light_gray, 
                              highlightthickness=1, relief="flat")
        
        # Текст "печатает..." с анимацией точек
        self.typing_label = tk.Label(typing_container, text="печатает...", 
                                   font=self.small_font, bg=self.light_gray, 
                                   fg=self.gray)
        self.typing_label.pack(side=tk.LEFT)
        
        # Индикаторы (точки) для анимации
        self.dot_labels = []
        for i in range(3):
            dot = tk.Label(typing_container, text="•", font=("Segoe UI", 12, "bold"),
                         bg=self.light_gray, fg=self.gray)
            dot.pack(side=tk.LEFT, padx=2)
            self.dot_labels.append(dot)
        
        # Запускаем анимацию
        self.animate_typing_dots()
        
        # Прокрутка вниз
        self.root.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
        # Применяем эффект появления
        self.animate_message_appear(typing_frame, steps=5, delay=30)
        
        return typing_frame
    
    def animate_typing_dots(self):
        """Анимация точек загрузки для индикатора печати"""
        if hasattr(self, 'dot_labels') and self.dot_labels:
            # Циклически меняем цвета точек
            colors = [
                self.primary_light,
                self.primary,
                self.primary_dark,
                self.gray
            ]
            
            # Обновляем цвета с эффектом пульсации
            for i, dot in enumerate(self.dot_labels):
                color_index = (i + self.typing_dots.count('.')) % len(colors)
                dot.config(fg=colors[color_index])
            
            # Обновляем счетчик для следующей анимации
            self.typing_dots = '.' * ((len(self.typing_dots) + 1) % 4)
            
            # Продолжаем анимацию
            self.typing_animation_id = self.root.after(300, self.animate_typing_dots)
    
    def get_response(self, message):
        """Получает ответ от API Ollama с анимацией ожидания"""
        # Обновляем статус и покажем индикатор загрузки
        self.status_label.config(text="Запрос к Ollama...", fg=self.warning)
        
        # Показываем анимированный индикатор печати
        typing_frame = self.show_typing_indicator()
        
        try:
            data = {
                "model": self.model,
                "prompt": message,
                "stream": False
            }
            
            response = requests.post(self.api_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result.get("response", "Извините, не удалось получить ответ.")
                
                # Небольшая задержка для реалистичности
                time.sleep(0.5)
                
                # Удаляем индикатор печати
                self.fade_out_widget(typing_frame, steps=5, delay=10)
                
                # Добавляем ответ бота
                self.add_bot_message(bot_response)
                self.status_label.config(text="Готов к общению", fg=self.secondary)
            else:
                # Удаляем индикатор печати
                self.fade_out_widget(typing_frame, steps=5, delay=10)
                
                # Показываем ошибку
                error_message = f"Ошибка API: {response.status_code}"
                self.add_bot_message(error_message)
                self.status_label.config(text=error_message, fg=self.danger)
                
        except Exception as e:
            # Удаляем индикатор печати
            self.fade_out_widget(typing_frame, steps=5, delay=10)
            
            # Показываем сообщение об ошибке
            error_message = f"Ошибка: {str(e)}"
            self.add_bot_message(error_message)
            self.status_label.config(text=error_message, fg=self.danger)

if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaChat(root)
    root.mainloop() 