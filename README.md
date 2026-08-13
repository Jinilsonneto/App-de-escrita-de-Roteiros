# 🎬 Roteirista Pro v3.0 - Studio Edition

Um editor profissional de roteiros para cinema e TV, desenvolvido com tecnologias web modernas.

![Versão](https://img.shields.io/badge/vers%C3%A3o-3.0-blue)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)
![Plataforma](https://img.shields.io/badge/plataforma-Linux%20%7C%20Web-lightgrey)

## ✨ Recursos

### Editor Profissional
- Formatação industry-standard (Hollywood)
- Suporte ao formato Fountain
- Atalhos de teclado completos
- Numeração de linhas
- Zoom ajustável

### Exportação Multi-formato
- **PDF** - Pronto para impressão
- **HTML** - Para visualização web
- **Fountain** - Formato padrão da indústria
- **Final Draft (.fdx)** - Compatível com software profissional

### Organização
- Navegador de cenas
- Lista de personagens
- Mapeamento de locações
- Sistema de notas

### Ferramentas Inteligentes
- Busca e substituição (com regex)
- Histórico de versões
- Auto-salvamento
- Backup automático
- Estatísticas em tempo real
- Estimativa de tempo de tela

### Interface Moderna
- Temas claro e escuro
- Design responsivo
- Painéis colapsáveis
- Notificações toast
- Menu de contexto

## 🚀 Instalação no Linux Mint/Ubuntu

### Método 1: Instalador Automático (Recomendado)

```bash
# Baixe ou clone o repositório
cd /workspace

# Execute o instalador (requer sudo)
sudo ./install.sh
```

Após a instalação:
- **Menu**: Applications → Office → Roteirista Pro
- **Terminal**: Digite `roteirista-pro`
- **Navegador**: Abra `file:///opt/roteirista-pro/index.html`

### Método 2: Manual

```bash
# Copie os arquivos para uma pasta
mkdir -p ~/Apps/roteirista-pro
cp index.html styles.css app.js ~/Apps/roteirista-pro/

# Abra no navegador
firefox ~/Apps/roteirista-pro/index.html
```

### Método 3: Uso Direto no Navegador

Simplesmente abra o arquivo `index.html` em qualquer navegador moderno:
- Google Chrome (recomendado)
- Chromium
- Firefox
- Microsoft Edge

## ⌨️ Atalhos de Teclado

| Ação | Atalho |
|------|--------|
| Novo arquivo | `Ctrl + N` |
| Abrir | `Ctrl + O` |
| Salvar | `Ctrl + S` |
| Exportar PDF | `Ctrl + E` |
| Desfazer | `Ctrl + Z` |
| Refazer | `Ctrl + Y` |
| Buscar | `Ctrl + F` |
| Substituir | `Ctrl + H` |
| Inserir Cena | `Ctrl + Shift + C` |
| Inserir Personagem | `Ctrl + P` |
| Inserir Diálogo | `Ctrl + D` |
| Inserir Transição | `Ctrl + T` |

## 📁 Estrutura de Arquivos

```
roteirista-pro/
├── index.html      # Página principal
├── styles.css      # Estilos e temas
├── app.js          # Lógica da aplicação
├── install.sh      # Script de instalação
└── README.md       # Este arquivo
```

## 🛠️ Requisitos

### Mínimos
- Navegador web moderno (Chrome 80+, Firefox 75+)
- 50 MB de espaço em disco
- Conexão internet (para carregar fontes e ícones)

### Recomendados
- Google Chrome ou Chromium
- 100 MB de RAM disponível
- Resolução 1920x1080 ou superior

## 🎯 Formatos de Roteiro Suportados

O aplicativo segue o padrão da indústria:

```
INT. LOCAL - DIA

JOÃO SILVA (40), detective cansado, entra na sala.

                    MARIA
          (surpresa)
          Onde você estava?

JOÃO
          Tive um dia longo.

CORTE PARA:
```

### Elementos Reconhecidos
- **CENA**: `INT./EXT. LOCAL - DIA/NOITE`
- **AÇÃO**: Texto normal
- **PERSONAGEM**: Texto em CAIXA ALTA
- **DIÁLOGO**: Após nome do personagem
- **PARENTHETICAL**: `(expressão)` entre parênteses
- **TRANSIÇÃO**: `CORTE PARA:`, `FADE OUT:`, etc.

## 🔧 Configurações

Acesse as configurações clicando no ícone de engrenagem:

- **Tema**: Claro, Escuro ou Sistema
- **Idioma**: Português, Inglês, Espanhol
- **Auto-salvar**: Intervalo configurável
- **Fonte**: Tamanho ajustável (10-24px)
- **Layout**: Largura da linha, numeração
- **Backup**: Local e retenção

## 💡 Dicas de Uso

1. **Use atalhos** para ganhar velocidade
2. **Ative auto-salvar** para não perder trabalho
3. **Crie snapshots** antes de grandes mudanças
4. **Use notas** para ideias durante a escrita
5. **Exporte PDF** para compartilhar com equipe

## 🐛 Solução de Problemas

### O aplicativo não carrega
- Verifique se o navegador está atualizado
- Limpe o cache do navegador
- Tente outro navegador

### Exportação PDF falha
- Certifique-se de estar online (usa biblioteca CDN)
- Tente exportar em HTML como alternativa

### Atalhos não funcionam
- Verifique se há conflito com extensões do navegador
- Tente usar o menu em vez de atalhos

## 📝 Changelog

### v3.0 (Atual)
- ✨ Interface completamente redesenhada
- ✨ Temas claro e escuro
- ✨ Exportação para múltiplos formatos
- ✨ Navegador de cenas e personagens
- ✨ Histórico de versões
- ✨ Busca com regex
- ✨ Modo fullscreen
- 🐛 Correções diversas de bugs

### v2.0
- Editor com formatação automática
- Salvamento local
- Estatísticas básicas

### v1.0
- Versão inicial
- Editor de texto simples

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch (`git checkout -b feature/nova-feature`)
3. Commitar mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Abrir Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Desenvolvedor

Desenvolvido com ❤️ para roteiristas brasileiros.

## 🔗 Links Úteis

- [Formato Fountain](https://fountain.io/)
- [Padrão Hollywood](https://www.scriptmag.com/features/the-elements-of-style-for-screenwriters)
- [Dicas de Roteiro](https://www.studiobinder.com/blog/screenplay-format/)

---

**Bons roteiros! 🎬✍️**
