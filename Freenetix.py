import sys
import pickle
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout,
    QWidget, QToolBar, QAction, QMessageBox, QFileDialog,
    QLineEdit, QDialog, QProgressBar, QPushButton, QLabel, QComboBox, QListWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, QFileInfo


# Configuração de idioma persistente
CONFIG_FILE = "config.pkl"


def load_config():
    try:
        with open(CONFIG_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {"language": "en"}  # Padrão: Inglês


def save_config(config):
    with open(CONFIG_FILE, "wb") as f:
        pickle.dump(config, f)

class ExtensionManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Salva o pai (Freenetix) para acessar métodos
        self.setWindowTitle(self.safe_translate("Manage Extensions", "Gerenciar Extensões"))

        # Lista de extensões
        self.extensions = self.load_extensions()

        # Layout
        self.layout = QVBoxLayout(self)

        # Botões para adicionar, remover e ativar/desativar
        self.add_button = QPushButton(self.safe_translate("Add Extension", "Adicionar Extensão"))
        self.add_button.clicked.connect(self.add_extension)
        self.layout.addWidget(self.add_button)

        self.extension_list = QListWidget(self)
        self.update_extension_list()
        self.layout.addWidget(self.extension_list)

        self.remove_button = QPushButton(self.safe_translate("Remove Selected", "Remover Selecionada"))
        self.remove_button.clicked.connect(self.remove_extension)
        self.layout.addWidget(self.remove_button)

        self.toggle_button = QPushButton(self.safe_translate("Toggle Enabled/Disabled", "Ativar/Desativar"))
        self.toggle_button.clicked.connect(self.toggle_extension)
        self.layout.addWidget(self.toggle_button)

    def safe_translate(self, en_text, pt_text):
        """Tenta usar o método de tradução do pai, ou retorna o texto padrão."""
        if self.parent and hasattr(self.parent, "translate"):
            return self.parent.translate(en_text, pt_text)
        return en_text  # Fallback para inglês se não houver pai

    def load_extensions(self):
        """Carrega extensões do arquivo."""
        try:
            with open("extensions.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_extensions(self):
        """Salva extensões no arquivo."""
        with open("extensions.json", "w") as f:
            json.dump(self.extensions, f, indent=4)

    def update_extension_list(self):
        """Atualiza a lista de extensões na interface."""
        self.extension_list.clear()
        for ext in self.extensions:
            status = "Enabled" if ext["enabled"] else "Disabled"
            self.extension_list.addItem(f'{ext["name"]} - {status}')

    def add_extension(self):
        """Permite ao usuário importar uma extensão."""
        ext_file, _ = QFileDialog.getOpenFileName(
            self,
            self.safe_translate("Select Extension", "Selecionar Extensão"),
            "",
            self.safe_translate("JSON Files (*.json)", "Arquivos JSON (*.json)")
        )
        if not ext_file:  # Verifica se o usuário cancelou
            return

        try:
            with open(ext_file, "r") as f:
                ext = json.load(f)

            # Valida os campos necessários
            if not all(key in ext for key in ["name", "script", "enabled"]):
                QMessageBox.warning(self, 
                    self.safe_translate("Invalid Extension", "Extensão Inválida"), 
                    self.safe_translate(
                        "The selected file is not a valid extension.", 
                        "O arquivo selecionado não é uma extensão válida."
                    )
                )
                return

            # Verifica se o caminho do script é válido
            if not os.path.exists(ext["script"]):
                QMessageBox.warning(self, 
                    self.safe_translate("Invalid Script Path", "Caminho do Script Inválido"), 
                    self.safe_translate(
                        "The script file path is invalid.", 
                        "O caminho do arquivo do script é inválido."
                    )
                )
                return

            # Adiciona a extensão e salva
            self.extensions.append(ext)
            self.save_extensions()
            self.update_extension_list()

        except json.JSONDecodeError:
            QMessageBox.critical(self, 
                self.safe_translate("Error", "Erro"), 
                self.safe_translate(
                    "The file is not a valid JSON.", 
                    "O arquivo não é um JSON válido."
                )
            )
        except Exception as e:
            QMessageBox.critical(self, 
                self.safe_translate("Error", "Erro"), 
                self.safe_translate(
                    f"Failed to load extension: {e}", 
                    f"Falha ao carregar a extensão: {e}"
                )
            )


    def remove_extension(self):
        """Remove a extensão selecionada."""
        selected = self.extension_list.currentRow()
        if selected != -1:
            del self.extensions[selected]
            self.save_extensions()
            self.update_extension_list()

    def toggle_extension(self):
        """Ativa ou desativa a extensão selecionada."""
        selected = self.extension_list.currentRow()
        if selected != -1:
            self.extensions[selected]["enabled"] = not self.extensions[selected]["enabled"]
            self.save_extensions()
            self.update_extension_list()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(600, 300, 300, 150)

        self.config = load_config()

        # Label para idioma
        self.language_label = QLabel("Language:", self)
        self.language_label.move(20, 20)

        # Combobox para selecionar idioma
        self.language_combo = QComboBox(self)
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Português", "pt")
        self.language_combo.move(100, 15)

        # Define o idioma atual
        current_language = self.config["language"]
        index = self.language_combo.findData(current_language)
        if index != -1:
            self.language_combo.setCurrentIndex(index)

        # Botão para salvar
        self.save_button = QPushButton("Save", self)
        self.save_button.move(100, 80)
        self.save_button.clicked.connect(self.save_settings)

    def save_settings(self):
        """Salva as configurações alteradas pelo usuário."""
        selected_language = self.language_combo.currentData()
        self.config["language"] = selected_language
        save_config(self.config)
        QMessageBox.information(self, "Settings", "Settings saved. Restart the browser to apply changes.")
        self.close()


class DownloadProgressDialog(QDialog):
    def __init__(self, download, parent=None):
        super().__init__(parent)
        self.download = download
        self.setWindowTitle("Download in Progress")
        self.setGeometry(500, 300, 300, 100)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Buttons
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_download)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        # Connect progress update
        self.download.downloadProgress.connect(self.update_progress)

    def update_progress(self, received, total):
        progress_percentage = (received / total) * 100
        self.progress_bar.setValue(progress_percentage)

    def cancel_download(self):
        self.download.cancel()
        self.close()


class BrowserTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)
        self.browser.setUrl(QUrl("https://duckduckgo.com"))

        self.browser.page().profile().downloadRequested.connect(self.on_download_requested)

    def on_download_requested(self, download):
        suggested_filename = download.url().fileName()
        download_path, _ = QFileDialog.getSaveFileName(self, "Save File", suggested_filename, "All Files (*)")
        if download_path:
            download.setPath(download_path)
            download.accept()
            self.show_download_progress(download)

    def show_download_progress(self, download):
        self.progress_dialog = DownloadProgressDialog(download, self)
        self.progress_dialog.show()


class Freenetix(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.language = self.config.get("language", "en")

        self.setWindowTitle("Freenetix")
        self.setGeometry(300, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.ico"))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)
        self.add_new_tab()

        self.create_toolbar()

    def translate(self, en_text, pt_text):
        """Tradução dinâmica com base na configuração do idioma."""
        return pt_text if self.language == "pt" else en_text

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        back_action = QAction(self.translate("Back", "Voltar"), self)
        back_action.triggered.connect(self.back)
        toolbar.addAction(back_action)

        forward_action = QAction(self.translate("Forward", "Avançar"), self)
        forward_action.triggered.connect(self.forward)
        toolbar.addAction(forward_action)

        reload_action = QAction(self.translate("Reload", "Recarregar"), self)
        reload_action.triggered.connect(self.reload)
        toolbar.addAction(reload_action)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        new_tab_action = QAction(self.translate("New Tab", "Nova Aba"), self)
        new_tab_action.triggered.connect(self.add_new_tab)
        toolbar.addAction(new_tab_action)
        
        # Botão para abrir o gerenciador de extensões
        extensions_action = QAction(self.translate("Extensions", "Extensões"), self)
        extensions_action.triggered.connect(self.open_extensions)
        toolbar.addAction(extensions_action)

        settings_action = QAction(self.translate("Settings", "Configurações"), self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

    def back(self):
        current_tab = self.tabs.currentWidget()
        if current_tab.browser.history().canGoBack():
            current_tab.browser.history().back()

    def forward(self):
        current_tab = self.tabs.currentWidget()
        if current_tab.browser.history().canGoForward():
            current_tab.browser.history().forward()

    def reload(self):
        current_tab = self.tabs.currentWidget()
        current_tab.browser.reload()

    def navigate_to_url(self):
        current_tab = self.tabs.currentWidget()
        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        current_tab.browser.setUrl(QUrl(url))

    def add_new_tab(self):
        new_tab = BrowserTab()
        index = self.tabs.addTab(new_tab, self.translate("New Tab", "Nova Aba"))
        self.tabs.setCurrentIndex(index)

        # Atualiza barra de URL e título
        new_tab.browser.urlChanged.connect(self.update_url_bar)
        new_tab.browser.titleChanged.connect(lambda title, tab=new_tab: self.update_tab_title(title, tab))

        # Injeta scripts após o carregamento da página
        new_tab.browser.loadFinished.connect(lambda _: self.inject_scripts(new_tab.browser))

    def inject_scripts(self, browser):
        """Injeta scripts das extensões ativadas."""
        extension_manager = ExtensionManager(parent=self)
        extensions = extension_manager.load_extensions()

        for ext in extensions:
            if ext["enabled"]:
                try:
                    with open(ext["script"], "r") as script_file:
                        script_content = script_file.read()
                        browser.page().runJavaScript(script_content, 
                            lambda result: print(f"Script '{ext['name']}' executed: {result}")
                        )
                except Exception as e:
                    QMessageBox.critical(self, 
                        self.translate("Error", "Erro"), 
                        self.translate(
                            f"Failed to inject script '{ext['name']}': {e}", 
                            f"Falha ao injetar o script '{ext['name']}': {e}"
                        )
                    )

    def update_url_bar(self, q):
        self.url_bar.setText(q.toString())

    def update_tab_title(self, title, tab):
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabText(index, title)

    def close_current_tab(self, index):
        """Fecha a aba atual."""
        if self.tabs.count() > 1:
            current_tab = self.tabs.widget(index)
            current_tab.browser.setUrl(QUrl("about:blank"))  # Evita travamentos ao fechar abas ativas
            self.tabs.removeTab(index)
        else:
            QMessageBox.warning(
                self,
                self.translate("Warning", "Aviso"),
                self.translate(
                    "Cannot close the last tab.", "Não é possível fechar a última aba."
                ),
            )
        
    def open_extensions(self):
        """Abre a janela de gerenciamento de extensões."""
        extension_manager = ExtensionManager(parent=self)
        extension_manager.exec_()

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Freenetix()
    window.show()
    sys.exit(app.exec_())
