from flask import Blueprint, render_template, jsonify
import os
from app.models import LicenseParser, UsageParser

main = Blueprint('main', __name__)

print("\n=== Initializing Flask Routes ===")

# Initialize parsers
license_parser = LicenseParser('storage/license_info.cid')
usage_parser = UsageParser('storage/usage_info.txt')

# Parse the files
print("\nParsing license and usage files...")
license_parser.parse()
usage_parser.parse()

# Display license information for debugging
print("\n=== License Information ===")
license_parser.display_licenses()

@main.route('/')
def index():
    print("\nServing index page")
    return render_template('index.html')

@main.route('/api/bundles')
def get_bundles():
    print("\nAPI request: /api/bundles")
    bundles = license_parser.get_bundles()
    print(f"Returning {len(bundles)} bundles")
    return jsonify({
        'bundles': bundles
    })

@main.route('/api/feature/<feature_name>')
def get_feature_owner(feature_name):
    print(f"\nAPI request: /api/feature/{feature_name}")
    result = license_parser.find_feature_owner(feature_name)
    print(f"Result: {result}")
    return jsonify({
        'result': result
    })

@main.route('/api/usage')
def get_usage():
    print("\nAPI request: /api/usage")
    usage = usage_parser.get_usage()
    print(f"Found usage data for {len(usage)} features")
    
    # Thêm thông tin về bundle cho mỗi feature đang được sử dụng
    usage_with_bundles = license_parser.get_usage_with_bundles(usage)
    
    # Chuyển đổi start_time thành started để khớp với frontend
    print("\nProcessing user timestamps...")
    for feature_info in usage_with_bundles.values():
        for user in feature_info['users']:
            user['started'] = user.pop('start_time')
    
    return jsonify({
        'usage': usage_with_bundles
    })

@main.route('/api/status')
def get_status():
    print("\nAPI request: /api/status")
    status = usage_parser.get_status()
    print(f"Server status: {status['status']}")
    return jsonify({
        'status': status
    })

@main.route('/api/summary')
def get_summary():
    """Get a summary of license usage including bundle information"""
    print("\nAPI request: /api/summary")
    bundles = license_parser.get_bundles()
    usage = usage_parser.get_usage()
    status = usage_parser.get_status()

    print(f"\nProcessing summary for {len(bundles)} bundles")
    bundle_usage = {}
    for bundle_name, bundle_info in bundles.items():
        print(f"\nProcessing bundle: {bundle_name}")
        used_features = []
        total_used = 0
        
        # Tính số lượng license đã sử dụng cho bundle này
        for feature_name in bundle_info['features']:
            if feature_name in usage:
                feature_users = usage[feature_name]
                used_features.extend(feature_users)
                total_used = max(total_used, len(feature_users))  # Lấy số lượng users lớn nhất
                print(f"  Feature {feature_name}: {len(feature_users)} users")

        # Loại bỏ duplicate users và chuyển đổi start_time thành started
        unique_users = []
        seen_users = set()
        for user in used_features:
            user_key = (user['user'], user['host'])
            if user_key not in seen_users:
                seen_users.add(user_key)
                user_copy = user.copy()
                user_copy['started'] = user_copy.pop('start_time')
                unique_users.append(user_copy)
        
        print(f"  Total unique users: {len(unique_users)}")
        print(f"  Total licenses used: {total_used}/{bundle_info['quantity']}")
        
        bundle_usage[bundle_name] = {
            'total_licenses': bundle_info['quantity'],
            'used_licenses': total_used,
            'available_licenses': bundle_info['quantity'] - total_used,
            'description': bundle_info['description'],
            'users': unique_users
        }

    return jsonify({
        'bundles': bundle_usage,
        'server_status': status
    }) 