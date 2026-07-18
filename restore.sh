#!/usr/bin/env bash
# ═══════════════════════════════════════════════════
# KaiRest POS — Restaurar base de datos desde backup
#
# Uso:
#   ./restore.sh                     # restaura el backup más reciente
#   ./restore.sh backups/archivo.dump   # restaura un backup específico
#
# Los backups se generan automáticamente cada hora en ./backups/
# (formato pg_dump -Fc) y antes de cada actualización (pre_update_*).
# ═══════════════════════════════════════════════════
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}${BOLD}🍽  KaiRest POS — Restaurar backup${NC}"
echo ""

# ── Detect compose command ──
if docker compose version &>/dev/null; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose &>/dev/null; then
  COMPOSE_CMD="docker-compose"
else
  echo -e "${RED}❌ Docker Compose no encontrado.${NC}"
  exit 1
fi

# ── Determine compose file (misma regla que update.sh) ──
if [ -d .git ] && [ -f docker-compose.yml ]; then
  COMPOSE_FILE=""
elif [ -f docker-compose.prod.yml ]; then
  COMPOSE_FILE="-f docker-compose.prod.yml"
elif [ -f docker-compose.yml ]; then
  COMPOSE_FILE=""
else
  echo -e "${RED}❌ No se encontró docker-compose.yml ni docker-compose.prod.yml${NC}"
  exit 1
fi

# ── Pick backup file ──
if [ $# -ge 1 ]; then
  DUMP="$1"
else
  DUMP=$(ls -t backups/*.dump 2>/dev/null | head -1 || true)
fi

if [ -z "${DUMP:-}" ] || [ ! -f "$DUMP" ]; then
  echo -e "${RED}❌ No se encontró ningún backup (.dump) en ./backups/${NC}"
  echo "   Uso: ./restore.sh [backups/archivo.dump]"
  exit 1
fi

SIZE=$(du -h "$DUMP" | cut -f1)
echo -e "${YELLOW}⚠️  Se restaurará:${NC} $DUMP (${SIZE})"
echo -e "${YELLOW}⚠️  ESTO REEMPLAZA TODOS LOS DATOS ACTUALES de la base.${NC}"
read -r -p "¿Continuar? (escribe SI para confirmar): " CONFIRM
if [ "$CONFIRM" != "SI" ]; then
  echo "Cancelado."
  exit 0
fi

# ── Safety backup of current state before restoring ──
echo -e "${BLUE}ℹ ${NC} Creando respaldo de seguridad del estado actual..."
mkdir -p backups
$COMPOSE_CMD $COMPOSE_FILE exec -T db pg_dump -Fc -U casaleones casaleones \
  > "backups/pre_restore_$(date +%Y%m%d_%H%M%S).dump" 2>/dev/null \
  || echo "⚠️  No se pudo respaldar el estado actual."

# ── Stop the app (keep db running) so no writes land mid-restore ──
echo -e "${BLUE}ℹ ${NC} Deteniendo la aplicación..."
$COMPOSE_CMD $COMPOSE_FILE stop web 2>&1 | tail -1

# ── Restore ──
echo -e "${BLUE}ℹ ${NC} Restaurando base de datos..."
$COMPOSE_CMD $COMPOSE_FILE exec -T db pg_restore \
  --clean --if-exists --no-owner --no-acl \
  -U casaleones -d casaleones < "$DUMP"

# ── Restart app ──
echo -e "${BLUE}ℹ ${NC} Reiniciando la aplicación..."
$COMPOSE_CMD $COMPOSE_FILE start web 2>&1 | tail -1

# ── Health check ──
PORT="${APP_PORT:-5005}"
for i in $(seq 1 60); do
  if curl -sf "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}${BOLD}✅ Backup restaurado y aplicación funcionando.${NC}"
    echo -e "${GREEN}   URL: http://localhost:${PORT}${NC}"
    exit 0
  fi
  sleep 2
  printf "."
done

echo ""
echo -e "${RED}⚠️  La app no respondió en 120s. Revisa: $COMPOSE_CMD $COMPOSE_FILE logs web${NC}"
exit 1
