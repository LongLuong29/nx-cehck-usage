import os
import re
from typing import Dict, Set, List

class LicenseParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.licenses: Dict[str, Dict] = {}  # {license_product: {'qty': int, 'description': str, 'features': set()}}
        print(f"\n=== Initializing LicenseParser with file: {file_path} ===")

    def parse(self) -> None:
        """Parse the license file and extract bundle and feature information."""
        print("\n=== Starting License Parser ===")
        if not os.path.exists(self.file_path):
            print(f"ERROR: File not found: {self.file_path}")
            raise FileNotFoundError(f"License file not found: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Read {len(lines)} lines from license file")

        current_license = None

        for line in lines:
            # Loại bỏ dấu # và khoảng trắng
            line = line.lstrip("#").strip()
            if not line:
                continue

            # Tách dữ liệu bằng khoảng trắng lớn (2 spaces trở lên)
            parts = re.split(r'\s{2,}', line)

            if len(parts) == 1:  # Dòng chỉ chứa feature
                if current_license:
                    # Xử lý feature có số lượng ở đầu
                    feature_parts = parts[0].strip().split(None, 1)
                    if len(feature_parts) == 2 and feature_parts[0].isdigit():
                        feature_name = feature_parts[1].strip()
                        if feature_name:
                            self.licenses[current_license]["features"].add(feature_name)
                            print(f"  Added feature: {feature_name} to {current_license}")

            else:  # Dòng chứa license product
                license_product = parts[0].strip()
                print(f"\nProcessing license: {license_product}")
                
                # Xử lý phần còn lại của dòng
                remaining = ' '.join(parts[1:]).strip()
                qty_and_desc = re.match(r'(\d+)\s*(.*)', remaining)
                
                if qty_and_desc:
                    qty = int(qty_and_desc.group(1))
                    description = qty_and_desc.group(2).strip()
                    print(f"  Quantity: {qty}")
                    print(f"  Description: {description}")

                    current_license = license_product
                    self.licenses[current_license] = {
                        "qty": qty,
                        "description": description,
                        "features": set()
                    }

                    # Kiểm tra nếu có feature trong description
                    if description:
                        desc_parts = re.split(r'\s+(\d+)\s+', description)
                        if len(desc_parts) > 1:
                            print("  Found features in description:")
                            self.licenses[current_license]["description"] = desc_parts[0].strip()
                            for i in range(1, len(desc_parts), 2):
                                if i + 1 < len(desc_parts):
                                    feature_name = desc_parts[i + 1].strip()
                                    if feature_name:
                                        self.licenses[current_license]["features"].add(feature_name)
                                        print(f"    - {feature_name}")

        print("\n=== License Parser Results ===")
        print(f"Total bundles found: {len(self.licenses)}")
        for bundle, info in self.licenses.items():
            print(f"\nBundle: {bundle}")
            print(f"  Description: {info['description']}")
            print(f"  Quantity: {info['qty']}")
            print(f"  Features: {len(info['features'])}")
            if len(info['features']) > 0:
                print("  Some features:", list(info['features'])[:3])

    def get_bundles(self) -> Dict[str, Dict]:
        """Get all bundles with their quantities and features."""
        return {
            bundle: {
                'quantity': info['qty'],
                'description': info['description'],
                'features': list(info['features'])
            }
            for bundle, info in self.licenses.items()
        }

    def find_feature_owner(self, feature_name: str) -> str:
        """Find which bundle owns a specific feature."""
        for license_product, details in self.licenses.items():
            if feature_name in details["features"]:
                return f"Feature '{feature_name}' thuộc về {license_product} ({details['description']})"
        return f"Feature '{feature_name}' không tìm thấy trong danh sách license."

    def display_licenses(self) -> None:
        """Display all licenses with their quantities."""
        for license_product, details in self.licenses.items():
            print(f"\n{license_product} ({details['description']}) - Số lượng license: {details['qty']}")
            print("Features:", ", ".join(sorted(details["features"])) if details["features"] else "Không có feature")

    def find_bundles_for_feature(self, feature_name: str) -> List[Dict[str, str]]:
        """Find all bundles that contain a specific feature."""
        print(f"\nSearching for feature: {feature_name}")
        bundles = []
        for bundle_name, details in self.licenses.items():
            if feature_name in details["features"]:
                print(f"  Found in bundle: {bundle_name}")
                bundles.append({
                    'name': bundle_name,
                    'description': details['description'],
                    'quantity': details['qty']
                })
        return bundles

    def get_usage_with_bundles(self, usage_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Convert usage data to include bundle information for each feature."""
        print("\n=== Processing Usage with Bundles ===")
        result = {}
        for feature_name, users in usage_data.items():
            print(f"\nProcessing feature: {feature_name}")
            bundles = self.find_bundles_for_feature(feature_name)
            result[feature_name] = {
                'bundles': bundles,
                'users': users
            }
            print(f"  Found {len(bundles)} bundles containing this feature")
            print(f"  Active users: {len(users)}")
        return result 