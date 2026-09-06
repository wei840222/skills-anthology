#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# AI Agent Skills Synchronization Script (sync.py)
# Description: Scans README.md for skill paths and symlinks them to target directory.
#              Supports interactive checkbox selection with Space key.
# ==============================================================================

import os
import sys
import re
import shutil
import select
import termios
import tty
import unicodedata

# ANSI Color and style codes
CYAN = '\033[0;36m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'
CLEAR_LINE = '\033[2K'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'
ALT_SCREEN_ON = '\033[?1049h'
ALT_SCREEN_OFF = '\033[?1049l'
CLEAR_SCREEN = '\033[H\033[2J'

DEFAULT_TARGET = os.path.expanduser("~/.openclaw/external-skills")

def get_char_width(ch):
    """Return terminal column width of a character."""
    status = unicodedata.east_asian_width(ch)
    return 2 if status in ('W', 'F') else 1

def string_width(s):
    """Return visible terminal width of a string ignoring ANSI codes."""
    w = 0
    in_escape = False
    for ch in s:
        if ch == '\033':
            in_escape = True
            continue
        if in_escape:
            if ch == 'm':
                in_escape = False
            continue
        w += get_char_width(ch)
    return w

def truncate_string(s, max_width):
    """Truncate a string to fit within max_width terminal columns."""
    if max_width <= 0:
        return ""
    cur_width = 0
    res = []
    for ch in s:
        w = get_char_width(ch)
        if cur_width + w > max_width:
            break
        res.append(ch)
        cur_width += w
    return "".join(res)

def parse_readme(repo_root):
    """Parse README.md to extract all skills with metadata."""
    readme_path = os.path.join(repo_root, "README.md")
    if not os.path.exists(readme_path):
        print(f"{RED}錯誤：在 {repo_root} 中找不到 README.md！{RESET}")
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_category = "其他"
    skills = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### "):
            current_category = stripped[4:].strip()
        elif stripped.startswith("|") and "`" in stripped:
            parts = [p.strip() for p in stripped.split("|")]
            if len(parts) >= 4:
                name_m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", parts[1])
                path_m = re.search(r"`([^`]+)`", parts[2])
                desc = parts[3].strip()
                if name_m and path_m:
                    s_name = name_m.group(1)
                    s_url = name_m.group(2)
                    s_path = path_m.group(1)
                    abs_p = os.path.join(repo_root, s_path)
                    if os.path.exists(abs_p):
                        skills.append({
                            "name": s_name,
                            "url": s_url,
                            "path": s_path,
                            "desc": desc,
                            "category": current_category
                        })

    return skills

def read_key(fd):
    """Read a single keypress or ANSI escape sequence from stdin."""
    ch = sys.stdin.read(1)
    if ch == '\x1b':
        # Check if there are following characters
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        if r:
            ch2 = sys.stdin.read(1)
            if ch2 in ('[', 'O'):
                ch3 = sys.stdin.read(1)
                if ch3 in ('1', '2', '3', '4', '5', '6', '7', '8'):
                    ch4 = sys.stdin.read(1)  # e.g. ~
                    return '\x1b' + ch2 + ch3 + ch4
                return '\x1b' + ch2 + ch3
            return '\x1b' + ch2
        return 'ESC'
    return ch

def interactive_checkbox_selector(skills):
    """
    Interactive TUI allowing users to toggle checkboxes with Space key,
    navigate with arrow keys, select all with 'a', and confirm with Enter.
    """
    if not sys.stdin.isatty():
        # Non-interactive fallback: select all
        return skills

    # Initial state: all selected by default
    selected_indices = set(range(len(skills)))
    cursor_idx = 0
    top_idx = 0

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    # Enter alternate screen buffer & hide cursor
    sys.stdout.write(ALT_SCREEN_ON + HIDE_CURSOR)
    sys.stdout.flush()

    try:
        tty.setraw(fd)

        while True:
            # Determine terminal dimensions
            term_size = shutil.get_terminal_size((80, 24))
            cols = term_size.columns
            rows = term_size.lines

            # Layout allocation:
            # Header: 4 lines
            # Details box: 5 lines
            # Footer: 2 lines
            # Separator / padding: 3 lines
            reserved_lines = 14
            viewport_size = max(5, rows - reserved_lines)

            # Adjust scroll viewport
            if cursor_idx < top_idx:
                top_idx = cursor_idx
            elif cursor_idx >= top_idx + viewport_size:
                top_idx = cursor_idx - viewport_size + 1

            # Prepare rendering buffer
            buf = [CLEAR_SCREEN]

            # Header
            header_title = " AI Agent Skills 互動勾選清單 (按 Space 勾選) "
            sep_line = "=" * min(cols, 80)
            buf.append(f"{CYAN}{BOLD}{header_title.center(min(cols, 80), '=')}{RESET}\r\n")
            buf.append(f"  {BOLD}操作指南：{RESET} [↑/↓ 或 j/k] 移動 | [空白鍵 Space] 勾選/取消 | [a] 全選/全取消\r\n")
            buf.append(f"            [i] 反選 | [Enter] 確認並開始同步 | [q / Esc] 取消並退出\r\n")
            buf.append(f"{DIM}{'-' * min(cols, 80)}{RESET}\r\n")

            # Scroll up indicator
            if top_idx > 0:
                buf.append(f"{YELLOW}{BOLD}    ▲ 向上滾動以查看更多 ({top_idx} 個技能)...{RESET}\r\n")
            else:
                buf.append("\r\n")

            # Skills list in viewport
            end_idx = min(len(skills), top_idx + viewport_size)
            for i in range(top_idx, end_idx):
                item = skills[i]
                is_cursor = (i == cursor_idx)
                is_checked = (i in selected_indices)

                # Cursor icon
                cursor_str = f"{YELLOW}{BOLD}➜{RESET} " if is_cursor else "  "

                # Checkbox
                if is_checked:
                    check_str = f"{GREEN}{BOLD}[✔]{RESET}"
                else:
                    check_str = f"{DIM}[ ]{RESET}"

                # Category badge
                cat_str = f"{CYAN}[{item['category']}]{RESET}"

                # Skill Name
                if is_cursor:
                    name_str = f"{BOLD}{YELLOW}{item['name']}{RESET}"
                else:
                    name_str = f"{BOLD}{item['name']}{RESET}"

                idx_str = f"{i + 1:2d}."
                line_content = f"{cursor_str}{check_str} {idx_str} {cat_str} {name_str}"
                buf.append(f"{line_content}\r\n")

            # Fill empty viewport lines if needed
            for _ in range(end_idx - top_idx, viewport_size):
                buf.append("\r\n")

            # Scroll down indicator
            remaining = len(skills) - end_idx
            if remaining > 0:
                buf.append(f"{YELLOW}{BOLD}    ▼ 向下滾動以查看更多 ({remaining} 個技能)...{RESET}\r\n")
            else:
                buf.append("\r\n")

            # Detail box for focused item
            cur_item = skills[cursor_idx]
            buf.append(f"{DIM}{'-' * min(cols, 80)}{RESET}\r\n")
            buf.append(f"{BOLD}【當前技能: {YELLOW}{cur_item['name']}{RESET}{BOLD}】{RESET} {DIM}({cur_item['url']}){RESET}\r\n")
            buf.append(f"  {CYAN}檔案路徑:{RESET} {cur_item['path']}\r\n")

            # Truncate description to fit terminal width
            desc_text = cur_item['desc']
            desc_prefix = f"  {CYAN}技能說明:{RESET} "
            avail_width = max(20, cols - string_width(desc_prefix) - 2)
            if string_width(desc_text) > avail_width:
                desc_text = truncate_string(desc_text, avail_width - 3) + "..."
            buf.append(f"{desc_prefix}{desc_text}\r\n")
            buf.append(f"{DIM}{'=' * min(cols, 80)}{RESET}\r\n")

            # Status footer
            status_text = f"已勾選: {len(selected_indices)} / {len(skills)} 個技能"
            buf.append(f" {GREEN}{BOLD}{status_text}{RESET}   {DIM}[Enter 確認 / q 離開]{RESET}\r\n")

            # Output to screen
            sys.stdout.write("".join(buf))
            sys.stdout.flush()

            # Read user input
            key = read_key(fd)

            if key in ('q', 'Q', 'ESC', '\x03'):  # Cancel
                return None
            elif key in ('\r', '\n'):  # Confirm Enter
                break
            elif key == ' ':  # Space - toggle selection
                if cursor_idx in selected_indices:
                    selected_indices.remove(cursor_idx)
                else:
                    selected_indices.add(cursor_idx)
            elif key in ('a', 'A'):  # Toggle select all
                if len(selected_indices) == len(skills):
                    selected_indices.clear()
                else:
                    selected_indices = set(range(len(skills)))
            elif key in ('i', 'I'):  # Invert selection
                selected_indices = set(range(len(skills))) - selected_indices
            elif key in ('\x1b[A', '\x1bOA', 'k', 'K'):  # Up arrow
                cursor_idx = (cursor_idx - 1) % len(skills)
            elif key in ('\x1b[B', '\x1bOB', 'j', 'J'):  # Down arrow
                cursor_idx = (cursor_idx + 1) % len(skills)
            elif key in ('\x1b[5~',):  # Page Up
                cursor_idx = max(0, cursor_idx - viewport_size)
            elif key in ('\x1b[6~',):  # Page Down
                cursor_idx = min(len(skills) - 1, cursor_idx + viewport_size)
            elif key in ('\x1b[H', '\x1b[1~'):  # Home
                cursor_idx = 0
            elif key in ('\x1b[F', '\x1b[4~'):  # End
                cursor_idx = len(skills) - 1

    finally:
        # Restore terminal settings & exit alt screen
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.stdout.write(ALT_SCREEN_OFF + SHOW_CURSOR)
        sys.stdout.flush()

    return [skills[i] for i in sorted(selected_indices)]

def run_sync():
    # Resolve repository root
    repo_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_root)

    # Parse arguments
    cli_target = None
    force_all = False
    force_interactive = False

    for arg in sys.argv[1:]:
        if arg in ('-a', '--all'):
            force_all = True
        elif arg in ('-i', '--interactive'):
            force_interactive = True
        elif arg in ('-h', '--help'):
            print(f"{BOLD}使用方式:{RESET}")
            print(f"  ./sync.py [目標目錄] [選項]")
            print(f"\n{BOLD}選項:{RESET}")
            print(f"  -a, --all          直接同步所有技能，不詢問")
            print(f"  -i, --interactive  直接進入空白鍵勾選清單")
            print(f"  -h, --help         顯示說明訊息")
            print(f"\n{BOLD}範例:{RESET}")
            print(f"  ./sync.py")
            print(f"  ./sync.py ~/.openclaw/external-skills")
            print(f"  ./sync.py ~/.openclaw/external-skills -i")
            sys.exit(0)
        elif not arg.startswith('-'):
            cli_target = arg

    print(f"{CYAN}{BOLD}===================================================={RESET}")
    print(f"{CYAN}{BOLD}      AI Agent Skills Auto Symlink Sync Tool        {RESET}")
    print(f"{CYAN}{BOLD}===================================================={RESET}\n")

    # Step 1: Target directory configuration
    print(f"{BOLD}[Step 1/2] 設定目標目錄{RESET}")
    if cli_target:
        target_dir = os.path.expanduser(cli_target)
        print(f"  {CYAN}(已使用指令參數指定路徑){RESET}")
    else:
        try:
            user_input = input(f"Enter target directory path [Default: {YELLOW}{DEFAULT_TARGET}{RESET}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{YELLOW}操作已取消。{RESET}")
            sys.exit(0)

        target_dir = os.path.expanduser(user_input) if user_input else DEFAULT_TARGET

    os.makedirs(target_dir, exist_ok=True)
    target_dir = os.path.abspath(target_dir)
    print(f"  {GREEN}➜ 目標目錄設定為:{RESET} {BOLD}{target_dir}{RESET}\n")

    # Parse README.md
    print(f"解析 {BOLD}README.md{RESET} 獲取技能目錄清單...")
    skills = parse_readme(repo_root)
    total_skills = len(skills)
    if total_skills == 0:
        print(f"{RED}在 README.md 中找不到有效的技能目錄！{RESET}")
        sys.exit(1)

    print(f"  {GREEN}➜ 成功解析 {total_skills} 個技能目錄項目。{RESET}\n")

    # Step 2: Synchronization Mode
    selected_skills = []
    if force_all:
        selected_skills = skills
    elif force_interactive:
        selected_skills = interactive_checkbox_selector(skills)
        if selected_skills is None:
            print(f"{YELLOW}操作已取消。{RESET}")
            sys.exit(0)
    else:
        print(f"{BOLD}[Step 2/2] 選擇同步模式{RESET}")
        print(f"  1) 全部同步 (共 {total_skills} 個技能)")
        print(f"  2) 互動勾選清單 (支援方向鍵移動與空白鍵勾選)")

        try:
            mode_choice = input(f"選擇模式 [{YELLOW}1{RESET}/2] (預設: 1): ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{YELLOW}操作已取消。{RESET}")
            sys.exit(0)

        if mode_choice == "2":
            selected_skills = interactive_checkbox_selector(skills)
            if selected_skills is None:
                print(f"{YELLOW}操作已取消。{RESET}")
                sys.exit(0)
        else:
            selected_skills = skills

    selected_count = len(selected_skills)
    if selected_count == 0:
        print(f"{YELLOW}未勾選任何技能目錄，已中止操作。{RESET}")
        sys.exit(0)

    print(f"\n即將建立 {BOLD}{selected_count}{RESET} 個技能目錄的軟連結至 {BOLD}{target_dir}{RESET} ...")

    # Perform symlink installation
    print(f"\n{BOLD}正在安裝技能軟連結...{RESET}")
    success_count = 0

    for item in selected_skills:
        src = os.path.join(repo_root, item["path"])
        dest = os.path.join(target_dir, item["name"])

        # Remove existing symlink or file/directory
        if os.path.islink(dest) or os.path.exists(dest):
            if os.path.islink(dest) or os.path.isfile(dest):
                os.unlink(dest)
            elif os.path.isdir(dest):
                shutil.rmtree(dest)

        os.symlink(src, dest)
        print(f"  [{GREEN}✓{RESET}] {item['path']} {CYAN}->{RESET} {dest}")
        success_count += 1

    print(f"\n{GREEN}{BOLD}===================================================={RESET}")
    print(f"{GREEN}{BOLD}  同步完成！已成功建立/更新 {success_count} 個技能軟連結。{RESET}")
    print(f"{GREEN}{BOLD}===================================================={RESET}\n")

if __name__ == "__main__":
    try:
        run_sync()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}操作已中止。{RESET}")
        sys.exit(130)
