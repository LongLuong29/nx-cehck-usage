import os
from typing import Dict

class LicenseParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.bundles: Dict[str, int] = {}

    def parse(self) -> None:
        """Parse the license file and extract bundle and license quantity information only."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"License file not found: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            # Loại bỏ dấu # và khoảng trắng đầu dòng
            line = line.lstrip('#').strip()
            if not line:
                continue
            # Nếu dòng không bắt đầu bằng khoảng trắng, kiểm tra có phải bundle không
            if not line.startswith(' '):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    bundle_name = parts[0]
                    quantity = int(parts[1])
                    self.bundles[bundle_name] = quantity

    def get_bundles(self) -> Dict[str, int]:
        """Get all bundles and their license quantities."""
        return self.bundles 