"""
Chart Intelligence Dashboard - Port 8542
Extracts, analyzes, and explains charts from research PDFs
"""

from flask import Flask, render_template, jsonify
import os
import json
import base64
from datetime import datetime
import anthropic
from unstructured_pdf_handler import UnstructuredPDFHandler

app = Flask(__name__)

# Initialize handlers
pdf_handler = UnstructuredPDFHandler()
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Chart analysis cache
CHART_CACHE_FILE = "chart_analysis_cache.json"

def load_chart_cache():
    """Load cached chart analyses"""
    if os.path.exists(CHART_CACHE_FILE):
        with open(CHART_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_chart_cache(cache):
    """Save chart analyses to cache"""
    with open(CHART_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def analyze_chart_with_vision(chart_base64, context=""):
    """Use Claude Vision to analyze and explain a chart"""
    try:
        response = anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": chart_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""Analyze this financial chart and provide:

1. **What it shows:** Brief description (1-2 sentences)
2. **Key observations:** 3-5 bullet points of important insights
3. **Data points:** Extract specific numbers, dates, levels
4. **Trading implications:** What this means for markets/trading (if applicable)
5. **Importance score:** Rate 1-10 how critical this chart is

Context: {context}

Be concise but insightful. Focus on actionable information."""
                    }
                ]
            }]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"Error analyzing chart: {str(e)}"

def process_pdf_and_extract_charts(pdf_path):
    """Process PDF and extract all charts with analysis"""
    
    print(f"📊 Processing PDF: {pdf_path}")
    
    # Use Unstructured API to extract content
    result = pdf_handler.process_pdf(pdf_path, sender_tag='default')
    
    charts = result.get('charts', [])
    
    if not charts:
        print("⚠️ No charts found in PDF")
        return []
    
    print(f"📈 Found {len(charts)} charts")
    
    analyzed_charts = []
    
    for idx, chart in enumerate(charts):
        chart_id = f"{os.path.basename(pdf_path)}_{idx}"
        
        # Check cache first
        cache = load_chart_cache()
        
        if chart_id in cache:
            print(f"✅ Using cached analysis for chart {idx+1}")
            analyzed_charts.append(cache[chart_id])
            continue
        
        # Get chart image
        chart_base64 = chart.get('base64')
        
        if not chart_base64:
            print(f"⚠️ No image data for chart {idx+1}")
            continue
        
        # Analyze with Claude Vision
        print(f"🔍 Analyzing chart {idx+1} with Claude Vision...")
        
        context = f"Chart from: {result.get('metadata', {}).get('file_name', 'Unknown')}"
        analysis = analyze_chart_with_vision(chart_base64, context)
        
        chart_data = {
            'id': chart_id,
            'image': chart_base64,
            'caption': chart.get('caption', f'Chart {idx+1}'),
            'analysis': analysis,
            'page_number': chart.get('page_number', 'Unknown'),
            'pdf_name': os.path.basename(pdf_path)
        }
        
        analyzed_charts.append(chart_data)
        
        # Cache the analysis
        cache[chart_id] = chart_data
        save_chart_cache(cache)
        
        print(f"✅ Chart {idx+1} analyzed")
    
    return analyzed_charts

def get_all_charts_from_drive():
    """Get all charts from processed Google Drive PDFs"""
    
    all_charts = []
    
    # Load processed files
    tracker_file = "processed_drive_files.json"
    if not os.path.exists(tracker_file):
        return []
    
    with open(tracker_file, 'r') as f:
        tracker = json.load(f)
    
    processed_files = tracker.get('processed_files', [])
    
    for pdf_info in processed_files:
        filename = pdf_info['filename']
        pdf_path = f"/tmp/drive_pdfs/{filename}"
        
        if os.path.exists(pdf_path):
            charts = process_pdf_and_extract_charts(pdf_path)
            for chart in charts:
                chart['company'] = pdf_info['company']
                chart['title'] = pdf_info['title']
                all_charts.append(chart)
    
    return all_charts

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('chart_dashboard.html')

@app.route('/api/charts')
def get_charts():
    """API endpoint to get all analyzed charts"""
    try:
        charts = get_all_charts_from_drive()
        return jsonify({
            'success': True,
            'total_charts': len(charts),
            'charts': charts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh')
def refresh_charts():
    """Force refresh all chart analyses"""
    try:
        # Clear cache
        if os.path.exists(CHART_CACHE_FILE):
            os.remove(CHART_CACHE_FILE)
        
        charts = get_all_charts_from_drive()
        return jsonify({
            'success': True,
            'message': f'Refreshed {len(charts)} charts',
            'total_charts': len(charts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure ANTHROPIC_API_KEY is set
    if not os.getenv('ANTHROPIC_API_KEY'):
        # Load from gmail_env.sh
        import subprocess
        result = subprocess.run(['bash', '-c', 'source gmail_env.sh && echo $ANTHROPIC_API_KEY'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            os.environ['ANTHROPIC_API_KEY'] = result.stdout.strip()
    
    print("🚀 Starting Chart Intelligence Dashboard on port 8542...")
    app.run(host='0.0.0.0', port=8542, debug=False)
