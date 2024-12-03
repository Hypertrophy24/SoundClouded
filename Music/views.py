# Music/views.py

import os
import random
import logging
import requests
import spotipy
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from spotipy import Spotify, SpotifyOAuth
from django.views.generic import TemplateView

# Setup logging
logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'play.html'

def favicon(request):
    # Return an empty response with a 204 No Content status
    return HttpResponse(status=204)

def get_weather_data(location=None):
    url = 'http://api.weatherstack.com/current'
    params = {
        'access_key': settings.WEATHERSTACK_API_KEY,
        'query': location if location else settings.LOCATION
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'current' in data:
        current = data['current']
        location_name = data['location']['name']
        weather_data = {
            'description': current['weather_descriptions'][0],
            'temperature': current['temperature'],
            'feelslike': current['feelslike'],
            'wind_speed': current['wind_speed'],
            'wind_dir': current['wind_dir'],
            'humidity': current['humidity'],
            'icon': current['weather_icons'][0] if 'weather_icons' in current and current['weather_icons'] else None,
            'location_name': location_name,
        }
        return weather_data
    else:
        return None

def get_genre_from_weather(weather_description):
    """Map weather description to a genre."""
    weather_description = weather_description.lower()
    if 'rain' in weather_description:
        return 'Rainy Day'
    elif 'cloud' in weather_description:
        return 'Chill'
    elif 'clear' in weather_description or 'sunny' in weather_description:
        return 'Happy'
    elif 'snow' in weather_description or 'winter' in weather_description:
        return 'Winter'
    else:
        return 'Pop'  # Default genre

genre_playlists = {
    'Rainy Day': [
        '6by1a3148JOzfqOjDLO4zJ',  # Chill Hits
    ],
    'Chill': [
        '6by1a3148JOzfqOjDLO4zJ',  # Chill Hits
    ],
    'Happy': [
        '6by1a3148JOzfqOjDLO4zJ',  # Chill Hits
    ],
    'Winter': [
        '6by1a3148JOzfqOjDLO4zJ',  # Chill Hits
    ],
    'Pop': [
        '6by1a3148JOzfqOjDLO4zJ',  # Chill Hits
        
    ],
}


def index(request):
    scope = "user-read-email user-read-private playlist-modify-public playlist-modify-private"
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=scope,
        show_dialog=True
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI
    )
    code = request.GET.get('code')
    error = request.GET.get('error')
    if error:
        return HttpResponse(f"Error during authentication: {error}")
    if not code:
        return HttpResponse("Error: No code parameter found in callback.")
    token_info = sp_oauth.get_access_token(code)
    if token_info is None:
        return HttpResponse("Error obtaining token info from Spotify.")
    request.session['token_info'] = token_info
    return redirect(reverse('play'))

def play(request):
    token_info = request.session.get('token_info', None)
    if not token_info:
        return redirect(reverse('index'))

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI
    )

    # Check if the token is expired and refresh it if necessary
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        request.session['token_info'] = token_info

    access_token = token_info['access_token']

    # Get location from GET parameters
    location = request.GET.get('location', None)

    weather_data = get_weather_data(location)
    if not weather_data:
        return HttpResponse("Error fetching weather data.")

    genre = get_genre_from_weather(weather_data['description'])
    playlists = genre_playlists.get(genre, genre_playlists['Pop'])
    if not playlists:
        logger.warning("No playlists available for the selected genre.")
        return HttpResponse("No playlists available for the selected genre.")

    sp = Spotify(auth=access_token)
    playlist_id = random.choice(playlists)  # Randomly select a playlist
    request.session['playlist_id'] = playlist_id  # Store playlist ID in session

    playlist_info = sp.playlist(playlist_id)

    context = {
        'playlist_id': playlist_id,
        'playlist_name': playlist_info['name'],
        'playlist_image': playlist_info['images'][0]['url'] if playlist_info['images'] else None,
        'weather_data': weather_data,
        'genre': genre,
        'LOCATION': weather_data['location_name'],
    }
    return render(request, 'home.html', context)

def save_playlist(request):
    if request.method != 'POST':
        return HttpResponse(status=405)  # Method Not Allowed

    token_info = request.session.get('token_info', None)
    if not token_info:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    playlist_id = request.session.get('playlist_id')
    if not playlist_id:
        return JsonResponse({'error': 'No playlist information found.'}, status=400)

    try:
        user_id = sp.current_user()['id']
        playlist_info = sp.playlist(playlist_id)
        playlist_name = playlist_info['name']
        playlist_description = playlist_info.get('description', '')
        track_uris = [item['track']['uri'] for item in playlist_info['tracks']['items']]

        # Check if a playlist with the same name already exists
        playlists = sp.current_user_playlists(limit=50)
        existing_playlist_id = None
        for pl in playlists['items']:
            if pl['name'] == playlist_name:
                existing_playlist_id = pl['id']
                break

        if existing_playlist_id:
            # Add tracks to the existing playlist
            sp.playlist_add_items(existing_playlist_id, track_uris)
            playlist_url = existing_playlist_id
        else:
            # Create a new playlist
            new_playlist = sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=True,
                description=f"Saved from SoundClouded: {playlist_description}"
            )
            sp.playlist_add_items(new_playlist['id'], track_uris)
            playlist_url = new_playlist['external_urls']['spotify']

        return JsonResponse({'message': 'Playlist saved to your Spotify account!', 'playlist_url': playlist_url})
    except spotipy.SpotifyException as e:
        return JsonResponse({'error': str(e)}, status=400)
