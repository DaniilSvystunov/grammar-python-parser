from abc import ABC, abstractmethod
import asyncio
import json
import os
import ssl
from typing import Dict
from urllib.parse import urlparse

import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup

from constants import GrammarWebSites


class ParserBase(ABC):
    PARSER_TYPE = "html.parser"

    OUTPUT_FILE = "result.json"

    OUTPUT_EXT = ".json"

    def __init__(self):
        """Init."""
        self.target_filename = f"{self.site_domain_name}{self.OUTPUT_EXT}"

    def get_web_response(self, url: str):
        """Makes request for the website and returns the response.

        Args:
            url (str): resourse url
        """
        return requests.get(url)

    def get_bs4_response(self, url: str):
        """Get the BeautifulSoup object.

        Args:
            url (str): resourse url
        """
        return BeautifulSoup(self.get_web_response(url).content, self.PARSER_TYPE)

    def _write_json(self, data: Dict) -> None:
        """Create and fill the file by given data.

        Args:
            data (Dict): dictionary as the result data
        """
        serialized_data = json.dumps(data)

        with open(self.target_filename, "a+") as file_json:
            file_json.write(serialized_data)

    async def get_web_async_response(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url, ssl=ssl.SSLContext()) as resp:
            return resp

    async def get_bs4_async_response(self, session: aiohttp.ClientSession, url: str):
        resp = await self.get_web_async_response(session, url)
        return BeautifulSoup(await resp.content, self.PARSER_TYPE)

    def write_all(self) -> None:
        """Create and write all the data at once."""
        data = self.parse()
        with open(self.target_filename, "w+") as f:
            f.write(json.dumps(data))

    async def write_async_json(self, data):
        async with aiofiles.open(self.OUTPUT_FILE, "w+") as file_json:
            await file_json.write(data)

    @abstractmethod
    def parse(self):
        """Abstractmethod for the parser itself."""
        pass

    @classmethod
    @property
    def site_domain_name(self):
        """Extract domain from the URL."""
        return urlparse(self.URL).netloc


class ParserDictionaryCOM(ParserBase):
    """Class for parsing the content of https://www.dictionary.com/ website."""

    URL = GrammarWebSites.DICTIONARY_COM

    def parse(self) -> None:
        """Method for parsing the content of the website."""

        abc_by_letters_content = self.get_bs4_response(self.URL).find_all(
            "li", class_="W2JN1pnuwI8hO1n0WQkT"
        )

        letter_links = [
            letter_content.find("a", href=True)["href"]
            for letter_content in abc_by_letters_content
        ]

        words_dict = {}
        _counter = 0
        for letter_link in letter_links:
            pages_counter = 0
            while True:
                if pages_counter != 0:
                    letter_link = f"{letter_link}/{pages_counter}"

                letter_link_resp = self.get_bs4_response(letter_link).find_all(
                    "div", class_="sw3o2JSDU4SEB11F3dUQ"
                )

                if letter_link_resp == []:
                    break

                for nested_letter_link_resp in letter_link_resp:
                    for nested_link in nested_letter_link_resp.find_all("a", href=True):
                        value = nested_link.get_text()
                        url = nested_link["href"]
                        print(f"{_counter}:{url}")
                        _counter += 1

                        description = {}

                        word_content = self.get_bs4_response(url).find(
                            "div", class_="css-10n3ydx e1hk9ate0"
                        )

                        if not word_content:
                            continue

                        for nested_div in word_content.find_all("div"):
                            _label = nested_div.find("span", class_="luna-label italic")
                            if _label:
                                _label = _label.get_text()

                            _description = nested_div.find(
                                "span", class_="one-click-content css-nnyc96 e1q3nk1v1"
                            )
                            if _description:
                                _description = _description.get_text()

                            if _label:
                                res_descr = f"{_label}. {_description}"
                            else:
                                res_descr = _description

                            _examples = [
                                expml.get_text()
                                for expml in nested_div.find_all(
                                    "span", class_="luna-example italic"
                                )
                            ]

                            description[res_descr] = _examples

                        _res = {
                            value: {
                                "url": url,
                                "description": description,
                            }
                        }

                        words_dict.update(_res)

        return words_dict


PARSER_STORAGE = {
    ParserDictionaryCOM.site_domain_name: ParserDictionaryCOM,
}
