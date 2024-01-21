# Simple VECO CPU Miner with GUI

This is a simple CPU miner for VECO with a user-friendly graphical interface.

## Download

Download the latest version [here](https://github.com/vecocoin/GPU-miner/releases/).

## Guide

1. Download the latest release.
2. Unpack the zip file.
3. Run "VECO_gui_miner.exe" to start the GUI miner.
4. Fill in the required fields and click the "Mine" button.

## Important Note

Miner programs are often flagged as malware by antivirus programs. This is a false positive, as they are flagged simply because they are cryptocurrency miners. The source code is open for anyone to inspect. If you don't trust the software, please do not use it.

## Compiling from Source

### Dependencies

- tkinter
- tkinter.font
- subprocess
- threading
- queue
- json
- re
- os

### Requirements

A suitable `cpuminer` and its associated DLL files must be located in the same root directory as the script.

### Compilation

To generate the executable, run:

```bash
pyinstaller --onefile --windowed --icon=veco.ico Main.py
