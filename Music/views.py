# Music/views.py

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from spotipy import SpotifyOAuth, Spotify
from django.urls import reverse
from django.http import HttpResponse
import random
from django.views.generic import TemplateView
class HomePageView(TemplateView):
    template_name = 'home.html'
def get_weather_description():
    url = 'http://api.weatherstack.com/current'
    params = {
        'access_key': settings.WEATHERSTACK_API_KEY,
        'query': settings.LOCATION
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'current' in data:
        description = data['current']['weather_descriptions'][0]
        return description
    else:
        return None

def get_genre_from_weather(weather_description):
    weather_description = weather_description.lower()
    if 'rain' in weather_description:
        return 'Rainy Day'
    elif 'cloud' in weather_description:
        return 'Chill'
    elif 'clear' in weather_description or 'sunny' in weather_description:
        return 'Happy'
    elif 'snow' in weather_description:
        return 'Winter'
    else:
        return 'Pop'  # Default genre

# Mapping genres to a list of playlist URIs
genre_playlists = {
    'Rainy Day': [
        'spotify:playlist:37i9dQZF1DXbvABJXBIyiY',
        'spotify:playlist:37i9dQZF1DWVqJMsgEN0F4',
        # Add more playlist URIs
    ],
    'Chill': [
        'spotify:playlist:37i9dQZF1DX4WYpdgoIcn6',
        'spotify:playlist:37i9dQZF1DX889U0CL85jj',
        # Add more playlist URIs
    ],
    'Happy': [
        'spotify:playlist:37i9dQZF1DX3rxVfibe1L0',
        'spotify:playlist:37i9dQZF1DX1H4LbvY4OJi',
        # Add more playlist URIs
    ],
    'Winter': [
        'spotify:playlist:37i9dQZF1DX2MyUCsl25eb',
        'spotify:playlist:37i9dQZF1DX2yvmlOdMYzV',
        # Add more playlist URIs
    ],
    'Pop': [
        'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M',
        'spotify:playlist:37i9dQZF1DX1IeqVkK7Ebc',
        # Add more playlist URIs
    ],
}

def index(request):
    weather_description = get_weather_description()
    if weather_description:
        request.session['weather_description'] = weather_description

        # Ensure the session has a session_key
        if not request.session.session_key:
            request.session.save()

        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-modify-playback-state user-read-playback-state",
            cache_path='.cache-' + request.session.session_key
        )
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:
        return HttpResponse("Error fetching weather data.")

def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state",
        cache_path='.cache-' + request.session.session_key
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    request.session['token_info'] = token_info

    return redirect(reverse('music:play'))

def play(request):
    token_info = request.session.get('token_info', None)
    if not token_info:
        return redirect(reverse('music:index'))

    sp = Spotify(auth=token_info['access_token'])
    weather_description = request.session.get('weather_description', 'Clear')

    # Get the genre based on the weather description
    genre = get_genre_from_weather(weather_description)

    # Get the list of playlists for the genre
    playlists = genre_playlists.get(genre, genre_playlists['Pop'])  # Default to 'Pop' if genre not found

    if not playlists:
        return HttpResponse("No playlists available for the selected genre.")

    # Select a random playlist from the list
    playlist_uri = random.choice(playlists)

    # Fetch playlist details
    playlist_info = sp.playlist(playlist_uri)
    playlist_name = playlist_info['name']
    playlist_image = playlist_info['images'][0]['url'] if playlist_info['images'] else None

    # Get available devices
    devices = sp.devices()
    if devices['devices']:
        device_id = devices['devices'][0]['id']
        # Start playback
        sp.start_playback(device_id=device_id, context_uri=playlist_uri)
        context = {
            'weather_description': weather_description,
            'genre': genre,
            'playlist_uri': playlist_uri,
            'playlist_name': playlist_name,
            'playlist_image': playlist_image,
        }
        return render(request, 'music/play.html', context)
    else:
        return HttpResponse("No active Spotify devices found. Please open Spotify on a device.")
