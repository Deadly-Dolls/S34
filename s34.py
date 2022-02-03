import os
import json
import threading
import requests

class Colors:
    def __init__(self):
        self.colors = {
            "reset" : "0",
            "red" : "31",
            "green" : "32",
            "yellow" : "33",
            "blue" : "34",
            "purple" : "35",
            "cyan" : "36",
            "white" : "37"
        }

    def get(self, color):
        if (color in self.colors.keys()):
            return (self.colors[color])
        return (self.colors["reset"])

    def build(self, color):
        return ("\033[{};{}m".format(
            self.get(color),
            1
        ))

class Logs:
    def __init__(self):
        self.colors = Colors()
        self.logs = {
            "action" : "::",
            "success" : "--",
            "error" : "--",
            "warning" : "=="
        }

    def action(self, message):
        self.render(
            self.colors.build("blue"),
            "{} {}{}".format(
                self.logs["action"],
                self.colors.build("reset"),
                message
            )
        )

    def success(self, message):
        self.render(
            self.colors.build("cyan"),
            "{} {} ".format(
                self.logs["success"],
                message
            )
        )

    def error(self, message):
        self.render(
            self.colors.build("red"),
            "{} {} ".format(
                self.logs["error"],
                message
            )
        )

    def warning(self, message):
        self.render(
            self.colors.build("yellow"),
            "{} {} ".format(
                self.logs["warning"],
                message
            )
        )

    def render(self, color, message):
        print("{}{}{}".format(
            color,
            message,
            self.colors.build("reset")
        ))


class S34:
    def __init__(self):
        self.banner = "banner"
        self.host = "https://rule34.xxx/index.php"
        self.flag = "__EMPTY__"
        self.pid = "__PID__"
        self.id = "__ID__"
        self.align = 42
        self.ids = []
        self.content = []
        self.threads = []
        self.current_album = None
        self.output = "downloads"
        self.hoster = "https://wimg.rule34.xxx"
        self.view = "{}?page=post&s=view&id={}".format(
            self.host,
            self.id
        )
        self.search = "{}?page=post&s=list&tags={}+&pid={}".format(
            self.host,
            self.flag,
            self.pid
        )
        self.tags = {
            "path" : "tags.txt",
            "content" : None
        }
        self.logs = Logs()

        self.header()
        self.load()
        self.run()

    def header(self):
        with open(self.banner, 'r') as f:
            print(f.read())

    def load(self):
        with open(self.tags["path"], 'r') as f:
            self.tags["content"] = f.read().split('\n')

    def run(self):
        url = None
        pid = 0
        tag_data = None
    
        for tag in self.tags["content"]:
            tag_data = tag.split()
            if (len(tag_data) == 2):
                self.current_album = tag_data[1]
                for i in range(0, int(tag_data[0])):
                    url = self.search.replace(self.flag, tag_data[1]).replace(self.pid, f"{pid}")
                    self.extract(url, pid)
                    self.ids = []
                    self.content = []
                    pid += self.align
            pid = 0

    def get_id(self, data):
        cleanned = ""

        if (data.startswith("id=") == True):
            for i in data:
                if (i.isdigit() == True):
                    cleanned += i
            if (cleanned not in self.ids and len(cleanned) > 0):
                # print(f"[+] id found: {cleanned}")
                self.ids.append(cleanned)

    def extract_content(self, id_page):
        url = self.view.replace(self.id, id_page)
        r = requests.get(url, timeout = 5)
        content = None

        if (r.status_code == 200):
            # print(f"[+] {id_page} authorized")
            content = r.text.split()
            for i in content:
                if (i.startswith(f"href=\"{self.hoster}") and id_page in i):
                    self.content.append(i.split('"')[1])
        else:
            self.logs.success(f"status code: {r.status_code}")

    def extract(self, url, id_page):
        r = requests.get(url, timeout = 5)
        content = None
        last_pid = None

        self.logs.action(f"extracting page: {id_page}")
        if (r.status_code == 200):
            self.logs.success(f"status code: {r.status_code}")
            content = r.text.split()
            for i in range(0, len(content)):
                self.get_id(content[i])
            self.logs.warning(f"total ids: {len(self.ids)}")
            self.logs.action(f"extracting ids content")
            for i in self.ids:
                self.extract_content(i)
            self.download()
        else:
            self.logs.error(f"status code: {r.status_code}")

    def get_file_name(self, data):
        for i in data:
            if ('?' in i):
                return (i.split('?')[0])
        return (None)

    def get_folder(self, path):
        if (os.path.isdir(f"{path}") == False):
            os.mkdir(f"{path}")

    def download_file(self, file_url):
        r = requests.get(file_url, timeout = 5)
        if (r.status_code == 200):
            informations = file_url.split('/')
            output = self.get_file_name(informations)
            self.logs.action(f"downloading: {output}")
            self.get_folder(self.output)
            if (output != None):
                self.get_folder(f"{self.output}/{self.current_album}")
                with open("{}/{}/{}".format(
                    self.output,
                    self.current_album,
                    output
                ), "wb") as f:
                    f.write(r.content)
                self.logs.success(f"downloaded: {output}")
            else:
                self.logs.error(f"fail to get file name: {informations}")
        else:
            self.logs.error(f"not authorized: {file_url}")

    def download(self):
        informations = None
        self.logs.warning(f"total content: {len(self.content)}")
        for i in range(0, len(self.content)):
            thread_download = threading.Thread(
                target = self.download_file,
                args = [self.content[i]]
            )
            thread_download.start()
            self.threads.append(thread_download)
        for thread in self.threads:
            thread.join()
            

if (__name__ == "__main__"):
    S34()
