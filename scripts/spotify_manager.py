#!/usr/bin/env python3
"""
Spotify Playlist Manager for Jarvis
Handles OAuth, playlist creation, and song management
"""

import json
import os
import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs
import threading

CREDS_FILE = os.path.expanduser("~/.spotify/credentials.json")
TOKEN_FILE = os.path.expanduser("~/.spotify/token.json")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# OAuth callback handler
authorization_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        query = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        authorization_code = query.get('code', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>Success!</h1><p>You can close this window and return to your terminal.</p></body></html>')
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

def load_credentials():
    """Load Spotify app credentials"""
    with open(CREDS_FILE, 'r') as f:
        return json.load(f)

def save_token(token_data):
    """Save access token"""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)

def load_token():
    """Load existing access token"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def get_authorization_code(creds):
    """Start OAuth flow and get authorization code"""
    global authorization_code
    
    scopes = [
        'playlist-modify-public',
        'playlist-modify-private',
        'playlist-read-private',
        'user-library-read'
    ]
    
    params = {
        'client_id': creds['client_id'],
        'response_type': 'code',
        'redirect_uri': creds['redirect_uri'],
        'scope': ' '.join(scopes)
    }
    
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    
    print(f"\n🎵 Opening browser for Spotify authorization...")
    print(f"If browser doesn't open, visit: {auth_url}\n")
    
    # Start local server to catch callback
    server = HTTPServer(('127.0.0.1', 8888), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.start()
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Wait for callback
    server_thread.join(timeout=120)
    server.server_close()
    
    return authorization_code

def exchange_code_for_token(creds, code):
    """Exchange authorization code for access token"""
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': creds['redirect_uri'],
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret']
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, data=data)
    if response.status_code == 200:
        token_data = response.json()
        save_token(token_data)
        print("✅ Access token obtained and saved!")
        return token_data
    else:
        print(f"❌ Failed to get token: {response.text}")
        return None

def refresh_token_if_needed():
    """Refresh token if expired"""
    token = load_token()
    if not token:
        return None
    
    # Try using current token
    headers = {'Authorization': f"Bearer {token['access_token']}"}
    response = requests.get(f"{SPOTIFY_API_BASE}/me", headers=headers)
    
    if response.status_code == 200:
        return token  # Token still valid
    
    # Token expired, refresh it
    creds = load_credentials()
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token['refresh_token'],
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret']
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, data=data)
    if response.status_code == 200:
        token_data = response.json()
        token_data['refresh_token'] = token['refresh_token']  # Keep refresh token
        save_token(token_data)
        return token_data
    
    return None

def authenticate():
    """Complete OAuth flow"""
    creds = load_credentials()
    
    # Try to use existing token
    token = refresh_token_if_needed()
    if token:
        return token
    
    # Need new authorization
    print("\n🔐 Spotify Authentication Required")
    code = get_authorization_code(creds)
    
    if not code:
        print("❌ Authorization failed")
        return None
    
    token = exchange_code_for_token(creds, code)
    return token

def get_user_id(token):
    """Get user's Spotify ID"""
    headers = {'Authorization': f"Bearer {token['access_token']}"}
    response = requests.get(f"{SPOTIFY_API_BASE}/me", headers=headers)
    
    if response.status_code == 200:
        return response.json()['id']
    return None

def create_playlist(token, name, description="", public=False):
    """Create a new playlist"""
    user_id = get_user_id(token)
    if not user_id:
        return None
    
    headers = {
        'Authorization': f"Bearer {token['access_token']}",
        'Content-Type': 'application/json'
    }
    
    data = {
        'name': name,
        'description': description,
        'public': public
    }
    
    response = requests.post(
        f"{SPOTIFY_API_BASE}/users/{user_id}/playlists",
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        playlist = response.json()
        print(f"✅ Created playlist: {name}")
        print(f"   URL: {playlist['external_urls']['spotify']}")
        return playlist
    else:
        print(f"❌ Failed to create playlist: {response.text}")
        return None

def search_track(token, query):
    """Search for a track"""
    headers = {'Authorization': f"Bearer {token['access_token']}"}
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    
    response = requests.get(
        f"{SPOTIFY_API_BASE}/search",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        results = response.json()
        if results['tracks']['items']:
            return results['tracks']['items'][0]
    return None

def add_tracks_to_playlist(token, playlist_id, track_uris):
    """Add tracks to a playlist"""
    headers = {
        'Authorization': f"Bearer {token['access_token']}",
        'Content-Type': 'application/json'
    }
    
    data = {
        'uris': track_uris
    }
    
    response = requests.post(
        f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
        headers=headers,
        json=data
    )
    
    return response.status_code == 201

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: spotify_manager.py <command> [args]")
        print("\nCommands:")
        print("  auth              - Authenticate with Spotify")
        print("  create <name>     - Create a new playlist")
        print("  search <query>    - Search for a track")
        return
    
    command = sys.argv[1]
    
    if command == 'auth':
        token = authenticate()
        if token:
            user_id = get_user_id(token)
            print(f"\n✅ Authenticated as user: {user_id}")
        else:
            print("\n❌ Authentication failed")
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Please provide a playlist name")
            return
        
        name = ' '.join(sys.argv[2:])
        token = authenticate()
        if token:
            create_playlist(token, name, "Created by Jarvis", public=False)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            return
        
        query = ' '.join(sys.argv[2:])
        token = authenticate()
        if token:
            track = search_track(token, query)
            if track:
                print(f"✅ Found: {track['name']} by {track['artists'][0]['name']}")
                print(f"   URI: {track['uri']}")
            else:
                print("❌ No tracks found")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()
