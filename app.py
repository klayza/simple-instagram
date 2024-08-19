from flask import Flask, jsonify, send_from_directory, make_response, request, Response
import json
import os
import requests

app = Flask(__name__, static_folder='.')

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'"
    return response

@app.route('/')
def serve_html():
    return send_from_directory('.', 'app.html')

@app.route('/api/users')
def get_users():
    with open('users/data.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# New route for the CORS proxy
@app.route('/proxy')
def proxy():
    # Get the URL from the query parameters
    url = request.args.get('url')
    
    if not url:
        return "URL parameter is missing", 400
    
    # Make a request to the actual resource
    response = requests.get(url)
    
    # Return the response content and headers
    return Response(response.content, headers=dict(response.headers))

if __name__ == '__main__':
    app.run(debug=True)
