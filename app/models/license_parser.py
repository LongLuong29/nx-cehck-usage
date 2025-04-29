import os
import re
from typing import Dict, Set

class LicenseParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.licenses: Dict[str, Dict] = {}  # {license_product: {'qty': int, 'description': str, 'features': set()}}

    def parse(self) -> None:
        """Parse the license file and extract bundle and feature information."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"License file not found: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

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

            else:  # Dòng chứa license product
                license_product = parts[0].strip()
                
                # Xử lý phần còn lại của dòng
                remaining = ' '.join(parts[1:]).strip()
                qty_and_desc = re.match(r'(\d+)\s*(.*)', remaining)
                
                if qty_and_desc:
                    qty = int(qty_and_desc.group(1))
                    description = qty_and_desc.group(2).strip()

                    current_license = license_product
                    self.licenses[current_license] = {
                        "qty": qty,
                        "description": description,
                        "features": set()
                    }

                    # Kiểm tra nếu có feature trong description (trường hợp TCADMIN)
                    if description:
                        # Tách description thành các phần bằng số lượng
                        desc_parts = re.split(r'\s+(\d+)\s+', description)
                        if len(desc_parts) > 1:
                            # Phần đầu tiên là description thực sự
                            self.licenses[current_license]["description"] = desc_parts[0].strip()
                            # Các phần còn lại có thể là features
                            for i in range(1, len(desc_parts), 2):
                                if i + 1 < len(desc_parts):
                                    feature_name = desc_parts[i + 1].strip()
                                    if feature_name:
                                        self.licenses[current_license]["features"].add(feature_name)

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