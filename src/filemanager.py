import os
import re
import dotenv
import pickle

dotenv.load_dotenv()


class FileReader:
    __LOGIN_DATA_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.getenv("LOGIN_DATA_FILENAME"))
    __PROXY_DATA_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.getenv("PROXY_DATA_FILENAME"))

    __LOGIN_DATA_REGEX = r"^.{1,50}@.{3,}\.\w{2,3}:.{4,}$"
    __PROXY_DATA_REGEX = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})(:.{3,}:.{3,})?$"

    def __init__(self):
        self.__create_input_files()

    def __create_input_files(self):
        is_login_file_exists = os.path.exists(self.__LOGIN_DATA_PATH)
        is_proxy_file_exists = os.getenv("USE_PROXY") in ("true", "1") and os.path.exists(self.__PROXY_DATA_PATH)

        if not is_login_file_exists:
            open(self.__LOGIN_DATA_PATH, "a")

        if not is_proxy_file_exists:
            open(self.__PROXY_DATA_PATH, "a")

        if not is_login_file_exists or not is_proxy_file_exists:
            raise FileNotFoundError(
                "Missing input data files have been created. Fill them out and run the program again."
            )

    def __read_filedata(self, filename: str) -> list[list[str]]:
        with open(filename, "r", encoding="utf-8") as file:
            data = file.readlines()

            if not data:
                raise ValueError(f"File {filename} is empty!")

            for account in data:
                if not re.match(
                        self.__LOGIN_DATA_REGEX if filename is self.__LOGIN_DATA_PATH else self.__PROXY_DATA_REGEX,
                        account.replace("\n", "")
                ):
                    raise ValueError(f"Incorrect credentials in {filename}!")

            return [line.split(":") for line in data]

    @property
    def accounts(self):
        return self.__read_filedata(self.__LOGIN_DATA_PATH)

    @property
    def proxies(self):
        return self.__read_filedata(self.__PROXY_DATA_PATH)


class CookieDumper:
    COOKIES_DIRNAME = os.path.join(os.path.dirname(__file__), os.pardir, os.getenv("COOKIES_DIRNAME"))
    __COOKIES_LIST_PATH = os.path.join(COOKIES_DIRNAME, os.getenv("COOKIES_LIST_FILENAME"))

    def __init__(self):
        if not os.path.isdir(self.COOKIES_DIRNAME):
            os.mkdir(self.COOKIES_DIRNAME)

    def is_cookies_exist(self, dump_filename: str) -> bool:
        if not os.path.exists(self.__COOKIES_LIST_PATH):
            return False

        with open(self.__COOKIES_LIST_PATH, "r", encoding="utf-8") as cookies_list_file:
            if (
                    dump_filename in cookies_list_file.read()
                    and os.path.exists(os.path.join(self.COOKIES_DIRNAME, dump_filename))
            ):
                return True

    def dump_cookies(self, cookies: list[dict], dump_filename: str):
        with open(dump_filename, "wb") as cookies_file:
            pickle.dump(cookies, cookies_file)

        with open(self.__COOKIES_LIST_PATH, "a", encoding="utf-8") as cookies_list_file:
            cookies_list_file.write(dump_filename + "\n")
