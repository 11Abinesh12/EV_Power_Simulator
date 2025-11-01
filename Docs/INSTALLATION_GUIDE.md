# 📥 Installation Guide - EV Power Train Simulation Tool

## 🎯 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.8 or higher
- **RAM**: 4 GB minimum
- **Disk Space**: 500 MB free space
- **Display**: 1280x720 resolution minimum

### Recommended Requirements
- **Operating System**: Windows 11 or macOS 12+
- **Python**: Version 3.10 or higher
- **RAM**: 8 GB or more
- **Disk Space**: 1 GB free space
- **Display**: 1920x1080 resolution or higher

---

## 🔧 Installation Steps

### Step 1: Install Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.10

# Verify installation
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
```

---

### Step 2: Download the Application

You should already have the project files in:
```
c:\Users\Abinesh\Downloads\EV_Simulation\
```

If not, ensure all these files are present:
- `main_app.py`
- `simulation_engine.py`
- `requirements.txt`
- `config.json`
- `run_app.bat` (Windows)
- Documentation files (*.md)

---

### Step 3: Install Dependencies

#### Option A: Using Command Prompt/Terminal (Recommended)

1. **Open Command Prompt/Terminal**
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - macOS/Linux: Open Terminal

2. **Navigate to project folder**
   ```bash
   cd c:\Users\Abinesh\Downloads\EV_Simulation
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - PyQt6 (6.6.1)
   - PyQt6-Charts (6.6.0)
   - numpy (1.26.2)
   - pandas (2.1.4)
   - matplotlib (3.8.2)
   - openpyxl (3.1.2)
   - scipy (1.11.4)

4. **Wait for installation to complete** (2-5 minutes)

#### Option B: Using Virtual Environment (Advanced)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 4: Verify Installation

Run this command to check if all packages are installed:

```bash
python -c "import PyQt6, numpy, pandas, matplotlib; print('All packages installed successfully!')"
```

Expected output:
```
All packages installed successfully!
```

If you see any errors, reinstall the missing package:
```bash
pip install [package-name] --upgrade
```

---

## 🚀 Running the Application

### Method 1: Using Batch File (Windows - Easiest)

1. Double-click `run_app.bat`
2. Application window should open

### Method 2: Using Command Line

```bash
# Navigate to project folder
cd c:\Users\Abinesh\Downloads\EV_Simulation

# Run the application
python main_app.py
```

### Method 3: Using Python IDE

1. Open `main_app.py` in your IDE (VS Code, PyCharm, etc.)
2. Run the file (F5 or Run button)

---

## ✅ First-Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] All project files present
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Application launches successfully
- [ ] Can run a simulation (click "Flat Terrain" → "Run Simulation")
- [ ] Graphs display correctly
- [ ] Can export results to CSV

---

## 🐛 Troubleshooting

### Problem 1: "Python is not recognized"

**Cause**: Python not in system PATH

**Solution**:
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH:
   - Windows: System Properties → Environment Variables → Path → Add Python folder

---

### Problem 2: "No module named 'PyQt6'"

**Cause**: PyQt6 not installed

**Solution**:
```bash
pip install PyQt6 PyQt6-Charts
```

---

### Problem 3: "ImportError: DLL load failed"

**Cause**: Missing Visual C++ redistributables (Windows)

**Solution**:
1. Download and install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Restart computer
3. Try running application again

---

### Problem 4: Application window is blank

**Cause**: Graphics driver issue or Qt platform plugin issue

**Solution**:
```bash
# Try different Qt platform
set QT_QPA_PLATFORM=windows  # Windows
export QT_QPA_PLATFORM=xcb   # Linux

# Or reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

---

### Problem 5: Plots not displaying

**Cause**: Matplotlib backend issue

**Solution**:
```bash
pip uninstall matplotlib
pip install matplotlib --upgrade
```

---

### Problem 6: "Permission denied" error

**Cause**: Insufficient permissions

**Solution**:
```bash
# Run as administrator (Windows)
# Or use --user flag
pip install -r requirements.txt --user
```

---

### Problem 7: Slow performance

**Cause**: Insufficient system resources

**Solution**:
1. Close other applications
2. Reduce simulation duration
3. Update graphics drivers
4. Check Task Manager for high CPU/memory usage

---

## 🔄 Updating the Application

### Update Python Packages

```bash
pip install -r requirements.txt --upgrade
```

### Update Specific Package

```bash
pip install [package-name] --upgrade
```

### Check Package Versions

```bash
pip list
```

---

## 🗑️ Uninstallation

### Remove Python Packages

```bash
pip uninstall PyQt6 PyQt6-Charts numpy pandas matplotlib openpyxl scipy -y
```

### Remove Virtual Environment (if used)

```bash
# Windows
rmdir /s venv

# macOS/Linux
rm -rf venv
```

### Remove Application Files

Simply delete the `EV_Simulation` folder

---

## 🌐 Platform-Specific Notes

### Windows
- Use `run_app.bat` for easy launching
- May need to allow through Windows Firewall
- Works best on Windows 10/11

### macOS
- May need to allow in Security & Privacy settings
- Use `python3` instead of `python`
- Use `pip3` instead of `pip`

### Linux
- May need to install additional Qt dependencies:
  ```bash
  sudo apt install libxcb-xinerama0 libxcb-cursor0
  ```
- Use `python3` and `pip3`

---

## 📦 Offline Installation

If you don't have internet access:

1. **Download packages on another computer**:
   ```bash
   pip download -r requirements.txt -d packages/
   ```

2. **Transfer `packages/` folder to offline computer**

3. **Install from local packages**:
   ```bash
   pip install --no-index --find-links=packages/ -r requirements.txt
   ```

---

## 🔐 Security Considerations

### Antivirus Software
- Some antivirus may flag Python scripts
- Add exception for the EV_Simulation folder
- Application does not access network or system files

### Permissions
- Application only needs read/write access to its own folder
- No admin privileges required
- No system modifications made

---

## 📊 Disk Space Breakdown

| Component | Size |
|-----------|------|
| Python packages | ~300 MB |
| Application files | ~50 KB |
| Documentation | ~100 KB |
| Sample data | ~500 KB |
| **Total** | **~300 MB** |

---

## ⚡ Performance Optimization

### For Faster Simulations
1. Use shorter durations (60-90s instead of 180s)
2. Close unnecessary applications
3. Use SSD instead of HDD
4. Ensure adequate RAM (8GB+)

### For Better Graphics
1. Update graphics drivers
2. Use dedicated GPU if available
3. Increase display resolution
4. Enable hardware acceleration

---

## 🆘 Getting Help

### If Installation Fails

1. **Check Python version**:
   ```bash
   python --version
   ```
   Should be 3.8 or higher

2. **Check pip version**:
   ```bash
   pip --version
   ```

3. **Try upgrading pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

4. **Clear pip cache**:
   ```bash
   pip cache purge
   ```

5. **Reinstall from scratch**:
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

---

## ✨ Post-Installation

### Recommended Next Steps

1. ✅ Read `QUICK_START.md` for usage guide
2. ✅ Run all three quick scenarios
3. ✅ Explore different parameters
4. ✅ Export and analyze results
5. ✅ Read `APP_README.md` for detailed documentation

### Optional Enhancements

- Create desktop shortcut to `run_app.bat`
- Pin to taskbar for quick access
- Set up virtual environment for isolation
- Configure IDE for Python development

---

## 📞 Support Resources

### Documentation
- `QUICK_START.md` - Quick start guide
- `APP_README.md` - Complete user manual
- `PROJECT_OVERVIEW.md` - Technical overview
- Code comments in `simulation_engine.py`

### Common Issues
- Check this troubleshooting section
- Review error messages carefully
- Verify all files are present
- Ensure Python version compatibility

---

## ✅ Installation Complete!

If you've reached this point successfully, you're ready to use the application!

**Next Steps**:
1. Run `python main_app.py` or double-click `run_app.bat`
2. Click "Flat Terrain (0°)"
3. Click "▶ Run Simulation"
4. Explore the results!

---

**Happy Simulating! 🚗⚡**

*Installation guide last updated: October 29, 2025*
