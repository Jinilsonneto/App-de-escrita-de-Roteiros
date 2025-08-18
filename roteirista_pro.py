import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk, colorchooser, simpledialog
import os
import sys
import json
from datetime import datetime
import re
from PIL import Image, ImageTk
import tempfile
import subprocess
import hashlib
from cryptography.fernet import Fernet
import base64
import time
import threading
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class ScriptWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roteirista Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')  # Fundo preto
        
        # Configurar cores
        self.bg_color = '#0a0a0a'
        self.fg_color = '#ffffff'
        self.blue_color = '#003366'
        self.highlight_color = '#0066cc'
        self.secondary_color = '#1a1a1a'
        self.accent_color = '#ff9900'
        self.cursor_color = '#00ff00'
        self.line_highlight_color = '#1a1a2e'
        
        # Configurar fonte padrão
        self.default_font = font.Font(family="Courier", size=12)
        self.title_font = font.Font(family="Arial", size=14, weight="bold")
        
        # Variável para controlar o arquivo atual
        self.current_file = None
        self.current_password = None
        
        # Configurações do aplicativo
        self.settings = {
            'auto_save': True,
            'auto_save_interval': 5,  # minutos
            'last_dir': os.path.expanduser('~'),
            'theme': 'dark',
            'font_size': 12,
            'font_family': 'Courier',
            'show_line_numbers': True,
            'word_wrap': True,
            'highlight_current_line': True,
            'show_cursor_position': True,
            'script_format': 'standard',  # standard, fountain, etc.
            'page_width': 80,  # caracteres por linha
            'character_width': 40,  # caracteres para nomes de personagens
            'dialogue_width': 35,  # caracteres para diálogos
            'action_width': 60,  # caracteres para ações
            'scene_width': 60  # caracteres para cenas
        }
        
        # Carregar configurações
        self.load_settings()
        
        # Aplicar tema
        self.apply_theme()
        
        # Criar componentes da interface
        self.create_toolbar()
        self.create_menu()
        self.create_status_bar()
        self.create_sidebar()
        self.create_text_editor()
        
        # Atalhos de teclado
        self.setup_shortcuts()
        
        # Iniciar auto-salvamento
        self.auto_save()
        
        # Personagens e cenas
        self.characters = []
        self.scenes = []
        
        # Estado da busca
        self.search_term = ""
        self.search_matches = []
        self.current_match = -1
        
        # Estado do cursor
        self.cursor_visible = True
        self.cursor_blink()
        
        # Estado da linha atual
        self.current_line_tag = None
        
        # Timer para salvar
        self.last_saved_time = time.time()
        
    def apply_theme(self):
        if self.settings['theme'] == 'light':
            self.bg_color = '#f0f0f0'
            self.fg_color = '#000000'
            self.blue_color = '#4a86e8'
            self.highlight_color = '#1155cc'
            self.secondary_color = '#e0e0e0'
            self.accent_color = '#ff6600'
            self.cursor_color = '#006600'
            self.line_highlight_color = '#e6e6e6'
        else:
            self.bg_color = '#0a0a0a'
            self.fg_color = '#ffffff'
            self.blue_color = '#003366'
            self.highlight_color = '#0066cc'
            self.secondary_color = '#1a1a1a'
            self.accent_color = '#ff9900'
            self.cursor_color = '#00ff00'
            self.line_highlight_color = '#1a1a2e'
    
    def create_toolbar(self):
        # Barra de ferramentas principal
        self.main_toolbar = tk.Frame(self.root, bg=self.secondary_color, height=40)
        self.main_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Barra de ferramentas de formatação
        self.format_toolbar = tk.Frame(self.root, bg=self.secondary_color, height=40)
        self.format_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Barra de ferramentas de elementos
        self.elements_toolbar = tk.Frame(self.root, bg=self.secondary_color, height=40)
        self.elements_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Botões da barra de ferramentas principal
        main_buttons = [
            ("Novo", self.new_file, "new.png"),
            ("Abrir", self.open_file, "open.png"),
            ("Salvar", self.save_file, "save.png"),
            ("Salvar Seguro", self.save_secure_file, "secure.png"),
            ("", None, ""),  # Separador
            ("Desfazer", self.undo, "undo.png"),
            ("Refazer", self.redo, "redo.png"),
            ("", None, ""),  # Separador
            ("Buscar", self.show_search_dialog, "search.png"),
            ("Substituir", self.show_replace_dialog, "replace.png"),
            ("", None, ""),  # Separador
            ("Estatísticas", self.show_stats, "stats.png"),
            ("Verificar Ortografia", self.check_spelling, "spell.png"),
            ("", None, ""),  # Separador
            ("PDF", self.export_pdf, "pdf.png"),
            ("Imprimir", self.print_script, "print.png")
        ]
        
        for text, command, icon in main_buttons:
            if text == "":
                # Separador
                separator = ttk.Separator(self.main_toolbar, orient='vertical')
                separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
            else:
                # Botão
                btn = tk.Button(self.main_toolbar, text=text, command=command,
                               bg=self.secondary_color, fg=self.fg_color,
                               bd=0, padx=10, pady=5)
                btn.pack(side=tk.LEFT, padx=2)
                
                # Adicionar tooltip
                self.create_tooltip(btn, text)
        
        # Botões da barra de ferramentas de formatação
        format_buttons = [
            ("Negrito", self.toggle_bold, "bold.png"),
            ("Itálico", self.toggle_italic, "italic.png"),
            ("Sublinhado", self.toggle_underline, "underline.png"),
            ("", None, ""),  # Separador
            ("Fonte", self.change_font, "font.png"),
            ("Cor", self.change_color, "color.png"),
            ("", None, ""),  # Separador
            ("Zoom In", self.zoom_in, "zoom_in.png"),
            ("Zoom Out", self.zoom_out, "zoom_out.png"),
            ("Zoom Normal", self.zoom_normal, "zoom_normal.png")
        ]
        
        for text, command, icon in format_buttons:
            if text == "":
                # Separador
                separator = ttk.Separator(self.format_toolbar, orient='vertical')
                separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
            else:
                # Botão
                btn = tk.Button(self.format_toolbar, text=text, command=command,
                               bg=self.secondary_color, fg=self.fg_color,
                               bd=0, padx=10, pady=5)
                btn.pack(side=tk.LEFT, padx=2)
                
                # Adicionar tooltip
                self.create_tooltip(btn, text)
        
        # Botões da barra de ferramentas de elementos
        elements_buttons = [
            ("Cena", self.insert_scene, "scene.png"),
            ("Personagem", self.insert_character, "character.png"),
            ("Diálogo", self.insert_dialogue, "dialogue.png"),
            ("Ação", self.insert_action, "action.png"),
            ("Transição", self.insert_transition, "transition.png"),
            ("Nota", self.insert_note, "note.png"),
            ("", None, ""),  # Separador
            ("Reformatar", self.reformat_script, "reformat.png"),
            ("Análise", self.analyze_script, "analyze.png")
        ]
        
        for text, command, icon in elements_buttons:
            if text == "":
                # Separador
                separator = ttk.Separator(self.elements_toolbar, orient='vertical')
                separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
            else:
                # Botão
                btn = tk.Button(self.elements_toolbar, text=text, command=command,
                               bg=self.secondary_color, fg=self.fg_color,
                               bd=0, padx=10, pady=5)
                btn.pack(side=tk.LEFT, padx=2)
                
                # Adicionar tooltip
                self.create_tooltip(btn, text)
    
    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, bg=self.secondary_color, fg=self.fg_color,
                            relief=tk.SOLID, borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.blue_color, fg=self.fg_color)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.blue_color, fg=self.fg_color)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Salvar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Como", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Salvar Seguro", command=self.save_secure_file, accelerator="Ctrl+Alt+S")
        file_menu.add_separator()
        file_menu.add_command(label="Importar", command=self.import_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar PDF", command=self.export_pdf, accelerator="Ctrl+E")
        file_menu.add_command(label="Exportar HTML", command=self.export_html)
        file_menu.add_command(label="Exportar Fountain", command=self.export_fountain)
        file_menu.add_separator()
        file_menu.add_command(label="Imprimir", command=self.print_script, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.exit_app, accelerator="Ctrl+Q")
        
        # Menu Editar
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.blue_color, fg=self.fg_color)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Refazer", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Colar", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Negrito", command=self.toggle_bold, accelerator="Ctrl+B")
        edit_menu.add_command(label="Itálico", command=self.toggle_italic, accelerator="Ctrl+I")
        edit_menu.add_command(label="Sublinhado", command=self.toggle_underline, accelerator="Ctrl+U")
        edit_menu.add_separator()
        edit_menu.add_command(label="Buscar", command=self.show_search_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Substituir", command=self.show_replace_dialog, accelerator="Ctrl+R")
        edit_menu.add_separator()
        edit_menu.add_command(label="Ir Para", command=self.go_to_line, accelerator="Ctrl+G")
        edit_menu.add_command(label="Selecionar Tudo", command=self.select_all, accelerator="Ctrl+A")
        
        # Menu Formato
        format_menu = tk.Menu(menubar, tearoff=0, bg=self.blue_color, fg=self.fg_color)
        menubar.add_cascade(label="Formato", menu=format_menu)
        format_menu.add_command(label="Personagem", command=self.insert_character, accelerator="Ctrl+P")
        format_menu.add_command(label="Diálogo", command=self.insert_dialogue, accelerator="Ctrl+D")
        format_menu.add_command(label="Ação", command=self.insert_action, accelerator="Ctrl+Shift+A")
        format_menu.add_command(label="Cena", command=self.insert_scene, accelerator="Ctrl+Shift+C")
        format_menu.add_command(label="Transição", command=self.insert_transition, accelerator="Ctrl+T")
        format_menu.add_command(label="Nota", command=self.insert_note, accelerator="Ctrl+Shift+N")
        format_menu.add_separator()
        format_menu.add_command(label="Reformatar Roteiro", command=self.reformat_script)
        format_menu.add_command(label="Configurar Formatação", command=self.configure_formatting)
        format_menu.add_separator()
        format_menu.add_command(label="Fonte", command=self.change_font)
        format_menu.add_command(label="Cor", command=self.change_color)
        format_menu.add_separator()
        format_menu.add_checkbutton(label="Quebra de Linha", command=self.toggle_word_wrap)
        format_menu.add_checkbutton(label="Números de Linha", command=self.toggle_line_numbers)
        format_menu.add_checkbutton(label="Destacar Linha Atual", command=self.toggle_line_highlight)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.blue_color, fg=self.fg_color)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_checkbutton(label="Auto-salvar", command=self.toggle_auto_save)
        tools_menu.add_command(label="Gerenciar Personagens", command=self.manage_characters)
        tools_menu.add_command(label="Gerenciar Cenas", command=self.manage_scenes)
        tools_menu.add_command(label="Contar Palavras", command=self.word_count)
        tools_menu.add_command(label="Estatísticas", command=self.show_stats)
        tools_menu.add_command(label="Verificar Ortografia", command=self.check_spelling)
        tools_menu.add_command(label="Analisar Roteiro", command=self.analyze_script)
        tools_menu.add_command(label="Tempo de Leitura", command=self.estimate_reading_time)
        tools_menu.add_separator()
        tools_menu.add_command(label="Configurações", command=self.show_settings)
        
        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.blue_color, fg=self.fg_color)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_radiobutton(label="Tema Escuro", command=lambda: self.change_theme('dark'))
        view_menu.add_radiobutton(label="Tema Claro", command=lambda: self.change_theme('light'))
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Zoom Normal", command=self.zoom_normal, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Barra de Ferramentas Principal", command=self.toggle_main_toolbar)
        view_menu.add_checkbutton(label="Barra de Formatação", command=self.toggle_format_toolbar)
        view_menu.add_checkbutton(label="Barra de Elementos", command=self.toggle_elements_toolbar)
        view_menu.add_checkbutton(label="Barra Lateral", command=self.toggle_sidebar)
        view_menu.add_checkbutton(label="Barra de Status", command=self.toggle_status_bar)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.blue_color, fg=self.fg_color)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Atalhos", command=self.show_shortcuts)
        help_menu.add_command(label="Tutorial", command=self.show_tutorial)
        help_menu.add_command(label="Guia de Formatação", command=self.show_formatting_guide)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def create_status_bar(self):
        # Barra de status
        self.status_bar = tk.Frame(self.root, bg=self.secondary_color, height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame para informações de status
        status_info_frame = tk.Frame(self.status_bar, bg=self.secondary_color)
        status_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Informações de status
        self.status_text = tk.StringVar()
        self.status_text.set("Pronto")
        
        self.status_label = tk.Label(status_info_frame, textvariable=self.status_text, 
                                    bg=self.secondary_color, fg=self.fg_color, 
                                    anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame para informações do documento
        doc_info_frame = tk.Frame(self.status_bar, bg=self.secondary_color)
        doc_info_frame.pack(side=tk.RIGHT)
        
        # Contador de palavras
        self.word_count_label = tk.Label(doc_info_frame, text="Palavras: 0", 
                                        bg=self.secondary_color, fg=self.fg_color, 
                                        padx=10)
        self.word_count_label.pack(side=tk.RIGHT)
        
        # Posição do cursor
        self.cursor_pos_label = tk.Label(doc_info_frame, text="Ln 1, Col 1", 
                                        bg=self.secondary_color, fg=self.fg_color, 
                                        padx=10)
        self.cursor_pos_label.pack(side=tk.RIGHT)
        
        # Formato do elemento atual
        self.element_format_label = tk.Label(doc_info_frame, text="Normal", 
                                           bg=self.secondary_color, fg=self.fg_color, 
                                           padx=10)
        self.element_format_label.pack(side=tk.RIGHT)
        
        # Indicador de salvamento
        self.save_indicator = tk.Label(doc_info_frame, text="●", 
                                      bg=self.secondary_color, fg=self.accent_color, 
                                      padx=5)
        self.save_indicator.pack(side=tk.RIGHT)
    
    def create_sidebar(self):
        # Frame do menu lateral
        self.sidebar = tk.Frame(self.root, bg=self.blue_color, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Botão para retrair/expandir
        self.toggle_button = tk.Button(self.sidebar, text="◀", command=self.toggle_sidebar, 
                                      bg=self.blue_color, fg=self.fg_color, bd=0)
        self.toggle_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Título do menu
        title_label = tk.Label(self.sidebar, text="Ferramentas de Roteiro", 
                              bg=self.blue_color, fg=self.fg_color, font=self.title_font)
        title_label.pack(pady=10)
        
        # Notebook para abas
        self.sidebar_notebook = ttk.Notebook(self.sidebar)
        self.sidebar_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de elementos
        elements_frame = tk.Frame(self.sidebar_notebook, bg=self.blue_color)
        self.sidebar_notebook.add(elements_frame, text="Elementos")
        
        # Funções de escrita
        self.functions = [
            ("Cena", self.insert_scene, "Ctrl+Shift+C"),
            ("Personagem", self.insert_character, "Ctrl+P"),
            ("Diálogo", self.insert_dialogue, "Ctrl+D"),
            ("Ação", self.insert_action, "Ctrl+Shift+A"),
            ("Transição", self.insert_transition, "Ctrl+T"),
            ("Nota", self.insert_note, "Ctrl+Shift+N")
        ]
        
        for func_name, command, shortcut in self.functions:
            btn_frame = tk.Frame(elements_frame, bg=self.blue_color)
            btn_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Ícone (simulado com texto)
            icon_label = tk.Label(btn_frame, text="●", bg=self.blue_color, fg=self.highlight_color)
            icon_label.pack(side=tk.LEFT, padx=5)
            
            # Botão
            btn = tk.Button(btn_frame, text=f"{func_name}", command=command,
                           bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w')
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Atalho
            shortcut_label = tk.Label(btn_frame, text=shortcut, bg=self.blue_color, fg=self.fg_color)
            shortcut_label.pack(side=tk.RIGHT, padx=5)
        
        # Aba de formatação
        format_frame = tk.Frame(self.sidebar_notebook, bg=self.blue_color)
        self.sidebar_notebook.add(format_frame, text="Formatação")
        
        format_functions = [
            ("Negrito", self.toggle_bold, "Ctrl+B"),
            ("Itálico", self.toggle_italic, "Ctrl+I"),
            ("Sublinhado", self.toggle_underline, "Ctrl+U"),
            ("Alinhar à Esquerda", self.align_left, ""),
            ("Centralizar", self.align_center, ""),
            ("Alinhar à Direita", self.align_right, "")
        ]
        
        for func_name, command, shortcut in format_functions:
            btn_frame = tk.Frame(format_frame, bg=self.blue_color)
            btn_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Ícone (simulado com texto)
            icon_label = tk.Label(btn_frame, text="●", bg=self.blue_color, fg=self.highlight_color)
            icon_label.pack(side=tk.LEFT, padx=5)
            
            # Botão
            btn = tk.Button(btn_frame, text=f"{func_name}", command=command,
                           bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w')
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Atalho
            if shortcut:
                shortcut_label = tk.Label(btn_frame, text=shortcut, bg=self.blue_color, fg=self.fg_color)
                shortcut_label.pack(side=tk.RIGHT, padx=5)
        
        # Aba de personagens
        self.characters_frame = tk.Frame(self.sidebar_notebook, bg=self.blue_color)
        self.sidebar_notebook.add(self.characters_frame, text="Personagens")
        
        # Lista de personagens
        self.characters_listbox = tk.Listbox(self.characters_frame, bg=self.secondary_color, 
                                            fg=self.fg_color, bd=0, height=10)
        self.characters_listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # Botões para personagens
        char_buttons_frame = tk.Frame(self.characters_frame, bg=self.blue_color)
        char_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_char_btn = tk.Button(char_buttons_frame, text="Adicionar", command=self.add_character,
                                bg=self.blue_color, fg=self.fg_color, bd=0)
        add_char_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        edit_char_btn = tk.Button(char_buttons_frame, text="Editar", command=self.edit_character,
                                 bg=self.blue_color, fg=self.fg_color, bd=0)
        edit_char_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        remove_char_btn = tk.Button(char_buttons_frame, text="Remover", command=self.remove_character,
                                   bg=self.blue_color, fg=self.fg_color, bd=0)
        remove_char_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Aba de cenas
        self.scenes_frame = tk.Frame(self.sidebar_notebook, bg=self.blue_color)
        self.sidebar_notebook.add(self.scenes_frame, text="Cenas")
        
        # Lista de cenas
        self.scenes_listbox = tk.Listbox(self.scenes_frame, bg=self.secondary_color, 
                                        fg=self.fg_color, bd=0, height=10)
        self.scenes_listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # Botões para cenas
        scene_buttons_frame = tk.Frame(self.scenes_frame, bg=self.blue_color)
        scene_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_scene_btn = tk.Button(scene_buttons_frame, text="Adicionar", command=self.add_scene,
                                 bg=self.blue_color, fg=self.fg_color, bd=0)
        add_scene_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        edit_scene_btn = tk.Button(scene_buttons_frame, text="Editar", command=self.edit_scene,
                                 bg=self.blue_color, fg=self.fg_color, bd=0)
        edit_scene_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        remove_scene_btn = tk.Button(scene_buttons_frame, text="Remover", command=self.remove_scene,
                                    bg=self.blue_color, fg=self.fg_color, bd=0)
        remove_scene_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Aba de notas
        self.notes_frame = tk.Frame(self.sidebar_notebook, bg=self.blue_color)
        self.sidebar_notebook.add(self.notes_frame, text="Notas")
        
        # Editor de notas
        self.notes_editor = tk.Text(self.notes_frame, bg=self.secondary_color, fg=self.fg_color,
                                   height=10, bd=0, wrap=tk.WORD)
        self.notes_editor.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # Botão para salvar notas
        save_notes_btn = tk.Button(self.notes_frame, text="Salvar Notas", command=self.save_notes,
                                  bg=self.blue_color, fg=self.fg_color, bd=0)
        save_notes_btn.pack(pady=5, padx=5, fill=tk.X)
        
        # Aba de ferramentas
        tools_frame = tk.Frame(self.sidebar_notebook, bg=self.blue_color)
        self.sidebar_notebook.add(tools_frame, text="Ferramentas")
        
        tools_functions = [
            ("Verificar Ortografia", self.check_spelling, ""),
            ("Contar Palavras", self.word_count, ""),
            ("Estatísticas", self.show_stats, ""),
            ("Analisar Roteiro", self.analyze_script, ""),
            ("Tempo de Leitura", self.estimate_reading_time, ""),
            ("Reformatar Roteiro", self.reformat_script, "")
        ]
        
        for func_name, command, shortcut in tools_functions:
            btn_frame = tk.Frame(tools_frame, bg=self.blue_color)
            btn_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Ícone (simulado com texto)
            icon_label = tk.Label(btn_frame, text="●", bg=self.blue_color, fg=self.highlight_color)
            icon_label.pack(side=tk.LEFT, padx=5)
            
            # Botão
            btn = tk.Button(btn_frame, text=f"{func_name}", command=command,
                           bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w')
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separador
        separator = tk.Frame(self.sidebar, height=2, bg=self.highlight_color)
        separator.pack(fill=tk.X, pady=10, padx=5)
        
        # Botões de arquivo
        file_btn = tk.Button(self.sidebar, text="Novo Roteiro", command=self.new_file,
                            bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w', width=20)
        file_btn.pack(pady=2, padx=5, fill=tk.X)
        
        open_btn = tk.Button(self.sidebar, text="Abrir Roteiro", command=self.open_file,
                            bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w', width=20)
        open_btn.pack(pady=2, padx=5, fill=tk.X)
        
        save_btn = tk.Button(self.sidebar, text="Salvar Roteiro", command=self.save_file,
                            bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w', width=20)
        save_btn.pack(pady=2, padx=5, fill=tk.X)
        
        secure_btn = tk.Button(self.sidebar, text="Salvar Seguro", command=self.save_secure_file,
                              bg=self.blue_color, fg=self.fg_color, bd=0, anchor='w', width=20)
        secure_btn.pack(pady=2, padx=5, fill=tk.X)
        
        # Estado do menu lateral (expandido ou retraído)
        self.sidebar_expanded = True
    
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            # Retrair
            self.sidebar.pack_forget()
            self.sidebar = tk.Frame(self.root, bg=self.blue_color, width=40)
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.toggle_button = tk.Button(self.sidebar, text="▶", command=self.toggle_sidebar,
                                          bg=self.blue_color, fg=self.fg_color, bd=0)
            self.toggle_button.pack(side=tk.RIGHT, fill=tk.Y)
            self.sidebar_expanded = False
        else:
            # Expandir
            self.sidebar.pack_forget()
            self.create_sidebar()
            self.sidebar_expanded = True
    
    def create_text_editor(self):
        # Frame do editor
        editor_frame = tk.Frame(self.root, bg=self.bg_color)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para números de linha e editor
        text_container = tk.Frame(editor_frame, bg=self.bg_color)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        # Números de linha
        if self.settings['show_line_numbers']:
            self.line_numbers = tk.Text(text_container, width=5, padx=3, takefocus=0, border=0,
                                       bg=self.secondary_color, fg=self.fg_color,
                                       font=self.default_font, state='disabled', wrap=tk.NONE)
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor de texto
        self.text_editor = tk.Text(text_container, bg=self.bg_color, fg=self.fg_color, 
                                  font=self.default_font, wrap=tk.WORD if self.settings['word_wrap'] else tk.NONE,
                                  undo=True, bd=0, padx=5, pady=5, insertbackground=self.cursor_color)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(editor_frame, command=self.on_scrollbar)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.config(yscrollcommand=scrollbar.set)
        
        # Configurar tags para formatação
        self.text_editor.tag_configure("bold", font=self.default_font.copy().configure(weight="bold"))
        self.text_editor.tag_configure("italic", font=self.default_font.copy().configure(slant="italic"))
        self.text_editor.tag_configure("underline", font=self.default_font.copy().configure(underline=True))
        self.text_editor.tag_configure("character", font=self.default_font.copy().configure(weight="bold"), 
                                      foreground=self.highlight_color)
        self.text_editor.tag_configure("scene", font=self.default_font.copy().configure(weight="bold"), 
                                      foreground=self.highlight_color)
        self.text_editor.tag_configure("transition", font=self.default_font.copy().configure(weight="bold"), 
                                      foreground=self.highlight_color)
        self.text_editor.tag_configure("note", font=self.default_font.copy().configure(slant="italic"), 
                                      foreground="#cccccc")
        self.text_editor.tag_configure("highlight", background=self.accent_color)
        self.text_editor.tag_configure("current_line", background=self.line_highlight_color)
        
        # Eventos do editor
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        self.text_editor.bind('<ButtonRelease-1>', self.on_cursor_move)
        self.text_editor.bind('<Key>', self.on_cursor_move)
        self.text_editor.bind('<FocusIn>', self.on_focus_in)
        self.text_editor.bind('<FocusOut>', self.on_focus_out)
        self.text_editor.bind('<MouseWheel>', self.on_mousewheel)
        
        # Atualizar números de linha
        if self.settings['show_line_numbers']:
            self.update_line_numbers()
        
        # Destacar linha atual
        if self.settings['highlight_current_line']:
            self.highlight_current_line()
    
    def on_scrollbar(self, *args):
        self.text_editor.yview(*args)
        if self.settings['show_line_numbers']:
            self.line_numbers.yview(*args)
            self.update_line_numbers()
    
    def on_text_change(self, event=None):
        # Atualizar contador de palavras
        self.update_word_count()
        
        # Atualizar números de linha
        if self.settings['show_line_numbers']:
            self.update_line_numbers()
        
        # Destacar linha atual
        if self.settings['highlight_current_line']:
            self.highlight_current_line()
        
        # Detectar formato do elemento atual
        self.detect_current_element_format()
        
        # Atualizar status
        self.update_status("Editando...")
        
        # Atualizar indicador de salvamento
        self.update_save_indicator()
    
    def on_cursor_move(self, event=None):
        # Atualizar posição do cursor
        line, col = self.text_editor.index(tk.INSERT).split('.')
        self.cursor_pos_label.config(text=f"Ln {int(line)}, Col {int(col)+1}")
        
        # Destacar linha atual
        if self.settings['highlight_current_line']:
            self.highlight_current_line()
        
        # Detectar formato do elemento atual
        self.detect_current_element_format()
    
    def on_focus_in(self, event=None):
        # Destacar linha atual quando o editor recebe foco
        if self.settings['highlight_current_line']:
            self.highlight_current_line()
    
    def on_focus_out(self, event=None):
        # Remover destaque da linha atual quando o editor perde foco
        if self.settings['highlight_current_line']:
            self.text_editor.tag_remove("current_line", "1.0", tk.END)
    
    def on_mousewheel(self, event):
        # Sincronizar a rolagem do mouse com os números de linha
        if self.settings['show_line_numbers']:
            self.update_line_numbers()
    
    def cursor_blink(self):
        # Alternar visibilidade do cursor
        if self.cursor_visible:
            self.text_editor.config(insertbackground=self.cursor_color)
        else:
            self.text_editor.config(insertbackground=self.bg_color)
        
        self.cursor_visible = not self.cursor_visible
        
        # Agendar próxima alternância
        self.root.after(500, self.cursor_blink)
    
    def highlight_current_line(self):
        # Remover destaque anterior
        self.text_editor.tag_remove("current_line", "1.0", tk.END)
        
        # Obter linha atual
        line = self.text_editor.index(tk.INSERT).split('.')[0]
        start_index = f"{line}.0"
        end_index = f"{line}.end"
        
        # Adicionar destaque
        self.text_editor.tag_add("current_line", start_index, end_index)
    
    def detect_current_element_format(self):
        # Obter linha atual
        line = self.text_editor.index(tk.INSERT).split('.')[0]
        start_index = f"{line}.0"
        end_index = f"{line}.end"
        
        # Obter texto da linha
        line_text = self.text_editor.get(start_index, end_index).strip()
        
        # Detectar formato
        if line_text.startswith("CENA:"):
            format_type = "Cena"
        elif line_text.isupper() and len(line_text) < self.settings['character_width']:
            format_type = "Personagem"
        elif line_text.startswith("TRANSIÇÃO:"):
            format_type = "Transição"
        elif line_text.startswith("NOTA:"):
            format_type = "Nota"
        else:
            # Verificar se é diálogo (linha após personagem)
            prev_line = int(line) - 1
            if prev_line > 0:
                prev_start = f"{prev_line}.0"
                prev_end = f"{prev_line}.end"
                prev_text = self.text_editor.get(prev_start, prev_end).strip()
                
                if prev_text.isupper() and len(prev_text) < self.settings['character_width']:
                    format_type = "Diálogo"
                else:
                    format_type = "Ação"
            else:
                format_type = "Ação"
        
        # Atualizar label
        self.element_format_label.config(text=format_type)
    
    def update_line_numbers(self):
        if not self.settings['show_line_numbers']:
            return
            
        # Obter número de linhas
        line_count = int(self.text_editor.index('end-1c').split('.')[0])
        
        # Configurar números de linha
        line_numbers_str = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        # Atualizar widget de números de linha
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_str)
        self.line_numbers.config(state='disabled')
        
        # Sincronizar scroll
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])
    
    def update_word_count(self):
        text = self.text_editor.get(1.0, tk.END)
        words = text.split()
        word_count = len(words)
        self.word_count_label.config(text=f"Palavras: {word_count}")
    
    def update_status(self, message):
        self.status_text.set(message)
        self.root.after(3000, lambda: self.status_text.set("Pronto"))
    
    def update_save_indicator(self):
        # Verificar se o arquivo foi modificado desde o último salvamento
        if self.text_editor.edit_modified():
            # Mudar cor do indicador para vermelho
            self.save_indicator.config(fg="#ff0000")
        else:
            # Mudar cor do indicador para verde
            self.save_indicator.config(fg=self.accent_color)
    
    def setup_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-s>', lambda e: self.save_file_as())
        self.root.bind('<Control-Alt-s>', lambda e: self.save_secure_file())
        self.root.bind('<Control-e>', lambda e: self.export_pdf())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-b>', lambda e: self.toggle_bold())
        self.root.bind('<Control-i>', lambda e: self.toggle_italic())
        self.root.bind('<Control-u>', lambda e: self.toggle_underline())
        self.root.bind('<Control-p>', lambda e: self.insert_character())
        self.root.bind('<Control-d>', lambda e: self.insert_dialogue())
        self.root.bind('<Control-Shift-a>', lambda e: self.insert_action())
        self.root.bind('<Control-Shift-c>', lambda e: self.insert_scene())
        self.root.bind('<Control-t>', lambda e: self.insert_transition())
        self.root.bind('<Control-Shift-n>', lambda e: self.insert_note())
        self.root.bind('<Control-f>', lambda e: self.show_search_dialog())
        self.root.bind('<Control-r>', lambda e: self.show_replace_dialog())
        self.root.bind('<Control-g>', lambda e: self.go_to_line())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_normal())
        self.root.bind('<F3>', lambda e: self.find_next())
        self.root.bind('<Shift-F3>', lambda e: self.find_prev())
        self.root.bind('<Control-a>', lambda e: self.select_all())
    
    # Funções de formatação
    def toggle_bold(self):
        try:
            current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
            if "bold" in current_tags:
                self.text_editor.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_editor.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def toggle_italic(self):
        try:
            current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
            if "italic" in current_tags:
                self.text_editor.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_editor.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def toggle_underline(self):
        try:
            current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
            if "underline" in current_tags:
                self.text_editor.tag_remove("underline", tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_editor.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def align_left(self):
        try:
            # Alinhar texto à esquerda
            start_index = self.text_editor.index(tk.SEL_FIRST)
            end_index = self.text_editor.index(tk.SEL_LAST)
            
            # Obter linhas selecionadas
            start_line = int(start_index.split('.')[0])
            end_line = int(end_index.split('.')[0])
            
            # Alinhar cada linha
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_text = self.text_editor.get(line_start, line_end)
                
                # Remover espaços em branco no início
                stripped_text = line_text.lstrip()
                
                # Substituir linha
                self.text_editor.delete(line_start, line_end)
                self.text_editor.insert(line_start, stripped_text)
        except:
            pass
    
    def align_center(self):
        try:
            # Centralizar texto
            start_index = self.text_editor.index(tk.SEL_FIRST)
            end_index = self.text_editor.index(tk.SEL_LAST)
            
            # Obter linhas selecionadas
            start_line = int(start_index.split('.')[0])
            end_line = int(end_index.split('.')[0])
            
            # Centralizar cada linha
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_text = self.text_editor.get(line_start, line_end).strip()
                
                # Calcular espaços necessários para centralizar
                line_length = len(line_text)
                total_spaces = self.settings['page_width'] - line_length
                left_spaces = total_spaces // 2
                right_spaces = total_spaces - left_spaces
                
                # Criar linha centralizada
                centered_text = ' ' * left_spaces + line_text + ' ' * right_spaces
                
                # Substituir linha
                self.text_editor.delete(line_start, line_end)
                self.text_editor.insert(line_start, centered_text)
        except:
            pass
    
    def align_right(self):
        try:
            # Alinhar texto à direita
            start_index = self.text_editor.index(tk.SEL_FIRST)
            end_index = self.text_editor.index(tk.SEL_LAST)
            
            # Obter linhas selecionadas
            start_line = int(start_index.split('.')[0])
            end_line = int(end_index.split('.')[0])
            
            # Alinhar cada linha
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_text = self.text_editor.get(line_start, line_end).strip()
                
                # Calcular espaços necessários para alinhar à direita
                line_length = len(line_text)
                left_spaces = self.settings['page_width'] - line_length
                
                # Criar linha alinhada à direita
                right_text = ' ' * left_spaces + line_text
                
                # Substituir linha
                self.text_editor.delete(line_start, line_end)
                self.text_editor.insert(line_start, right_text)
        except:
            pass
    
    # Funções de inserção de elementos de roteiro
    def insert_character(self):
        # Inserir elemento de personagem formatado
        self.text_editor.insert(tk.INSERT, "\n\n")
        
        # Calcular espaços para centralizar
        char_name = "NOME DO PERSONAGEM"
        char_length = len(char_name)
        total_spaces = self.settings['page_width'] - char_length
        left_spaces = total_spaces // 2
        
        # Inserir nome do personagem centralizado
        self.text_editor.insert(tk.INSERT, ' ' * left_spaces + char_name + '\n')
        self.text_editor.tag_add("character", "insert-1l linestart", "insert-1l lineend")
        
        # Posicionar cursor para diálogo
        self.text_editor.insert(tk.INSERT, "\n")
        self.text_editor.mark_set(tk.INSERT, "insert-1l lineend")
        
        self.update_status("Personagem inserido")
    
    def insert_dialogue(self):
        # Inserir elemento de diálogo formatado
        self.text_editor.insert(tk.INSERT, "\n\n")
        
        # Calcular espaços para diálogo
        dialogue_text = "Diálogo do personagem aqui..."
        dialogue_length = len(dialogue_text)
        left_spaces = 15  # Padrão para diálogos
        
        # Inserir diálogo
        self.text_editor.insert(tk.INSERT, ' ' * left_spaces + dialogue_text + '\n')
        
        # Posicionar cursor no final do diálogo
        self.text_editor.mark_set(tk.INSERT, "insert-1l lineend")
        
        self.update_status("Diálogo inserido")
    
    def insert_action(self):
        # Inserir elemento de ação formatado
        self.text_editor.insert(tk.INSERT, "\n\n")
        
        # Calcular espaços para ação
        action_text = "Ação ou descrição da cena..."
        action_length = len(action_text)
        left_spaces = 10  # Padrão para ações
        
        # Inserir ação
        self.text_editor.insert(tk.INSERT, ' ' * left_spaces + action_text + '\n')
        
        # Posicionar cursor no final da ação
        self.text_editor.mark_set(tk.INSERT, "insert-1l lineend")
        
        self.update_status("Ação inserida")
    
    def insert_scene(self):
        # Inserir elemento de cena formatado
        self.text_editor.insert(tk.INSERT, "\n\n")
        
        # Formato padrão para cenas
        scene_text = "CENA: LOCAL - DIA/NOITE"
        
        # Inserir cena
        self.text_editor.insert(tk.INSERT, scene_text + '\n')
        self.text_editor.tag_add("scene", "insert-1l linestart", "insert-1l lineend")
        
        # Inserir linha em branco
        self.text_editor.insert(tk.INSERT, "\n")
        
        # Posicionar cursor após a cena
        self.text_editor.mark_set(tk.INSERT, "insert-1l lineend")
        
        self.update_status("Cena inserida")
    
    def insert_transition(self):
        # Inserir elemento de transição formatado
        self.text_editor.insert(tk.INSERT, "\n\n")
        
        # Calcular espaços para transição (alinhado à direita)
        transition_text = "TRANSIÇÃO: CORTE PARA:"
        transition_length = len(transition_text)
        total_spaces = self.settings['page_width'] - transition_length
        left_spaces = total_spaces
        
        # Inserir transição
        self.text_editor.insert(tk.INSERT, ' ' * left_spaces + transition_text + '\n')
        self.text_editor.tag_add("transition", "insert-1l linestart", "insert-1l lineend")
        
        # Posicionar cursor no final da transição
        self.text_editor.mark_set(tk.INSERT, "insert lineend")
        
        self.update_status("Transição inserida")
    
    def insert_note(self):
        # Inserir elemento de nota formatado
        self.text_editor.insert(tk.INSERT, "\n\n")
        
        # Formato padrão para notas
        note_text = "NOTA: "
        
        # Inserir nota
        self.text_editor.insert(tk.INSERT, note_text)
        self.text_editor.tag_add("note", "insert-1l linestart", "insert-1l lineend")
        
        # Posicionar cursor após a nota
        self.text_editor.mark_set(tk.INSERT, "insert lineend")
        
        self.update_status("Nota inserida")
    
    # Funções de arquivo
    def new_file(self):
        if self.current_file and self.text_editor.edit_modified():
            response = messagebox.askyesnocancel("Salvar alterações", 
                                                 "Deseja salvar as alterações antes de criar um novo roteiro?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        self.text_editor.delete(1.0, tk.END)
        self.current_file = None
        self.current_password = None
        self.text_editor.edit_modified(False)
        self.root.title("Roteirista Pro - Novo Roteiro")
        self.update_status("Novo roteiro criado")
        self.update_save_indicator()
    
    def open_file(self):
        if self.text_editor.edit_modified():
            response = messagebox.askyesnocancel("Salvar alterações", 
                                                 "Deseja salvar as alterações antes de abrir outro arquivo?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        file_path = filedialog.askopenfilename(
            initialdir=self.settings['last_dir'],
            defaultextension=".rtf",
            filetypes=[("Roteiros", "*.rtf"), ("Arquivos de Texto", "*.txt"), ("Arquivos FDX", "*.fdx"), ("Arquivos Seguros", "*.sec"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Verificar se é um arquivo seguro
                if file_path.endswith('.sec'):
                    # Pedir senha
                    password = simpledialog.askstring("Senha", "Digite a senha para abrir o arquivo:", show='*')
                    if not password:
                        return
                    
                    # Tentar descriptografar
                    try:
                        with open(file_path, "rb") as file:
                            encrypted_data = file.read()
                            
                        # Decodificar base64
                        encrypted_data = base64.b64decode(encrypted_data)
                        
                        # Gerar chave a partir da senha
                        password_hash = hashlib.sha256(password.encode()).digest()
                        key = base64.urlsafe_b64encode(password_hash)
                        
                        # Descriptografar
                        fernet = Fernet(key)
                        decrypted_data = fernet.decrypt(encrypted_data)
                        
                        # Decodificar texto
                        content = decrypted_data.decode('utf-8')
                        
                        # Carregar conteúdo
                        self.text_editor.delete(1.0, tk.END)
                        self.text_editor.insert(1.0, content)
                        
                        # Salvar senha para uso futuro
                        self.current_password = password
                    except Exception as e:
                        messagebox.showerror("Erro", "Senha incorreta ou arquivo corrompido.")
                        return
                else:
                    # Arquivo normal
                    with open(file_path, "r", encoding="utf-8") as file:
                        self.text_editor.delete(1.0, tk.END)
                        self.text_editor.insert(1.0, file.read())
                        self.current_password = None
                
                self.current_file = file_path
                self.text_editor.edit_modified(False)
                self.root.title(f"Roteirista Pro - {os.path.basename(file_path)}")
                self.settings['last_dir'] = os.path.dirname(file_path)
                self.update_status(f"Arquivo aberto: {os.path.basename(file_path)}")
                self.update_save_indicator()
                
                # Tentar carregar personagens e cenas
                self.load_metadata()
            except Exception as e:
                messagebox.showerror("Erro ao abrir arquivo", f"Não foi possível abrir o arquivo: {str(e)}")
    
    def save_file(self):
        if not self.current_file:
            self.save_file_as()
        else:
            try:
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(self.text_editor.get(1.0, tk.END))
                    self.text_editor.edit_modified(False)
                    self.root.title(f"Roteirista Pro - {os.path.basename(self.current_file)}")
                    self.update_status(f"Arquivo salvo: {os.path.basename(self.current_file)}")
                    self.update_save_indicator()
                    
                    # Salvar metadados (personagens e cenas)
                    self.save_metadata()
            except Exception as e:
                messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o arquivo: {str(e)}")
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            initialdir=self.settings['last_dir'],
            defaultextension=".rtf",
            filetypes=[("Roteiros", "*.rtf"), ("Arquivos de Texto", "*.txt"), ("Arquivos FDX", "*.fdx"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            self.current_password = None
            self.save_file()
            self.settings['last_dir'] = os.path.dirname(file_path)
    
    def save_secure_file(self):
        # Pedir senha
        password = simpledialog.askstring("Senha", "Digite uma senha para o arquivo:", show='*')
        if not password:
            return
        
        # Confirmar senha
        confirm_password = simpledialog.askstring("Confirmar Senha", "Confirme a senha:", show='*')
        if password != confirm_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
        
        # Escolher local para salvar
        file_path = filedialog.asksaveasfilename(
            initialdir=self.settings['last_dir'],
            defaultextension=".sec",
            filetypes=[("Arquivos Seguros", "*.sec"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Obter conteúdo do editor
                content = self.text_editor.get(1.0, tk.END)
                
                # Gerar chave a partir da senha
                password_hash = hashlib.sha256(password.encode()).digest()
                key = base64.urlsafe_b64encode(password_hash)
                
                # Criptografar conteúdo
                fernet = Fernet(key)
                encrypted_data = fernet.encrypt(content.encode('utf-8'))
                
                # Codificar em base64
                encrypted_data = base64.b64encode(encrypted_data)
                
                # Salvar arquivo
                with open(file_path, "wb") as file:
                    file.write(encrypted_data)
                
                self.current_file = file_path
                self.current_password = password
                self.text_editor.edit_modified(False)
                self.root.title(f"Roteirista Pro - {os.path.basename(file_path)} [Seguro]")
                self.update_status(f"Arquivo seguro salvo: {os.path.basename(file_path)}")
                self.update_save_indicator()
                
                # Salvar metadados (personagens e cenas)
                self.save_metadata()
            except Exception as e:
                messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o arquivo seguro: {str(e)}")
    
    def import_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.settings['last_dir'],
            filetypes=[("Arquivos FDX", "*.fdx"), ("Arquivos PDF", "*.pdf"), ("Arquivos Word", "*.docx"), ("Arquivos Fountain", "*.fountain"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Lógica de importação depende do tipo de arquivo
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.fdx':
                    # Importar do Final Draft
                    self.import_fdx(file_path)
                elif ext == '.pdf':
                    # Importar do PDF (mais complexo)
                    self.import_pdf(file_path)
                elif ext == '.docx':
                    # Importar do Word
                    self.import_docx(file_path)
                elif ext == '.fountain':
                    # Importar do Fountain
                    self.import_fountain(file_path)
                else:
                    messagebox.showwarning("Formato não suportado", "Este formato de arquivo não é suportado para importação.")
                    
                self.update_status(f"Arquivo importado: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Erro ao importar", f"Não foi possível importar o arquivo: {str(e)}")
    
    def export_pdf(self):
        if not self.current_file:
            messagebox.showwarning("Exportar PDF", "Por favor, salve o roteiro antes de exportar.")
            return
            
        # Escolher local para salvar
        pdf_path = filedialog.asksaveasfilename(
            initialdir=self.settings['last_dir'],
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os Arquivos", "*.*")]
        )
        
        if pdf_path:
            try:
                # Criar documento PDF
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                # Obter conteúdo do editor
                content = self.text_editor.get(1.0, tk.END)
                lines = content.split('\n')
                
                # Adicionar título
                title = os.path.basename(self.current_file)
                if title.endswith('.rtf') or title.endswith('.txt'):
                    title = title[:-4]
                
                title_style = styles["Title"]
                title_style.alignment = TA_CENTER
                story.append(Paragraph(title, title_style))
                story.append(Spacer(1, 12))
                
                # Processar cada linha
                for line in lines:
                    stripped = line.strip()
                    
                    if not stripped:
                        # Linha em branco
                        story.append(Spacer(1, 6))
                    elif stripped.startswith("CENA:"):
                        # Cena
                        scene_style = styles["Normal"]
                        scene_style.fontName = "Courier-Bold"
                        scene_style.textColor = blue
                        scene_style.alignment = TA_LEFT
                        story.append(Paragraph(stripped, scene_style))
                        story.append(Spacer(1, 6))
                    elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                        # Personagem
                        char_style = styles["Normal"]
                        char_style.fontName = "Courier-Bold"
                        char_style.textColor = blue
                        char_style.alignment = TA_CENTER
                        story.append(Paragraph(stripped, char_style))
                    elif stripped.startswith("TRANSIÇÃO:"):
                        # Transição
                        trans_style = styles["Normal"]
                        trans_style.fontName = "Courier-Bold"
                        trans_style.textColor = blue
                        trans_style.alignment = TA_RIGHT
                        story.append(Paragraph(stripped, trans_style))
                        story.append(Spacer(1, 6))
                    elif stripped.startswith("NOTA:"):
                        # Nota
                        note_style = styles["Normal"]
                        note_style.fontName = "Courier-Italic"
                        note_style.textColor = black
                        note_style.alignment = TA_LEFT
                        story.append(Paragraph(stripped, note_style))
                        story.append(Spacer(1, 6))
                    else:
                        # Verificar se é diálogo (linha após personagem)
                        if story and isinstance(story[-1], Paragraph) and story[-1].style.alignment == TA_CENTER:
                            # Diálogo
                            dialogue_style = styles["Normal"]
                            dialogue_style.fontName = "Courier"
                            dialogue_style.textColor = black
                            dialogue_style.leftIndent = 1.5 * inch
                            story.append(Paragraph(stripped, dialogue_style))
                        else:
                            # Ação
                            action_style = styles["Normal"]
                            action_style.fontName = "Courier"
                            action_style.textColor = black
                            action_style.leftIndent = 0.5 * inch
                            story.append(Paragraph(stripped, action_style))
                
                # Construir PDF
                doc.build(story)
                
                messagebox.showinfo("Exportar PDF", f"PDF exportado com sucesso:\n{pdf_path}")
                self.update_status(f"PDF exportado: {os.path.basename(pdf_path)}")
            except Exception as e:
                messagebox.showerror("Erro ao exportar PDF", f"Não foi possível exportar para PDF: {str(e)}")
    
    def export_html(self):
        if not self.current_file:
            messagebox.showwarning("Exportar HTML", "Por favor, salve o roteiro antes de exportar.")
            return
            
        html_content = self.generate_html()
        html_path = os.path.splitext(self.current_file)[0] + '.html'
        
        try:
            with open(html_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            messagebox.showinfo("Exportar HTML", f"HTML exportado com sucesso:\n{html_path}")
            self.update_status(f"HTML exportado: {os.path.basename(html_path)}")
        except Exception as e:
            messagebox.showerror("Erro ao exportar HTML", f"Não foi possível exportar para HTML: {str(e)}")
    
    def export_fountain(self):
        if not self.current_file:
            messagebox.showwarning("Exportar Fountain", "Por favor, salve o roteiro antes de exportar.")
            return
            
        # Converter para formato Fountain
        fountain_content = self.convert_to_fountain()
        fountain_path = os.path.splitext(self.current_file)[0] + '.fountain'
        
        try:
            with open(fountain_path, 'w', encoding='utf-8') as file:
                file.write(fountain_content)
            messagebox.showinfo("Exportar Fountain", f"Arquivo Fountain exportado com sucesso:\n{fountain_path}")
            self.update_status(f"Fountain exportado: {os.path.basename(fountain_path)}")
        except Exception as e:
            messagebox.showerror("Erro ao exportar Fountain", f"Não foi possível exportar para Fountain: {str(e)}")
    
    def convert_to_fountain(self):
        # Converter o conteúdo do editor para formato Fountain
        content = self.text_editor.get(1.0, tk.END)
        lines = content.split('\n')
        fountain_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # Linha em branco
                fountain_lines.append("")
            elif stripped.startswith("CENA:"):
                # Cena
                fountain_lines.append("." + stripped[6:])
            elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                # Personagem
                fountain_lines.append(stripped)
            elif stripped.startswith("TRANSIÇÃO:"):
                # Transição
                fountain_lines.append("> " + stripped[11:])
            elif stripped.startswith("NOTA:"):
                # Nota
                fountain_lines.append("[[" + stripped[6:] + "]]")
            else:
                # Ação ou diálogo
                # Verificar se a linha anterior é um personagem
                if fountain_lines and fountain_lines[-1].isupper() and len(fountain_lines[-1]) < self.settings['character_width']:
                    # Diálogo
                    fountain_lines.append(stripped)
                else:
                    # Ação
                    fountain_lines.append(stripped)
        
        return '\n'.join(fountain_lines)
    
    def import_fountain(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Converter do formato Fountain para o formato interno
            lines = content.split('\n')
            converted_lines = []
            
            for line in lines:
                stripped = line.strip()
                
                if not stripped:
                    # Linha em branco
                    converted_lines.append("")
                elif stripped.startswith('.'):
                    # Cena
                    converted_lines.append("CENA:" + stripped[1:])
                elif stripped.startswith('[') and stripped.endswith(']'):
                    # Nota
                    converted_lines.append("NOTA:" + stripped[2:-2])
                elif stripped.startswith('>'):
                    # Transição
                    converted_lines.append("TRANSIÇÃO:" + stripped[2:])
                elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                    # Personagem
                    converted_lines.append(stripped)
                else:
                    # Ação ou diálogo
                    # Verificar se a linha anterior é um personagem
                    if converted_lines and converted_lines[-1].isupper() and len(converted_lines[-1]) < self.settings['character_width']:
                        # Diálogo
                        converted_lines.append(stripped)
                    else:
                        # Ação
                        converted_lines.append(stripped)
            
            # Limpar o editor
            self.text_editor.delete(1.0, tk.END)
            
            # Inserir conteúdo convertido
            self.text_editor.insert(1.0, '\n'.join(converted_lines))
            
            # Aplicar formatação
            self.apply_formatting()
            
            self.update_status(f"Arquivo Fountain importado: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Erro ao importar", f"Não foi possível importar o arquivo Fountain: {str(e)}")
    
    def generate_html(self):
        # Gerar HTML a partir do conteúdo do editor
        content = self.text_editor.get(1.0, tk.END)
        
        # Analisar conteúdo e aplicar formatação HTML
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # Linha em branco
                html_lines.append("<br>")
            elif stripped.startswith("CENA:"):
                # Cena
                html_lines.append(f'<div class="scene">{stripped}</div>')
            elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                # Personagem
                html_lines.append(f'<div class="character">{stripped}</div>')
            elif stripped.startswith("TRANSIÇÃO:"):
                # Transição
                html_lines.append(f'<div class="transition">{stripped}</div>')
            elif stripped.startswith("NOTA:"):
                # Nota
                html_lines.append(f'<div class="note">{stripped}</div>')
            else:
                # Ação ou diálogo
                # Verificar se a linha anterior é um personagem
                if html_lines and html_lines[-1].startswith('<div class="character">'):
                    # Diálogo
                    html_lines.append(f'<div class="dialogue">{stripped}</div>')
                else:
                    # Ação
                    html_lines.append(f'<div class="action">{stripped}</div>')
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Courier, monospace;
                    font-size: 12pt;
                    line-height: 1.5;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    color: #000000;
                }}
                .scene {{
                    font-weight: bold;
                    color: #0066cc;
                    text-transform: uppercase;
                    margin-top: 20px;
                    text-align: left;
                }}
                .character {{
                    font-weight: bold;
                    color: #0066cc;
                    text-align: center;
                    margin-top: 20px;
                }}
                .dialogue {{
                    margin-left: 150px;
                    margin-right: 150px;
                }}
                .action {{
                    margin-top: 10px;
                }}
                .transition {{
                    font-weight: bold;
                    color: #0066cc;
                    text-align: right;
                    margin-top: 20px;
                }}
                .note {{
                    font-style: italic;
                    color: #666666;
                    margin-top: 10px;
                }}
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                @media print {{
                    body {{
                        margin: 0;
                        padding: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        return html_content.format(
            title=os.path.basename(self.current_file) if self.current_file else "Roteiro",
            content='\n'.join(html_lines)
        )
    
    def print_script(self):
        # Imprimir o roteiro
        try:
            # Criar um arquivo temporário HTML
            html_content = self.generate_html()
            
            # Salvar o HTML em um arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write(html_content)
                temp_html_path = temp_file.name
            
            # Abrir o HTML no navegador padrão para impressão
            if sys.platform == 'win32':
                os.startfile(temp_html_path, 'print')
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-a', 'Preview', temp_html_path])
            else:
                subprocess.run(['xdg-open', temp_html_path])
                
            self.update_status("Roteiro enviado para impressão")
        except Exception as e:
            messagebox.showerror("Erro ao imprimir", f"Não foi possível imprimir o roteiro: {str(e)}")
    
    def undo(self):
        self.text_editor.edit_undo()
        self.update_status("Desfazer")
    
    def redo(self):
        self.text_editor.edit_redo()
        self.update_status("Refazer")
    
    def cut_text(self):
        try:
            self.text_editor.event_generate("<<Cut>>")
            self.update_status("Recortar")
        except:
            pass
    
    def copy_text(self):
        try:
            self.text_editor.event_generate("<<Copy>>")
            self.update_status("Copiar")
        except:
            pass
    
    def paste_text(self):
        try:
            self.text_editor.event_generate("<<Paste>>")
            self.update_status("Colar")
        except:
            pass
    
    def select_all(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.update_status("Selecionar tudo")
    
    def go_to_line(self):
        # Criar janela para ir para linha
        goto_window = tk.Toplevel(self.root)
        goto_window.title("Ir Para Linha")
        goto_window.geometry("300x120")
        goto_window.configure(bg=self.secondary_color)
        goto_window.transient(self.root)
        goto_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(goto_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campo para número da linha
        tk.Label(main_frame, text="Número da linha:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        line_var = tk.StringVar()
        line_entry = tk.Entry(main_frame, textvariable=line_var, bg=self.bg_color, fg=self.fg_color)
        line_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        line_entry.focus_set()
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        def go_to():
            try:
                line_num = int(line_var.get())
                if line_num < 1:
                    line_num = 1
                
                # Obter número total de linhas
                total_lines = int(self.text_editor.index('end-1c').split('.')[0])
                if line_num > total_lines:
                    line_num = total_lines
                
                # Mover cursor para a linha
                self.text_editor.mark_set(tk.INSERT, f"{line_num}.0")
                self.text_editor.see(tk.INSERT)
                
                # Destacar linha
                if self.settings['highlight_current_line']:
                    self.highlight_current_line()
                
                goto_window.destroy()
                self.update_status(f"Movido para linha {line_num}")
            except ValueError:
                messagebox.showwarning("Erro", "Por favor, digite um número válido.")
        
        go_btn = tk.Button(button_frame, text="Ir", command=go_to,
                          bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        go_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=goto_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def show_search_dialog(self):
        # Criar janela de busca
        search_window = tk.Toplevel(self.root)
        search_window.title("Buscar")
        search_window.geometry("400x150")
        search_window.configure(bg=self.secondary_color)
        search_window.transient(self.root)
        search_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(search_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campo de busca
        tk.Label(main_frame, text="Buscar:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        search_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        search_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        search_entry.focus_set()
        
        # Opções
        case_var = tk.IntVar()
        case_check = tk.Checkbutton(main_frame, text="Diferenciar maiúsculas/minúsculas", 
                                   variable=case_var, bg=self.secondary_color, fg=self.fg_color,
                                   selectcolor=self.bg_color, activebackground=self.secondary_color,
                                   activeforeground=self.fg_color)
        case_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        word_var = tk.IntVar()
        word_check = tk.Checkbutton(main_frame, text="Palavra inteira", 
                                   variable=word_var, bg=self.secondary_color, fg=self.fg_color,
                                   selectcolor=self.bg_color, activebackground=self.secondary_color,
                                   activeforeground=self.fg_color)
        word_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        def do_search():
            term = search_entry.get()
            if not term:
                return
                
            self.search_term = term
            self.search_matches = []
            self.current_match = -1
            
            # Configurar opções de busca
            flags = 0
            if not case_var.get():
                flags |= re.IGNORECASE
                
            # Buscar no texto
            text = self.text_editor.get(1.0, tk.END)
            
            if word_var.get():
                # Buscar por palavra inteira
                pattern = r'\b' + re.escape(term) + r'\b'
            else:
                pattern = re.escape(term)
                
            matches = list(re.finditer(pattern, text, flags))
            
            if matches:
                self.search_matches = [(m.start(), m.end()) for m in matches]
                self.find_next()
                search_window.destroy()
            else:
                messagebox.showinfo("Buscar", f"Não foram encontradas ocorrências de '{term}'")
        
        search_btn = tk.Button(button_frame, text="Buscar", command=do_search,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=search_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def show_replace_dialog(self):
        # Criar janela de substituição
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Substituir")
        replace_window.geometry("400x200")
        replace_window.configure(bg=self.secondary_color)
        replace_window.transient(self.root)
        replace_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(replace_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campo de busca
        tk.Label(main_frame, text="Buscar:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        search_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        search_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        search_entry.focus_set()
        
        # Campo de substituição
        tk.Label(main_frame, text="Substituir por:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        replace_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        replace_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Opções
        case_var = tk.IntVar()
        case_check = tk.Checkbutton(main_frame, text="Diferenciar maiúsculas/minúsculas", 
                                   variable=case_var, bg=self.secondary_color, fg=self.fg_color,
                                   selectcolor=self.bg_color, activebackground=self.secondary_color,
                                   activeforeground=self.fg_color)
        case_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        word_var = tk.IntVar()
        word_check = tk.Checkbutton(main_frame, text="Palavra inteira", 
                                   variable=word_var, bg=self.secondary_color, fg=self.fg_color,
                                   selectcolor=self.bg_color, activebackground=self.secondary_color,
                                   activeforeground=self.fg_color)
        word_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def do_replace():
            search_term = search_entry.get()
            replace_term = replace_entry.get()
            
            if not search_term:
                return
                
            # Configurar opções de busca
            flags = 0
            if not case_var.get():
                flags |= re.IGNORECASE
                
            # Buscar no texto
            text = self.text_editor.get(1.0, tk.END)
            
            if word_var.get():
                # Buscar por palavra inteira
                pattern = r'\b' + re.escape(search_term) + r'\b'
            else:
                pattern = re.escape(search_term)
                
            # Substituir
            new_text = re.sub(pattern, replace_term, text, flags=flags)
            
            if new_text != text:
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, new_text)
                count = len(re.findall(pattern, text, flags=flags))
                messagebox.showinfo("Substituir", f"Foram substituídas {count} ocorrências de '{search_term}' por '{replace_term}'")
                replace_window.destroy()
            else:
                messagebox.showinfo("Substituir", f"Não foram encontradas ocorrências de '{search_term}'")
        
        replace_btn = tk.Button(button_frame, text="Substituir Tudo", command=do_replace,
                               bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        replace_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=replace_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def find_next(self):
        if not self.search_matches:
            return
            
        self.current_match = (self.current_match + 1) % len(self.search_matches)
        start, end = self.search_matches[self.current_match]
        
        # Converter para índices do Tkinter
        start_index = f"1.0 + {start} chars"
        end_index = f"1.0 + {end} chars"
        
        # Remover destaque anterior
        self.text_editor.tag_remove("highlight", "1.0", tk.END)
        
        # Adicionar destaque
        self.text_editor.tag_add("highlight", start_index, end_index)
        
        # Rolar para a posição
        self.text_editor.see(start_index)
        
        # Selecionar o texto
        self.text_editor.tag_add(tk.SEL, start_index, end_index)
        self.text_editor.mark_set(tk.INSERT, end_index)
        
        self.update_status(f"Ocorrência {self.current_match + 1} de {len(self.search_matches)}")
    
    def find_prev(self):
        if not self.search_matches:
            return
            
        self.current_match = (self.current_match - 1) % len(self.search_matches)
        start, end = self.search_matches[self.current_match]
        
        # Converter para índices do Tkinter
        start_index = f"1.0 + {start} chars"
        end_index = f"1.0 + {end} chars"
        
        # Remover destaque anterior
        self.text_editor.tag_remove("highlight", "1.0", tk.END)
        
        # Adicionar destaque
        self.text_editor.tag_add("highlight", start_index, end_index)
        
        # Rolar para a posição
        self.text_editor.see(start_index)
        
        # Selecionar o texto
        self.text_editor.tag_add(tk.SEL, start_index, end_index)
        self.text_editor.mark_set(tk.INSERT, end_index)
        
        self.update_status(f"Ocorrência {self.current_match + 1} de {len(self.search_matches)}")
    
    def change_font(self):
        # Criar janela de seleção de fonte
        font_window = tk.Toplevel(self.root)
        font_window.title("Selecionar Fonte")
        font_window.geometry("400x300")
        font_window.configure(bg=self.secondary_color)
        font_window.transient(self.root)
        font_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(font_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de fontes
        tk.Label(main_frame, text="Fonte:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        font_listbox = tk.Listbox(main_frame, bg=self.bg_color, fg=self.fg_color, height=10)
        font_listbox.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        
        # Preencher lista de fontes
        available_fonts = sorted(font.families())
        for family in available_fonts:
            font_listbox.insert(tk.END, family)
            
        # Selecionar fonte atual
        current_font = self.settings['font_family']
        try:
            index = available_fonts.index(current_font)
            font_listbox.selection_set(index)
            font_listbox.see(index)
        except ValueError:
            pass
        
        # Tamanho da fonte
        tk.Label(main_frame, text="Tamanho:", bg=self.secondary_color, fg=self.fg_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        size_var = tk.IntVar(value=self.settings['font_size'])
        size_spinbox = tk.Spinbox(main_frame, from_=8, to=24, textvariable=size_var, 
                                 bg=self.bg_color, fg=self.fg_color, width=10)
        size_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Amostra
        tk.Label(main_frame, text="Amostra:", bg=self.secondary_color, fg=self.fg_color).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        sample_text = tk.Text(main_frame, height=5, bg=self.bg_color, fg=self.fg_color, 
                             wrap=tk.WORD, bd=1, relief=tk.SOLID)
        sample_text.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        sample_text.insert(tk.END, "O rápido raposa marrom salta sobre o cão preguiçoso.\n\n" + 
                                 "NOME DO PERSONAGEM\n\n" + 
                                 "Diálogo do personagem aqui...")
        
        # Função para atualizar amostra
        def update_sample(event=None):
            try:
                selected = font_listbox.curselection()
                if selected:
                    family = available_fonts[selected[0]]
                    size = size_var.get()
                    sample_font = font.Font(family=family, size=size)
                    sample_text.config(font=sample_font)
            except:
                pass
        
        font_listbox.bind('<<ListboxSelect>>', update_sample)
        size_spinbox.bind('<KeyRelease>', update_sample)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        def apply_font():
            try:
                selected = font_listbox.curselection()
                if selected:
                    family = available_fonts[selected[0]]
                    size = size_var.get()
                    
                    # Atualizar configurações
                    self.settings['font_family'] = family
                    self.settings['font_size'] = size
                    
                    # Atualizar fonte padrão
                    self.default_font = font.Font(family=family, size=size)
                    
                    # Atualizar editor
                    self.text_editor.config(font=self.default_font)
                    
                    # Atualizar tags de formatação
                    self.text_editor.tag_configure("bold", font=self.default_font.copy().configure(weight="bold"))
                    self.text_editor.tag_configure("italic", font=self.default_font.copy().configure(slant="italic"))
                    self.text_editor.tag_configure("underline", font=self.default_font.copy().configure(underline=True))
                    self.text_editor.tag_configure("character", font=self.default_font.copy().configure(weight="bold"), 
                                                  foreground=self.highlight_color)
                    self.text_editor.tag_configure("scene", font=self.default_font.copy().configure(weight="bold"), 
                                                  foreground=self.highlight_color)
                    self.text_editor.tag_configure("transition", font=self.default_font.copy().configure(weight="bold"), 
                                                  foreground=self.highlight_color)
                    self.text_editor.tag_configure("note", font=self.default_font.copy().configure(slant="italic"), 
                                                  foreground="#cccccc")
                    
                    # Atualizar números de linha
                    if self.settings['show_line_numbers']:
                        self.line_numbers.config(font=self.default_font)
                        self.update_line_numbers()
                    
                    font_window.destroy()
                    self.update_status(f"Fonte alterada: {family} {size}pt")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível alterar a fonte: {str(e)}")
        
        apply_btn = tk.Button(button_frame, text="Aplicar", command=apply_font,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=font_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Inicializar amostra
        update_sample()
    
    def change_color(self):
        # Abrir seletor de cores
        color = colorchooser.askcolor(initialcolor=self.fg_color)
        
        if color[1]:
            # Alterar cor do texto
            self.fg_color = color[1]
            self.text_editor.config(fg=self.fg_color)
            self.update_status(f"Cor alterada: {color[1]}")
    
    def toggle_word_wrap(self):
        self.settings['word_wrap'] = not self.settings['word_wrap']
        wrap_mode = tk.WORD if self.settings['word_wrap'] else tk.NONE
        self.text_editor.config(wrap=wrap_mode)
        self.update_status(f"Quebra de linha: {'Ativada' if self.settings['word_wrap'] else 'Desativada'}")
    
    def toggle_line_numbers(self):
        self.settings['show_line_numbers'] = not self.settings['show_line_numbers']
        
        if self.settings['show_line_numbers']:
            # Recrear o editor com números de linha
            self.text_editor.pack_forget()
            self.create_text_editor()
        else:
            # Recrear o editor sem números de linha
            self.text_editor.pack_forget()
            if hasattr(self, 'line_numbers'):
                self.line_numbers.pack_forget()
            self.create_text_editor()
            
        self.update_status(f"Números de linha: {'Ativados' if self.settings['show_line_numbers'] else 'Desativados'}")
    
    def toggle_line_highlight(self):
        self.settings['highlight_current_line'] = not self.settings['highlight_current_line']
        
        if self.settings['highlight_current_line']:
            # Destacar linha atual
            self.highlight_current_line()
            self.update_status("Destaque de linha atual: Ativado")
        else:
            # Remover destaque
            self.text_editor.tag_remove("current_line", "1.0", tk.END)
            self.update_status("Destaque de linha atual: Desativado")
    
    def toggle_main_toolbar(self):
        if self.main_toolbar.winfo_ismapped():
            self.main_toolbar.pack_forget()
            self.update_status("Barra de ferramentas principal: Oculta")
        else:
            self.main_toolbar.pack(side=tk.TOP, fill=tk.X)
            self.update_status("Barra de ferramentas principal: Visível")
    
    def toggle_format_toolbar(self):
        if self.format_toolbar.winfo_ismapped():
            self.format_toolbar.pack_forget()
            self.update_status("Barra de formatação: Oculta")
        else:
            self.format_toolbar.pack(side=tk.TOP, fill=tk.X)
            self.update_status("Barra de formatação: Visível")
    
    def toggle_elements_toolbar(self):
        if self.elements_toolbar.winfo_ismapped():
            self.elements_toolbar.pack_forget()
            self.update_status("Barra de elementos: Oculta")
        else:
            self.elements_toolbar.pack(side=tk.TOP, fill=tk.X)
            self.update_status("Barra de elementos: Visível")
    
    def toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
            self.update_status("Barra lateral: Oculta")
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.update_status("Barra lateral: Visível")
    
    def toggle_status_bar(self):
        if self.status_bar.winfo_ismapped():
            self.status_bar.pack_forget()
            self.update_status("Barra de status: Oculta")
        else:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.update_status("Barra de status: Visível")
    
    def change_theme(self, theme):
        self.settings['theme'] = theme
        self.apply_theme()
        
        # Atualizar cores dos componentes
        self.root.configure(bg=self.bg_color)
        self.status_bar.configure(bg=self.secondary_color)
        self.status_label.configure(bg=self.secondary_color, fg=self.fg_color)
        self.word_count_label.configure(bg=self.secondary_color, fg=self.fg_color)
        self.cursor_pos_label.configure(bg=self.secondary_color, fg=self.fg_color)
        self.element_format_label.configure(bg=self.secondary_color, fg=self.fg_color)
        
        # Atualizar cores do editor
        self.text_editor.configure(bg=self.bg_color, fg=self.fg_color)
        
        # Atualizar cores das barras de ferramentas
        self.main_toolbar.configure(bg=self.secondary_color)
        self.format_toolbar.configure(bg=self.secondary_color)
        self.elements_toolbar.configure(bg=self.secondary_color)
        
        for widget in self.main_toolbar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=self.secondary_color, fg=self.fg_color)
                
        for widget in self.format_toolbar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=self.secondary_color, fg=self.fg_color)
                
        for widget in self.elements_toolbar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=self.secondary_color, fg=self.fg_color)
        
        # Atualizar cores do menu lateral
        self.sidebar.configure(bg=self.blue_color)
        self.toggle_button.configure(bg=self.blue_color, fg=self.fg_color)
        
        # Atualizar cores das abas
        self.characters_frame.configure(bg=self.blue_color)
        self.scenes_frame.configure(bg=self.blue_color)
        self.notes_frame.configure(bg=self.blue_color)
        
        # Atualizar cores dos widgets das abas
        self.characters_listbox.configure(bg=self.secondary_color, fg=self.fg_color)
        self.scenes_listbox.configure(bg=self.secondary_color, fg=self.fg_color)
        self.notes_editor.configure(bg=self.secondary_color, fg=self.fg_color)
        
        self.update_status(f"Tema alterado: {'Claro' if theme == 'light' else 'Escuro'}")
    
    def zoom_in(self):
        current_size = self.settings['font_size']
        if current_size < 24:
            self.settings['font_size'] += 1
            self.default_font = font.Font(family=self.settings['font_family'], size=self.settings['font_size'])
            self.text_editor.config(font=self.default_font)
            
            # Atualizar tags de formatação
            self.text_editor.tag_configure("bold", font=self.default_font.copy().configure(weight="bold"))
            self.text_editor.tag_configure("italic", font=self.default_font.copy().configure(slant="italic"))
            self.text_editor.tag_configure("underline", font=self.default_font.copy().configure(underline=True))
            self.text_editor.tag_configure("character", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("scene", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("transition", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("note", font=self.default_font.copy().configure(slant="italic"), 
                                          foreground="#cccccc")
            
            # Atualizar números de linha
            if self.settings['show_line_numbers']:
                self.line_numbers.config(font=self.default_font)
                self.update_line_numbers()
                
            self.update_status(f"Zoom: {self.settings['font_size']}pt")
    
    def zoom_out(self):
        current_size = self.settings['font_size']
        if current_size > 8:
            self.settings['font_size'] -= 1
            self.default_font = font.Font(family=self.settings['font_family'], size=self.settings['font_size'])
            self.text_editor.config(font=self.default_font)
            
            # Atualizar tags de formatação
            self.text_editor.tag_configure("bold", font=self.default_font.copy().configure(weight="bold"))
            self.text_editor.tag_configure("italic", font=self.default_font.copy().configure(slant="italic"))
            self.text_editor.tag_configure("underline", font=self.default_font.copy().configure(underline=True))
            self.text_editor.tag_configure("character", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("scene", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("transition", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("note", font=self.default_font.copy().configure(slant="italic"), 
                                          foreground="#cccccc")
            
            # Atualizar números de linha
            if self.settings['show_line_numbers']:
                self.line_numbers.config(font=self.default_font)
                self.update_line_numbers()
                
            self.update_status(f"Zoom: {self.settings['font_size']}pt")
    
    def zoom_normal(self):
        self.settings['font_size'] = 12
        self.default_font = font.Font(family=self.settings['font_family'], size=self.settings['font_size'])
        self.text_editor.config(font=self.default_font)
        
        # Atualizar tags de formatação
        self.text_editor.tag_configure("bold", font=self.default_font.copy().configure(weight="bold"))
        self.text_editor.tag_configure("italic", font=self.default_font.copy().configure(slant="italic"))
        self.text_editor.tag_configure("underline", font=self.default_font.copy().configure(underline=True))
        self.text_editor.tag_configure("character", font=self.default_font.copy().configure(weight="bold"), 
                                      foreground=self.highlight_color)
        self.text_editor.tag_configure("scene", font=self.default_font.copy().configure(weight="bold"), 
                                      foreground=self.highlight_color)
        self.text_editor.tag_configure("transition", font=self.default_font.copy().configure(weight="bold"), 
                                      foreground=self.highlight_color)
        self.text_editor.tag_configure("note", font=self.default_font.copy().configure(slant="italic"), 
                                      foreground="#cccccc")
        
        # Atualizar números de linha
        if self.settings['show_line_numbers']:
            self.line_numbers.config(font=self.default_font)
            self.update_line_numbers()
            
        self.update_status(f"Zoom: {self.settings['font_size']}pt")
    
    def toggle_auto_save(self):
        self.settings['auto_save'] = not self.settings['auto_save']
        if self.settings['auto_save']:
            messagebox.showinfo("Auto-salvar", "Auto-salvamento ativado!")
            self.update_status("Auto-salvamento ativado")
        else:
            messagebox.showinfo("Auto-salvar", "Auto-salvamento desativado!")
            self.update_status("Auto-salvamento desativado")
    
    def manage_characters(self):
        # Criar janela de gerenciamento de personagens
        char_window = tk.Toplevel(self.root)
        char_window.title("Gerenciar Personagens")
        char_window.geometry("500x400")
        char_window.configure(bg=self.secondary_color)
        char_window.transient(self.root)
        char_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(char_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de personagens
        list_frame = tk.Frame(main_frame, bg=self.secondary_color)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Personagens:", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).pack(anchor=tk.W, pady=5)
        
        # Lista com scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        char_list = tk.Listbox(list_frame, bg=self.bg_color, fg=self.fg_color, 
                              yscrollcommand=scrollbar.set, height=10)
        char_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=char_list.yview)
        
        # Preencher lista
        for char in self.characters:
            char_list.insert(tk.END, char['name'])
        
        # Detalhes do personagem
        details_frame = tk.Frame(main_frame, bg=self.secondary_color)
        details_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(details_frame, text="Nome:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(details_frame, bg=self.bg_color, fg=self.fg_color, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        tk.Label(details_frame, text="Descrição:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(details_frame, bg=self.bg_color, fg=self.fg_color, height=5, width=40)
        desc_text.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        def add_character():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Por favor, insira um nome para o personagem.")
                return
                
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe
            for char in self.characters:
                if char['name'].lower() == name.lower():
                    messagebox.showwarning("Aviso", "Já existe um personagem com este nome.")
                    return
            
            # Adicionar personagem
            self.characters.append({
                'name': name,
                'description': description
            })
            
            # Atualizar listas
            char_list.insert(tk.END, name)
            self.characters_listbox.insert(tk.END, name)
            
            # Limpar campos
            name_entry.delete(0, tk.END)
            desc_text.delete(1.0, tk.END)
            
            self.update_status(f"Personagem adicionado: {name}")
        
        def update_character():
            selection = char_list.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione um personagem para editar.")
                return
                
            index = selection[0]
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Por favor, insira um nome para o personagem.")
                return
                
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe (exceto o atual)
            for i, char in enumerate(self.characters):
                if i != index and char['name'].lower() == name.lower():
                    messagebox.showwarning("Aviso", "Já existe um personagem com este nome.")
                    return
            
            # Atualizar personagem
            self.characters[index] = {
                'name': name,
                'description': description
            }
            
            # Atualizar listas
            char_list.delete(index)
            char_list.insert(index, name)
            char_list.selection_set(index)
            
            self.characters_listbox.delete(index)
            self.characters_listbox.insert(index, name)
            
            self.update_status(f"Personagem atualizado: {name}")
        
        def delete_character():
            selection = char_list.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione um personagem para remover.")
                return
                
            index = selection[0]
            name = self.characters[index]['name']
            
            if messagebox.askyesno("Confirmar", f"Deseja realmente remover o personagem '{name}'?"):
                # Remover personagem
                del self.characters[index]
                
                # Atualizar listas
                char_list.delete(index)
                self.characters_listbox.delete(index)
                
                # Limpar campos
                name_entry.delete(0, tk.END)
                desc_text.delete(1.0, tk.END)
                
                self.update_status(f"Personagem removido: {name}")
        
        def select_character(event=None):
            selection = char_list.curselection()
            if selection:
                index = selection[0]
                char = self.characters[index]
                name_entry.delete(0, tk.END)
                name_entry.insert(0, char['name'])
                desc_text.delete(1.0, tk.END)
                desc_text.insert(1.0, char['description'])
        
        # Configurar eventos
        char_list.bind('<<ListboxSelect>>', select_character)
        
        # Botões
        add_btn = tk.Button(button_frame, text="Adicionar", command=add_character,
                           bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(button_frame, text="Atualizar", command=update_character,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(button_frame, text="Remover", command=delete_character,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Fechar", command=char_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar grid
        details_frame.columnconfigure(1, weight=1)
    
    def add_character(self):
        # Criar janela para adicionar personagem
        add_window = tk.Toplevel(self.root)
        add_window.title("Adicionar Personagem")
        add_window.geometry("400x200")
        add_window.configure(bg=self.secondary_color)
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(add_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos
        tk.Label(main_frame, text="Nome:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        name_entry.focus_set()
        
        tk.Label(main_frame, text="Descrição:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, bg=self.bg_color, fg=self.fg_color, height=5, width=30)
        desc_text.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        def save_character():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Por favor, insira um nome para o personagem.")
                return
                
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe
            for char in self.characters:
                if char['name'].lower() == name.lower():
                    messagebox.showwarning("Aviso", "Já existe um personagem com este nome.")
                    return
            
            # Adicionar personagem
            self.characters.append({
                'name': name,
                'description': description
            })
            
            # Atualizar lista
            self.characters_listbox.insert(tk.END, name)
            
            add_window.destroy()
            self.update_status(f"Personagem adicionado: {name}")
        
        save_btn = tk.Button(button_frame, text="Salvar", command=save_character,
                            bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=add_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def edit_character(self):
        selection = self.characters_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um personagem para editar.")
            return
            
        index = selection[0]
        char = self.characters[index]
        
        # Criar janela para editar personagem
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Personagem")
        edit_window.geometry("400x200")
        edit_window.configure(bg=self.secondary_color)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(edit_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos
        tk.Label(main_frame, text="Nome:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        name_entry.insert(0, char['name'])
        name_entry.focus_set()
        
        tk.Label(main_frame, text="Descrição:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, bg=self.bg_color, fg=self.fg_color, height=5, width=30)
        desc_text.grid(row=1, column=1, sticky=tk.EW, pady=5)
        desc_text.insert(1.0, char['description'])
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        def update_character():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Por favor, insira um nome para o personagem.")
                return
                
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe (exceto o atual)
            for i, c in enumerate(self.characters):
                if i != index and c['name'].lower() == name.lower():
                    messagebox.showwarning("Aviso", "Já existe um personagem com este nome.")
                    return
            
            # Atualizar personagem
            self.characters[index] = {
                'name': name,
                'description': description
            }
            
            # Atualizar lista
            self.characters_listbox.delete(index)
            self.characters_listbox.insert(index, name)
            self.characters_listbox.selection_set(index)
            
            edit_window.destroy()
            self.update_status(f"Personagem atualizado: {name}")
        
        update_btn = tk.Button(button_frame, text="Atualizar", command=update_character,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=edit_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def remove_character(self):
        selection = self.characters_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um personagem para remover.")
            return
            
        index = selection[0]
        name = self.characters[index]['name']
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente remover o personagem '{name}'?"):
            # Remover personagem
            del self.characters[index]
            
            # Atualizar lista
            self.characters_listbox.delete(index)
            
            self.update_status(f"Personagem removido: {name}")
    
    def manage_scenes(self):
        # Criar janela de gerenciamento de cenas
        scene_window = tk.Toplevel(self.root)
        scene_window.title("Gerenciar Cenas")
        scene_window.geometry("500x400")
        scene_window.configure(bg=self.secondary_color)
        scene_window.transient(self.root)
        scene_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(scene_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de cenas
        list_frame = tk.Frame(main_frame, bg=self.secondary_color)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Cenas:", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).pack(anchor=tk.W, pady=5)
        
        # Lista com scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        scene_list = tk.Listbox(list_frame, bg=self.bg_color, fg=self.fg_color, 
                               yscrollcommand=scrollbar.set, height=10)
        scene_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=scene_list.yview)
        
        # Preencher lista
        for scene in self.scenes:
            scene_list.insert(tk.END, scene['title'])
        
        # Detalhes da cena
        details_frame = tk.Frame(main_frame, bg=self.secondary_color)
        details_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(details_frame, text="Título:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        title_entry = tk.Entry(details_frame, bg=self.bg_color, fg=self.fg_color, width=40)
        title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        tk.Label(details_frame, text="Local:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        location_entry = tk.Entry(details_frame, bg=self.bg_color, fg=self.fg_color, width=40)
        location_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        tk.Label(details_frame, text="Horário:", bg=self.secondary_color, fg=self.fg_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        time_entry = tk.Entry(details_frame, bg=self.bg_color, fg=self.fg_color, width=40)
        time_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        tk.Label(details_frame, text="Descrição:", bg=self.secondary_color, fg=self.fg_color).grid(row=3, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(details_frame, bg=self.bg_color, fg=self.fg_color, height=5, width=40)
        desc_text.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def add_scene():
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Aviso", "Por favor, insira um título para a cena.")
                return
                
            location = location_entry.get().strip()
            time = time_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe
            for scene in self.scenes:
                if scene['title'].lower() == title.lower():
                    messagebox.showwarning("Aviso", "Já existe uma cena com este título.")
                    return
            
            # Adicionar cena
            self.scenes.append({
                'title': title,
                'location': location,
                'time': time,
                'description': description
            })
            
            # Atualizar listas
            scene_list.insert(tk.END, title)
            self.scenes_listbox.insert(tk.END, title)
            
            # Limpar campos
            title_entry.delete(0, tk.END)
            location_entry.delete(0, tk.END)
            time_entry.delete(0, tk.END)
            desc_text.delete(1.0, tk.END)
            
            self.update_status(f"Cena adicionada: {title}")
        
        def update_scene():
            selection = scene_list.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione uma cena para editar.")
                return
                
            index = selection[0]
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Aviso", "Por favor, insira um título para a cena.")
                return
                
            location = location_entry.get().strip()
            time = time_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe (exceto a atual)
            for i, scene in enumerate(self.scenes):
                if i != index and scene['title'].lower() == title.lower():
                    messagebox.showwarning("Aviso", "Já existe uma cena com este título.")
                    return
            
            # Atualizar cena
            self.scenes[index] = {
                'title': title,
                'location': location,
                'time': time,
                'description': description
            }
            
            # Atualizar listas
            scene_list.delete(index)
            scene_list.insert(index, title)
            scene_list.selection_set(index)
            
            self.scenes_listbox.delete(index)
            self.scenes_listbox.insert(index, title)
            
            self.update_status(f"Cena atualizada: {title}")
        
        def delete_scene():
            selection = scene_list.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione uma cena para remover.")
                return
                
            index = selection[0]
            title = self.scenes[index]['title']
            
            if messagebox.askyesno("Confirmar", f"Deseja realmente remover a cena '{title}'?"):
                # Remover cena
                del self.scenes[index]
                
                # Atualizar listas
                scene_list.delete(index)
                self.scenes_listbox.delete(index)
                
                # Limpar campos
                title_entry.delete(0, tk.END)
                location_entry.delete(0, tk.END)
                time_entry.delete(0, tk.END)
                desc_text.delete(1.0, tk.END)
                
                self.update_status(f"Cena removida: {title}")
        
        def select_scene(event=None):
            selection = scene_list.curselection()
            if selection:
                index = selection[0]
                scene = self.scenes[index]
                title_entry.delete(0, tk.END)
                title_entry.insert(0, scene['title'])
                location_entry.delete(0, tk.END)
                location_entry.insert(0, scene['location'])
                time_entry.delete(0, tk.END)
                time_entry.insert(0, scene['time'])
                desc_text.delete(1.0, tk.END)
                desc_text.insert(1.0, scene['description'])
        
        # Configurar eventos
        scene_list.bind('<<ListboxSelect>>', select_scene)
        
        # Botões
        add_btn = tk.Button(button_frame, text="Adicionar", command=add_scene,
                           bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(button_frame, text="Atualizar", command=update_scene,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(button_frame, text="Remover", command=delete_scene,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Fechar", command=scene_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar grid
        details_frame.columnconfigure(1, weight=1)
    
    def add_scene(self):
        # Criar janela para adicionar cena
        add_window = tk.Toplevel(self.root)
        add_window.title("Adicionar Cena")
        add_window.geometry("400x250")
        add_window.configure(bg=self.secondary_color)
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(add_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos
        tk.Label(main_frame, text="Título:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        title_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        title_entry.focus_set()
        
        tk.Label(main_frame, text="Local:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        location_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        location_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        tk.Label(main_frame, text="Horário:", bg=self.secondary_color, fg=self.fg_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        time_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        time_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        tk.Label(main_frame, text="Descrição:", bg=self.secondary_color, fg=self.fg_color).grid(row=3, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, bg=self.bg_color, fg=self.fg_color, height=5, width=30)
        desc_text.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def save_scene():
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Aviso", "Por favor, insira um título para a cena.")
                return
                
            location = location_entry.get().strip()
            time = time_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe
            for scene in self.scenes:
                if scene['title'].lower() == title.lower():
                    messagebox.showwarning("Aviso", "Já existe uma cena com este título.")
                    return
            
            # Adicionar cena
            self.scenes.append({
                'title': title,
                'location': location,
                'time': time,
                'description': description
            })
            
            # Atualizar lista
            self.scenes_listbox.insert(tk.END, title)
            
            add_window.destroy()
            self.update_status(f"Cena adicionada: {title}")
        
        save_btn = tk.Button(button_frame, text="Salvar", command=save_scene,
                            bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=add_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def edit_scene(self):
        selection = self.scenes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione uma cena para editar.")
            return
            
        index = selection[0]
        scene = self.scenes[index]
        
        # Criar janela para editar cena
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Cena")
        edit_window.geometry("400x250")
        edit_window.configure(bg=self.secondary_color)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(edit_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos
        tk.Label(main_frame, text="Título:", bg=self.secondary_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        title_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        title_entry.insert(0, scene['title'])
        title_entry.focus_set()
        
        tk.Label(main_frame, text="Local:", bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        location_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        location_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        location_entry.insert(0, scene['location'])
        
        tk.Label(main_frame, text="Horário:", bg=self.secondary_color, fg=self.fg_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        time_entry = tk.Entry(main_frame, bg=self.bg_color, fg=self.fg_color, width=30)
        time_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        time_entry.insert(0, scene['time'])
        
        tk.Label(main_frame, text="Descrição:", bg=self.secondary_color, fg=self.fg_color).grid(row=3, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, bg=self.bg_color, fg=self.fg_color, height=5, width=30)
        desc_text.grid(row=3, column=1, sticky=tk.EW, pady=5)
        desc_text.insert(1.0, scene['description'])
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def update_scene():
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Aviso", "Por favor, insira um título para a cena.")
                return
                
            location = location_entry.get().strip()
            time = time_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            
            # Verificar se já existe (exceto a atual)
            for i, s in enumerate(self.scenes):
                if i != index and s['title'].lower() == title.lower():
                    messagebox.showwarning("Aviso", "Já existe uma cena com este título.")
                    return
            
            # Atualizar cena
            self.scenes[index] = {
                'title': title,
                'location': location,
                'time': time,
                'description': description
            }
            
            # Atualizar lista
            self.scenes_listbox.delete(index)
            self.scenes_listbox.insert(index, title)
            self.scenes_listbox.selection_set(index)
            
            edit_window.destroy()
            self.update_status(f"Cena atualizada: {title}")
        
        update_btn = tk.Button(button_frame, text="Atualizar", command=update_scene,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=edit_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def remove_scene(self):
        selection = self.scenes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione uma cena para remover.")
            return
            
        index = selection[0]
        title = self.scenes[index]['title']
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente remover a cena '{title}'?"):
            # Remover cena
            del self.scenes[index]
            
            # Atualizar lista
            self.scenes_listbox.delete(index)
            
            self.update_status(f"Cena removida: {title}")
    
    def save_notes(self):
        # Salvar notas no arquivo de metadados
        self.save_metadata()
        self.update_status("Notas salvas")
    
    def word_count(self):
        text = self.text_editor.get(1.0, tk.END)
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        messagebox.showinfo("Contagem de Palavras", 
                           f"Palavras: {word_count}\nCaracteres: {char_count}")
    
    def estimate_reading_time(self):
        text = self.text_editor.get(1.0, tk.END)
        words = text.split()
        word_count = len(words)
        
        # Estimativa: 200 palavras por minuto
        reading_time_minutes = word_count / 200
        
        # Converter para minutos e segundos
        minutes = int(reading_time_minutes)
        seconds = int((reading_time_minutes - minutes) * 60)
        
        messagebox.showinfo("Tempo de Leitura", 
                           f"Tempo estimado de leitura: {minutes} minutos e {seconds} segundos\n"
                           f"Baseado em 200 palavras por minuto")
    
    def show_stats(self):
        text = self.text_editor.get(1.0, tk.END)
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        lines = text.split('\n')
        line_count = len(lines) - 1  # -1 porque a última linha é vazia
        
        # Contar personagens
        character_count = len(self.characters)
        
        # Contar cenas
        scene_count = len(self.scenes)
        
        # Contar elementos de roteiro
        scene_headings = 0
        character_names = 0
        dialogues = 0
        actions = 0
        transitions = 0
        notes = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("CENA:"):
                scene_headings += 1
            elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                character_names += 1
            elif stripped.startswith("TRANSIÇÃO:"):
                transitions += 1
            elif stripped.startswith("NOTA:"):
                notes += 1
            elif stripped:
                # Verificar se é diálogo (linha após personagem)
                # Esta é uma simplificação; em um cenário real, precisaríamos analisar melhor
                dialogues += 1
        
        # Estimar páginas (considerando 55 linhas por página)
        page_count = max(1, line_count // 55)
        
        stats = f"Estatísticas do Roteiro:\n\n"
        stats += f"Palavras: {word_count}\n"
        stats += f"Caracteres: {char_count}\n"
        stats += f"Linhas: {line_count}\n"
        stats += f"Páginas (estimado): {page_count}\n\n"
        stats += f"Elementos de Roteiro:\n"
        stats += f"Cenas: {scene_headings}\n"
        stats += f"Personagens: {character_names}\n"
        stats += f"Diálogos: {dialogues}\n"
        stats += f"Ações: {actions}\n"
        stats += f"Transições: {transitions}\n"
        stats += f"Notas: {notes}\n\n"
        stats += f"Personagens cadastrados: {character_count}\n"
        stats += f"Cenas cadastradas: {scene_count}"
        
        messagebox.showinfo("Estatísticas", stats)
    
    def check_spelling(self):
        # Simulação de verificação ortográfica
        text = self.text_editor.get(1.0, tk.END)
        
        # Palavras comuns em português para simulação
        common_words = [
            "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
            "em", "no", "na", "nos", "nas", "por", "pelo", "pela", "pelos", "pelas",
            "com", "como", "para", "sem", "sob", "sobre", "entre", "até", "a", "ante",
            "após", "desde", "durante", "mediante", "perante", "salvo", "segundo", "senão",
            "tirante", "fora", "exceto", "que", "se", "não", "é", "ser", "estar", "ter",
            "haver", "fazer", "ir", "poder", "dizer", "dar", "ver", "saber", "querer",
            "chegar", "passar", "ficar", "tomar", "voltar", "por", "ainda", "agora", "já",
            "aqui", "ali", "lá", "acolá", "hoje", "ontem", "amanhã", "depois", "antes",
            "muito", "pouco", "mais", "menos", "tão", "quanto", "como", "bem", "mal",
            "grande", "pequeno", "longe", "perto", "alto", "baixo", "melhor", "pior"
        ]
        
        # Dividir texto em palavras
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Encontrar palavras que não estão na lista de palavras comuns
        misspelled = [word for word in words if word not in common_words and len(word) > 3]
        
        # Remover duplicatas
        misspelled = list(set(misspelled))
        
        if misspelled:
            # Criar janela de verificação ortográfica
            spell_window = tk.Toplevel(self.root)
            spell_window.title("Verificação Ortográfica")
            spell_window.geometry("400x300")
            spell_window.configure(bg=self.secondary_color)
            spell_window.transient(self.root)
            spell_window.grab_set()
            
            # Frame principal
            main_frame = tk.Frame(spell_window, bg=self.secondary_color)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(main_frame, text="Possíveis erros de ortografia:", 
                    bg=self.secondary_color, fg=self.fg_color, font=self.title_font).pack(anchor=tk.W, pady=5)
            
            # Lista de palavras
            list_frame = tk.Frame(main_frame, bg=self.secondary_color)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            word_list = tk.Listbox(list_frame, bg=self.bg_color, fg=self.fg_color, 
                                  yscrollcommand=scrollbar.set)
            word_list.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=word_list.yview)
            
            # Preencher lista
            for word in sorted(misspelled):
                word_list.insert(tk.END, word)
            
            # Botões
            button_frame = tk.Frame(main_frame, bg=self.secondary_color)
            button_frame.pack(fill=tk.X, pady=10)
            
            ignore_btn = tk.Button(button_frame, text="Ignorar Tudo", command=spell_window.destroy,
                                  bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
            ignore_btn.pack(side=tk.RIGHT, padx=5)
            
            # Configurar eventos
            def on_double_click(event):
                selection = word_list.curselection()
                if selection:
                    word = word_list.get(selection[0])
                    
                    # Buscar a palavra no texto
                    text = self.text_editor.get(1.0, tk.END)
                    pattern = r'\b' + re.escape(word) + r'\b'
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    
                    if matches:
                        self.search_matches = [(m.start(), m.end()) for m in matches]
                        self.current_match = -1
                        self.find_next()
            
            word_list.bind('<Double-Button-1>', on_double_click)
        else:
            messagebox.showinfo("Verificação Ortográfica", "Nenhum erro de ortografia encontrado.")
    
    def analyze_script(self):
        # Analisar o roteiro e fornecer sugestões
        text = self.text_editor.get(1.0, tk.END)
        lines = text.split('\n')
        
        # Análise básica
        analysis = {
            'scenes': [],
            'characters': {},
            'dialogues': {},
            'actions': 0,
            'transitions': 0,
            'notes': 0,
            'issues': [],
            'suggestions': []
        }
        
        # Variáveis para rastrear o estado atual
        current_character = None
        current_scene = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Identificar elementos de roteiro
            if stripped.startswith("CENA:"):
                # Nova cena
                current_scene = stripped[6:].strip()
                analysis['scenes'].append({
                    'title': current_scene,
                    'line': i + 1
                })
                current_character = None
            elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                # Novo personagem
                current_character = stripped
                if current_character not in analysis['characters']:
                    analysis['characters'][current_character] = {
                        'dialogues': 0,
                        'first_appearance': i + 1
                    }
            elif current_character and not stripped.startswith("TRANSIÇÃO:") and not stripped.startswith("NOTA:"):
                # Diálogo do personagem atual
                if current_character not in analysis['dialogues']:
                    analysis['dialogues'][current_character] = []
                analysis['dialogues'][current_character].append({
                    'text': stripped,
                    'line': i + 1
                })
                if current_character in analysis['characters']:
                    analysis['characters'][current_character]['dialogues'] += 1
            elif stripped.startswith("TRANSIÇÃO:"):
                # Transição
                analysis['transitions'] += 1
                current_character = None
            elif stripped.startswith("NOTA:"):
                # Nota
                analysis['notes'] += 1
                current_character = None
            else:
                # Ação
                analysis['actions'] += 1
                current_character = None
        
        # Gerar problemas e sugestões
        if len(analysis['scenes']) < 3:
            analysis['issues'].append("O roteiro tem poucas cenas. Considere adicionar mais cenas para desenvolver melhor a história.")
        
        if len(analysis['characters']) < 2:
            analysis['issues'].append("O roteiro tem poucos personagens. Considere adicionar mais personagens para enriquecer a história.")
        
        # Verificar personagens com poucos diálogos
        for char, data in analysis['characters'].items():
            if data['dialogues'] < 3:
                analysis['suggestions'].append(f"O personagem '{char}' tem poucos diálogos. Considere desenvolver mais este personagem.")
        
        # Verificar cenas muito longas ou muito curtas
        scene_lengths = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("CENA:"):
                scene_name = stripped[6:].strip()
                if scene_name not in scene_lengths:
                    scene_lengths[scene_name] = {'start': i, 'lines': 0}
            elif scene_lengths:
                # Incrementar contador de linhas para a cena atual
                current_scene = list(scene_lengths.keys())[-1]
                scene_lengths[current_scene]['lines'] += 1
        
        for scene, data in scene_lengths.items():
            if data['lines'] < 10:
                analysis['suggestions'].append(f"A cena '{scene}' parece ser muito curta. Considere adicionar mais detalhes ou diálogos.")
            elif data['lines'] > 100:
                analysis['suggestions'].append(f"A cena '{scene}' parece ser muito longa. Considere dividi-la em cenas menores.")
        
        # Criar janela de análise
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Análise de Roteiro")
        analysis_window.geometry("600x500")
        analysis_window.configure(bg=self.secondary_color)
        analysis_window.transient(self.root)
        
        # Frame principal
        main_frame = tk.Frame(analysis_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de resumo
        summary_frame = tk.Frame(notebook, bg=self.secondary_color)
        notebook.add(summary_frame, text="Resumo")
        
        summary_text = tk.Text(summary_frame, bg=self.bg_color, fg=self.fg_color, 
                             wrap=tk.WORD, bd=0, padx=10, pady=10)
        summary_text.pack(fill=tk.BOTH, expand=True)
        
        summary_content = f"""
Resumo da Análise:

Cenas: {len(analysis['scenes'])}
Personagens: {len(analysis['characters'])}
Ações: {analysis['actions']}
Diálogos: {sum(data['dialogues'] for data in analysis['characters'].values())}
Transições: {analysis['transitions']}
Notas: {analysis['notes']}

Personagens com mais diálogos:
"""
        
        # Ordenar personagens por número de diálogos
        sorted_characters = sorted(analysis['characters'].items(), key=lambda x: x[1]['dialogues'], reverse=True)
        
        for char, data in sorted_characters[:5]:
            summary_content += f"- {char}: {data['dialogues']} diálogos\n"
        
        summary_text.insert(tk.END, summary_content)
        summary_text.config(state=tk.DISABLED)
        
        # Aba de problemas
        issues_frame = tk.Frame(notebook, bg=self.secondary_color)
        notebook.add(issues_frame, text="Problemas")
        
        issues_text = tk.Text(issues_frame, bg=self.bg_color, fg=self.fg_color, 
                            wrap=tk.WORD, bd=0, padx=10, pady=10)
        issues_text.pack(fill=tk.BOTH, expand=True)
        
        if analysis['issues']:
            for issue in analysis['issues']:
                issues_text.insert(tk.END, f"• {issue}\n\n")
        else:
            issues_text.insert(tk.END, "Nenhum problema identificado.")
        
        issues_text.config(state=tk.DISABLED)
        
        # Aba de sugestões
        suggestions_frame = tk.Frame(notebook, bg=self.secondary_color)
        notebook.add(suggestions_frame, text="Sugestões")
        
        suggestions_text = tk.Text(suggestions_frame, bg=self.bg_color, fg=self.fg_color, 
                                  wrap=tk.WORD, bd=0, padx=10, pady=10)
        suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        if analysis['suggestions']:
            for suggestion in analysis['suggestions']:
                suggestions_text.insert(tk.END, f"• {suggestion}\n\n")
        else:
            suggestions_text.insert(tk.END, "Nenhuma sugestão no momento.")
        
        suggestions_text.config(state=tk.DISABLED)
        
        # Aba de personagens
        characters_frame = tk.Frame(notebook, bg=self.secondary_color)
        notebook.add(characters_frame, text="Personagens")
        
        # Lista de personagens
        list_frame = tk.Frame(characters_frame, bg=self.secondary_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        characters_list = tk.Listbox(list_frame, bg=self.bg_color, fg=self.fg_color, 
                                     yscrollcommand=scrollbar.set)
        characters_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=characters_list.yview)
        
        # Preencher lista
        for char, data in sorted_characters:
            characters_list.insert(tk.END, f"{char} - {data['dialogues']} diálogos (linha {data['first_appearance']})")
        
        # Botão Fechar
        close_btn = tk.Button(main_frame, text="Fechar", command=analysis_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(pady=10)
    
    def reformat_script(self):
        # Reformatar o roteiro de acordo com o padrão da indústria
        text = self.text_editor.get(1.0, tk.END)
        lines = text.split('\n')
        
        reformatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # Manter linhas em branco
                reformatted_lines.append("")
            elif stripped.startswith("CENA:"):
                # Formatar cena
                scene_text = stripped[6:].strip().upper()
                reformatted_lines.append(f"CENA: {scene_text}")
            elif stripped.isupper() and len(stripped) < self.settings['character_width']:
                # Formatar personagem (centralizado)
                char_length = len(stripped)
                total_spaces = self.settings['page_width'] - char_length
                left_spaces = total_spaces // 2
                reformatted_lines.append(' ' * left_spaces + stripped)
            elif stripped.startswith("TRANSIÇÃO:"):
                # Formatar transição (alinhado à direita)
                transition_text = stripped[11:].strip().upper()
                transition_length = len(transition_text) + 11  # Incluir "TRANSIÇÃO: "
                total_spaces = self.settings['page_width'] - transition_length
                left_spaces = total_spaces
                reformatted_lines.append(' ' * left_spaces + f"TRANSIÇÃO: {transition_text}")
            elif stripped.startswith("NOTA:"):
                # Formatar nota
                note_text = stripped[6:].strip()
                reformatted_lines.append(f"NOTA: {note_text}")
            else:
                # Verificar se é diálogo (linha após personagem)
                if reformatted_lines and reformatted_lines[-1].isupper() and len(reformatted_lines[-1].strip()) < self.settings['character_width']:
                    # Formatar diálogo (com recuo)
                    dialogue_text = stripped
                    reformatted_lines.append(' ' * 15 + dialogue_text)
                else:
                    # Formatar ação (com recuo menor)
                    action_text = stripped
                    reformatted_lines.append(' ' * 10 + action_text)
        
        # Atualizar o editor
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, '\n'.join(reformatted_lines))
        
        # Aplicar formatação
        self.apply_formatting()
        
        self.update_status("Roteiro reformatado")
    
    def apply_formatting(self):
        # Aplicar formatação ao texto do editor
        text = self.text_editor.get(1.0, tk.END)
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            start_index = f"{i+1}.0"
            end_index = f"{i+1}.end"
            
            if line.strip().startswith("CENA:"):
                self.text_editor.tag_add("scene", start_index, end_index)
            elif line.strip().isupper() and len(line.strip()) < self.settings['character_width']:
                self.text_editor.tag_add("character", start_index, end_index)
            elif line.strip().startswith("TRANSIÇÃO:"):
                self.text_editor.tag_add("transition", start_index, end_index)
            elif line.strip().startswith("NOTA:"):
                self.text_editor.tag_add("note", start_index, end_index)
    
    def configure_formatting(self):
        # Criar janela de configuração de formatação
        format_window = tk.Toplevel(self.root)
        format_window.title("Configurar Formatação")
        format_window.geometry("400x300")
        format_window.configure(bg=self.secondary_color)
        format_window.transient(self.root)
        format_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(format_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurações
        tk.Label(main_frame, text="Configurações de Formatação:", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Largura da página
        tk.Label(main_frame, text="Largura da página (caracteres):", 
                bg=self.secondary_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        page_width_var = tk.IntVar(value=self.settings['page_width'])
        page_width_spinbox = tk.Spinbox(main_frame, from_=60, to=100, textvariable=page_width_var, 
                                       bg=self.bg_color, fg=self.fg_color, width=10)
        page_width_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Largura do personagem
        tk.Label(main_frame, text="Largura do personagem (caracteres):", 
                bg=self.secondary_color, fg=self.fg_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        character_width_var = tk.IntVar(value=self.settings['character_width'])
        character_width_spinbox = tk.Spinbox(main_frame, from_=20, to=60, textvariable=character_width_var, 
                                           bg=self.bg_color, fg=self.fg_color, width=10)
        character_width_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Largura do diálogo
        tk.Label(main_frame, text="Largura do diálogo (caracteres):", 
                bg=self.secondary_color, fg=self.fg_color).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        dialogue_width_var = tk.IntVar(value=self.settings['dialogue_width'])
        dialogue_width_spinbox = tk.Spinbox(main_frame, from_=20, to=60, textvariable=dialogue_width_var, 
                                           bg=self.bg_color, fg=self.fg_color, width=10)
        dialogue_width_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Largura da ação
        tk.Label(main_frame, text="Largura da ação (caracteres):", 
                bg=self.secondary_color, fg=self.fg_color).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        action_width_var = tk.IntVar(value=self.settings['action_width'])
        action_width_spinbox = tk.Spinbox(main_frame, from_=20, to=80, textvariable=action_width_var, 
                                         bg=self.bg_color, fg=self.fg_color, width=10)
        action_width_spinbox.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Largura da cena
        tk.Label(main_frame, text="Largura da cena (caracteres):", 
                bg=self.secondary_color, fg=self.fg_color).grid(row=5, column=0, sticky=tk.W, pady=5)
        
        scene_width_var = tk.IntVar(value=self.settings['scene_width'])
        scene_width_spinbox = tk.Spinbox(main_frame, from_=20, to=80, textvariable=scene_width_var, 
                                        bg=self.bg_color, fg=self.fg_color, width=10)
        scene_width_spinbox.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        def save_formatting():
            # Salvar configurações
            self.settings['page_width'] = page_width_var.get()
            self.settings['character_width'] = character_width_var.get()
            self.settings['dialogue_width'] = dialogue_width_var.get()
            self.settings['action_width'] = action_width_var.get()
            self.settings['scene_width'] = scene_width_var.get()
            
            format_window.destroy()
            self.update_status("Configurações de formatação salvas")
            
            # Perguntar se deseja reformatar o roteiro
            if messagebox.askyesno("Reformatar", "Deseja reformatar o roteiro com as novas configurações?"):
                self.reformat_script()
        
        save_btn = tk.Button(button_frame, text="Salvar", command=save_formatting,
                            bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=format_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def show_settings(self):
        # Criar janela de configurações
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("400x350")
        settings_window.configure(bg=self.secondary_color)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(settings_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurações
        tk.Label(main_frame, text="Configurações:", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Auto-salvar
        auto_save_var = tk.IntVar(value=1 if self.settings['auto_save'] else 0)
        auto_save_check = tk.Checkbutton(main_frame, text="Auto-salvar", variable=auto_save_var,
                                        bg=self.secondary_color, fg=self.fg_color,
                                        selectcolor=self.bg_color, activebackground=self.secondary_color,
                                        activeforeground=self.fg_color)
        auto_save_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Intervalo de auto-salvamento
        tk.Label(main_frame, text="Intervalo de auto-salvamento (minutos):", 
                bg=self.secondary_color, fg=self.fg_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        interval_var = tk.IntVar(value=self.settings['auto_save_interval'])
        interval_spinbox = tk.Spinbox(main_frame, from_=1, to=60, textvariable=interval_var, 
                                     bg=self.bg_color, fg=self.fg_color, width=10)
        interval_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Tema
        tk.Label(main_frame, text="Tema:", bg=self.secondary_color, fg=self.fg_color).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        theme_frame = tk.Frame(main_frame, bg=self.secondary_color)
        theme_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        theme_var = tk.StringVar(value=self.settings['theme'])
        dark_radio = tk.Radiobutton(theme_frame, text="Escuro", variable=theme_var, value="dark",
                                   bg=self.secondary_color, fg=self.fg_color,
                                   selectcolor=self.bg_color, activebackground=self.secondary_color,
                                   activeforeground=self.fg_color)
        dark_radio.pack(side=tk.LEFT, padx=5)
        
        light_radio = tk.Radiobutton(theme_frame, text="Claro", variable=theme_var, value="light",
                                    bg=self.secondary_color, fg=self.fg_color,
                                    selectcolor=self.bg_color, activebackground=self.secondary_color,
                                    activeforeground=self.fg_color)
        light_radio.pack(side=tk.LEFT, padx=5)
        
        # Fonte
        tk.Label(main_frame, text="Fonte:", bg=self.secondary_color, fg=self.fg_color).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        font_frame = tk.Frame(main_frame, bg=self.secondary_color)
        font_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        font_var = tk.StringVar(value=self.settings['font_family'])
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, values=sorted(font.families()), width=15)
        font_combo.pack(side=tk.LEFT, padx=5)
        
        # Tamanho da fonte
        size_var = tk.IntVar(value=self.settings['font_size'])
        size_spinbox = tk.Spinbox(font_frame, from_=8, to=24, textvariable=size_var, 
                                 bg=self.bg_color, fg=self.fg_color, width=5)
        size_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Números de linha
        line_numbers_var = tk.IntVar(value=1 if self.settings['show_line_numbers'] else 0)
        line_numbers_check = tk.Checkbutton(main_frame, text="Mostrar números de linha", 
                                           variable=line_numbers_var,
                                           bg=self.secondary_color, fg=self.fg_color,
                                           selectcolor=self.bg_color, activebackground=self.secondary_color,
                                           activeforeground=self.fg_color)
        line_numbers_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Quebra de linha
        word_wrap_var = tk.IntVar(value=1 if self.settings['word_wrap'] else 0)
        word_wrap_check = tk.Checkbutton(main_frame, text="Quebra de linha automática", 
                                        variable=word_wrap_var,
                                        bg=self.secondary_color, fg=self.fg_color,
                                        selectcolor=self.bg_color, activebackground=self.secondary_color,
                                        activeforeground=self.fg_color)
        word_wrap_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Destacar linha atual
        line_highlight_var = tk.IntVar(value=1 if self.settings['highlight_current_line'] else 0)
        line_highlight_check = tk.Checkbutton(main_frame, text="Destacar linha atual", 
                                            variable=line_highlight_var,
                                            bg=self.secondary_color, fg=self.fg_color,
                                            selectcolor=self.bg_color, activebackground=self.secondary_color,
                                            activeforeground=self.fg_color)
        line_highlight_check.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        def save_settings():
            # Salvar configurações
            self.settings['auto_save'] = bool(auto_save_var.get())
            self.settings['auto_save_interval'] = interval_var.get()
            self.settings['theme'] = theme_var.get()
            self.settings['font_family'] = font_var.get()
            self.settings['font_size'] = size_var.get()
            self.settings['show_line_numbers'] = bool(line_numbers_var.get())
            self.settings['word_wrap'] = bool(word_wrap_var.get())
            self.settings['highlight_current_line'] = bool(line_highlight_var.get())
            
            # Aplicar configurações
            self.change_theme(self.settings['theme'])
            self.default_font = font.Font(family=self.settings['font_family'], size=self.settings['font_size'])
            self.text_editor.config(font=self.default_font)
            
            # Atualizar tags de formatação
            self.text_editor.tag_configure("bold", font=self.default_font.copy().configure(weight="bold"))
            self.text_editor.tag_configure("italic", font=self.default_font.copy().configure(slant="italic"))
            self.text_editor.tag_configure("underline", font=self.default_font.copy().configure(underline=True))
            self.text_editor.tag_configure("character", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("scene", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("transition", font=self.default_font.copy().configure(weight="bold"), 
                                          foreground=self.highlight_color)
            self.text_editor.tag_configure("note", font=self.default_font.copy().configure(slant="italic"), 
                                          foreground="#cccccc")
            
            # Atualizar quebra de linha
            wrap_mode = tk.WORD if self.settings['word_wrap'] else tk.NONE
            self.text_editor.config(wrap=wrap_mode)
            
            # Atualizar números de linha
            if self.settings['show_line_numbers']:
                if not hasattr(self, 'line_numbers'):
                    # Recrear o editor com números de linha
                    self.text_editor.pack_forget()
                    self.create_text_editor()
                else:
                    self.line_numbers.config(font=self.default_font)
                    self.update_line_numbers()
            else:
                if hasattr(self, 'line_numbers'):
                    # Recrear o editor sem números de linha
                    self.text_editor.pack_forget()
                    self.line_numbers.pack_forget()
                    self.create_text_editor()
            
            # Atualizar destaque de linha atual
            if self.settings['highlight_current_line']:
                self.highlight_current_line()
            else:
                self.text_editor.tag_remove("current_line", "1.0", tk.END)
            
            settings_window.destroy()
            self.update_status("Configurações salvas")
        
        save_btn = tk.Button(button_frame, text="Salvar", command=save_settings,
                            bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=settings_window.destroy,
                              bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def show_shortcuts(self):
        # Criar janela de atalhos
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Atalhos de Teclado")
        shortcuts_window.geometry("500x600")
        shortcuts_window.configure(bg=self.secondary_color)
        shortcuts_window.transient(self.root)
        
        # Frame principal
        main_frame = tk.Frame(shortcuts_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(main_frame, text="Atalhos de Teclado", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).pack(anchor=tk.W, pady=10)
        
        # Frame para atalhos
        shortcuts_frame = tk.Frame(main_frame, bg=self.secondary_color)
        shortcuts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(shortcuts_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Texto com atalhos
        shortcuts_text = tk.Text(shortcuts_frame, bg=self.bg_color, fg=self.fg_color, 
                                wrap=tk.WORD, yscrollcommand=scrollbar.set, bd=0, padx=10, pady=10)
        shortcuts_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=shortcuts_text.yview)
        
        # Conteúdo
        shortcuts_content = """
Arquivo:
Ctrl+N - Novo Roteiro
Ctrl+O - Abrir Roteiro
Ctrl+S - Salvar Roteiro
Ctrl+Shift+S - Salvar Como
Ctrl+Alt+S - Salvar Seguro
Ctrl+E - Exportar PDF
Ctrl+Q - Sair

Editar:
Ctrl+Z - Desfazer
Ctrl+Y - Refazer
Ctrl+X - Recortar
Ctrl+C - Copiar
Ctrl+V - Colar
Ctrl+F - Buscar
Ctrl+R - Substituir
Ctrl+G - Ir Para Linha
Ctrl+A - Selecionar Tudo

Formato:
Ctrl+B - Negrito
Ctrl+I - Itálico
Ctrl+U - Sublinhado
Ctrl+P - Inserir Personagem
Ctrl+D - Inserir Diálogo
Ctrl+Shift+A - Inserir Ação
Ctrl+Shift+C - Inserir Cena
Ctrl+T - Inserir Transição
Ctrl+Shift+N - Inserir Nota

Visualizar:
Ctrl++ - Zoom In
Ctrl+- - Zoom Out
Ctrl+0 - Zoom Normal

Navegação:
F3 - Próxima ocorrência
Shift+F3 - Ocorrência anterior
        """
        
        shortcuts_text.insert(tk.END, shortcuts_content)
        shortcuts_text.config(state=tk.DISABLED)
        
        # Botão Fechar
        close_btn = tk.Button(main_frame, text="Fechar", command=shortcuts_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(pady=10)
    
    def show_tutorial(self):
        # Criar janela de tutorial
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("Tutorial")
        tutorial_window.geometry("700x500")
        tutorial_window.configure(bg=self.secondary_color)
        tutorial_window.transient(self.root)
        
        # Frame principal
        main_frame = tk.Frame(tutorial_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(main_frame, text="Tutorial do Roteirista Pro", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).pack(anchor=tk.W, pady=10)
        
        # Notebook para abas do tutorial
        tutorial_notebook = ttk.Notebook(main_frame)
        tutorial_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Introdução
        intro_frame = tk.Frame(tutorial_notebook, bg=self.secondary_color)
        tutorial_notebook.add(intro_frame, text="Introdução")
        
        intro_text = tk.Text(intro_frame, bg=self.bg_color, fg=self.fg_color, 
                            wrap=tk.WORD, bd=0, padx=10, pady=10)
        intro_text.pack(fill=tk.BOTH, expand=True)
        
        intro_content = """
Bem-vindo ao Roteirista Pro!

Este é um aplicativo projetado para ajudar roteiristas a criar e formatar roteiros de filmes, séries e vídeos de forma profissional.

Com o Roteirista Pro, você pode:

• Escrever e formatar roteiros no padrão da indústria
• Gerenciar personagens e cenas
• Exportar para PDF e outros formatos
• Usar atalhos de teclado para aumentar sua produtividade
• Personalizar a aparência do aplicativo
• Salvar roteiros com segurança usando senha
• Analisar seu roteiro para obter sugestões de melhoria

Navegue pelas abas deste tutorial para aprender mais sobre cada recurso do aplicativo.
        """
        
        intro_text.insert(tk.END, intro_content)
        intro_text.config(state=tk.DISABLED)
        
        # Aba 2: Interface
        interface_frame = tk.Frame(tutorial_notebook, bg=self.secondary_color)
        tutorial_notebook.add(interface_frame, text="Interface")
        
        interface_text = tk.Text(interface_frame, bg=self.bg_color, fg=self.fg_color, 
                                wrap=tk.WORD, bd=0, padx=10, pady=10)
        interface_text.pack(fill=tk.BOTH, expand=True)
        
        interface_content = """
Interface do Roteirista Pro

A interface do aplicativo é composta por:

1. Barras de Ferramentas: Localizadas na parte superior, contêm botões para as funções mais comuns, organizadas em três categorias:
   - Barra principal: funções de arquivo, edição e exportação
   - Barra de formatação: opções de formatação de texto
   - Barra de elementos: inserção de elementos de roteiro

2. Menu: Abaixo das barras de ferramentas, oferece acesso a todas as funções do aplicativo.

3. Barra Lateral: No lado esquerdo, contém abas para organizar melhor as ferramentas:
   - Elementos: inserção de elementos de roteiro
   - Formatação: opções de formatação de texto
   - Personagens: gerenciamento de personagens
   - Cenas: gerenciamento de cenas
   - Notas: anotações sobre o roteiro
   - Ferramentas: ferramentas de análise e formatação

4. Editor de Texto: Área principal onde você escreve seu roteiro, com destaque da linha atual e cursor visível.

5. Barra de Status: Na parte inferior, exibe informações sobre o documento, posição do cursor, formato do elemento atual e indicador de salvamento.

Você pode ocultar ou mostrar cada uma das barras de ferramentas e a barra lateral através do menu Visualizar.
        """
        
        interface_text.insert(tk.END, interface_content)
        interface_text.config(state=tk.DISABLED)
        
        # Aba 3: Formatação
        format_frame = tk.Frame(tutorial_notebook, bg=self.secondary_color)
        tutorial_notebook.add(format_frame, text="Formatação")
        
        format_text = tk.Text(format_frame, bg=self.bg_color, fg=self.fg_color, 
                             wrap=tk.WORD, bd=0, padx=10, pady=10)
        format_text.pack(fill=tk.BOTH, expand=True)
        
        format_content = """
Formatação de Roteiros

O Roteirista Pro facilita a formatação de roteiros no padrão da indústria. Os principais elementos são:

• Cena: Local e horário da cena (ex: "CENA: CASA DE JOÃO - DIA"). Deve estar em maiúsculas.

• Personagem: Nome do personagem em maiúsculas e centralizado.

• Diálogo: Texto falado pelo personagem, com recuo à esquerda.

• Ação: Descrição de ações, cenas e personagens, com recuo menor que o diálogo.

• Transição: Indicações de transição entre cenas (ex: "TRANSIÇÃO: CORTE PARA:"). Alinhado à direita.

• Nota: Comentários ou anotações sobre o roteiro.

Você pode inserir esses elementos usando os botões na barra lateral, no menu Formato ou com atalhos de teclado.

Para formatar texto como negrito, itálico ou sublinhado, selecione o texto e use os botões na barra lateral, no menu Editar ou com atalhos de teclado.

O Roteirista Pro também oferece uma função de reformatar automaticamente todo o roteiro para garantir que ele siga o padrão da indústria.
        """
        
        format_text.insert(tk.END, format_content)
        format_text.config(state=tk.DISABLED)
        
        # Aba 4: Segurança
        security_frame = tk.Frame(tutorial_notebook, bg=self.secondary_color)
        tutorial_notebook.add(security_frame, text="Segurança")
        
        security_text = tk.Text(security_frame, bg=self.bg_color, fg=self.fg_color, 
                              wrap=tk.WORD, bd=0, padx=10, pady=10)
        security_text.pack(fill=tk.BOTH, expand=True)
        
        security_content = """
Segurança de Roteiros

O Roteirista Pro oferece recursos para proteger seus roteiros:

Salvamento Seguro:

Você pode salvar seus roteiros com proteção por senha usando a função "Salvar Seguro". Isso criptografa o conteúdo do arquivo, tornando-o inacessível sem a senha correta.

Para salvar um roteiro seguro:
1. Clique em "Salvar Seguro" no menu Arquivo ou na barra lateral
2. Digite uma senha
3. Confirme a senha
4. Escolha onde salvar o arquivo

Para abrir um roteiro seguro:
1. Clique em "Abrir" no menu Arquivo
2. Selecione o arquivo seguro (.sec)
3. Digite a senha correta

Auto-salvamento:

O aplicativo pode salvar automaticamente seu trabalho em intervalos regulares, evitando perda de dados em caso de problemas.

Para configurar o auto-salvamento:
1. Clique em "Configurações" no menu Ferramentas
2. Marque a opção "Auto-salvar"
3. Defina o intervalo de salvamento

Lembre-se de escolher uma senha forte e não compartilhá-la com pessoas não autorizadas.
        """
        
        security_text.insert(tk.END, security_content)
        security_text.config(state=tk.DISABLED)
        
        # Aba 5: Análise
        analysis_frame = tk.Frame(tutorial_notebook, bg=self.secondary_color)
        tutorial_notebook.add(analysis_frame, text="Análise")
        
        analysis_text = tk.Text(analysis_frame, bg=self.bg_color, fg=self.fg_color, 
                               wrap=tk.WORD, bd=0, padx=10, pady=10)
        analysis_text.pack(fill=tk.BOTH, expand=True)
        
        analysis_content = """
Análise de Roteiros

O Roteirista Pro oferece ferramentas para analisar seu roteiro e obter sugestões de melhoria:

Análise Completa:

A função "Analisar Roteiro" examina seu roteiro e fornece:
• Contagem de cenas, personagens, diálogos, etc.
• Identificação de possíveis problemas (poucas cenas, poucos personagens, etc.)
• Sugestões para melhorar o roteiro
• Lista de personagens e suas estatísticas

Tempo de Leitura:

Calcula o tempo estimado para ler o roteiro, baseado em 200 palavras por minuto.

Estatísticas:

Fornece estatísticas detalhadas sobre o roteiro, incluindo:
• Número de palavras e caracteres
• Número de linhas e páginas estimadas
• Contagem de cada tipo de elemento de roteiro
• Informações sobre personagens e cenas

Verificação Ortográfica:

Verifica o texto em busca de possíveis erros de ortografia e permite que você corrija-os facilmente.

Para usar essas ferramentas, acesse o menu Ferramentas ou a aba "Ferramentas" na barra lateral.
        """
        
        analysis_text.insert(tk.END, analysis_content)
        analysis_text.config(state=tk.DISABLED)
        
        # Aba 6: Exportação
        export_frame = tk.Frame(tutorial_notebook, bg=self.secondary_color)
        tutorial_notebook.add(export_frame, text="Exportação")
        
        export_text = tk.Text(export_frame, bg=self.bg_color, fg=self.fg_color, 
                             wrap=tk.WORD, bd=0, padx=10, pady=10)
        export_text.pack(fill=tk.BOTH, expand=True)
        
        export_content = """
Exportação de Roteiros

O Roteirista Pro oferece várias opções de exportação:

PDF:

Para exportar seu roteiro como PDF:
1. Salve seu roteiro (Ctrl+S)
2. Clique em "Exportar PDF" no menu Arquivo ou na barra de ferramentas
3. Escolha o local para salvar o arquivo PDF

HTML:

Para exportar seu roteiro como HTML:
1. Salve seu roteiro (Ctrl+S)
2. Clique em "Exportar HTML" no menu Arquivo
3. Escolha o local para salvar o arquivo HTML

Fountain:

Para exportar seu roteiro como Fountain:
1. Salve seu roteiro (Ctrl+S)
2. Clique em "Exportar Fountain" no menu Arquivo
3. Escolha o local para salvar o arquivo Fountain

O formato Fountain é um formato de texto simples para roteiros que pode ser lido por humanos e processado por software.

Impressão:

Para imprimir seu roteiro:
1. Salve seu roteiro (Ctrl+S)
2. Clique em "Imprimir" no menu Arquivo ou pressione Ctrl+P
3. Seu roteiro será aberto no navegador padrão para impressão

Importação:

Você também pode importar roteiros de outros formatos:
• FDX (Final Draft)
• PDF
• DOCX (Word)
• Fountain

Clique em "Importar" no menu Arquivo para selecionar um arquivo para importar.
        """
        
        export_text.insert(tk.END, export_content)
        export_text.config(state=tk.DISABLED)
        
        # Botão Fechar
        close_btn = tk.Button(main_frame, text="Fechar", command=tutorial_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(pady=10)
    
    def show_formatting_guide(self):
        # Criar janela de guia de formatação
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Guia de Formatação")
        guide_window.geometry("700x500")
        guide_window.configure(bg=self.secondary_color)
        guide_window.transient(self.root)
        
        # Frame principal
        main_frame = tk.Frame(guide_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(main_frame, text="Guia de Formatação de Roteiros", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).pack(anchor=tk.W, pady=10)
        
        # Notebook para abas do guia
        guide_notebook = ttk.Notebook(main_frame)
        guide_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Padrão da Indústria
        standard_frame = tk.Frame(guide_notebook, bg=self.secondary_color)
        guide_notebook.add(standard_frame, text="Padrão da Indústria")
        
        standard_text = tk.Text(standard_frame, bg=self.bg_color, fg=self.fg_color, 
                               wrap=tk.WORD, bd=0, padx=10, pady=10)
        standard_text.pack(fill=tk.BOTH, expand=True)
        
        standard_content = """
Padrão de Formatação da Indústria

O padrão de formatação de roteiros segue convenções estabelecidas pela indústria cinematográfica. Aqui estão as principais regras:

Cenas:

As cenas devem ser formatadas da seguinte maneira:

CENA: LOCAL - DIA/NOITE

• A palavra "CENA:" deve estar em maiúsculas
• O local deve ser descrito de forma clara e concisa
• O horário deve ser "DIA" ou "NOITE" (ou variações como "MANHÃ", "TARDE", "NOITE", "MADRUGADA", etc.)
• Cenas devem ser escritas em maiúsculas
• Cenas devem ser alinhadas à esquerda

Personagens:

Os nomes dos personagens devem ser formatados da seguinte maneira:

                                     NOME DO PERSONAGEM

• Nomes de personagens devem estar em maiúsculas
• Nomes de personagens devem ser centralizados na página
• Nomes de personagens não devem ultrapassar 40 caracteres

Diálogos:

Os diálogos devem ser formatados da seguinte maneira:

               Diálogo do personagem aqui...

• Diálogos devem ter um recuo de aproximadamente 15 espaços
• Diálogos não devem ultrapassar 35 caracteres por linha
• Diálogos devem seguir imediatamente após o nome do personagem

Ações:

As ações devem ser formatadas da seguinte maneira:

          Ação ou descrição da cena aqui...

• Ações devem ter um recuo de aproximadamente 10 espaços
• Ações devem ser escritas em letra minúscula, exceto nomes próprios
• Ações devem descrever visualmente o que acontece na cena

Transições:

As transições devem ser formatadas da seguinte maneira:

                                    TRANSIÇÃO: CORTE PARA:

• Transições devem ser alinhadas à direita
• Transições devem estar em maiúsculas
• Transições comuns incluem "CORTE PARA:", "DISSOLVÊNCIA PARA:", "FADE OUT:", etc.

Notas:

As notas devem ser formatadas da seguinte maneira:

NOTA: Esta é uma nota sobre o roteiro.

• Notas devem começar com "NOTA:"
• Notas devem ser usadas para comentários ou anotações
• Notas não devem fazer parte do roteiro final
        """
        
        standard_text.insert(tk.END, standard_content)
        standard_text.config(state=tk.DISABLED)
        
        # Aba 2: Exemplos
        examples_frame = tk.Frame(guide_notebook, bg=self.secondary_color)
        guide_notebook.add(examples_frame, text="Exemplos")
        
        examples_text = tk.Text(examples_frame, bg=self.bg_color, fg=self.fg_color, 
                               wrap=tk.WORD, bd=0, padx=10, pady=10)
        examples_text.pack(fill=tk.BOTH, expand=True)
        
        examples_content = """
Exemplos de Formatação

Aqui estão alguns exemplos de como formatar diferentes elementos de um roteiro:

Exemplo de Cena:

CENA: CASA DE JOÃO - SALA DE ESTAR - NOITE

A sala está iluminada apenas pela luz da TV. JOÃO (30) está sentado no sofá, assistindo a um filme.

                                     JOÃO
               (para si mesmo)
               Eu deveria ter ido para a cama mais cedo.

João se levanta e caminha até a janela. Ele olha para fora.

                                     JOÃO
               (suspirando)
               Mais uma noite sem dormir.

Exemplo de Diálogo:

                                     MARIA
               Você não vai dormir nunca?

                                     JOÃO
               (virando-se)
               Maria! Eu não te ouvi entrar.

                                     MARIA
               Claro, você estava muito concentrado
               na TV.

                                     JOÃO
               É que... eu não consigo dormir
               ultimamente.

Exemplo de Ação:

Maria se aproxima de João e coloca a mão no seu ombro.

                                     MARIA
               (com voz suave)
               Eu sei. Mas você precisa tentar.

João olha para Maria e sorri fracamente.

                                     JOÃO
               Você sempre sabe o que dizer.

Exemplo de Transição:

CENA: QUARTO DE JOÃO - NOITE

João está deitado na cama, olhando para o teto. Maria está ao seu lado.

                                     MARIA
               Agora tente dormir. Eu fico aqui
               com você.

                                     JOÃO
               (fechando os olhos)
               Obrigado, Maria.

Maria beija a testa de João.

                                    TRANSIÇÃO: FADE OUT.

Exemplo de Nota:

NOTA: Esta cena precisa de mais diálogo para desenvolver melhor a relação entre os personagens.
        """
        
        examples_text.insert(tk.END, examples_content)
        examples_text.config(state=tk.DISABLED)
        
        # Aba 3: Dicas
        tips_frame = tk.Frame(guide_notebook, bg=self.secondary_color)
        guide_notebook.add(tips_frame, text="Dicas")
        
        tips_text = tk.Text(tips_frame, bg=self.bg_color, fg=self.fg_color, 
                           wrap=tk.WORD, bd=0, padx=10, pady=10)
        tips_text.pack(fill=tk.BOTH, expand=True)
        
        tips_content = """
Dicas de Formatação

Aqui estão algumas dicas para formatar seu roteiro de forma profissional:

Consistência:

Mantenha a formatação consistente em todo o roteiro. Isso torna mais fácil para os leitores (diretores, produtores, atores) entenderem seu trabalho.

Clareza:

Seja claro e conciso em suas descrições. Evite jargões desnecessários e descreva apenas o que pode ser visto ou ouvido.

Diálogos:

Mantenha os diálogos naturais e realistas. Evite monólogos longos, a menos que sejam essenciais para a história.

Personagens:

Apresente seus personagens de forma clara. Na primeira aparição, inclua uma breve descrição entre parênteses.

                                     JOÃO (30)
               (vestido com roupas informais)
               Um homem cansado, com olheiras profundas.

Ações:

Descreva as ações de forma visual. Em vez de "João está triste", escreva "João chora silenciosamente" ou "João se senta e esconde o rosto nas mãos".

Cenas:

Mantenha as cenas breves e dinâmicas. Cenas muito longas podem tornar o roteiro cansativo de ler.

Transições:

Use transições com moderação. Na maioria dos casos, "CORTE PARA:" é suficiente. Transições mais elaboradas como "DISSOLVÊNCIA PARA:" devem ser usadas apenas quando necessárias.

Notas:

Use notas com moderação. Elas são úteis para lembrar-se de algo, mas não devem fazer parte do roteiro final.

Revisão:

Revise seu roteiro várias vezes. Verifique a formatação, a gramática e a ortografia. Peça para outras pessoas lerem e darem opiniões.

Software:

Use um software de formatação de roteiros como o Roteirista Pro para garantir que seu roteiro siga o padrão da indústria.

Lembre-se: um roteiro bem formatado é mais fácil de ler e profissional. Isso pode fazer a diferença entre seu roteiro ser lido ou ignorado.
        """
        
        tips_text.insert(tk.END, tips_content)
        tips_text.config(state=tk.DISABLED)
        
        # Botão Fechar
        close_btn = tk.Button(main_frame, text="Fechar", command=guide_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(pady=10)
    
    def show_about(self):
        # Criar janela Sobre
        about_window = tk.Toplevel(self.root)
        about_window.title("Sobre")
        about_window.geometry("400x300")
        about_window.configure(bg=self.secondary_color)
        about_window.transient(self.root)
        
        # Frame principal
        main_frame = tk.Frame(about_window, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(main_frame, text="Roteirista Pro v2.0", bg=self.secondary_color, fg=self.fg_color, 
                font=self.title_font).pack(anchor=tk.W, pady=10)
        
        # Conteúdo
        about_text = tk.Text(main_frame, bg=self.bg_color, fg=self.fg_color, 
                            wrap=tk.WORD, bd=0, padx=10, pady=10, height=10)
        about_text.pack(fill=tk.BOTH, expand=True)
        
        about_content = """
Roteirista Pro é um aplicativo para escrita de roteiros de filmes, séries e vídeos.

Desenvolvido com Python e Tkinter, este aplicativo oferece uma interface intuitiva e recursos poderosos para roteiristas profissionais e amadores.

Recursos principais:
• Formatação profissional de roteiros
• Gerenciamento de personagens e cenas
• Exportação para PDF, HTML e Fountain
• Interface personalizável
• Atalhos de teclado para aumentar a produtividade
• Salvamento seguro com senha
• Análise de roteiros com sugestões de melhoria

© 2025 - Todos os direitos reservados.
        """
        
        about_text.insert(tk.END, about_content)
        about_text.config(state=tk.DISABLED)
        
        # Botão Fechar
        close_btn = tk.Button(main_frame, text="Fechar", command=about_window.destroy,
                             bg=self.blue_color, fg=self.fg_color, bd=0, padx=10)
        close_btn.pack(pady=10)
    
    def exit_app(self):
        if self.text_editor.edit_modified():
            response = messagebox.askyesnocancel("Salvar alterações", 
                                                 "Deseja salvar as alterações antes de sair?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        self.save_settings()
        self.root.destroy()
    
    def auto_save(self):
        if self.settings['auto_save'] and self.current_file and self.text_editor.edit_modified():
            self.save_file()
        
        # Agendar próximo auto-salvamento
        self.root.after(self.settings['auto_save_interval'] * 60000, self.auto_save)
    
    def load_settings(self):
        settings_path = os.path.join(os.path.expanduser('~'), '.roteirista_pro_settings.json')
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    self.settings.update(json.load(f))
            except:
                pass
    
    def save_settings(self):
        settings_path = os.path.join(os.path.expanduser('~'), '.roteirista_pro_settings.json')
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f)
        except:
            pass
    
    def save_metadata(self):
        if not self.current_file:
            return
            
        # Salvar metadados (personagens, cenas e notas) em um arquivo separado
        metadata_path = os.path.splitext(self.current_file)[0] + '.meta'
        
        metadata = {
            'characters': self.characters,
            'scenes': self.scenes,
            'notes': self.notes_editor.get(1.0, tk.END).strip()
        }
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f)
        except:
            pass
    
    def load_metadata(self):
        if not self.current_file:
            return
            
        # Carregar metadados (personagens, cenas e notas) de um arquivo separado
        metadata_path = os.path.splitext(self.current_file)[0] + '.meta'
        
        if not os.path.exists(metadata_path):
            return
            
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # Carregar personagens
            self.characters = metadata.get('characters', [])
            self.characters_listbox.delete(0, tk.END)
            for char in self.characters:
                self.characters_listbox.insert(tk.END, char['name'])
                
            # Carregar cenas
            self.scenes = metadata.get('scenes', [])
            self.scenes_listbox.delete(0, tk.END)
            for scene in self.scenes:
                self.scenes_listbox.insert(tk.END, scene['title'])
                
            # Carregar notas
            notes = metadata.get('notes', '')
            self.notes_editor.delete(1.0, tk.END)
            self.notes_editor.insert(1.0, notes)
        except:
            pass
    
    def import_fdx(self, file_path):
        # Importar do formato Final Draft (FDX)
        # Esta é uma implementação simplificada
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Limpar o editor
            self.text_editor.delete(1.0, tk.END)
            
            # Extrair conteúdo
            for paragraph in root.findall('.//Paragraph'):
                element_type = paragraph.get('Type')
                text = paragraph.text or ''
                
                if element_type == 'Scene Heading':
                    self.text_editor.insert(tk.END, f"\n\n{text}\n")
                    self.text_editor.tag_add("scene", "insert-2l linestart", "insert-2l lineend")
                elif element_type == 'Character':
                    self.text_editor.insert(tk.END, f"\n\n{text}\n")
                    self.text_editor.tag_add("character", "insert-2l linestart", "insert-2l lineend")
                elif element_type == 'Dialogue':
                    self.text_editor.insert(tk.END, f"{text}\n")
                elif element_type == 'Action':
                    self.text_editor.insert(tk.END, f"\n\n{text}\n")
                elif element_type == 'Transition':
                    self.text_editor.insert(tk.END, f"\n\n{text}\n")
                    self.text_editor.tag_add("transition", "insert-2l linestart", "insert-2l lineend")
                else:
                    self.text_editor.insert(tk.END, f"{text}\n")
            
            self.update_status(f"Arquivo FDX importado: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Erro ao importar", f"Não foi possível importar o arquivo FDX: {str(e)}")
    
    def import_pdf(self, file_path):
        # Importar do formato PDF
        # Esta é uma implementação simplificada que requer a biblioteca PyPDF2
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                
                # Limpar o editor
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, text)
                
                self.update_status(f"Arquivo PDF importado: {os.path.basename(file_path)}")
        except ImportError:
            messagebox.showerror("Erro ao importar", "Para importar arquivos PDF, é necessário instalar a biblioteca PyPDF2.")
        except Exception as e:
            messagebox.showerror("Erro ao importar", f"Não foi possível importar o arquivo PDF: {str(e)}")
    
    def import_docx(self, file_path):
        # Importar do formato DOCX (Word)
        # Esta é uma implementação simplificada que requer a biblioteca python-docx
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n\n"
            
            # Limpar o editor
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, text)
            
            self.update_status(f"Arquivo DOCX importado: {os.path.basename(file_path)}")
        except ImportError:
            messagebox.showerror("Erro ao importar", "Para importar arquivos DOCX, é necessário instalar a biblioteca python-docx.")
        except Exception as e:
            messagebox.showerror("Erro ao importar", f"Não foi possível importar o arquivo DOCX: {str(e)}")

def create_desktop_shortcut():
    """Cria um atalho na área de trabalho para o aplicativo"""
    try:
        import win32com.client
        
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        path = os.path.join(desktop, "Roteirista Pro.lnk")
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = os.path.abspath(__file__)
        shortcut.IconLocation = sys.executable + ",0"
        shortcut.save()
        
        messagebox.showinfo("Atalho Criado", "Um atalho foi criado na área de trabalho!")
    except:
        messagebox.showwarning("Atalho Não Criado", 
                             "Não foi possível criar o atalho automaticamente. "
                             "Você pode criar um manualmente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptWriterApp(root)
    
    # Verificar se foi passado o argumento para criar atalho
    if len(sys.argv) > 1 and sys.argv[1] == "--create-shortcut":
        create_desktop_shortcut()
    
    root.mainloop()