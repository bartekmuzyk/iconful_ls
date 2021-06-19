# iconful_ls
An `ls` alternative for directory listings with icons and colors.

# Usage
```bash
python main.py [PATH]
```
If `PATH` is not given, the program will list the current directory.

# Recommended installation method
If you want to create an executable, follow the steps in the *Building from source* section below.

# Building from source
**This is not a recommended installation method, as the compiled executable is significantly slower. This is a limitation of `pyinstaller` and I can't do anything about it.**

### Dependencies
| Name        | Version |
|-------------|---------|
| pyinstaller | >=4.3   |

Execute the `build_and_install.sh` script.
```
chmod +x build_and_install.sh
./build_and_install.sh
```
