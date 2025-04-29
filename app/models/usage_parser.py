import os
from typing import Dict, List
from datetime import datetime

class UsageParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.usage_data: Dict[str, List[Dict]] = {}
        self.server_status: Dict = {}
        print(f"\n=== Initializing UsageParser with file: {file_path} ===")

    def parse(self) -> None:
        """Parse the usage file and extract usage information."""
        print("\n=== Starting Usage Parser ===")
        if not os.path.exists(self.file_path):
            print(f"ERROR: File not found: {self.file_path}")
            raise FileNotFoundError(f"Usage file not found: {self.file_path}")

        with open(self.file_path, 'r') as file:
            content = file.read()

        # Split content into sections
        sections = content.split('--------')
        print(f"Found {len(sections)} sections in the file")
        
        # Parse usage information
        for section in sections:
            if 'Users of' in section:
                self._parse_usage_section(section)
            elif 'Status' in section:
                self._parse_status_section(section)

        print("\n=== Usage Parser Results ===")
        print(f"Total features found: {len(self.usage_data)}")
        print("Features with active users:")
        for feature, users in self.usage_data.items():
            if users:  # Only show features with active users
                print(f"- {feature}: {len(users)} users")
        print("\nServer Status:", self.server_status)

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
                    feature_info = parts[1].split(':')[0].strip()
                    current_feature = feature_info
                    self.usage_data[feature_info] = []
                    print(f"\nProcessing feature: {feature_info}")
                    
                    # Kiểm tra xem có phải là feature lỗi không
                    if 'Error:' in line:
                        print(f"  Skipping feature due to error: {line}")
                        continue
                    
            elif current_feature and 'start' in line.lower():
                # This is a user line
                try:
                    parts = line.split()
                    if len(parts) >= 4:
                        user = parts[0].strip('"')
                        host = parts[1]
                        
                        # Tìm phần start time trong dòng
                        start_index = line.lower().find('start')
                        if start_index != -1:
                            time_str = line[start_index:].split('start')[1].strip()
                            print(f"  Found user: {user} on {host}")
                            print(f"  Start time string: {time_str}")
                            
                            # Thêm năm vào thời gian
                            current_year = datetime.now().year
                            try:
                                start_time = datetime.strptime(f"{time_str} {current_year}", '%a %m/%d %H:%M %Y')
                                # Chuyển đổi sang chuỗi định dạng đẹp hơn
                                formatted_time = start_time.strftime('%m/%d/%Y, %H:%M:%S')
                                print(f"  Formatted time: {formatted_time}")
                                
                                self.usage_data[current_feature].append({
                                    'user': user,
                                    'host': host,
                                    'start_time': formatted_time
                                })
                            except ValueError as e:
                                print(f"  WARNING: Could not parse time '{time_str}' for feature {current_feature}")
                                print(f"  Error: {str(e)}")
                                continue
                            
                except Exception as e:
                    print(f"  WARNING: Error parsing user line '{line}' for feature {current_feature}")
                    print(f"  Error: {str(e)}")
                    continue

    def _parse_status_section(self, section: str) -> None:
        """Parse the server status section."""
        print("\n=== Parsing Server Status Section ===")
        lines = section.split('\n')
        self.server_status = {
            'status': 'DOWN',
            'server': '',
            'license_file': '',
            'version': ''
        }
        
        for line in lines:
            line = line.strip()
            if 'License server status:' in line:
                self.server_status['server'] = line.split(':')[-1].strip()
                print(f"Found server: {self.server_status['server']}")
            elif 'License file(s)' in line:
                self.server_status['license_file'] = line.split(':')[-1].strip()
                print(f"Found license file: {self.server_status['license_file']}")
            elif 'license server UP' in line:
                self.server_status['status'] = 'UP'
                if 'v' in line:
                    self.server_status['version'] = line.split('v')[-1].strip()
                print(f"Server is UP, version: {self.server_status['version']}")

    def get_usage(self) -> Dict[str, List[Dict]]:
        """Get all usage information."""
        return self.usage_data

    def get_status(self) -> Dict:
        """Get server status information."""
        return self.server_status

    def get_feature_usage(self, feature: str) -> List[Dict]:
        """Get usage information for a specific feature."""
        return self.usage_data.get(feature, []) 