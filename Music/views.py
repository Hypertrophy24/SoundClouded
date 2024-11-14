# Music/views.py

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
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
        '37i9dQZF1DXbvABJXBIyiY',
        '37i9dQZF1DWVqJMsgEN0F4',
        # Add more playlist IDs
    ],
    'Chill': [
        '37i9dQZF1DX4WYpdgoIcn6',
        '37i9dQZF1DX889U0CL85jj',
        # Add more playlist IDs
    ],
    'Happy': [
        '37i9dQZF1DX3rxVfibe1L0',
        '37i9dQZF1DX1H4LbvY4OJi',
        # Add more playlist IDs
    ],
    'Winter': [
        '37i9dQZF1DX2MyUCsl25eb',
        '37i9dQZF1DX2yvmlOdMYzV',
        # Add more playlist IDs
    ],
    'Pop': [
        '37i9dQZF1DXcBWIGoYBM5M',
        '37i9dQZF1DX1IeqVkK7Ebc',
        # Add more playlist IDs
    ],
}

def index(request):
    weather_description = get_weather_description()
    if weather_description:
        request.session['weather_description'] = weather_description
        return redirect(reverse('music:home'))
    else:
        return HttpResponse("Error fetching weather data.")

def play(request):
    weather_description = request.session.get('weather_description', 'Clear')

    # Get the genre based on the weather description
    genre = get_genre_from_weather(weather_description)

    # Get the list of playlists for the genre
    playlists = genre_playlists.get(genre, genre_playlists['Pop'])  # Default to 'Pop' if genre not found

    if not playlists:
        return HttpResponse("No playlists available for the selected genre.")

    # Prepare Spotify client with client credentials
    sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
    ))

    playlist_data = []

    for playlist_id in playlists:
        playlist_info = sp.playlist(playlist_id)
        playlist_name = playlist_info['name']
        playlist_image = playlist_info['images'][0]['url'] if playlist_info['images'] else None
        playlist_embed_url = f"https://open.spotify.com/embed/playlist/{playlist_info['id']}"

        playlist_data.append({
            'name': playlist_name,
            'image': playlist_image,
            'embed_url': playlist_embed_url,
        })

    context = {
        'weather_description': weather_description,
        'genre': genre,
        'playlists': playlist_data,
    }
    return render(request, 'home.html', context)
