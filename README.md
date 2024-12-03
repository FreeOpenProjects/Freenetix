# Freenetix

**Freenetix** is a minimalist and customizable browser built with PyQt5 and Qt WebEngine. The project aims to provide a simple browsing experience with support for custom script extensions, download management, and multilingual interface (English and Portuguese).

## Features

- **Functional Browser**: Support for tabbed browsing, navigation history, reload, forward, and back actions.
- **Extension Support**: Import extensions in JSON format to inject custom JavaScript scripts into web pages.
- **Download Management**: Choose file-saving locations and track progress through a dedicated interface.
- **Multilingual Settings**: Toggle between **English** and **Portuguese**.
- **User-Friendly Interface**: URL bar, quick settings access, and simplified navigation.

---

## Screenshots

![Browser in action]![Screenshot1](https://github.com/user-attachments/assets/df45fe54-a132-49f9-b3f1-0b4b6a4c5b76)
 
*Example of a tab with a loaded website.*

![Extension manager]![Screenshot2](https://github.com/user-attachments/assets/95dab76a-c009-4aff-8c18-245089b878f5)
  
*Managing custom extensions.*

---

## Installation

### Prerequisites

Ensure you have the following installed:

- **Python 3.8 or later**
- **pip** (Python package manager)
- **PyQt5** and **Qt WebEngine**

### Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/Freenetix.git
   cd Freenetix

2. Compile to exe:

    ```bash
    python compile.py
    cd dist

3. Run the application:

    ```bash
    python Freenetix.py

### Settings

When you launch Freenetix for the first time, a config.pkl file will be created to store your language preferences.
You can access the settings interface to change the language.

### Using Extensions

Extensions are JSON files that inject JavaScript into loaded web pages.

## Example Extension:
    {
    "name": "Dark Mode Toggle",
    "enabled": true,
    "script": "scripts/dark_mode.js"
    }

### Adding Extensions:
1. Click the Extensions button in the toolbar.
2. Select a .json file containing the extension details.
3. Enable/disable extensions as needed.

### Contributing

Contributions are welcome!

1. Fork the project.
2. Create a branch for your feature or fix (git checkout -b my-feature).
3. Commit your changes (git commit -m 'Added a new feature').
4. Open a pull request.

### License
This project is licensed under the MIT License. See the LICENSE file for more details.
