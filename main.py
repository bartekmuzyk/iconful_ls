import sys
import os
import platform
from pathlib import Path
from typing import Optional, Dict, Tuple, List
import shutil

from icons import icons
from colors import TerminalStyles
import extensions as ext

terminal_size = shutil.get_terminal_size((-1, -1))
if terminal_size.lines == -1 or terminal_size.columns == -1:
    sys.exit(1)

del terminal_size

system: str = platform.system().lower()

if system == "windows":
    def is_executable(path: Path) -> bool:
        n: str = path.name.lower()
        return n.endswith(".exe") or n.endswith(".com")
elif system == "linux":
    def is_executable(path: Path) -> bool:
        return path.is_file() and os.access(path, os.X_OK)
else:
    def is_executable(path: Path):
        return False

source_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

# A list of file extensions that are the same as the icon name they are assigned
# (check spread syntax in single_extensions_icons below)
self_defining_extensions_icons = (
    "go", "bin", "ts", "js", "lua", "php", "css", "rust", "json", "md"
)

# One icon for one file type
single_extensions_icons: Dict[str, str] = {
    "apk": "android",
    "exe": "win10",
    "wim": "win-xp",
    "com": "ms-dos",
    "lnk": "internet",
    "styl": "stylus",
    "psd": "ps",
    "sln": "vs",
    "rb": "ruby",
    "txt": "text",
    "deb": "debian",
    "cs": "csharp",
    "pem": "key",
    "dmg": "apple",

    **{e: e for e in self_defining_extensions_icons}
}

# Icons for multiple extensions
extension_groups: Dict[tuple, str] = {
    ext.shell_script: "shell",
    ext.picture: "pic",
    ext.python: "python",
    ext.cpp: "cpp",
    ext.c: "c",
    ext.haskell: "haskell",
    ext.db: "db",
    ext.sound: "sound",
    ext.html: "html5",
    ext.packed: "packed",
    ext.java: "java",
    ext.image: "img",
    ext.sass: "sass"
}

# Special icons for directories with certain names
special_dirs: Dict[str, str] = {
    ".config": "config_dir",
    ".git": "git_dir",
    "node_modules": "npm_dir"
}

# Special icons for file with certain names
special_files: Dict[str, str] = {
    "Dockerfile": "tasks",
    "docker-compose.yaml": "docker",
    "docker-compose.yml": "docker",
    "package.json": "npm",
    ".bashrc": "shell",
    "vmlinuz": "linux"
}

# Extension colors mapping
# (for symlink, fifo and executable files colors check the get_styling_for_path function below)
color_filters: Dict[tuple, Tuple[str, bool]] = {
    ext.picture:
        (TerminalStyles.MAGENTA, True),

    ext.packed + ("jar", "deb"):
        (TerminalStyles.RED, True),

    ext.sound:
        (TerminalStyles.CYAN, False)
}


def get_extension_from_path(path: Path) -> Optional[str]:
    return path.name.split('.')[1].lower() if '.' in path.name else None


def get_icon_for_path(path: Path, e: Optional[str]) -> str:
    if path.is_symlink():
        return icons["symlink"]
    elif path.is_fifo():
        return icons["fifo"]
    elif path.is_dir():
        icon_name = special_dirs.get(path.name, "dir")  # Check if special directory, if not, return default icon
        return icons[icon_name]
    elif path.is_file():
        n: str = path.name

        if n in special_files:  # Check if special file
            return icons[special_files[n]]

        if e in single_extensions_icons:  # Check for single extension icon
            return icons[single_extensions_icons[e]]

        for icon_group, icon_name in extension_groups.items():  # Check for extension groups
            if e in icon_group:
                return icons[icon_name]

        return icons["empty"]  # Return default icon if none found


# (foreground: str, background: str, bold: bool, underlined: bool)
Styling = Tuple[str, str, bool, bool]


def get_styling_for_path(path: Path, extension: str) -> Styling:
    if path.is_dir():
        return (
            TerminalStyles.BLUE,
            TerminalStyles.BG_DARK_GRAY if path.is_symlink() else "",
            True,
            path.is_symlink()
        )

    if path.is_fifo():
        return (
            TerminalStyles.YELLOW,
            TerminalStyles.BG_DARK_GRAY,
            False,
            False
        )

    if is_executable(path):
        return (
            TerminalStyles.LIGHT_GREEN,
            TerminalStyles.BG_DARK_GRAY if path.is_symlink() else "",
            True,
            path.is_symlink()
        )

    for extension_rules, (fg, bold) in color_filters.items():
        if extension in extension_rules:
            return (
                fg,
                TerminalStyles.BG_DARK_GRAY if path.is_symlink() else "",
                bold,
                path.is_symlink()
            )

    return TerminalStyles.DEFAULT, TerminalStyles.BG_DEFAULT, False, False


def apply_ellipsis(source: str, max_width: int) -> str:
    if len(source) > max_width:
        return source[:max_width - 3] + "..."
    else:
        return source


def terminal_format(icon: str, styling: Styling, path_name: str, max_width: Optional[int]) -> str:
    fg, bg, bold, underlined = styling

    bold_start = TerminalStyles.BOLD if bold else ""
    underline_start = TerminalStyles.UNDERLINE if underlined else ""

    name: str
    extension: str

    if '.' in path_name:
        name, extension = path_name.split('.', 1)
    else:
        name = path_name
        extension = ""

    name_with_ellipsis: str = name

    if max_width is not None:
        room_for_name_only: int = max_width - 2

        if extension != "":
            room_for_name_only -= len(extension) + 1
            extension = '.' + extension

        name_with_ellipsis = apply_ellipsis(name, room_for_name_only)

    return f"{fg}{bg}" \
           f"{icon} " \
           f"{bold_start}{underline_start}" \
           f"{name_with_ellipsis}{extension}" \
           f"{TerminalStyles.END}"


# Prepares the final listing entry
def listing_entry(path: Path, max_width: Optional[int] = None) -> str:
    extension: str = get_extension_from_path(path)

    icon: str = get_icon_for_path(path, extension)
    styling: Styling = get_styling_for_path(path, extension)

    ret = terminal_format(icon, styling, path.name, max_width)

    if max_width is not None:
        ret += ' ' * (max_width - len(path.name) - 2)

    return ret


def slice_per(source: list, step: int) -> List[list]:
    return [(source[s:s + step]) for s in range(0, len(source), step)]


if source_path.exists():
    if source_path.is_dir():
        paths: List[Path] = sorted(source_path.iterdir(), key=lambda v: v.name.lower())

        terminal_width: int = shutil.get_terminal_size().columns
        cell_width = 20
        column_count: int = terminal_width // (cell_width + 1)

        entries: List[str] = [
            listing_entry(path, cell_width)
            for path in paths
        ]
        rows: List[List[str]] = slice_per(entries, column_count)
        for row in rows:
            for column in row:
                print(column, end=' ')
            print()
    else:
        print(listing_entry(source_path))
else:
    print(TerminalStyles.RED +
          f"Path '{source_path}' doesn't exist."
          + TerminalStyles.END)
