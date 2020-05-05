"""Module: SwaggerV2 YAML parser"""

from copy import deepcopy
from typing import Set, Dict

from swagger2locustio.parsers.base_parser import SwaggerBaseParser


class SwaggerV2YamlParser(SwaggerBaseParser):
    """Class: SwaggerV2 YAML parser"""

    def parse_security_data(self, file_content: dict) -> dict:
        security = {}
        # print(111, file_content)
        security_definitions = file_content.get("securityDefinitions", {})
        for security_mode, security_config in security_definitions.items():
            print(222, security_config['type'])
            if security_config['type'] in ("BasicAuth", "apiKey"):
                security[security_mode] = security_config
            else:
                raise ValueError("Security type %s is not supported" % security_config['type'])
        return security

    def parse_host_data(self, file_content: dict) -> str:
        return file_content.get("host", "")

    def parse_paths_data(self, file_content: dict, mask: Dict[str, Set[str]]) -> dict:
        paths_white_list = mask["paths_white_list"]
        paths_black_list = mask["paths_black_list"]
        tags_white_list = mask["tags_white_list"]
        tags_black_list = mask["tags_black_list"]

        api_paths = {}
        paths = file_content.get("paths")
        if paths is None:
            raise ValueError("No paths is found in swagger file")
        for path, path_data in paths.items():
            valid_path_methods = {}
            if (paths_white_list and path.lower() not in paths_white_list) or (path.lower() in paths_black_list):
                continue

            for path_method, method_data in path_data.items():
                if path_method.lower() not in mask["operations_white_list"]:
                    continue
                tags = set(tag.lower() for tag in method_data.get("tags", []))
                if tags_white_list and not tags_white_list.intersection(tags) or tags_black_list.intersection(tags):
                    continue
                valid_path_methods[path_method] = {
                    "params": self._parse_params(method_data.get("parameters", [])),
                    "responses": method_data.get("responses", {}),
                }
            api_paths[path] = valid_path_methods
        return api_paths

    @staticmethod
    def _parse_params(params: dict) -> dict:
        param_data = {}
        for param in params:
            param_name = param.get("name")
            # if not param_name or not param.get("default") or not param.get("in"):
            if not param_name or not param.get("in"):
                if param.get("required"):
                    raise ValueError("Not full info about required param")
                continue
            param_data[param_name] = deepcopy(param)
        return param_data

    def parse_definitions(self, file_content: dict) -> dict:
        return {}