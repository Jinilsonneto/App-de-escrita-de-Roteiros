#!/bin/bash

# ============================================
# ROTEIRISTA PRO v3.0 - Instalador para Linux
# Fácil instalação no Linux Mint/Ubuntu
# ============================================

echo "╔════════════════════════════════════════╗"
echo "║   ROTEIRISTA PRO v3.0 - Instalador    ║"
echo "║        Studio Edition                 ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Este script precisa de privilégios de administrador${NC}"
    echo "Por favor, execute com: sudo ./install.sh"
    exit 1
fi

# Obter o diretório atual do script (não assumir /workspace)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Diretório de instalação
INSTALL_DIR="/opt/roteirista-pro"
APP_NAME="Roteirista Pro"

echo -e "${BLUE}📦 Preparando instalação...${NC}"
echo ""

# Criar diretório de instalação
echo -e "${YELLOW}[1/5]${NC} Criando diretório de instalação..."
mkdir -p "$INSTALL_DIR"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Diretório criado: $INSTALL_DIR${NC}"
else
    echo -e "${RED}✗ Erro ao criar diretório${NC}"
    exit 1
fi

# Copiar arquivos - usar SCRIPT_DIR em vez de /workspace fixo
echo -e "${YELLOW}[2/5]${NC} Copiando arquivos do aplicativo..."
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Arquivos copiados com sucesso${NC}"
else
    echo -e "${RED}✗ Erro ao copiar arquivos${NC}"
    exit 1
fi

# Instalar dependências (opcional - navegador já deve estar instalado)
echo -e "${YELLOW}[3/5]${NC} Verificando dependências..."

# Verificar se tem Firefox ou Chrome
if command -v firefox &> /dev/null || command -v google-chrome &> /dev/null || command -v chromium &> /dev/null; then
    echo -e "${GREEN}✓ Navegador web encontrado${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum navegador encontrado. Instalando Firefox...${NC}"
    apt update && apt install -y firefox
fi

# Criar atalho desktop
echo -e "${YELLOW}[4/5]${NC} Criando atalho na área de trabalho..."

cat > /usr/share/applications/roteirista-pro.desktop << DESKTOP
[Desktop Entry]
Version=3.0
Name=Roteirista Pro
Comment=Editor profissional de roteiros - Studio Edition
Exec=/usr/local/bin/roteirista-pro
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=Office;TextEditor;
MimeType=text/plain;
Keywords=roteiro;screenplay;escrita;cinema;
DESKTOP

# Se não tiver ícone, criar um placeholder
if [ ! -f "$INSTALL_DIR/icon.png" ]; then
    echo -e "${YELLOW}Criando ícone padrão...${NC}"
    # Ícone SVG simples
    cat > "$INSTALL_DIR/icon.svg" << 'SVGICON'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="15" fill="#6366f1"/>
  <text x="50" y="65" font-size="50" text-anchor="middle" fill="white" font-family="Arial" font-weight="bold">RP</text>
</svg>
SVGICON
fi

chmod +x /usr/share/applications/roteirista-pro.desktop
echo -e "${GREEN}✓ Atalho criado no menu de aplicativos${NC}"

# Criar script de lançamento
echo -e "${YELLOW}[5/5]${NC} Criando script de lançamento..."

cat > /usr/local/bin/roteirista-pro << 'LAUNCHER'
#!/bin/bash
# Lançar Roteirista Pro - usa caminho relativo ao local de instalação

INSTALL_DIR="/opt/roteirista-pro"

# Tentar diferentes navegadores
if command -v google-chrome &> /dev/null; then
    google-chrome --app="file://$INSTALL_DIR/index.html" "$@"
elif command -v chromium &> /dev/null; then
    chromium --app="file://$INSTALL_DIR/index.html" "$@"
elif command -v firefox &> /dev/null; then
    firefox --new-window "file://$INSTALL_DIR/index.html" "$@"
else
    echo "Erro: Nenhum navegador compatível encontrado!"
    echo "Por favor, instale Google Chrome, Chromium ou Firefox."
    exit 1
fi
LAUNCHER

chmod +x /usr/local/bin/roteirista-pro
echo -e "${GREEN}✓ Script de lançamento criado${NC}"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║         ✅ Instalação Completa!        ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 Roteirista Pro foi instalado com sucesso!${NC}"
echo ""
echo -e "${BLUE}Como usar:${NC}"
echo "  • Pelo menu: Applications → Office → Roteirista Pro"
echo "  • Pelo terminal: Digite ${YELLOW}roteirista-pro${NC}"
echo "  • Direto no navegador: Abra file://$INSTALL_DIR/index.html"
echo ""
echo -e "${BLUE}Recursos incluídos:${NC}"
echo "  ✓ Editor de roteiros formato industry-standard"
echo "  ✓ Exportação para PDF, HTML, Fountain e Final Draft"
echo "  ✓ Temas claro e escuro"
echo "  ✓ Auto-salvamento"
echo "  ✓ Navegador de cenas e personagens"
echo "  ✓ Estatísticas em tempo real"
echo "  ✓ Histórico de versões"
echo "  ✓ Busca e substituição"
echo "  ✓ Atalhos de teclado completos"
echo ""
echo -e "${YELLOW}Dica:${NC} Para atualizar, rode este script novamente."
echo -e "${YELLOW}      ${NC} Para desinstalar: sudo rm -rf $INSTALL_DIR /usr/local/bin/roteirista-pro /usr/share/applications/roteirista-pro.desktop"
echo ""

exit 0
