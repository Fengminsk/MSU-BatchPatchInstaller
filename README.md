
## **适用于 Windows 的 MSU 系统补丁批量安装工具**  
## **Batch Installer for Windows MSU System Updates**  
*为便捷运维开荒提供帮助*  
*Designed to streamline system setup and maintenance*

---

### **开发环境 | Development Environment**  
- 基于 **Python 3.9.13 (64-bit)** 开发编译  
- Developed and compiled using **Python 3.9.13 (64-bit)**  

---

### **打包命令 | Packaging Command**  
```bash
pyinstaller --onefile --exclude-module tkinter --icon=logo.png --name=MSU-BatchPatchInstaller main.py
```
- **说明 | Note**:  
  使用 PyInstaller 将 Python 脚本打包为单个可执行文件。  
  Use PyInstaller to package the Python script into a single executable file.

---

### **UPX 压缩命令 | UPX Compression Command**  
```bash
upx --best --lzma --force MSU-BatchPatchInstaller.exe
```
- **说明 | Note**:  
  使用 UPX 对打包后的可执行文件进行高效压缩，减少文件体积。  
  Use UPX to compress the packaged executable for reduced file size.

---
