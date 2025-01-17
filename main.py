# -*- coding: utf_8 -*-

import os
import sys
import ctypes
from subprocess import run, CalledProcessError
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress
from rich.text import Text
from time import sleep

def is_admin():
    """检查当前是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行并关闭当前窗口"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        os._exit(0)  # 强制退出当前窗口

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_patches_folder(folder):
    """创建 Patches 文件夹并打开"""
    if not folder.exists():
        folder.mkdir()
        with open(folder / "请将需要安装的msu补丁拷贝至本文件夹中.txt", "w", encoding="utf-8") as f_cn:
            f_cn.write("请将需要安装的msu补丁拷贝至本文件夹中。")
        with open(folder / "Please copy the MSU patches you want to install into this folder.txt", "w", encoding="utf-8") as f_en:
            f_en.write("Please copy the MSU patches you want to install into this folder.")
    # 打开文件夹
    if folder.exists():
        run(f'explorer "{folder}"', shell=True)

def move_to_done(file, done_folder):
    """将文件移动到 Done 文件夹"""
    done_folder.mkdir(exist_ok=True)
    file.rename(done_folder / file.name)

def log_error(log_file, idx, patch_file, error_message):
    """记录错误信息到日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{idx}] {timestamp} - {patch_file.name} - {error_message}\n")
        
def set_console_width(width):
    """设置控制台窗口宽度"""
    if os.name == 'nt':
        os.system(f'mode con: cols={width}')

def install_patch(patch_file, idx, log_file, progress, task_id, console):
    """安装单个补丁"""
    try:
        progress.update(task_id, description=f"Installing {patch_file.name}")
        result = run(["dism", "/online", "/add-package", f"/packagepath:{patch_file}"], check=True)
        progress.update(task_id, advance=1)
        console.print(f"[green]⚪ {idx}: {patch_file.name} - Successfully installed.[/green]", highlight=False)
        return True
    except CalledProcessError as e:
        error_message = str(e)
        if "Error: 0x800f081e" in error_message:
            detailed_error = f"错误: 此补丁不适用于当前系统 | Error: This patch is not applicable to the current system."
        elif "Error: 0x800f0922" in error_message:
            detailed_error = f"错误: 补丁无法安装，可能是系统组件问题 | Error: Patch could not be installed, possible system component issue."
        elif "Error: 0x80070002" in error_message:
            detailed_error = f"错误: 找不到指定文件 | Error: The specified file was not found."
        elif "Error: 0x80073701" in error_message:
            detailed_error = f"错误: 某些组件无法安装 | Error: Some components could not be installed."
        elif e.returncode == 50:  # 检查 DISM 返回码
            detailed_error = f"错误: 补丁已安装 | Error: The patch is already installed."
        else:
            detailed_error = f"未知错误 | Unknown error: {error_message}"

        console.print(f"[red]⚪ {idx}: {patch_file.name} - {detailed_error}[/red]", highlight=False)
        log_error(log_file, idx, patch_file, detailed_error)
        progress.update(task_id, advance=1)
        return False
    


def display_logo(console):
    """展示Logo，并增加逐行扫描效果"""
    logo_lines = r"""
    
    
 ____   ___  ______   ___ __  __ ____   ___  ______   ___ __  __ __ __  __  __  ______  ___  __    __     ____ ____ 
 || )) // \\ | || |  //   ||  || || \\ // \\ | || |  //   ||  || || ||\ || (( \ | || | // \\ ||    ||    ||    || \\
 ||=)  ||=||   ||   ((    ||==|| ||_// ||=||   ||   ((    ||==|| || ||\\||  \\    ||   ||=|| ||    ||    ||==  ||_//
 ||_)) || ||   ||    \\__ ||  || ||    || ||   ||    \\__ ||  || || || \|| \_))   ||   || || ||__| ||__| ||___ || \\
                                                                                                                    
                                                                             v₁.₀₀
MSU Batch Patch Installer
Windows MSU补丁文件快速安装工具
                                                 
 """.splitlines()
    for line in logo_lines:
        console.print(line, style="bold")
        sleep(0.2)  # 模拟逐行加载的效果

def main():
    console = Console()
    if os.name != 'nt':
        sys.exit("此脚本仅能在 Windows 上运行 | This script can only be run on Windows.")

    run_as_admin()
    set_console_width(150)  # 设置控制台宽度为 150
    clear_screen()

    patches_folder = Path("C:/Patches")
    done_folder = patches_folder / "Done"
    log_folder = patches_folder / "Log"

    # 确保 Patches 文件夹已创建
    create_patches_folder(patches_folder)

    # 确保 Log 文件夹存在
    log_folder.mkdir(exist_ok=True)

    log_file = log_folder / f"Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    while True:
        clear_screen()
        display_logo(console)
        print("\n1: 安装 | Installation\n2: 打开 Patches 目录 | Open Patches folder\n0: 退出 | Exit")
        choice = input("\n请输入选择 | Enter your choice: ")
        if choice == "0":
            sys.exit("退出中... | Exiting...")
        elif choice == "1":
            clear_screen()
            patches = list(patches_folder.glob("*.msu"))

            if not patches:
                console.print("[bold red]未找到 MSU 文件，请将文件拷贝到文件夹中 | No MSU files found. Please copy the files into the folder.[/bold red]")
                input("按回车键继续... | Press Enter to continue...")
                continue

            console.print("[bold cyan]以下补丁将被安装 | The following patches will be installed:[/bold cyan]")
            for idx, patch in enumerate(patches, start=1):
                console.print(f"{idx}. {patch.name}")

            while True:
                start_choice = input("按回车键开始安装，或按 0 返回主菜单... | Press Enter to start installation, or press 0 to return to the main menu: ")
                if start_choice == "0":
                    break
                elif start_choice == "":
                    with Progress() as progress:
                        task_id = progress.add_task("Installing patches", total=len(patches))
                        for idx, patch in enumerate(patches, start=1):
                            if install_patch(patch, idx, log_file, progress, task_id, console):
                                move_to_done(patch, done_folder)

                    console.print("[bold green]安装完成 | Installation complete.[/bold green]", highlight=False)
                    if log_file.exists() and log_file.stat().st_size > 0:
                        run(f'notepad "{log_file}"', shell=True)
                    run(f'explorer "{patches_folder}"', shell=True)
                    break
                else:
                    console.print("[bold red]无效输入，请重试 | Invalid input, please try again.[/bold red]")
        elif choice == "2":
            run(f'explorer "{patches_folder}"', shell=True)
        else:
            console.print("[bold red]无效输入，请重试 | Invalid input, please try again.[/bold red]")

if __name__ == "__main__":
    main()
