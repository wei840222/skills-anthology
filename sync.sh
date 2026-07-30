#!/usr/bin/env bash
# ==============================================================================
# AI Agent Skills Synchronization Script (sync.sh)
# Description: Automatically scans README.md for skill package paths and links
#              them directly to a specified target directory.
# ==============================================================================

set -e

# Change directory to the repository root where script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ANSI color codes for terminal formatting
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: README.md not found in $SCRIPT_DIR!${NC}"
    exit 1
fi

echo -e "${CYAN}${BOLD}====================================================${NC}"
echo -e "${CYAN}${BOLD}      AI Agent Skills Auto Symlink Sync Tool        ${NC}"
echo -e "${CYAN}${BOLD}====================================================${NC}"
echo ""

# ------------------------------------------------------------------------------
# Step 1: Target directory resolution (CLI argument or interactive prompt)
# ------------------------------------------------------------------------------
DEFAULT_TARGET="$HOME/.hermes/external-skills"

echo -e "${BOLD}[步驟 1/2] 設定目標資料夾${NC}"

if [ -n "$1" ]; then
    TARGET_INPUT="$1"
    TARGET_DIR="${TARGET_INPUT/#\~/$HOME}"
    echo -e "  ${CYAN}(使用命令列參數指定之目標路徑)${NC}"
else
    read -p "$(echo -e "請輸入目標資料夾路徑 [預設: ${YELLOW}$DEFAULT_TARGET${NC}]: ")" TARGET_INPUT

    if [ -z "$TARGET_INPUT" ]; then
        TARGET_DIR="$DEFAULT_TARGET"
    else
        # Expand tilde ~ to $HOME
        TARGET_DIR="${TARGET_INPUT/#\~/$HOME}"
    fi
fi

# Create target directory if it does not exist
mkdir -p "$TARGET_DIR"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo -e "  ${GREEN}➜ 目標資料夾已設定為:${NC} ${BOLD}$TARGET_DIR${NC}"
echo ""

# ------------------------------------------------------------------------------
# Parse README.md and extract skill directory paths
# ------------------------------------------------------------------------------
echo -e "正在解析 ${BOLD}README.md${NC} 提取技能目錄列表..."

SKILLS_JSON=$(python3 - <<'EOF'
import re, os, json, sys

readme_path = "README.md"
if not os.path.exists(readme_path):
    sys.exit(1)

with open(readme_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

repo_root = os.getcwd()
entries = []

for line in lines:
    if line.strip().startswith("|") and "`" in line:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            name_m = re.search(r"\[([^\]]+)\]", parts[1])
            path_m = re.search(r"`([^`]+)`", parts[2])
            if name_m and path_m:
                s_name = name_m.group(1)
                s_path = path_m.group(1)
                abs_p = os.path.join(repo_root, s_path)
                if os.path.exists(abs_p):
                    entries.append({"name": s_name, "path": s_path})

print(json.dumps(entries))
EOF
)

# Convert JSON to Bash array of lines: "path|name"
mapfile -t ALL_SKILLS < <(python3 -c "import json, sys; [print(f\"{e['path']}|{e['name']}\") for e in json.loads(sys.argv[1])]" "$SKILLS_JSON")

TOTAL_SKILLS=${#ALL_SKILLS[@]}
if [ "$TOTAL_SKILLS" -eq 0 ]; then
    echo -e "${RED}未在 README.md 找到任何有效的技能目錄！${NC}"
    exit 1
fi

echo -e "  ${GREEN}➜ 成功解析到 $TOTAL_SKILLS 個技能目錄項目。${NC}"
echo ""

# ------------------------------------------------------------------------------
# Step 2: Prompt user for sync mode (All vs Selective)
# ------------------------------------------------------------------------------
echo -e "${BOLD}[步驟 2/2] 請選擇同步模式${NC}"
echo "  1) 全部同步 (共 $TOTAL_SKILLS 個技能目錄)"
echo "  2) 逐個選擇 / 挑選清單"
read -p "$(echo -e "請選擇 [${YELLOW}1${NC}/2] (預設: 1): ")" MODE_CHOICE
MODE_CHOICE=${MODE_CHOICE:-1}

SELECTED_SKILLS=()

if [ "$MODE_CHOICE" -eq 1 ]; then
    SELECTED_SKILLS=("${ALL_SKILLS[@]}")
elif [ "$MODE_CHOICE" -eq 2 ]; then
    echo ""
    echo -e "${CYAN}${BOLD}------------------- 可用技能目錄清單 -------------------${NC}"
    for i in "${!ALL_SKILLS[@]}"; do
        idx=$((i + 1))
        IFS='|' read -r sk_path sk_name <<< "${ALL_SKILLS[$i]}"
        printf "  [${YELLOW}%2d${NC}] %-55s -> %s\n" "$idx" "$sk_path" "$sk_name"
    done
    echo -e "${CYAN}${BOLD}--------------------------------------------------------${NC}"
    echo -e "提示: 可輸入空格/逗號分隔的編號 (如: ${YELLOW}1 3 5${NC})、範圍 (如: ${YELLOW}1-10${NC})、或輸入 ${YELLOW}all${NC} 選取全部。"
    read -p "請輸入欲同步的技能目錄編號: " SELECTION_INPUT

    if [ "$SELECTION_INPUT" = "all" ]; then
        SELECTED_SKILLS=("${ALL_SKILLS[@]}")
    else
        # Replace commas with spaces and tokenize input
        CLEANED_INPUT="${SELECTION_INPUT//,/ }"
        read -ra TOKENS <<< "$CLEANED_INPUT"
        
        for token in "${TOKENS[@]}"; do
            if [[ "$token" =~ ^([0-9]+)-([0-9]+)$ ]]; then
                start="${BASH_REMATCH[1]}"
                end="${BASH_REMATCH[2]}"
                for ((n=start; n<=end; n++)); do
                    if [ "$n" -ge 1 ] && [ "$n" -le "$TOTAL_SKILLS" ]; then
                        SELECTED_SKILLS+=("${ALL_SKILLS[$((n-1))]}")
                    fi
                done
            elif [[ "$token" =~ ^[0-9]+$ ]]; then
                n="$token"
                if [ "$n" -ge 1 ] && [ "$n" -le "$TOTAL_SKILLS" ]; then
                    SELECTED_SKILLS+=("${ALL_SKILLS[$((n-1))]}")
                fi
            fi
        done
    fi
else
    echo -e "${RED}無效選項，取消操作。${NC}"
    exit 1
fi

# Remove duplicate selections
mapfile -t SELECTED_SKILLS < <(printf "%s\n" "${SELECTED_SKILLS[@]}" | sort -u)

SELECTED_COUNT=${#SELECTED_SKILLS[@]}
if [ "$SELECTED_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}未選擇任何技能目錄，終止操作。${NC}"
    exit 0
fi

echo ""
echo -e "即將將 ${BOLD}$SELECTED_COUNT${NC} 個技能目錄建立軟連結至 ${BOLD}$TARGET_DIR${NC} ..."
read -p "$(echo -e "確認執行？ [${GREEN}Y${NC}/n]: ")" CONFIRM
CONFIRM=${CONFIRM:-Y}

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消操作。${NC}"
    exit 0
fi

# ------------------------------------------------------------------------------
# Install selected skills (symlink)
# ------------------------------------------------------------------------------
echo ""
echo -e "${BOLD}開始安裝技能...${NC}"

SUCCESS_COUNT=0
REPO_PWD="$(pwd)"

for item in "${SELECTED_SKILLS[@]}"; do
    IFS='|' read -r sk_path sk_name <<< "$item"
    SRC="$REPO_PWD/$sk_path"
    DEST="$TARGET_DIR/$sk_name"
    
    # Remove existing link/file to prevent dereferencing into target directory
    rm -rf "$DEST"
    
    # Standard symlink installation for all skills
    ln -sfn "$SRC" "$DEST"
    echo -e "  [${GREEN}✓${NC}] $sk_path ${CYAN}->${NC} $DEST"
    
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
done

echo ""
echo -e "${GREEN}${BOLD}====================================================${NC}"
echo -e "${GREEN}${BOLD}  同步完成！共成功建立/更新 $SUCCESS_COUNT 個技能目錄軟連結。 ${NC}"
echo -e "${GREEN}${BOLD}====================================================${NC}"
