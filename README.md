# 🗡️ Project Katana

*A Modern Game Automation & Benchmarking Framework*

<div align="center">

![Project Katana Logo](https://img.shields.io/badge/Project-Katana-red?style=for-the-badge&logo=windows&logoColor=white)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)

**Automate game benchmarks with precision and style**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

## 🎯 What is Project Katana?

Project Katana is a powerful, modular game automation framework designed for performance enthusiasts, overclockers, and hardware reviewers. Built with a focus on precision and reliability, Katana automates the entire benchmarking workflow - from game launch to results capture.

### 🚀 Perfect For:
- **Hardware Reviewers** - Automate consistent benchmark runs across multiple configurations
- **Overclockers** - Test stability with automated benchmark sequences  
- **Performance Engineers** - Gather reproducible performance data
- **Gaming Enthusiasts** - Compare performance across different settings

---

## ✨ Features

### 🎮 **Game Automation**
- **Steam Integration** - Automatic game detection and launching
- **Template Matching** - Visual UI automation using OpenCV
- **Workflow Engine** - YAML-based workflow definitions
- **Smart Navigation** - Handles menus, dialogs, and loading screens

### 🎯 **Template System**
- **Visual Template Capture** - Point-and-click template creation
- **Real-time Testing** - Live confidence scoring and feedback
- **Template Monitoring** - Continuous detection with logging
- **Multi-game Support** - Organized template library per game

### ⚡ **Workflow Management**
- **YAML Configuration** - Human-readable workflow definitions
- **Modular Actions** - Reusable workflow components
- **Error Handling** - Robust retry mechanisms and fallbacks
- **Live Monitoring** - Real-time workflow execution logs

### 🎨 **Modern GUI**
- **Tabbed Interface** - Organized workflow, template, and control panels
- **Real-time Feedback** - Live confidence monitoring and status updates
- **Dark Theme** - Professional appearance with modern styling
- **Progress Tracking** - Visual progress bars and status indicators

---

## 🎯 Supported Games

| Game | Status | Templates | Workflow |
|------|--------|-----------|----------|
| **Counter-Strike 2** | ✅ Full Support | Main Menu, Workshop, Benchmark Map | Complete |
| **Black Myth Wukong** | 🔄 In Progress | Settings, Graphics, Benchmark | Partial |
| **F1 24** | 📋 Planned | - | - |
| **Custom Games** | ✅ Template System | User-defined | User-defined |

---

## 📋 Requirements

### **System Requirements**
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for installation + logs/screenshots

### **Dependencies**
- **OpenCV** - Computer vision and template matching
- **PyAutoGUI** - Input automation and screen capture
- **MSS** - High-performance screen capture
- **psutil** - Process monitoring and management
- **PyYAML** - Configuration file parsing

---

## 🚀 Installation

### **Method 1: Quick Install (Windows)**
```batch
# Clone the repository
git clone https://github.com/yourusername/project-katana.git
cd project-katana

# Run the installer
scripts\install.bat

# Launch Katana
scripts\run_katana.bat
```

### **Method 2: Manual Install**
```bash
# Clone the repository
git clone https://github.com/yourusername/project-katana.git
cd project-katana

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run Katana
python katana_gui.py
```

### **Requirements.txt**
```txt
opencv-python>=4.5.0
numpy>=1.21.0
mss>=6.1.0
pyautogui>=0.9.54
psutil>=5.8.0
pyyaml>=6.0
pillow>=8.3.0
```

---

## ⚡ Quick Start

### **1. Launch Katana**
```bash
python katana_gui.py
```

### **2. Verify Installation**
1. Go to **Games & Control** tab
2. Click **"Test Components"**
3. Ensure all systems show ✅

### **3. Set Up Your First Game**
1. Click **"Refresh Games"** to detect installed games
2. Select **CS2** from the game list
3. Go to **Template Tools** tab
4. Capture your first template:
   - Click **"Capture Template"**
   - Name it `main_menu`
   - Select `CS2` as the game
   - Position CS2's main menu and wait for capture

### **4. Run Your First Workflow**
1. Return to **Games & Control** tab
2. Select **CS2** from the game list
3. Click **"Start Workflow"**
4. Watch the automation magic! ✨

---

## 📖 Documentation

### **🎯 Creating Templates**

Templates are the foundation of Katana's visual automation. They're small images of UI elements that Katana uses to navigate games.

#### **Capturing Templates:**
1. **Launch your game** and navigate to the screen you want to automate
2. **Go to Template Tools** → Click **"Capture Template"**
3. **Name your template** (e.g., `play_button`, `settings_menu`)
4. **Select the game** it belongs to
5. **Position the UI element** on screen
6. **Wait for automatic capture** (5 second countdown)

#### **Testing Templates:**
- Use **"Test Template"** to verify template detection
- **Monitor Template** for real-time confidence tracking
- Templates should achieve **80%+ confidence** for reliable automation

### **⚙️ Workflow Configuration**

Workflows are defined in YAML files located in `config/games/`. Here's a basic workflow structure:

```yaml
name: "CS2"
type: "steam"
app_id: "730"
process_name: "cs2"
startup_time: 45

workflow:
  # Launch the game
  - action: "launch_game"
  
  # Wait for main menu
  - action: "wait_for_template"
    template: "main_menu.png"
    timeout: 60
  
  # Click play button
  - action: "click_template"
    template: "play_button.png"
    timeout: 15
    move_duration: 0.8
    pre_click_delay: 0.5
    post_click_delay: 1.0
  
  # Take screenshot
  - action: "take_screenshot"
    name: "workflow_complete"
```

#### **Available Actions:**

# Project Katana - Complete Workflow Actions Reference

## 🎮 Game Control Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `launch_game` | Launch the configured game | None | None |
| `wait_for_game` | Wait for game process to start | None | `timeout` (default: 300)<br>`process_name` (override) |
| `exit_game` | Close the game process | None | `force` (default: false)<br>`process_name` (override) |

## 🎯 Template Matching Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `wait_for_template` | Wait for a UI template to appear | `template` (filename) | `timeout` (default: 300)<br>`region` [x1, y1, x2, y2]<br>`threshold` (confidence) |
| `wait_for_any_template` | Wait for any of multiple templates | `templates` (list) | `timeout` (default: 300)<br>`region` [x1, y1, x2, y2]<br>`threshold` (confidence) |
| `wait_for_template_disappear` | Wait for a template to disappear | `template` (filename) | `timeout` (default: 300)<br>`region` [x1, y1, x2, y2]<br>`threshold` (confidence) |
| `click_template` | Find and click on a template | `template` (filename) | `timeout` (default: 10)<br>`region` [x1, y1, x2, y2]<br>`threshold` (confidence)<br>`button` (left/right/middle)<br>`offset` [x, y]<br>`move_duration` (default: 0.5)<br>`pre_click_delay` (default: 0.3)<br>`post_click_delay` (default: 0.5) |
| `click_template_if_exists` | Click template if exists (non-blocking) | `template` (filename) | `region` [x1, y1, x2, y2]<br>`threshold` (confidence)<br>`button` (default: left)<br>`delay` (legacy)<br>`offset` [x, y] |
| `check_template` | Check if template exists | `template` (filename) | `region` [x1, y1, x2, y2]<br>`threshold` (confidence) |

## 🖱️ Input Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `press_key` | Press and release a keyboard key | `key` (key name) | `delay` (after press) |
| `hold_key` | Hold a key for specified duration | `key` (key name) | `duration` (default: 1.0) |
| `type_text` | Type a text string | `text` (string to type) | `delay` (after typing) |
| `click` | Click at specific coordinates | `x` (coordinate)<br>`y` (coordinate) | `button` (default: left)<br>`delay` (after click) |

## 📸 Screen Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `take_screenshot` | Capture a screenshot | None | `name` (filename prefix)<br>`region` [x1, y1, x2, y2] |
| `wait_for_screen_change` | Wait for significant screen change | None | `timeout` (default: 300)<br>`region` [x1, y1, x2, y2]<br>`threshold` (default: 0.95) |

## ⏱️ Timing & Flow Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `wait` | Wait for specified time | None | `seconds` (default: 1) |
| `log_message` | Log message with timestamp | None | `message` (default: LOG_MESSAGE) |
| `retry_action` | Retry a sub-action multiple times | `action_to_retry` (sub-action) | `max_retries` (default: 3)<br>`retry_delay` (default: 1) |

## 🔧 Global Parameters

These parameters can be applied to **any action**:

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `optional` | If true, failure won't stop workflow | false |
| `step_delay` | Delay after this step completes | 0 |

## 📋 Common Key Names

For `press_key` and `hold_key` actions:

| Key Category | Available Keys |
|--------------|----------------|
| **Letters** | a-z |
| **Numbers** | 0-9 |
| **Function Keys** | f1-f12 |
| **Navigation** | up, down, left, right, home, end, pageup, pagedown |
| **Modifiers** | shift, ctrl, alt, cmd |
| **Special** | space, enter, return, tab, backspace, delete, escape |
| **Symbols** | comma, period, slash, backslash, semicolon, quote |

## 📋 Mouse Button Options

For `click_template`, `click_template_if_exists`, and `click` actions:

| Button | Description |
|--------|-------------|
| `left` | Left mouse button (default) |
| `right` | Right mouse button |
| `middle` | Middle mouse button/scroll wheel |

## 📝 Example Usage

```yaml
workflow:
  # Game Control
  - action: "launch_game"
  
  # Template Matching with Enhanced Timing
  - action: "click_template"
    template: "play_button.png"
    timeout: 15
    move_duration: 0.8
    pre_click_delay: 0.5
    post_click_delay: 1.0
    optional: false
  
  # Input Actions
  - action: "press_key"
    key: "escape"
    delay: 2
  
  # Screen Capture
  - action: "take_screenshot"
    name: "benchmark_results"
  
  # Timing
  - action: "log_message"
    message: "BENCHMARK_START_TIME"
  
  - action: "wait"
    seconds: 180
    step_delay: 1
```

## 💡 Pro Tips

1. **Use `optional: true`** for unstable UI elements that might not always appear
2. **Adjust timing parameters** (`move_duration`, `pre_click_delay`, `post_click_delay`) for slower systems
3. **Use `log_message`** with specific markers for automated benchmark timing analysis
4. **Combine `check_template`** with conditional logic for dynamic workflows
5. **Use `retry_action`** for unreliable network-dependent operations

| Action | Description | Parameters |
|--------|-------------|------------|
| `launch_game` | Launch the game | - |
| `wait_for_template` | Wait for template to appear | `template`, `timeout`, `region` |
| `click_template` | Click on template | `template`, `timeout`, `move_duration` |
| `press_key` | Press keyboard key | `key`, `delay` |
| `type_text` | Type text string | `text`, `delay` |
| `take_screenshot` | Capture screenshot | `name` |
| `wait` | Wait for specified time | `seconds` |

### **🎮 Adding New Games**

1. **Create game configuration:**
   ```yaml
   # config/games/mygame.yaml
   name: "My Game"
   type: "steam"  # or "epic", "other"
   app_id: "12345"
   exe_name: "mygame.exe"
   process_name: "mygame"
   startup_time: 30
   
   workflow:
     - action: "launch_game"
     # Add your workflow steps
   ```

2. **Capture templates:**
   - Create `templates/screens/mygame/` directory
   - Capture UI elements as PNG files
   - Test templates for reliability

3. **Test and refine:**
   - Start with simple workflows
   - Add error handling and retries
   - Use `optional: true` for unstable elements

---

## ⚙️ Configuration

### **Global Settings** (`config/settings.yaml`)
```yaml
# Steam Configuration
steam_path: 'C:/Program Files (x86)/Steam'

# Mouse Timing (adjust for your system)
mouse_move_duration: 0.6    # Mouse movement speed
pre_click_delay: 0.4        # Delay before clicking
post_click_delay: 0.8       # Delay after clicking

# Template Matching
template_matching_threshold: 0.8  # Detection confidence
timeout: 300                      # Default action timeout

# Output
screenshot_dir: 'output/screenshots'
log_level: 'INFO'
```

### **Advanced Mouse Timing**

Fine-tune clicking behavior for your system:

| Setting | Fast PC | Slow PC | Description |
|---------|---------|---------|-------------|
| `mouse_move_duration` | 0.3 | 1.0 | Mouse movement time |
| `pre_click_delay` | 0.2 | 0.6 | Wait before clicking |
| `post_click_delay` | 0.5 | 1.2 | Wait after clicking |

---

## 🎯 Template Monitoring

The **Monitor Template** feature is perfect for detecting dynamic game states:

### **Use Cases:**
- **Benchmark Detection** - Know exactly when benchmarks start/end
- **Loading Screens** - Wait for loading to complete
- **Dynamic UI** - Track changing game states
- **Performance Testing** - Measure UI responsiveness

### **How to Use:**
1. **Select template** to monitor
2. **Configure parameters:**
   - **Poll Interval**: How often to check (0.5-5 seconds)
   - **Duration**: How long to monitor (10-300 seconds)
   - **Threshold**: Detection confidence (0.1-1.0)
3. **Enable Alt+Tab** to switch to game
4. **Watch real-time confidence** and detection log

---

## 🛠️ Troubleshooting

### **Common Issues:**

#### **🎮 Game Not Detected**
```
Problem: Game doesn't appear in game list
Solutions:
✅ Click "Refresh Games"
✅ Check Steam path in settings.yaml
✅ Verify game is installed
✅ Check game configuration file exists
```

#### **🎯 Template Not Matching**
```
Problem: Template confidence is low (<80%)
Solutions:
✅ Recapture template at current resolution
✅ Crop template to just the UI element
✅ Test on different game screens
✅ Lower threshold in workflow (temporary)
```

#### **🖱️ Clicks Too Fast**
```
Problem: Clicks happening too quickly
Solutions:
✅ Increase mouse timing in settings.yaml
✅ Add delays in workflow YAML
✅ Use move_duration, pre_click_delay, post_click_delay
```

#### **⚡ Workflow Fails**
```
Problem: Workflow stops with errors
Solutions:
✅ Check template paths and file names
✅ Verify game is running and focused
✅ Use optional: true for unstable steps
✅ Add retry mechanisms
✅ Check workflow logs for specific errors
```

### **Debug Mode:**
Enable detailed logging by setting `log_level: DEBUG` in settings.yaml.

---

## 🏗️ Project Structure

```
project_katana/
├── 📁 katana/                 # Core framework
│   ├── 📁 core/              # Main modules
│   │   ├── game_finder.py    # Game detection
│   │   ├── game_controller.py # Game launching
│   │   ├── screen_analyzer.py # Template matching
│   │   ├── input_simulator.py # Mouse/keyboard
│   │   └── workflow_engine.py # Workflow execution
│   └── 📁 utils/             # Utilities
├── 📁 config/                # Configuration
│   ├── 📁 games/            # Game definitions
│   └── settings.yaml        # Global settings
├── 📁 templates/            # Template library
│   └── 📁 screens/          # Screen templates
├── 📁 output/               # Results
│   ├── 📁 logs/            # Execution logs
│   └── 📁 screenshots/     # Captured images
├── 📁 scripts/             # Helper scripts
├── katana_gui.py           # Main application
└── requirements.txt        # Dependencies
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **🐛 Bug Reports**
1. Check existing issues
2. Include system info (OS, Python version)
3. Provide steps to reproduce
4. Attach logs and screenshots

### **✨ Feature Requests**
1. Describe the use case
2. Explain expected behavior
3. Consider implementation complexity

### **🔧 Code Contributions**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow existing code style
4. Add tests for new functionality
5. Submit pull request

### **📝 Documentation**
- Improve README sections
- Add game-specific guides
- Create video tutorials
- Update troubleshooting guides

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenCV Team** - Computer vision foundation
- **PyAutoGUI Contributors** - Input automation
- **Gaming Community** - Testing and feedback
- **Hardware Reviewers** - Real-world use cases

---

## 📞 Support

### **Getting Help:**
- 📖 **Documentation**: Check this README first
- 🐛 **Issues**: [GitHub Issues](https://github.com/YpS-YpS/project-katana/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YpS-YpS/project-katana/discussions)
- 📧 **Email**: random.satyajit@gmail.com

### **Community:**
- 🎮 **Discord**: [Project Katana Community](https://discord.gg/yourserver)
- 🐦 **Twitter**: [@ProjectKatana](https://twitter.com/ProjectKatana)
- 📹 **YouTube**: [Katana Tutorials](https://youtube.com/ProjectKatana)

---

<div align="center">

**Built with ❤️ for the gaming and hardware community**

⭐ **Star this repo** if Project Katana helped automate your benchmarks!

[⬆ Back to Top](#-project-katana)

</div>

---

*Project Katana - Slice through manual benchmarking with automated precision* 🗡️
