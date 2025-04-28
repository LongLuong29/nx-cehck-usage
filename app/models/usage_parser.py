import os
from typing import Dict, List
from datetime import datetime

class UsageParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.usage_data: Dict[str, List[Dict]] = {}
        self.server_status: Dict = {}

    def parse(self) -> None:
        """Parse the usage file and extract usage information."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Usage file not found: {self.file_path}")

        with open(self.file_path, 'r') as file:
            content = file.read()

        # Split content into sections
        sections = content.split('--------')
        
        # Parse usage information
        for section in sections:
            if 'Users of' in section:
                self._parse_usage_section(section)
            elif 'Status' in section:
                self._parse_status_section(section)

    def _parse_usage_section(self, section: str) -> None:
        """Parse a section containing usage information."""
        lines = section.split('\n')
        current_feature = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Users of'):
                # This is a feature line
                parts = line.split('Users of')
                if len(parts) > 1:
                    feature = parts[1].split(':')[0].strip()
                    current_feature = feature
                    self.usage_data[feature] = []
            elif current_feature and 'start' in line.lower():
                # This is a user line
                parts = line.split()
                if len(parts) >= 4:
                    user = parts[0]
                    host = parts[1]
                    start_time = ' '.join(parts[-4:])  # Get the last 4 parts for start time
                    
                    try:
                        start_time = datetime.strptime(start_time, '%a %m/%d %H:%M')
                    except ValueError:
                        start_time = line.split('start')[-1].strip()
                    
                    self.usage_data[current_feature].append({
                        'user': user,
                        'host': host,
                        'start_time': start_time
                    })

    def _parse_status_section(self, section: str) -> None:
        """Parse the server status section."""
        lines = section.split('\n')
        for line in lines:
            if 'License server status:' in line:
                self.server_status['server'] = line.split(':')[-1].strip()
            elif 'License file(s)' in line:
                self.server_status['license_file'] = line.split(':')[-1].strip()
            elif 'license server UP' in line:
                self.server_status['status'] = 'UP'
                self.server_status['version'] = line.split('v')[-1].strip()

    def get_usage(self) -> Dict[str, List[Dict]]:
        """Get all usage information."""
        return self.usage_data

    def get_status(self) -> Dict:
        """Get server status information."""
        return self.server_status

    def get_feature_usage(self, feature: str) -> List[Dict]:
        """Get usage information for a specific feature."""
        return self.usage_data.get(feature, []) 