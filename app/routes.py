from flask import Blueprint, render_template, jsonify
import os
from app.models import LicenseParser, UsageParser

main = Blueprint('main', __name__)

# Initialize parsers
license_parser = LicenseParser('storage/license_info.cid')
usage_parser = UsageParser('storage/usage_info.txt')

# Parse the files
license_parser.parse()
usage_parser.parse()

# Display license information for debugging
print("\n=== License Information ===")
license_parser.display_licenses()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/bundles')
def get_bundles():
    bundles = license_parser.get_bundles()
    return jsonify({
        'bundles': bundles
    })

@main.route('/api/feature/<feature_name>')
def get_feature_owner(feature_name):
    result = license_parser.find_feature_owner(feature_name)
    return jsonify({
        'result': result
    })

@main.route('/api/usage')
def get_usage():
    usage = usage_parser.get_usage()
    return jsonify({
        'usage': usage
    })

@main.route('/api/status')
def get_status():
    status = usage_parser.get_status()
    return jsonify({
        'status': status
    })

@main.route('/api/summary')
def get_summary():
    """Get a summary of license usage including bundle information"""
    bundles = license_parser.get_bundles()
    usage = usage_parser.get_usage()
    status = usage_parser.get_status()

    bundle_usage = {}
    for bundle_name, bundle_info in bundles.items():
        used_features = []
        total_used = 0
        
        # Tính số lượng license đã sử dụng cho bundle này
        for feature_name in bundle_info['features']:
            if feature_name in usage:
                feature_users = usage[feature_name]
                used_features.extend(feature_users)
                total_used = max(total_used, len(feature_users))  # Lấy số lượng users lớn nhất

        # Loại bỏ duplicate users
        unique_users = list(set(used_features))
        
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