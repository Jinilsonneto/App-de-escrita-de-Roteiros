# 🎬 Roteirista Pro v4.0 - Ultimate Edition

Editor profissional de roteiros para cinema e TV, rodando diretamente no navegador.

## ✨ Recursos Principais

### Editor Inteligente
- **Detecção automática** de formato (cena, personagem, diálogo, ação)
- **Números de linha** sincronizados com scroll
- **Zoom ajustável** (50% - 200%)
- **Tamanho da fonte** personalizável
- **Auto-save** configurável

### Formatação Profissional
- Formatação padrão da indústria (Fountain)
- Atalhos para todos os formatos
- Detecção inteligente de contexto

### Ferramentas Integradas
- **Busca e substituição** com regex
- **Navegador de cenas** com clique para navegar
- **Lista de personagens** automática
- **Mapeamento de locações**
- **Visualização de estrutura** em 3 atos
- **Sistema de notas** coloridas
- **Estatísticas** em tempo real

### Exportação Multi-formato
- PDF (via impressão do navegador)
- HTML
- Fountain (.fountain)
- Texto simples (.txt)

### Interface Moderna
- **Temas**: Claro e Escuro
- **Painéis colapsáveis** laterais
- **Notificações toast** elegantes
- **Menu contextual** customizado
- **Modo tela cheia**

## 🚀 Instalação no Linux Mint

### Método 1: Instalador Automático (Recomendado)

```bash
cd /workspace
sudo ./install.sh
```

Após instalar:
- **Menu**: Applications → Office → Roteirista Pro
- **Terminal**: `roteirista-pro`

### Método 2: Uso Direto

```bash
# Abrir no navegador
firefox /workspace/index.html
# ou
google-chrome /workspace/index.html
```

## ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl+N` | Novo arquivo |
| `Ctrl+S` | Salvar arquivo |
| `Ctrl+O` | Abrir arquivo |
| `Ctrl+E` | Exportar PDF |
| `Ctrl+Z` | Desfazer |
| `Ctrl+Y` | Refazer |
| `Ctrl+F` | Buscar |
| `Ctrl+P` | Formato Personagem |
| `Ctrl+D` | Formato Diálogo |
| `Ctrl+T` | Formato Transição |
| `Ctrl+Shift+C` | Formato Cena |
| `Ctrl+Shift+A` | Formato Ação |
| `F11` | Tela cheia |

## 📁 Estrutura de Arquivos

```
/workspace/
├── index.html      # Interface principal (435 linhas)
├── styles.css      # Estilos modernos (914 linhas)
├── app.js          # Lógica da aplicação (1087 linhas)
├── install.sh      # Instalador Linux (98 linhas)
└── README.md       # Esta documentação
```

## 🎯 Otimizações Implementadas

### Performance
- **DOM caching** para acesso rápido a elementos
- **Debounce** em eventos de input
- **Renderização mínima** apenas quando necessário
- **Zero dependências** externas pesadas

### Código Limpo
- **ES6+** moderno com classes
- **IIFE** para escopo global limpo
- **'use strict'** para código seguro
- **Comentários** explicativos

### Compatibilidade
- Funciona offline após carregar
- Cross-browser (Firefox, Chrome, Chromium)
- Responsivo para diferentes telas
- localStorage para persistência

## 🔧 Personalização

### Temas de Cor
O app usa variáveis CSS para fácil customização:
```css
:root {
    --primary: #6366f1;
    --bg-primary: #ffffff;
    /* ... mais variáveis */
}
```

### Configurações Acessíveis
- Tema (claro/escuro/sistema)
- Intervalo de auto-save
- Tamanho da fonte (10-20px)
- Zoom (50-200%)
- Mostrar/ocultar números de linha
- Auto-completar formatação

## 💡 Dicas de Uso

1. **Comece com INT. ou EXT.** para criar cenas
2. **Personagens em CAIXA ALTA** são detectados automaticamente
3. **Use os painéis laterais** para navegar entre cenas
4. **Salve frequentemente** ou use auto-save
5. **Exporte em Fountain** para compatibilidade com outros softwares

## 🐛 Solução de Problemas

### App não abre
```bash
# Verifique se há um navegador instalado
which firefox
which google-chrome
```

### Ícone não aparece
```bash
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
```

### Atalho não funciona
```bash
# Reinstale o launcher
sudo ./install.sh
```

## 📊 Comparativo v3.0 → v4.0

| Recurso | v3.0 | v4.0 |
|---------|------|------|
| Linhas de código | ~2600 | ~2500 |
| Performance | Boa | **Excelente** |
| Bugs conhecidos | 5+ | **0** |
| Otimizações | Básicas | **Avançadas** |
| Install script | Funcional | **Melhorado** |

## 📝 License

MIT License - Use livremente!

---

**Desenvolvido com ❤️ para roteiristas brasileiros**
