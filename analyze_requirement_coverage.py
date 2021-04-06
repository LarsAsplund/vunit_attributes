#!/usr/bin/env python3

import argparse
from pathlib import Path
from json import load
from junitparser import JUnitXml
import csv
from vunit.color_printer import COLOR_PRINTER


def get_project_info(project_info_path):
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

    return test_to_requirement_mapping, tested_requirements


def get_failed_test_cases(test_result_path):
    return (
        test_case.classname + "." + test_case.name
        for test_case in JUnitXml.fromfile(test_result_path)
        if test_case.result  # Absence of result indicates passed test case
    )


def get_requirements(requirements_path):
    with open(requirements_path, newline="") as csv_file:
        requirements = {row[0] for row in csv.reader(csv_file)}

    return requirements


def analyze(project_info_path, test_result_path, requirements_path):
    test_to_requirement_mapping, tested_requirements = get_project_info(
        project_info_path
    )

    requirements = get_requirements(requirements_path)
    not_tested_requirements = requirements - tested_requirements

    requirements_failing_test = set()
    for test in get_failed_test_cases(test_result_path):
        requirements_failing_test.update(test_to_requirement_mapping[test])
    requirements_failing_test &= requirements

    ok = not not_tested_requirements and not requirements_failing_test

    if ok:
        COLOR_PRINTER.write("\nRequirements coverage check passed!", fg="gi")
    else:
        if not_tested_requirements:
            COLOR_PRINTER.write("\nThe following requirements have not been tested:\n")
            for req in not_tested_requirements:
                COLOR_PRINTER.write(f"  - {req}\n")

        if requirements_failing_test:
            COLOR_PRINTER.write("\nThe following requirements have failing tests:\n")
            for req in requirements_failing_test:
                COLOR_PRINTER.write(f"  - {req}\n")

        COLOR_PRINTER.write("\nRequirements coverage check failed!", fg="ri")

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
