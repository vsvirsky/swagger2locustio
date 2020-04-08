import json
from pathlib import Path
from typing import Set, Dict

from swagger2locustio.strategy.base_strategy import BaseStrategy
from swagger2locustio.parsers.base_parser import SwaggerBaseParser
from swagger2locustio.parsers.json_parsers.swagger_v2 import SwaggerV2JsonParser


class JsonStrategy(BaseStrategy):
    def __init__(self, file_name: Path, results_path: Path, mask: Dict[str, Set[str]], strict: bool):
        super().__init__(file_name, results_path, mask, strict)

    @staticmethod
    def read_file_content(file_name: str) -> dict:
        with open(file_name) as f:
            return json.load(f)

    def get_specific_version_parser(self) -> SwaggerBaseParser:
        swagger_version = self.swagger_file_content.get("swagger")
        openapi_version = self.swagger_file_content.get("openapi")
        version = swagger_version if swagger_version else openapi_version
        if not version:
            raise ValueError("No swagger version is specified")
        version = int(version[0])
        if version == 2:
            parser = SwaggerV2JsonParser()
        elif version == 3:
            parser = ellipsis
        else:
            raise ValueError("Incorrect swagger file version")
        return parser
