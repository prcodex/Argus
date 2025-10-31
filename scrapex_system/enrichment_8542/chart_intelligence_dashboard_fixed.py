"""
Chart Intelligence Dashboard - CACHE-BUSTED VERSION
"""

from flask import Flask, render_template, jsonify, make_response
import os
import json
from datetime import datetime

app = Flask(__name__)

CHART_CACHE_FILE = "chart_analysis_cache.json"

def load_chart_cache():
    """Load cached chart analyses"""
    if os.path.exists(CHART_CACHE_FILE):
        with open(CHART_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

@app.route('/')
def index():
    """Main dashboard page with cache busting"""
    response = make_response(render_template('chart_dashboard.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/charts')
def get_charts():
    """API endpoint with cache busting"""
    try:
        cache = load_chart_cache()
        charts = list(cache.values())
        
        response = make_response(jsonify({
            'success': True,
            'total_charts': len(charts),
            'charts': charts,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0'  # Version bump
        }))
        
        # Aggressive cache busting
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh')
def refresh_charts():
    """Force refresh"""
    try:
        if os.path.exists(CHART_CACHE_FILE):
            os.remove(CHART_CACHE_FILE)
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Chart Intelligence Dashboard on port 8542...")
    
    if os.path.exists(CHART_CACHE_FILE):
        cache = load_chart_cache()
        print(f"✅ Found {len(cache)} charts in cache")
        
        # Check chart sizes
        for chart_id, chart in cache.items():
            img_len = len(chart.get('image', ''))
            print(f"   {chart['caption']}: {img_len:,} chars")
    else:
        print("⚠️ No chart cache found")
    
    app.run(host='0.0.0.0', port=8542, debug=False)
