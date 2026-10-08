import json
import sys


REQUIRED_FIELDS = [
    "environment",
    "node_type",
    "min_nodes",
    "max_nodes"
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

    if data["min_nodes"] < 1:
        print("ERROR: min_nodes must be at least 1")
        return False

    if data["max_nodes"] < data["min_nodes"]:
        print("ERROR: max_nodes cannot be less than min_nodes")
        return False

    print("Validation successful")
    return True


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python validate_node.py <json-file>")
        sys.exit(1)

    if not validate_file(sys.argv[1]):
        sys.exit(1)
