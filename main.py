from js import document
from js import alert
from pyodide.ffi import create_proxy
import webbrowser
import re
import sqlite3 as sql
from pyscript import display


class VideoHotSpot:
    player = ""
    active_video = ""
    debug = False

    def __init__(self):
        connection = sql.connect("aquarium.db")
        cursor = connection.cursor()

        rows = cursor.execute("SELECT name, species, tank_number FROM fish").fetchall()
        alert(rows)

        """
        target_fish_name = "Jamie"
        rows = cursor.execute(
            "SELECT name, species, tank_number FROM fish WHERE name = ?",
            (target_fish_name,),
        ).fetchall()
        display(rows)
        """
        cursor.close()
        connection.commit()

        self.player = document.getElementById("player")
        self.player.addEventListener("timeupdate", create_proxy(self.time_update))
        self.load_main_video()

        debugElem = document.getElementById("debug")
        if debugElem.value.upper() == "Y":
            self.debug = True
            self.init_buttons_visibility(True)

    def time_update(self, event):
        buttons = document.getElementById('video_content').getElementsByTagName('input')
        for button in buttons:
            btn_ref = button.getAttribute('_ref')
            if btn_ref == self.active_video:
                btn_title = button.getAttribute('_title')
                button.setAttribute("title", btn_title)

                btn_time_visible = button.getAttribute('_visible')
                if btn_time_visible is not None:
                    btn_time_visible = float(btn_time_visible)

                btn_time_hidden = button.getAttribute('_hidden')
                if btn_time_hidden:
                    btn_time_hidden = float(btn_time_hidden)

                btn_pause = button.getAttribute('_pause')
                if btn_time_visible is not None and btn_time_hidden is not None:
                    if btn_time_visible <= self.player.currentTime <= btn_time_hidden:
                        if not button.style.visibility == "visible":
                            button.style.visibility = "visible"
                            if btn_pause is not None:
                                self.player.pause()
                    else:
                        if not button.style.visibility == "hidden" and not self.debug:
                            button.style.visibility = "hidden"
            else:
                if not button.style.visibility == "hidden" and not self.debug:
                    button.style.visibility = "hidden"

    def click(self, event):
        event_id = event.target.getAttribute('id')
        if event_id == "video_content":
            if self.player.paused:
                self.player.play()
            else:
                self.player.pause()
        else:
            btn_url = event.target.getAttribute('_url')
            if btn_url:
                self.player.pause()
                strUrlType = self.get_url_type(btn_url)
                if strUrlType == "URL":
                    webbrowser.open(btn_url, new=0, autoraise=True)
                elif strUrlType == "VIDEO":
                    self.player.poster = ""
                    video_elem = document.getElementById(btn_url)
                    if video_elem:
                        video_url = video_elem.getAttribute('_url')
                        if video_url:
                            video_id = video_elem.getAttribute('id')
                            if video_id:
                                self.init_buttons_visibility(False)
                                self.active_video = video_id
                                self.player.src = f"./assets/videos/{video_url}"
                                self.player.play()

    @staticmethod
    def get_url_type(url):
        strRes = ""
        pattern = r'^(http|https):\/\/([\w.-]+)(\.[\w.-]+)+([\/\w\.-]*)*\/?$'
        if re.match(pattern, url):
            strRes = "URL"
        else:
            if "video_" in url:
                strRes = "VIDEO"
        return strRes

    def load_main_video(self):
        main_video = document.getElementById('video_main')
        if main_video:
            _url = main_video.getAttribute('_url')
            if _url:
                self.active_video = main_video.getAttribute('id')
                self.player.src = f"./assets/videos/{_url}"

    def init_buttons_visibility(self, bolVisible):
        if not bolVisible and self.debug:
            bolVisible = True
        buttons = document.getElementById('video_content').getElementsByTagName('input')
        for button in buttons:
            if bolVisible:
                if not button.style.visibility == "visible":
                    button.style.visibility = "visible"
            else:
                if not button.style.visibility == "hidden":
                    button.style.visibility = "hidden"


PYSCR = VideoHotSpot()
