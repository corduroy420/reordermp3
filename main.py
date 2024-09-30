import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

def load_spotify_credentials(json_path):
    """Load Spotify API credentials from a JSON file."""
    with open(json_path, 'r') as file:
        credentials = json.load(file)
    return credentials

def extract_playlist_id(playlist_url):
    """Extract the playlist ID from the full Spotify playlist URL."""
    # The playlist URL should contain '/playlist/' followed by the playlist ID
    match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid playlist URL")

def get_spotify_playlist_tracks(playlist_id, credentials):
    """Fetch the list of track names from a Spotify playlist."""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=credentials['client_id'],
                                                   client_secret=credentials['client_secret'],
                                                   redirect_uri=credentials['redirect_uri'],
                                                   scope='playlist-read-private'))
    
    # Get the playlist tracks
    results = sp.playlist_tracks(playlist_id)
    
    # Extract the track names from the playlist
    tracks = []
    for item in results['items']:
        track = item['track']
        track_name = track['name']
        tracks.append(track_name)
    
    return tracks

def rename_mp3_files(folder_path, track_names):
    """Rename mp3 files in the folder according to the track names."""
    try:
        # List all mp3 files in the folder
        mp3_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]

        # Ensure that the number of mp3 files matches the number of tracks in the playlist
        if len(mp3_files) != len(track_names):
            print(f"Error: Number of mp3 files ({len(mp3_files)}) doesn't match the number of tracks in the playlist ({len(track_names)}).")
            return

        # Sort the mp3 files alphabetically
        mp3_files.sort()

        # Rename each file based on the track list
        for i, track_name in enumerate(track_names):
            track_number = f"{i+1:02d}_"  # Generate 01_, 02_, etc.
            old_file_path = os.path.join(folder_path, mp3_files[i])
            new_file_name = track_number + track_name + '.mp3'
            new_file_path = os.path.join(folder_path, new_file_name)
            
            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed '{mp3_files[i]}' to '{new_file_name}'")
        
        print("Renaming complete!")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Step 1: Load Spotify credentials from JSON file
    credentials_file = 'spotify_credentials.json'
    credentials = load_spotify_credentials(credentials_file)
    
    # Step 2: Get playlist link and extract the playlist ID
    playlist_url = input("Enter the Spotify playlist URL: ")
    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print(e)
        return

    # Step 3: Get folder path containing the mp3 files
    folder_path = input("Enter the path to the folder containing the mp3 files: ")

    # Step 4: Fetch the track names from the Spotify playlist
    try:
        track_names = get_spotify_playlist_tracks(playlist_id, credentials)
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return

    # Step 5: Rename the mp3 files based on the Spotify playlist
    rename_mp3_files(folder_path, track_names)

if __name__ == "__main__":
    main()
