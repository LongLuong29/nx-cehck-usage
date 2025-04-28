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

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/bundles')
def get_bundles():
    bundles = license_parser.get_bundles()
    return jsonify({
        'bundles': bundles
    })

@main.route('/api/features')
def get_features():
    features = license_parser.get_features()
    return jsonify({
        'features': features
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
    
    # Calculate usage per bundle
    bundle_usage = {}
    for bundle_name, bundle_info in bundles.items():
        features = bundle_info['features']
        total_used = 0
        users = []
        
        for feature in features:
            if feature in usage:
                feature_users = usage[feature]
                total_used += len(feature_users)
                users.extend(feature_users)
        
        bundle_usage[bundle_name] = {
            'total_licenses': bundle_info['quantity'],
            'used_licenses': total_used,
            'available_licenses': bundle_info['quantity'] - total_used,
            'users': users
        }
    
    return jsonify({
        'bundles': bundle_usage,
        'server_status': status
    }) 