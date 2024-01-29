import os
import random
import zipfile
import requests
import socket

from typing import Optional
from filemanager import FileReader


class ProxyServer:
    def __init__(self, ip: str, port: int, username: Optional[str], password: Optional[str]):
        self.__ip = ip
        self.__port = port
        self.__username = username
        self.__password = password

        self.__check_proxy_available()

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def port(self) -> int:
        return self.__port

    @property
    def username(self) -> str:
        return self.__username

    @property
    def password(self) -> str:
        return self.__password

    @property
    def address(self) -> str:
        return f"{self.ip}:{self.port}"

    @property
    def plugin_path(self) -> Optional[str]:
        if self.username and self.password:
            return os.path.join(ProxyRepository.PROXIES_PATH, f"{self.ip}_plugin.zip")

    def __check_proxy_available(self) -> None:
        try:
            requests.get(os.getenv("PROXY_REQUEST_URL"), proxies={
                "http": f"http://{self.address}",
                "https": f"http://{self.address}"
            })
        except requests.exceptions.ProxyError:
            raise NotAvailableProxyException(self)


class ProxyRepository:
    __PROXY_SOURCE_DIRNAME = os.getenv("PROXY_SOURCE_DIRNAME")
    __PROXY_MANIFEST_PATH = os.path.join(__PROXY_SOURCE_DIRNAME, os.getenv("PROXY_MANIFEST_FILENAME"))
    __PROXY_BACKGROUND_PATH = os.path.join(__PROXY_SOURCE_DIRNAME, os.getenv("PROXY_BACKGROUND_FILENAME"))

    PROXIES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.getenv("PROXIES_DIRNAME"))

    def __init__(self, reader: FileReader):
        self.__reader = reader
        self.__proxies: list[ProxyServer] = []
        self.__is_available = False

        socket.setdefaulttimeout(120)

        if os.getenv("USE_PROXY").lower() in ("true", "1"):
            if os.path.isdir(self.PROXIES_PATH):
                for plugin in os.listdir(self.PROXIES_PATH):
                    os.remove(plugin)
            else:
                os.mkdir(self.PROXIES_PATH)

            self.__init_proxies()
            self.__is_available = True

    @property
    def is_available(self) -> bool:
        return self.__is_available

    def __create_plugin(self, server: ProxyServer):
        with zipfile.ZipFile(server.plugin_path, "w") as zp:
            with open(self.__PROXY_MANIFEST_PATH, "r", encoding="utf-8") as manifest_file:
                zp.writestr("manifest.json", manifest_file.read())

            with open(self.__PROXY_BACKGROUND_PATH, "r", encoding="utf-8") as background_file:
                zp.writestr(
                    "background.js",
                    background_file.read() % (
                        server.ip,
                        server.port,
                        server.username,
                        server.password.replace("\n", "")
                    )
                )

    def __init_proxies(self) -> None:
        for proxy_credentials in self.__reader.proxies:
            ip = proxy_credentials[0]
            port = int(proxy_credentials[1])
            username = None if len(proxy_credentials) != 4 else proxy_credentials[2]
            password = None if len(proxy_credentials) != 4 else proxy_credentials[3]

            try:
                server = ProxyServer(ip=ip, port=port, username=username, password=password)
            except NotAvailableProxyException as error:
                print(error)
            else:
                self.__proxies.append(server)

                if not server.plugin_path:
                    continue

                self.__create_plugin(server)

        if len(self.__proxies) == 0:
            raise NoWorkingProxyServersError()

    def get_random_proxy(self) -> ProxyServer:
        return self.__proxies[random.randint(0, len(self.__proxies) - 1)]


class NotAvailableProxyException(Exception):
    def __init__(self, server: ProxyServer):
        self.__server = server

    def __str__(self):
        return f"Proxy server {self.__server.address} is not available!"


class NoWorkingProxyServersError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "There are no working proxy servers!"
