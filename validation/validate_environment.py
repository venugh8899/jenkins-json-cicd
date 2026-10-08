import json
import sys


REQUIRED_FIELDS = [
    "environment",
    "application",
    "region",
    "replicas",
    "debug"
]


def validate_file(file_path):
    print(f"\nValidating: {file_path}")

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        return False

    for field in REQUIRED_FIELDS:
        if field not in data:
            print(f"ERROR: Missing required field: {field}")
            return False

    if data["environment"] not in ["dev", "stage", "uat", "prod"]:
        print("ERROR: Invalid environment")
        return False

    if not isinstance(data["replicas"], int) or data["replicas"] < 1:
        print("ERROR: replicas must be a positive integer")
        return False

    print("Validation successful")
    return True


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python validate_environment.py <json-file>")
        sys.exit(1)

    if not validate_file(sys.argv[1]):
        sys.exit(1)
