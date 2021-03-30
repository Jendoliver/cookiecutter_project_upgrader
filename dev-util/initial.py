"""
Script to execute after creating the project.
- Updates PyCharm configuration if detected
-- Sets the test runner to pytest
-- Excludes cache directories
"""

import subprocess
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from pathlib import Path
from typing import cast, Dict

try:
    import yaml
except ImportError as error:
    print("Attempting to install pyyaml")
    subprocess.run(["pip", "install", "pyyaml"])
    try:
        import yaml
    except ImportError as error:
        raise Exception(
            "Could not install pyyaml automatically successfully, please install it manually first") from error


def _get_project_name():
    return cast(Path, Path.cwd()).parent.name


@dataclass
class _XmlElementData:
    tag: str
    attributes: Dict[str, str]
    identifying_attribute: str


class PyCharmConfigUpdater:

    def __init__(self):
        self.updated = False

    def update_pycharm_config(self,
                              update_testrunner_to_pytest: bool,
                              exclude_cache_and_build_directories: bool):
        project_name = _get_project_name()
        idea_project_config_file = Path("../.idea", f"{project_name}.iml")
        if idea_project_config_file.exists():
            tree = ElementTree.parse(idea_project_config_file)
            if update_testrunner_to_pytest:
                self._update_testrunner_to_pytest(tree)
            if exclude_cache_and_build_directories:
                self._exclude_cache_and_build_directories(tree)
            if self.updated:
                tree.write(idea_project_config_file, encoding="UTF-8", xml_declaration=True)
                print(f"Updated PyCharm config file {idea_project_config_file}")
            else:
                print(f"PyCharm config file {idea_project_config_file} was already correct.")
        else:
            print("No PyCharm project configuration file found.")

    def _update_testrunner_to_pytest(self, tree: ElementTree.ElementTree):
        root = tree.getroot()

        test_runner_element = self._create_or_update_element_if_necessary(root, _XmlElementData(
            tag="component",
            attributes={"name": "TestRunnerService"},
            identifying_attribute="name"
        ))
        self._create_or_update_element_if_necessary(test_runner_element, _XmlElementData(
            tag="option",
            attributes={"name": "projectConfiguration", "value": "pytest"},
            identifying_attribute="name"
        ))
        self._create_or_update_element_if_necessary(test_runner_element, _XmlElementData(
            tag="option",
            attributes={"name": "PROJECT_TEST_RUNNER", "value": "pytest"},
            identifying_attribute="name"
        ))

    def _exclude_cache_and_build_directories(self, tree: ElementTree.ElementTree):
        root = tree.getroot()

        module_root_manager_element = self._create_or_update_element_if_necessary(root, _XmlElementData(
            tag="component",
            attributes={"name": "NewModuleRootManager"},
            identifying_attribute="name"
        ))
        content_element = self._create_or_update_element_if_necessary(module_root_manager_element, _XmlElementData(
            tag="content",
            attributes={"url": "file://$MODULE_DIR$"},
            identifying_attribute="url"
        ))

        excluded_folders = [
            "file://$MODULE_DIR$/.dev",
            f"file://$MODULE_DIR$/{_get_project_name()}.egg-info",
        ]
        for excluded_folder in excluded_folders:
            self._create_or_update_element_if_necessary(content_element, _XmlElementData(
                tag="excludeFolder",
                attributes={"url": excluded_folder},
                identifying_attribute="url"
            ))

    def _create_or_update_element_if_necessary(self, parent: ElementTree.ElementTree,
                                               desired_xml_element: _XmlElementData) -> ElementTree.ElementTree:
        """
        Makes sure the parent has an sub element as described.
        :param parent:
        :param desired_xml_element:
        :return: relevant real XML element which may have been created or updated
        """
        identifying_attribute_value = desired_xml_element.attributes.get(desired_xml_element.identifying_attribute)
        searched_element = next(
            (element for element in parent.findall(desired_xml_element.tag)
             if element.get(desired_xml_element.identifying_attribute) == identifying_attribute_value), None)
        if searched_element is not None:
            for key, value in desired_xml_element.attributes.items():
                if searched_element.get(key) != value:
                    searched_element.set(key, value)
                    self.updated = True
            return searched_element
        else:
            new_element = ElementTree.SubElement(parent, desired_xml_element.tag, desired_xml_element.attributes)
            self.updated = True
            return new_element


PyCharmConfigUpdater().update_pycharm_config(
    update_testrunner_to_pytest=True,
    exclude_cache_and_build_directories=True
)
