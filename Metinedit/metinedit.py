from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
IMAGE_EXTENSIONS = ['.jpg', '.png', '.bmp']  # Açılacak resim uzantıları
HTML_EXTENSIONS = ['.htm', '.html', '.txt']  # Açılacak metin uzantıları


def hexuuid():
    return uuid.uuid4().hex
    # rastgele bir benzersiz kimlik tanımlayıcısı (UUID) oluşturur ve onu onaltılık (hexadecimal) formatta döndür

def splitext(p):
    return os.path.splitext(p)[1].lower()
    # bir dosya yolunun (path) uzantısını ayıklar ve daha sonra bu uzantıyı küçük harflerle döndür

class TextEdit(QTextEdit):

    def canInsertFromMimeData(self, source):

        if source.hasImage():
            return True
        else:
            return super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):

        cursor = self.textCursor() # metin düzenleyici içindeki imlecin (cursor) bulunduğu konumu alır
        document = self.document() # metin düzenleyici içindeki belgenin (document) referansını alır.

        if source.hasUrls():

            for u in source.urls():
                file_ext = splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QTextDocument.ImageResource, u, image)
                    cursor.insertImage(u.toLocalFile())
                    # insertImage() metodu kullanılarak belgede bir resim nesnesi olarak ekleme işlemi gerçekleştirilir
                else:
                    break
            else:
                return


        elif source.hasImage():
            image = source.imageData() # kaynaktaki (source) görüntü verilerini imageData() yöntemiyle elde eder.
            uuid = hexuuid() # bir benzersiz kimlik tanımlayıcısı (UUID) oluşturmak için hexuuid() fonksiyonunu çağırır.
            document.addResource(QTextDocument.ImageResource, uuid, image)
            cursor.insertImage(uuid)
            # belgedeki imlecin konumuna (cursor.insertImage()) UUID ile eklenecek olan QImage nesnesi eklenir
            return

        super(TextEdit, self).insertFromMimeData(source)
        #  belgedeki metin düzenleyicisine kaynak (source) verilerinden veri eklemek için kullanılan bir yöntemi çağırır.


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()

        # Bir TextEdit nesnesi oluşturulur ve özellikleri ayarlanır
        self.editor = TextEdit()
        self.editor.setAutoFormatting(QTextEdit.AutoAll)
        self.editor.selectionChanged.connect(self.update_format)
        font = QFont('Arial', 14)  # Varsayılan Font ve Font Size
        self.editor.setFont(font)
        self.editor.setFontPointSize(14)  # Editör Font Size

        # Pencere boyutu ayarlanır ve layout oluşturulur
        self.setGeometry(0, 0, 1200, 768)  # pencere boyutunu ayarla
        self.path = None

        # TextEdit nesnesi, layout'a eklenir
        layout.addWidget(self.editor)

        # Layout, QWidget nesnesi içine yerleştirilir ve merkezi bileşen olarak ayarlanır
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Icon Dosyası yolu ve icon seçme
        icon_path = 'images/icon.png'
        app.setWindowIcon(QIcon(icon_path))

        # Durum çubuğu oluşturulur ve ayarlanır
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Dosya araç çubuğu ve menüsü oluşturulur
        file_toolbar = QToolBar("Dosya")
        file_toolbar.setIconSize(QSize(35, 35))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        # Dosya Aç işlevi oluşturulur ve araç çubuğu/menüye eklenir
        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Dosya Aç...", self)
        open_file_action.setStatusTip("Dosya aç")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        # Dosya Kaydet işlevi oluşturulur ve araç çubuğu/menüye eklenir
        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Kaydet", self)
        save_file_action.setStatusTip("Sayfayı kaydet")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        # Dosya Farklı Kaydet işlevi oluşturulur ve araç çubuğu/menüye eklenir
        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Farklı Kaydet...", self)
        saveas_file_action.setStatusTip("Sayfayı Farklı Kaydet")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        # Dosya Yazdır işlevi oluşturulur ve araç çubuğu/menüye eklenir
        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Yazdır...", self)
        print_action.setStatusTip("Sayfayı yazdır")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        # düzenleme aracı tasarlanmasını sağlar ve geri alma, ileri alma, kesme ve kopyalama işlevleri
        edit_toolbar = QToolBar("Düzenle")
        edit_toolbar.setIconSize(QSize(35, 35))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Geri Al", self)
        undo_action.setStatusTip("Geri al")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Ileri Al", self)
        redo_action.setStatusTip("İleri al")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        # Edit menüsüne bir ayırıcı ekler.
        edit_menu.addSeparator()

        # "Kes" butonu oluşturuluyor, buton simgesi belirleniyor, kısayol tuşu atanıyor, işlevi tanımlanıyor
        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Kes", self)
        cut_action.setStatusTip("Metini kes")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        # kısayolu atar, editör nesnesinin "copy" fonksiyonuna bağlanır, ve "cut" aksiyonu gibi düzenleme araç çubuğuna ve düzen menüsüne ekle
        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Kopyala", self)
        copy_action.setStatusTip("Metini kopyala")
        cut_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        # yapıştırma işlevselliği ekleyen yapıştırma işlevselliği oluşturur ve menüye QAction nesnesini ekler.
        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Yapıştır", self)
        paste_action.setStatusTip("Yapıştır")
        cut_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        # metnin tamamını seçmek için tıklanabilir
        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Tümünü Seç", self)
        select_action.setStatusTip("Tümünü seç")
        cut_action.setShortcut(QKeySequence.SelectAll)
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        # "Metni Kaydır" işlevi ekler ve kullanıcının metin kaydırma özelliğini açıp kapatabilmesine olanak tanır.
        wrap_action = QAction(QIcon(os.path.join('images', 'arrow-continue.png')), "Metni Kaydır", self)
        wrap_action.setStatusTip("Metini kaydır")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        # Yeni bir QToolBar ve menü oluşturuluyor.
        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(35, 35))
        self.addToolBar(format_toolbar)
        format_menu = self.menuBar().addMenu("&Format")

        # yazı tipi seçildiğinde, editördeki metnin yazı tipi bu seçime göre değiştirilir.
        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.editor.setCurrentFont)
        format_toolbar.addWidget(self.fonts)

        # Fontları göster
        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])

        # widget'lar editor üzerinde font ve boyut değişikliklerini sağlama
        self.fontsize.currentIndexChanged[str].connect(lambda s: self.editor.setFontPointSize(float(s)))
        format_toolbar.addWidget(self.fontsize)

        # Kalın yazı tipi seçeneği eklenir, kullanıcı kalın yazı tipini seçip kaldırabilir.
        self.bold_action = QAction(QIcon(os.path.join('images', 'edit-bold.png')), "Kalın", self)
        self.bold_action.setStatusTip("Kalınlık")
        self.bold_action.setShortcut(QKeySequence.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.toggled.connect(lambda x: self.editor.setFontWeight(QFont.Bold if x else QFont.Normal))
        format_toolbar.addAction(self.bold_action)
        format_menu.addAction(self.bold_action)

        # Yazı editoründe italik yazı stili seçeneği eklenir
        self.italic_action = QAction(QIcon(os.path.join('images', 'edit-italic.png')), "Italik", self)
        self.italic_action.setStatusTip("İtalik")
        self.italic_action.setShortcut(QKeySequence.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.toggled.connect(self.editor.setFontItalic)
        format_toolbar.addAction(self.italic_action)
        format_menu.addAction(self.italic_action)

        # Altı çizili butonunu oluşturur ve ilgili eylemleri bağlar
        self.underline_action = QAction(QIcon(os.path.join('images', 'edit-underline.png')), "Altı Çizili", self)
        self.underline_action.setStatusTip("Altı Çizili")
        self.underline_action.setShortcut(QKeySequence.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.toggled.connect(self.editor.setFontUnderline)
        format_toolbar.addAction(self.underline_action)
        format_menu.addAction(self.underline_action)

        format_menu.addSeparator()

        # Sol Hizala eylemi oluştur ve format araç çubuğuna ve menüsüne ekle
        self.alignl_action = QAction(QIcon(os.path.join('images', 'edit-alignment.png')), "Sola Hizala", self)
        self.alignl_action.setStatusTip("Metni sola hizala")
        self.alignl_action.setCheckable(True)
        self.alignl_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignLeft))
        format_toolbar.addAction(self.alignl_action)
        format_menu.addAction(self.alignl_action)

        # Metni merkeze hizalama işlemini gerçekleştiren buton oluştur ve araç çubuğuna ekle
        self.alignc_action = QAction(QIcon(os.path.join('images', 'edit-alignment-center.png')), "Merkeze Hizala", self)
        self.alignc_action.setStatusTip("Metni merkeze hizala")
        self.alignc_action.setCheckable(True)
        self.alignc_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignCenter))
        format_toolbar.addAction(self.alignc_action)
        format_menu.addAction(self.alignc_action)

        # Metni sağa, sola veya ortaya hizalamak için araç çubuğu ve menü öğesi ekle
        self.alignr_action = QAction(QIcon(os.path.join('images', 'edit-alignment-right.png')), "Sağa Hizala", self)
        self.alignr_action.setStatusTip("Metni sağa hizala")
        self.alignr_action.setCheckable(True)
        self.alignr_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignRight))
        format_toolbar.addAction(self.alignr_action)
        format_menu.addAction(self.alignr_action)

        # Metni sığdırma için araç çubuğu ve menü öğesi ekle
        self.alignj_action = QAction(QIcon(os.path.join('images', 'edit-alignment-justify.png')), "Sığdır", self)
        self.alignj_action.setStatusTip("Metni iki yana sığdır")
        self.alignj_action.setCheckable(True)
        self.alignj_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignJustify))
        format_toolbar.addAction(self.alignj_action)
        format_menu.addAction(self.alignj_action)

        # Metin hizalama işlemlerini gruplamak için bir eylem grubu oluştur
        format_group = QActionGroup(self)
        format_group.setExclusive(True)
        format_group.addAction(self.alignl_action)
        format_group.addAction(self.alignc_action)
        format_group.addAction(self.alignr_action)
        format_group.addAction(self.alignj_action)

        format_menu.addSeparator()

        # bazı formatlama işlemlerinin araç çubuğundaki eylemlerini ve menü öğelerini içeren bir listeyi tanımlar
        self._format_actions = [
            self.fonts,
            self.fontsize,
            self.bold_action,
            self.italic_action,
            self.underline_action,
        ]

        self.update_format()
        self.update_title()
        self.show()

    def block_signals(self, objects, b):
        # Başka nesnelerin sinyallerini engelleyen bir fonksiyon.
        for o in objects:
            o.blockSignals(b)

    def update_format(self):  # Yazı biçimi ayarlarını güncelle.
        self.block_signals(self._format_actions, True)

        self.fonts.setCurrentFont(self.editor.currentFont())
        self.fontsize.setCurrentText(str(int(self.editor.fontPointSize())))

        self.italic_action.setChecked(self.editor.fontItalic())
        self.underline_action.setChecked(self.editor.fontUnderline())
        self.bold_action.setChecked(self.editor.fontWeight() == QFont.Bold)

        self.alignl_action.setChecked(self.editor.alignment() == Qt.AlignLeft)
        self.alignc_action.setChecked(self.editor.alignment() == Qt.AlignCenter)
        self.alignr_action.setChecked(self.editor.alignment() == Qt.AlignRight)
        self.alignj_action.setChecked(self.editor.alignment() == Qt.AlignJustify)

        self.block_signals(self._format_actions, False)

    def dialog_critical(self, s): # Hata mesajı için kritik bir iletişim kutusu oluştur
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self): # Seçilen dosyanın yolunu path değişkeninde sakla
        path, _ = QFileDialog.getOpenFileName(self, "Dosya aç", "",
                                              "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        try:
            with open(path, 'rU') as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.editor.setText(text)
            self.update_title()

    def file_save(self): # Dosya kaydetme işlemini gerçekleştirirken hata oluşursa hata mesajı gösteren bir fonksiyon
        if self.path is None:
            return self.file_saveas()

        text = self.editor.toHtml() if splitext(self.path) in HTML_EXTENSIONS else self.editor.toPlainText()

        try:
            with open(self.path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Dosya kaydet", "",
                                              "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        if not path:
            return

        text = self.editor.toHtml() if splitext(path) in HTML_EXTENSIONS else self.editor.toPlainText()

        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle("%sMetin Editör" % (os.path.basename(self.path) if self.path else " "))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)


# Uygulama Çalıştırma
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #.setApplicationName("WebNot")
    window = MainWindow()
    app.exec_()
