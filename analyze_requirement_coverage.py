#!/usr/bin/env python3

import argparse
from pathlib import Path
from json import load
from xml.etree import ElementTree
import csv


def analyze(project_info_path, test_result_path, requirements_path):
    test_to_requirement_mapping = dict()
    tested_requirements = set()
    with open(project_info_path) as json_file:
        project_info = load(json_file)
        for test in project_info["tests"]:
            requirements = []
            for attribute in test["attributes"].keys():
                if attribute.startswith(".req"):
                    requirements.append(attribute[1:])
            tested_requirements.update(requirements)
            test_to_requirement_mapping[test["name"]] = requirements

    with open(test_result_path) as xml_file:
        tree = ElementTree.parse(xml_file)
        test_result = tree.getroot()

        all_test_cases = set()
        passed_test_cases = set()
        for test in test_result.iter("testcase"):
            name = test.attrib["classname"] + "." + test.attrib["name"]
            all_test_cases.add(name)
            if test.find("skipped") is None and test.find("failure") is None:
                passed_test_cases.add(name)

    with open(requirements_path, newline="") as csv_file:
        requirements = {row[0] for row in csv.reader(csv_file)}

    not_tested_requirements = requirements - tested_requirements
    if not_tested_requirements:
        print("\nThe following requirements have not been tested:")
        for req in not_tested_requirements:
            print(f"  - {req}")

    requirements_failing_test = set()
    for test in all_test_cases - passed_test_cases:
        requirements_failing_test.update(test_to_requirement_mapping[test])
    requirements_failing_test &= requirements

    if requirements_failing_test:
        print("\nThe following requirements have failing tests:")
        for req in requirements_failing_test:
            print(f"  - {req}")

    ok = not not_tested_requirements and not requirements_failing_test

    if ok:
        print("\nFull test coverage!")

    return ok


def main():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze requirement coverage")
    parser.add_argument(
        "project_info_path",
        help="JSON file containing project information",
        type=Path,
    )
    parser.add_argument(
        "test_result_path",
        help="XML file containing test result",
        type=Path,
    )
    parser.add_argument(
        "requirements_path",
        help="CSV file containing requirements",
        type=Path,
    )

    args = parser.parse_args()

    ok = analyze(args.project_info_path, args.test_result_path, args.requirements_path)
    if not ok:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
