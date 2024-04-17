from PyQt5.QtCore import (
    Qt,
    QObject,
    pyqtSignal,
    QThread,
    QMutex,
    QMutexLocker,
    QWaitCondition,
)
from pytube import YouTube, Playlist
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
)

from PyQt5.QtGui import QFont

class DownloaderWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.tasks = []

    def add_task(self, url, resolution):
        with QMutexLocker(self.mutex):
            self.tasks.append((url, resolution))
            self.condition.wakeOne()

    def run(self):
        while True:
            with QMutexLocker(self.mutex):
                if not self.tasks:
                    self.condition.wait(self.mutex)
                if self.tasks:
                    url, resolution = self.tasks.pop(0)
                else:
                    continue

            self.finished.emit("Download Start")
            try:
                download(url, resolution)
            except Exception as e:
                print(f"Error during download: {e}")
                setStatus(f"Error during download: {e}")


def download(url, resolution):
    if "playlist" in url.lower():
        download_playlist(url, resolution)
    else:
        download_video(url, os.getcwd(), resolution)


def get_available_resolutions(video):
    return [stream.resolution for stream in video.streams if stream.resolution]


def download_playlist(playlist_url, resolution):
    try:
        i = 0
        playlist = Playlist(playlist_url)
        output_path = os.path.join(os.getcwd(), "Playlist Downloads")
        os.makedirs(output_path, exist_ok=True)
        applied_resolution = None

        z = len(playlist.video_urls)

        for video_url in playlist.video_urls:
            applied_resolution = download_video(
                video_url, output_path, applied_resolution or resolution
            )
            i = i + 1
            setStatus(str(i) + "/" + str(z))

        setStatus("Playlist Download completed")

    except Exception as e:
        print(f"Error downloading playlist: {e}")
        setStatus(f"Error downloading playlist: {e}")


def download_video(video_url, output_path, resolution):
    try:
        yt = YouTube(video_url)
        video_title = yt.title
        available_resolutions = get_available_resolutions(yt)
        if resolution and resolution not in available_resolutions:
            print("Selected resolution is unavailable for this video.")
            setStatus("Selected resolution is unavailable for this video.")
            stream = yt.streams.first()
        else:
            stream = yt.streams.filter(res=resolution).first()

        setStatus(f"Downloading video: {video_title} [{resolution}]")

        stream.download(output_path)
        setStatus("Video downloaded successfully!")
        return resolution
    except Exception as e:
        print(f"Error downloading video: {e}")
        setStatus(f"Error downloading video: {e}")


def setStatus(txt):
    st.setText("Status: " + txt)


def getDropdown():
    s = dropdown.currentText()
    print("Resolution changed:", s)
    return s


def down_btn():
    url = txt_box.text()
    resolution = getDropdown()
    worker.add_task(url, resolution)


res = ["720p", "480p", "360p", "144p"]

app = QApplication([])

main_window = QWidget()
main_window.setWindowTitle("Downloader")
main_window.resize(400, 100)

txt_box = QLineEdit()
dow = QPushButton("Download")
dropdown = QComboBox()
st = QLabel("Status: Ready")

master_layout = QVBoxLayout()
# master_layout.styleSheet("QVBoxLayout{background-color:yellow}")
# app.setStyleSheet("QVBoxLayout { background-color: #323842 ;}")
# app.setStyleSheet("""background-color:#323842;color:#ebf2ff;""")
# app.setStyleSheet("QLabel { color: #ebf2ff ;}")
# app.setStyleSheet("Qlable { background-color: #323842 ;}")

row1 = QHBoxLayout()
row1.addWidget(txt_box)
master_layout.addLayout(row1)

row2 = QHBoxLayout()
row2.addWidget(dow)
master_layout.addLayout(row2)

row3 = QHBoxLayout()
dropdown.addItems(res)
row3.addWidget(dropdown)
master_layout.addLayout(row3)

row4 = QHBoxLayout()
row4.addWidget(st)
master_layout.addLayout(row4)

main_window.setLayout(master_layout)

dow.clicked.connect(down_btn)
dropdown.currentTextChanged.connect(getDropdown)

main_window.show()

worker = DownloaderWorker()
thread = QThread()
worker.moveToThread(thread)
thread.started.connect(worker.run)
thread.start()

app.exec_()
