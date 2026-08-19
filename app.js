/**
 * ROTEIRISTA PRO v4.0 - Ultimate Edition
 * Optimized JavaScript Application
 * Performance-focused with minimal memory footprint
 */

(function() {
    'use strict';

    // ============================================
    // CORE APPLICATION CLASS
    // ============================================
    class RoteiristaPro {
        constructor() {
            // State management with minimal re-renders
            this.state = {
                content: '',
                fileName: 'Sem Título.fountain',
                isModified: false,
                theme: 'light',
                zoom: 100,
                fontSize: 12,
                autoSaveInterval: 5,
                showLineNumbers: true,
                autoComplete: true,
                characters: [],
                scenes: [],
                locations: [],
                notes: [],
                history: [],
                historyIndex: -1,
                searchMatches: [],
                currentSearchIndex: -1
            };

            // DOM cache for performance
            this.dom = {};
            this.init();
        }

        // ============================================
        // INITIALIZATION
        // ============================================
        init() {
            this.cacheDOM();
            this.loadFromStorage();
            this.bindEvents();
            this.applyTheme();
            this.updateZoom();
            this.startAutoSave();
            this.renderAll();
            this.updateStats();
            
            // Sample content for first-time users
            if (!this.state.content) {
                this.setSampleContent();
            }
            
            this.showToast('Bem-vindo ao Roteirista Pro v4.0!', 'success');
        }

        // Cache DOM elements for performance
        cacheDOM() {
            this.dom = {
                editor: document.getElementById('editor'),
                lineNumbers: document.getElementById('lineNumbers'),
                fileName: document.getElementById('fileName'),
                saveStatus: document.getElementById('saveStatus'),
                zoomLevel: document.getElementById('zoomLevel'),
                cursorPosition: document.getElementById('cursorPosition'),
                currentFormat: document.getElementById('currentFormat'),
                pageCount: document.getElementById('pageCount'),
                wordCount: document.getElementById('wordCount'),
                charCount: document.getElementById('charCount'),
                sceneCount: document.getElementById('sceneCount'),
                timeEstimate: document.getElementById('timeEstimate'),
                scenesList: document.getElementById('scenesList'),
                charactersList: document.getElementById('charactersList'),
                locationsList: document.getElementById('locationsList'),
                notesList: document.getElementById('notesList'),
                structureViz: document.getElementById('structureViz'),
                searchBar: document.getElementById('searchBar'),
                searchInput: document.getElementById('searchInput'),
                replaceInput: document.getElementById('replaceInput'),
                leftSidebar: document.getElementById('leftSidebar'),
                rightSidebar: document.getElementById('rightSidebar'),
                themeToggle: document.getElementById('themeToggle'),
                contextMenu: document.getElementById('contextMenu')
            };
        }

        // ============================================
        // EVENT BINDING
        // ============================================
        bindEvents() {
            // Editor events with debounce for performance
            this.dom.editor.addEventListener('input', () => this.debounce(this.handleInput, 50)());
            this.dom.editor.addEventListener('scroll', () => this.syncScroll());
            this.dom.editor.addEventListener('click', () => this.updateCursorPosition());
            this.dom.editor.addEventListener('keyup', () => this.updateCursorPosition());
            this.dom.editor.addEventListener('keydown', (e) => this.handleKeydown(e));
            this.dom.editor.addEventListener('contextmenu', (e) => this.showContextMenu(e));

            // Toolbar actions
            document.querySelectorAll('[data-action]').forEach(btn => {
                btn.addEventListener('click', (e) => this.handleAction(e));
            });

            // Dropdown menus
            document.querySelectorAll('[data-dropdown]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleDropdown(btn.dataset.dropdown);
                });
            });

            // Panel toggles
            document.querySelectorAll('[data-panel]').forEach(header => {
                header.addEventListener('click', () => this.togglePanel(header.dataset.panel));
            });

            // Sidebar toggles
            document.querySelectorAll('.sidebar-toggle').forEach(btn => {
                btn.addEventListener('click', () => this.toggleSidebar(btn.dataset.target));
            });

            // Modal controls
            document.querySelectorAll('[data-modal]').forEach(btn => {
                btn.addEventListener('click', () => this.closeModal(btn.dataset.modal));
            });

            // Theme toggle
            this.dom.themeToggle.addEventListener('click', () => this.toggleTheme());

            // Color picker
            document.querySelectorAll('.color-option').forEach(opt => {
                opt.addEventListener('click', () => this.selectColor(opt.dataset.color));
            });

            // Search events
            this.dom.searchInput.addEventListener('input', () => this.performSearch());
            this.dom.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') e.shiftKey ? this.findPrevious() : this.findNext();
            });

            // Close dropdowns and context menu on click outside
            document.addEventListener('click', () => {
                this.closeAllDropdowns();
                this.hideContextMenu();
            });

            // Fullscreen
            document.getElementById('fullscreenBtn')?.addEventListener('click', () => this.toggleFullscreen());

            // Window events
            window.addEventListener('beforeunload', (e) => this.handleBeforeUnload(e));
            window.addEventListener('resize', () => this.debounce(() => this.updateLineNumbers(), 100)());
        }

        // ============================================
        // CORE EDITOR FUNCTIONS
        // ============================================
        handleInput() {
            const content = this.dom.editor.value;
            this.state.content = content;
            this.state.isModified = true;
            
            this.updateLineNumbers();
            this.parseContent();
            this.renderAll();
            this.updateStats();
            this.updateSaveStatus('modificado');
        }

        handleKeydown(e) {
            // Keyboard shortcuts
            const shortcuts = {
                'ctrl+n': () => this.fileNew(),
                'ctrl+s': () => { e.preventDefault(); this.fileSave(); },
                'ctrl+o': () => { e.preventDefault(); this.fileOpen(); },
                'ctrl+z': () => { e.preventDefault(); this.undo(); },
                'ctrl+y': () => { e.preventDefault(); this.redo(); },
                'ctrl+f': () => { e.preventDefault(); this.toggleSearch(); },
                'ctrl+h': () => { e.preventDefault(); this.toggleSearch(); },
                'ctrl+e': () => { e.preventDefault(); this.exportPDF(); },
                'ctrl+p': () => { e.preventDefault(); this.formatAs('character'); },
                'ctrl+d': () => { e.preventDefault(); this.formatAs('dialogue'); },
                'ctrl+t': () => { e.preventDefault(); this.formatAs('transition'); },
                'f11': () => { e.preventDefault(); this.toggleFullscreen(); },
                'escape': () => this.closeAllModals()
            };

            const key = `${e.ctrlKey ? 'ctrl+' : ''}${e.shiftKey ? 'shift+' : ''}${e.key.toLowerCase()}`;
            
            if (shortcuts[key]) {
                shortcuts[key]();
            }

            // Format-specific shortcuts
            if (e.ctrlKey && e.shiftKey) {
                if (e.key === 'C') { e.preventDefault(); this.formatAs('scene'); }
                if (e.key === 'A') { e.preventDefault(); this.formatAs('action'); }
                if (e.key === 'P') { e.preventDefault(); this.formatAs('parenthetical'); }
            }
        }

        formatAs(format) {
            const editor = this.dom.editor;
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            const text = editor.value;
            const selectedText = text.substring(start, end);
            
            let formatted = '';
            switch(format) {
                case 'scene':
                    formatted = (selectedText || 'INT. LOCAL - DIA').toUpperCase();
                    break;
                case 'character':
                    formatted = (selectedText || 'PERSONAGEM').toUpperCase();
                    break;
                case 'dialogue':
                    formatted = selectedText || 'Diálogo do personagem...';
                    break;
                case 'action':
                    formatted = selectedText || 'Descrição da ação...';
                    break;
                case 'transition':
                    formatted = (selectedText || 'CORTE PARA:').toUpperCase();
                    break;
                case 'parenthetical':
                    formatted = selectedText ? `(${selectedText})` : '(entre parênteses)';
                    break;
            }

            this.insertAtCursor(formatted);
            this.handleInput();
        }

        insertAtCursor(text) {
            const editor = this.dom.editor;
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            const content = editor.value;
            
            editor.value = content.substring(0, start) + text + content.substring(end);
            editor.selectionStart = editor.selectionEnd = start + text.length;
            editor.focus();
        }

        updateLineNumbers() {
            if (!this.state.showLineNumbers) {
                this.dom.lineNumbers.innerHTML = '';
                return;
            }

            const lines = this.dom.editor.value.split('\n').length;
            let html = '';
            for (let i = 1; i <= lines; i++) {
                html += `<div>${i}</div>`;
            }
            this.dom.lineNumbers.innerHTML = html;
        }

        syncScroll() {
            this.dom.lineNumbers.scrollTop = this.dom.editor.scrollTop;
        }

        updateCursorPosition() {
            const editor = this.dom.editor;
            const text = editor.value.substring(0, editor.selectionStart);
            const lines = text.split('\n');
            const line = lines.length;
            const col = lines[lines.length - 1].length + 1;
            
            this.dom.cursorPosition.textContent = `Ln ${line}, Col ${col}`;
            this.detectCurrentFormat(line, lines);
        }

        detectCurrentFormat(lineNum, lines) {
            const prevLine = lines[lineNum - 2] || '';
            const currentLine = lines[lineNum - 1] || '';
            
            let format = 'Ação';
            
            if (/^(INT\.|EXT\.|I\/E\.)/i.test(currentLine)) {
                format = 'Cena';
            } else if (/^[A-Z\s]+$/.test(currentLine.trim()) && currentLine.trim().length > 2) {
                format = 'Personagem';
            } else if (/^\s*\(/.test(currentLine)) {
                format = 'Parenthetical';
            } else if (/^(CORTE PARA|DISSOLVE|FADE IN|FADE OUT)/i.test(currentLine)) {
                format = 'Transição';
            } else if (prevLine && /^[A-Z\s]+$/.test(prevLine.trim())) {
                format = 'Diálogo';
            }

            this.dom.currentFormat.textContent = `Formato: ${format}`;
        }

        // ============================================
        // CONTENT PARSING & ANALYSIS
        // ============================================
        parseContent() {
            const content = this.state.content;
            const lines = content.split('\n');
            
            this.state.scenes = [];
            this.state.characters = new Set();
            this.state.locations = new Set();

            lines.forEach((line, index) => {
                const trimmed = line.trim();
                
                // Detect scenes
                if (/^(INT\.|EXT\.|I\/E\.)\s+/i.test(trimmed)) {
                    this.state.scenes.push({
                        number: this.state.scenes.length + 1,
                        text: trimmed,
                        line: index + 1
                    });
                    
                    // Extract location
                    const locationMatch = trimmed.match(/^(?:INT\.|EXT\.|I\/E\.)\s+([^-]+)/i);
                    if (locationMatch) {
                        this.state.locations.add(locationMatch[1].trim());
                    }
                }
                
                // Detect characters (all caps, short lines before dialogue)
                if (/^[A-Z][A-Z\s]{2,}$/.test(trimmed) && trimmed.length < 40) {
                    this.state.characters.add(trimmed);
                }
            });

            this.state.characters = Array.from(this.state.characters);
            this.state.locations = Array.from(this.state.locations);
        }

        renderAll() {
            this.renderScenes();
            this.renderCharacters();
            this.renderLocations();
            this.renderNotes();
            this.renderStructure();
        }

        renderScenes() {
            if (!this.dom.scenesList) return;
            
            this.dom.scenesList.innerHTML = this.state.scenes.map(scene => `
                <div class="scene-item" data-line="${scene.line}">
                    <strong>CENA ${scene.number}</strong><br>
                    <small>${scene.text.substring(0, 50)}${scene.text.length > 50 ? '...' : ''}</small>
                </div>
            `).join('') || '<p style="color:var(--text-tertiary);font-size:0.85rem;">Nenhuma cena detectada</p>';

            // Add click handlers
            this.dom.scenesList.querySelectorAll('.scene-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.goToLine(parseInt(item.dataset.line));
                });
            });
        }

        renderCharacters() {
            if (!this.dom.charactersList) return;
            
            this.dom.charactersList.innerHTML = this.state.characters.map(char => `
                <div class="character-item">
                    <i class="fas fa-user"></i> ${char}
                </div>
            `).join('') || '<p style="color:var(--text-tertiary);font-size:0.85rem;">Nenhum personagem detectado</p>';
        }

        renderLocations() {
            if (!this.dom.locationsList) return;
            
            this.dom.locationsList.innerHTML = this.state.locations.map(loc => `
                <div class="location-item">
                    <i class="fas fa-map-marker-alt"></i> ${loc}
                </div>
            `).join('') || '<p style="color:var(--text-tertiary);font-size:0.85rem;">Nenhuma locação detectada</p>';
        }

        renderStructure() {
            if (!this.dom.structureViz) return;
            
            const totalScenes = this.state.scenes.length;
            if (totalScenes === 0) {
                this.dom.structureViz.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.85rem;">Escreva cenas para ver a estrutura</p>';
                return;
            }

            // Simple 3-act structure visualization
            const act1 = Math.ceil(totalScenes * 0.25);
            const act2 = Math.ceil(totalScenes * 0.5);
            const act3 = totalScenes - act1 - act2;

            this.dom.structureViz.innerHTML = `
                <div class="structure-segment act1" style="width:100%" title="Ato 1: ${act1} cenas"></div>
                <div class="structure-segment act2" style="width:100%" title="Ato 2: ${act2} cenas"></div>
                <div class="structure-segment act3" style="width:100%" title="Ato 3: ${act3} cenas"></div>
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-top:4px;">
                    <span>Ato 1</span><span>Ato 2</span><span>Ato 3</span>
                </div>
            `;
        }

        // ============================================
        // STATISTICS
        // ============================================
        updateStats() {
            const content = this.state.content;
            const words = content.trim() ? content.trim().split(/\s+/).length : 0;
            const chars = content.length;
            const pages = Math.ceil(words / 250); // Approximate: 250 words per page
            const minutes = Math.round(pages * 1); // 1 page ≈ 1 minute

            this.dom.pageCount.textContent = pages;
            this.dom.wordCount.textContent = words.toLocaleString();
            this.dom.charCount.textContent = chars.toLocaleString();
            this.dom.sceneCount.textContent = this.state.scenes.length;
            this.dom.timeEstimate.textContent = `${minutes} min`;
        }

        // ============================================
        // SEARCH & REPLACE
        // ============================================
        toggleSearch() {
            this.dom.searchBar.classList.toggle('hidden');
            if (!this.dom.searchBar.classList.contains('hidden')) {
                this.dom.searchInput.focus();
            }
        }

        performSearch() {
            const query = this.dom.searchInput.value;
            const content = this.dom.editor.value;
            this.state.searchMatches = [];
            
            if (!query) return;

            const regex = document.getElementById('regexToggle')?.checked 
                ? new RegExp(query, 'gi') 
                : new RegExp(this.escapeRegex(query), 'gi');
            
            let match;
            while ((match = regex.exec(content)) !== null) {
                this.state.searchMatches.push({
                    start: match.index,
                    end: match.index + match[0].length
                });
            }

            this.state.currentSearchIndex = -1;
            if (this.state.searchMatches.length > 0) {
                this.findNext();
            }
        }

        findNext() {
            if (this.state.searchMatches.length === 0) return;
            
            this.state.currentSearchIndex = (this.state.currentSearchIndex + 1) % this.state.searchMatches.length;
            this.highlightSearch();
        }

        findPrevious() {
            if (this.state.searchMatches.length === 0) return;
            
            this.state.currentSearchIndex = (this.state.currentSearchIndex - 1 + this.state.searchMatches.length) % this.state.searchMatches.length;
            this.highlightSearch();
        }

        highlightSearch() {
            const match = this.state.searchMatches[this.state.currentSearchIndex];
            if (!match) return;

            this.dom.editor.setSelectionRange(match.start, match.end);
            this.dom.editor.focus();
        }

        replace() {
            const replacement = this.dom.replaceInput.value;
            const match = this.state.searchMatches[this.state.currentSearchIndex];
            if (!match) return;

            const content = this.dom.editor.value;
            const newContent = content.substring(0, match.start) + replacement + content.substring(match.end);
            this.dom.editor.value = newContent;
            this.handleInput();
            this.performSearch();
        }

        replaceAll() {
            const query = this.dom.searchInput.value;
            const replacement = this.dom.replaceInput.value;
            if (!query) return;

            const regex = document.getElementById('regexToggle')?.checked 
                ? new RegExp(query, 'gi') 
                : new RegExp(this.escapeRegex(query), 'gi');
            
            this.dom.editor.value = this.dom.editor.value.replace(regex, replacement);
            this.handleInput();
            this.performSearch();
            this.showToast(`${this.state.searchMatches.length} substituições realizadas`, 'success');
        }

        escapeRegex(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        }

        // ============================================
        // FILE OPERATIONS
        // ============================================
        fileNew() {
            if (this.state.isModified && !confirm('Descartar alterações não salvas?')) return;
            
            this.dom.editor.value = '';
            this.state.content = '';
            this.state.fileName = 'Sem Título.fountain';
            this.dom.fileName.value = this.state.fileName;
            this.state.isModified = false;
            this.state.history = [];
            this.state.historyIndex = -1;
            
            this.handleInput();
            this.showToast('Novo arquivo criado', 'success');
        }

        fileOpen() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.fountain,.txt,.fdx';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (!file) return;

                this.state.fileName = file.name;
                this.dom.fileName.value = file.name;

                const reader = new FileReader();
                reader.onload = (e) => {
                    this.dom.editor.value = e.target.result;
                    this.handleInput();
                    this.showToast(`Arquivo "${file.name}" aberto`, 'success');
                };
                reader.readAsText(file);
            };
            input.click();
        }

        fileSave() {
            const content = this.dom.editor.value;
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = this.dom.fileName.value;
            a.click();
            
            URL.revokeObjectURL(url);
            this.state.isModified = false;
            this.updateSaveStatus('salvo');
            this.saveToStorage();
            this.showToast('Arquivo salvo com sucesso', 'success');
        }

        // ============================================
        // EXPORT FUNCTIONS
        // ============================================
        async exportPDF() {
            this.showToast('Gerando PDF...', 'info');
            
            // Simulate progress
            const modal = document.getElementById('exportModal');
            const progress = document.getElementById('exportProgress');
            const status = document.getElementById('exportStatus');
            
            modal?.classList.remove('hidden');
            
            for (let i = 0; i <= 100; i += 10) {
                progress.style.width = i + '%';
                status.textContent = `Gerando PDF... ${i}%`;
                await this.sleep(100);
            }

            // Create printable content
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>${this.state.fileName.replace('.fountain', '.pdf')}</title>
                    <style>
                        body { font-family: 'Courier Prime', monospace; font-size: 12px; line-height: 1.6; padding: 2cm; }
                        pre { white-space: pre-wrap; margin: 0; }
                    </style>
                </head>
                <body>
                    <pre>${this.dom.editor.value}</pre>
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();

            setTimeout(() => {
                modal?.classList.add('hidden');
                this.showToast('PDF gerado com sucesso', 'success');
            }, 500);
        }

        exportHTML() {
            const content = this.dom.editor.value
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');

            const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>${this.state.fileName}</title>
    <style>
        body { font-family: 'Courier Prime', monospace; padding: 40px; max-width: 800px; margin: 0 auto; background: #fff; color: #1e293b; }
        pre { white-space: pre-wrap; line-height: 1.6; }
    </style>
</head>
<body>
    <pre>${content}</pre>
</body>
</html>`;

            this.downloadFile(html, this.state.fileName.replace('.fountain', '.html'), 'text/html');
            this.showToast('HTML exportado', 'success');
        }

        exportFountain() {
            this.downloadFile(this.dom.editor.value, this.state.fileName, 'text/plain');
            this.showToast('Fountain exportado', 'success');
        }

        exportTXT() {
            this.downloadFile(this.dom.editor.value, this.state.fileName.replace('.fountain', '.txt'), 'text/plain');
            this.showToast('Texto exportado', 'success');
        }

        downloadFile(content, filename, type) {
            const blob = new Blob([content], { type });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }

        // ============================================
        // NOTES SYSTEM
        // ============================================
        addNote() {
            document.getElementById('noteId').value = '';
            document.getElementById('noteTitle').value = '';
            document.getElementById('noteContent').value = '';
            document.getElementById('noteColor').value = 'yellow';
            document.getElementById('noteModalTitle').textContent = 'Nova Nota';
            
            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
            document.querySelector('.color-option[data-color="yellow"]')?.classList.add('selected');
            
            this.openModal('noteModal');
        }

        saveNote() {
            const id = document.getElementById('noteId').value;
            const title = document.getElementById('noteTitle').value;
            const content = document.getElementById('noteContent').value;
            const color = document.getElementById('noteColor').value;

            if (!title.trim()) {
                this.showToast('Título da nota é obrigatório', 'warning');
                return;
            }

            const note = { id: id || Date.now().toString(), title, content, color, date: new Date().toISOString() };

            if (id) {
                const index = this.state.notes.findIndex(n => n.id === id);
                if (index !== -1) this.state.notes[index] = note;
            } else {
                this.state.notes.push(note);
            }

            this.saveToStorage();
            this.renderNotes();
            this.closeModal('noteModal');
            this.showToast('Nota salva', 'success');
        }

        renderNotes() {
            if (!this.dom.notesList) return;

            this.dom.notesList.innerHTML = this.state.notes.map(note => `
                <div class="note-item ${note.color}" onclick="app.editNote('${note.id}')">
                    <strong>${note.title}</strong>
                    <small style="display:block;color:var(--text-secondary);margin-top:4px;">
                        ${note.content.substring(0, 50)}${note.content.length > 50 ? '...' : ''}
                    </small>
                </div>
            `).join('') || '<p style="color:var(--text-tertiary);font-size:0.85rem;">Nenhuma nota</p>';
        }

        editNote(id) {
            const note = this.state.notes.find(n => n.id === id);
            if (!note) return;

            document.getElementById('noteId').value = note.id;
            document.getElementById('noteTitle').value = note.title;
            document.getElementById('noteContent').value = note.content;
            document.getElementById('noteColor').value = note.color;
            document.getElementById('noteModalTitle').textContent = 'Editar Nota';

            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
            document.querySelector(`.color-option[data-color="${note.color}"]`)?.classList.add('selected');

            this.openModal('noteModal');
        }

        selectColor(color) {
            document.getElementById('noteColor').value = color;
            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
            document.querySelector(`.color-option[data-color="${color}"]`)?.classList.add('selected');
        }

        // ============================================
        // SETTINGS
        // ============================================
        openSettings() {
            document.getElementById('settingTheme').value = this.state.theme;
            document.getElementById('settingAutoSave').value = this.state.autoSaveInterval;
            document.getElementById('settingFontSize').value = this.state.fontSize;
            document.getElementById('settingZoom').value = this.state.zoom;
            document.getElementById('settingLineNumbers').checked = this.state.showLineNumbers;
            document.getElementById('settingAutoComplete').checked = this.state.autoComplete;

            document.getElementById('fontSizeValue').textContent = `${this.state.fontSize}px`;
            document.getElementById('zoomValue').textContent = `${this.state.zoom}%`;

            this.openModal('settingsModal');
        }

        saveSettings() {
            this.state.theme = document.getElementById('settingTheme').value;
            this.state.autoSaveInterval = parseInt(document.getElementById('settingAutoSave').value);
            this.state.fontSize = parseInt(document.getElementById('settingFontSize').value);
            this.state.zoom = parseInt(document.getElementById('settingZoom').value);
            this.state.showLineNumbers = document.getElementById('settingLineNumbers').checked;
            this.state.autoComplete = document.getElementById('settingAutoComplete').checked;

            this.applyTheme();
            this.updateZoom();
            this.updateLineNumbers();
            this.saveToStorage();
            this.closeModal('settingsModal');
            this.showToast('Configurações salvas', 'success');
        }

        // ============================================
        // THEME & UI
        // ============================================
        toggleTheme() {
            this.state.theme = this.state.theme === 'light' ? 'dark' : 'light';
            this.applyTheme();
            this.saveToStorage();
        }

        applyTheme() {
            document.documentElement.setAttribute('data-theme', this.state.theme);
            const icon = this.dom.themeToggle.querySelector('i');
            icon.className = this.state.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }

        updateZoom() {
            this.dom.editor.style.fontSize = `${this.state.fontSize * (this.state.zoom / 100)}px`;
            this.dom.lineNumbers.style.fontSize = `${this.state.fontSize * (this.state.zoom / 100)}px`;
            this.dom.zoomLevel.textContent = `${this.state.zoom}%`;
        }

        zoomIn() {
            this.state.zoom = Math.min(200, this.state.zoom + 10);
            this.updateZoom();
        }

        zoomOut() {
            this.state.zoom = Math.max(50, this.state.zoom - 10);
            this.updateZoom();
        }

        toggleSidebar(target) {
            const sidebar = document.getElementById(target);
            sidebar?.classList.toggle('collapsed');
        }

        togglePanel(panelId) {
            const panel = document.getElementById(panelId);
            const header = document.querySelector(`[data-panel="${panelId}"]`);
            const icon = header?.querySelector('.fa-chevron-down');
            
            panel?.classList.toggle('collapsed');
            icon?.classList.toggle('fa-chevron-down');
            icon?.classList.toggle('fa-chevron-up');
        }

        toggleDropdown(menuId) {
            const menu = document.getElementById(menuId);
            menu?.classList.toggle('show');
        }

        closeAllDropdowns() {
            document.querySelectorAll('.dropdown-menu').forEach(menu => menu.classList.remove('show'));
        }

        // ============================================
        // MODALS
        // ============================================
        openModal(modalId) {
            document.getElementById('modalOverlay')?.classList.remove('hidden');
            document.getElementById(modalId)?.classList.remove('hidden');
        }

        closeModal(modalId) {
            document.getElementById('modalOverlay')?.classList.add('hidden');
            document.getElementById(modalId)?.classList.add('hidden');
        }

        closeAllModals() {
            document.querySelectorAll('.modal, .modal-overlay').forEach(el => el.classList.add('hidden'));
        }

        // ============================================
        // CONTEXT MENU
        // ============================================
        showContextMenu(e) {
            e.preventDefault();
            const menu = this.dom.contextMenu;
            menu.style.left = `${e.clientX}px`;
            menu.style.top = `${e.clientY}px`;
            menu.classList.remove('hidden');
        }

        hideContextMenu() {
            this.dom.contextMenu?.classList.add('hidden');
        }

        // ============================================
        // UTILITIES
        // ============================================
        undo() {
            if (this.state.historyIndex > 0) {
                this.state.historyIndex--;
                this.dom.editor.value = this.state.history[this.state.historyIndex];
                this.handleInput();
            }
        }

        redo() {
            if (this.state.historyIndex < this.state.history.length - 1) {
                this.state.historyIndex++;
                this.dom.editor.value = this.state.history[this.state.historyIndex];
                this.handleInput();
            }
        }

        goToLine(lineNum) {
            const lines = this.dom.editor.value.split('\n');
            let position = 0;
            for (let i = 0; i < lineNum - 1; i++) {
                position += lines[i].length + 1;
            }
            this.dom.editor.setSelectionRange(position, position);
            this.dom.editor.focus();
        }

        toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }

        handleAction(e) {
            const action = e.currentTarget.dataset.action;
            const actions = {
                'new': () => this.fileNew(),
                'open': () => this.fileOpen(),
                'save': () => this.fileSave(),
                'undo': () => this.undo(),
                'redo': () => this.redo(),
                'search': () => this.toggleSearch(),
                'notes': () => this.addNote(),
                'characters': () => {},
                'scenes': () => {},
                'zoom-in': () => this.zoomIn(),
                'zoom-out': () => this.zoomOut(),
                'search-prev': () => this.findPrevious(),
                'search-next': () => this.findNext(),
                'search-close': () => this.dom.searchBar.classList.add('hidden'),
                'replace': () => this.replace(),
                'replaceAll': () => this.replaceAll(),
                'addNote': () => this.addNote(),
                'saveNote': () => this.saveNote(),
                'saveSettings': () => this.saveSettings(),
                'export-pdf': () => this.exportPDF(),
                'export-html': () => this.exportHTML(),
                'export-fountain': () => this.exportFountain(),
                'export-txt': () => this.exportTXT(),
                'ctx-cut': () => document.execCommand('cut'),
                'ctx-copy': () => document.execCommand('copy'),
                'ctx-paste': () => navigator.clipboard.readText().then(text => this.insertAtCursor(text)),
                'ctx-undo': () => this.undo(),
                'ctx-redo': () => this.redo(),
                'ctx-selectall': () => this.dom.editor.select()
            };

            // Format actions
            if (action.startsWith('format-')) {
                this.formatAs(action.replace('format-', ''));
            } else if (actions[action]) {
                actions[action]();
            }

            e.stopPropagation();
        }

        updateSaveStatus(status) {
            const icon = status === 'salvo' ? 'fa-check-circle' : 'fa-circle';
            const text = status === 'modificado' ? 'Não salvo' : 'Salvo';
            this.dom.saveStatus.innerHTML = `<i class="fas ${icon}"></i> ${text}`;
        }

        showToast(message, type = 'info') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            `;
            container.appendChild(toast);

            setTimeout(() => {
                toast.style.animation = 'slideIn 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        setSampleContent() {
            const sample = `FADE IN:

INT. CAFÉ - DIA

Um café acolhedor no centro da cidade. JOÃO (30), vestido casualmente, está sentado em uma mesa perto da janela.

Ele olha para o relógio, impaciente.

                    JOÃO
          Onde ela está?

A porta se abre. MARIA (28) entra, olhando ao redor.

                    MARIA
          Desculpe o atraso! O trânsito...

                    JOÃO
          (sorrindo)
          Tudo bem. Eu também acabei de chegar.

CORTE PARA:

EXT. PARQUE - TARDE

João e Maria caminham pelo parque, conversando animadamente.

                    MARIA
          Então você realmente escreveu um roteiro inteiro?

                    JOÃO
          Quase isso. Estou na página 45.

Eles riem. O sol se põe ao fundo.

FADE OUT.`;

            this.dom.editor.value = sample;
            this.handleInput();
        }

        // ============================================
        // STORAGE
        // ============================================
        saveToStorage() {
            try {
                localStorage.setItem('roteirista_content', this.dom.editor.value);
                localStorage.setItem('roteirista_filename', this.state.fileName);
                localStorage.setItem('roteirista_settings', JSON.stringify({
                    theme: this.state.theme,
                    zoom: this.state.zoom,
                    fontSize: this.state.fontSize,
                    autoSaveInterval: this.state.autoSaveInterval,
                    showLineNumbers: this.state.showLineNumbers,
                    autoComplete: this.state.autoComplete
                }));
                localStorage.setItem('roteirista_notes', JSON.stringify(this.state.notes));
            } catch (e) {
                console.warn('Storage unavailable');
            }
        }

        loadFromStorage() {
            try {
                const content = localStorage.getItem('roteirista_content');
                const filename = localStorage.getItem('roteirista_filename');
                const settings = localStorage.getItem('roteirista_settings');
                const notes = localStorage.getItem('roteirista_notes');

                if (content) this.dom.editor.value = content;
                if (filename) {
                    this.state.fileName = filename;
                    this.dom.fileName.value = filename;
                }
                if (settings) {
                    const s = JSON.parse(settings);
                    Object.assign(this.state, s);
                }
                if (notes) {
                    this.state.notes = JSON.parse(notes);
                }
            } catch (e) {
                console.warn('Could not load from storage');
            }
        }

        startAutoSave() {
            setInterval(() => {
                if (this.state.isModified) {
                    this.saveToStorage();
                    this.updateSaveStatus('salvo');
                }
            }, this.state.autoSaveInterval * 60 * 1000);
        }

        handleBeforeUnload(e) {
            if (this.state.isModified) {
                e.preventDefault();
                e.returnValue = '';
            }
        }
    }

    // Initialize app when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => window.app = new RoteiristaPro());
    } else {
        window.app = new RoteiristaPro();
    }
})();
