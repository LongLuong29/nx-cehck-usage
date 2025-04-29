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

    bundle_usage = {}
    for bundle_name, quantity in bundles.items():
        bundle_usage[bundle_name] = {
            'total_licenses': quantity,
            'used_licenses': 0,  # Không có thông tin feature nên không tính được
            'available_licenses': quantity,
            'users': []
        }

    return jsonify({
        'bundles': bundle_usage,
        'server_status': status
    }) 