import os
from typing import Dict, List

class LicenseParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.bundles: Dict[str, Dict] = {}
        self.features: Dict[str, str] = {}  # feature -> bundle mapping

    def parse(self) -> None:
        """Parse the license file and extract bundle and feature information."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"License file not found: {self.file_path}")

        with open(self.file_path, 'r') as file:
            content = file.read()

        # Split content into sections
        sections = content.split('# ---------------')
        
        # Find the section with bundle information
        for section in sections:
            if 'LICENSE PRODUCT' in section:
                self._parse_bundle_section(section)

    def _parse_bundle_section(self, section: str) -> None:
        """Parse a section containing bundle information."""
        lines = section.split('\n')
        current_bundle = None
        in_bundle_section = False
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check if we're in the bundle section
            if 'LICENSE PRODUCT' in line:
                in_bundle_section = True
                continue

            if not in_bundle_section:
                continue

            # Check if this is a bundle line
            if line and not line.startswith(' '):
                # This is a bundle line
                parts = line.split()
                if len(parts) >= 2:
                    bundle_name = parts[0]
                    try:
                        quantity = int(parts[1])
                        self.bundles[bundle_name] = {
                            'quantity': quantity,
                            'features': []
                        }
                        current_bundle = bundle_name
                    except ValueError:
                        # Skip lines that don't have valid quantity
                        continue
            elif current_bundle and line.startswith(' '):
                # This is a feature line
                feature = line.strip()
                if feature:
                    self.bundles[current_bundle]['features'].append(feature)
                    self.features[feature] = current_bundle

    def get_bundles(self) -> Dict[str, Dict]:
        """Get all bundles and their information."""
        return self.bundles

    def get_features(self) -> Dict[str, str]:
        """Get feature to bundle mapping."""
        return self.features

    def get_bundle_features(self, bundle_name: str) -> List[str]:
        """Get all features for a specific bundle."""
        return self.bundles.get(bundle_name, {}).get('features', []) 