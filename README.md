# Flash Floppy Helper

Flash Floppy Helper is a Python-based utility designed to make working with **FlashFloppy-powered Gotek drives** easier and more efficient. It provides tools for managing disk images, handling FlashFloppy configuration profiles, and streamlining common workflows used by retro computing enthusiasts.

This project is especially useful if you regularly move disk images between systems, maintain multiple FlashFloppy configurations, or want a more automated way to organize and prepare USB sticks for legacy hardware.

---

## Features

* 📁 **Disk Image Management**

  * Organize, move, and prepare disk images for FlashFloppy
  * Batch operations for common workflows
  * Utilities for handling and renaming disk images

* ⚙️ **FlashFloppy Configuration Helpers**

  * Manage and switch between multiple FF.CFG profiles
  * Store reusable configuration templates
  * Quickly deploy known-good configurations

* 🧠 **Preferences & Customization**

  * Persistent preferences via JSON
  * Configurable paths and defaults
  * Modular design for easy extension

* 🛠️ **Utility Tools**

  * Supporting scripts for disk and configuration handling
  * Shared helper functions for reuse

---

## Project Structure

```
Flash-Floppy-Helper/
├── ffhelper.py                  # Main entry point
├── ffhelper_logic.py            # Core logic
├── ffhelper_utils.py            # Shared helper functions
├── ffhelper_prefs.py            # Preferences handling
├── ffhelper_prefs.json          # User preferences storage
├── ffhelper_configurations.py   # Configuration profile handling
├── diskmanager.py               # Disk image management utilities
├── undmk.py                     # Supporting disk utility
├── configurations/              # FlashFloppy configuration templates
├── support/                     # Supporting files
└── README.md                    # This file
```

---

## Requirements

* Python 3.8+
* FlashFloppy firmware (for actual Gotek usage)

No external Python dependencies are required unless otherwise noted in the code.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/kevin143carr/Flash-Floppy-Helper.git
cd Flash-Floppy-Helper
```

Run using Python:

```bash
python3 ffhelper.py
```

(Additional CLI arguments and features may be added in future releases.)

---

## Use Cases

* Preparing USB sticks for Gotek drives
* Managing large disk image collections
* Switching between different FlashFloppy setups
* Automating repetitive retro-computing workflows

---

## Philosophy

Flash Floppy Helper is built with these principles in mind:

* 🧩 Modular design
* 🛠️ Practical retro-computing workflows
* 📦 Minimal dependencies
* 🧠 Clear and maintainable code

---

## License

MIT License

Copyright (c) 2026 Kevin Carr

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Roadmap (Proposed)

* [ ] CLI argument support
* [ ] GUI frontend
* [ ] Profile switching automation
* [ ] Disk image format conversion helpers
* [ ] USB layout validation
* [ ] FlashFloppy compatibility checks

---

## Author

**Kevin Carr**
GitHub: [https://github.com/kevin143carr](https://github.com/kevin143carr)

---

If you have ideas, feature requests, or improvements, feel free to open an issue or submit a pull request.
