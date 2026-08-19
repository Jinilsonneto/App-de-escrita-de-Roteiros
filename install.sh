#!/bin/bash

# ============================================
# ROTEIRISTA PRO v4.0 - Ultimate Edition
# Instalador para Linux Mint/Ubuntu
# ============================================

set -e

echo "╔════════════════════════════════════════╗"
echo "║  ROTEIRISTA PRO v4.0 - Instalador     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Erro: Execute como sudo (sudo ./install.sh)${NC}"
    exit 1
fi

INSTALL_DIR="/opt/roteirista-pro"
APP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
BIN_DIR="/usr/local/bin"

echo -e "${BLUE}→ Removendo versão anterior...${NC}"
rm -rf "$INSTALL_DIR" 2>/dev/null || true

echo -e "${BLUE}→ Criando diretórios...${NC}"
mkdir -p "$INSTALL_DIR" "$APP_DIR" "$ICON_DIR"

echo -e "${BLUE}→ Copiando arquivos...${NC}"
cd "$(dirname "$0")"
cp index.html styles.css app.js "$INSTALL_DIR/"

echo -e "${BLUE}→ Criando ícone...${NC}"
cat > "$ICON_DIR/roteirista-pro.svg" << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1"/>
    <stop offset="100%" style="stop-color:#4f46e5;stop-opacity:1"/>
  </linearGradient></defs>
  <rect width="256" height="256" rx="48" fill="url(#grad)"/>
  <text x="128" y="160" font-family="Arial" font-size="120" font-weight="bold" fill="white" text-anchor="middle">R</text>
  <text x="128" y="220" font-family="Arial" font-size="28" fill="white" text-anchor="middle">PRO</text>
</svg>
SVGEOF

echo -e "${BLUE}→ Criando launcher...${NC}"
cat > "$APP_DIR/roteirista-pro.desktop" << 'DESKTOPEOF'
[Desktop Entry]
Version=4.0
Type=Application
Name=Roteirista Pro
GenericName=Editor de Roteiros
Comment=Editor profissional de roteiros para cinema e TV
Exec=/opt/roteirista-pro/launch.sh
Icon=roteirista-pro
Terminal=false
Categories=Office;TextEditor;
Keywords=roteiro;cinema;tv;screenplay;
StartupNotify=true
DESKTOPEOF

cat > "$INSTALL_DIR/launch.sh" << 'LAUNCHEOF'
#!/bin/bash
BROWSER=""
for b in firefox google-chrome chromium chromium-browser; do
    command -v $b >/dev/null && BROWSER=$b && break
done
[ -z "$BROWSER" ] && echo "Instale Firefox ou Chromium" && exit 1
$BROWSER --app=file:///opt/roteirista-pro/index.html --class=roteirista-pro
LAUNCHEOF

chmod +x "$INSTALL_DIR/launch.sh"
ln -sf "$INSTALL_DIR/launch.sh" "$BIN_DIR/roteirista-pro"

update-desktop-database "$APP_DIR" 2>/dev/null || true
gtk-update-icon-cache -f "$ICON_DIR" 2>/dev/null || true

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Instalação concluída com sucesso!    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Como usar:${NC}"
echo "  • Menu: Applications → Office → Roteirista Pro"
echo "  • Terminal: roteirista-pro"
echo ""
echo -e "${BLUE}Atalhos:${NC} Ctrl+N (Novo), Ctrl+S (Salvar), Ctrl+E (PDF), Ctrl+F (Buscar)"
echo ""
