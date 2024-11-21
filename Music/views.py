# Music/views.py

import os
import random
import logging
import requests
import spotipy
from django.conf import settings
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
import spotipy
from spotipy import Spotify, SpotifyOAuth
from django.views.generic import TemplateView
import os
class HomePageView(TemplateView):
    template_name = 'play.html'
def favicon(request):
    # Return an empty response with a 204 No Content status
    return HttpResponse(status=204)
def get_weather_data():
    url = 'http://api.weatherstack.com/current'
    params = {
        'access_key': settings.WEATHERSTACK_API_KEY,
        'query': settings.LOCATION
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'current' in data:
        current = data['current']
        weather_data = {
            'description': current['weather_descriptions'][0],
            'temperature': current['temperature'],
            'feelslike': current['feelslike'],
            'wind_speed': current['wind_speed'],
            'wind_dir': current['wind_dir'],
            'humidity': current['humidity'],
            'icon': current['weather_icons'][0] if 'weather_icons' in current and current['weather_icons'] else None,
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

# Mapping genres to a list of playlist IDs
genre_playlists = {
    'Rainy Day': [
        '37i9dQZF1DXbvABJXBIyiY',  # Rainy Day
        '37i9dQZF1DXdwTUxmGKrdN',  # Rainy Day Jazz
        '37i9dQZF1DWZkhexA0Z7aP',  # Rainy Day Mood
        '37i9dQZF1DXaXDsfv6nvZ5',  # Rainy Day Blues
        '37i9dQZF1DX3woOVffrpln',  # Rainy Day Instrumental
        '37i9dQZF1DX2Z5uXwixuEP',  # Rainy Day Relax
        '37i9dQZF1DXdV4VkZg6NlO',  # Rainy Day Beats
        '37i9dQZF1DX6bBjHfdRnza',  # Rainy Day Coffee
        '37i9dQZF1DWV0gynK7G6pD',  # Rain Sounds
        '37i9dQZF1DX2r0FByV5U4C',  # Rainy Day Vibes
        '37i9dQZF1DX0MuOvUqmxDz',  # Rainy Day Pop
        '37i9dQZF1DX6VdMW310YC7',  # Rainy Day Indie
        '37i9dQZF1DX889U0CL85jj',  # Rainy Day Chill
        '37i9dQZF1DX2cEUXdJJLVG',  # Rainy Day Classical
        '37i9dQZF1DXdEw8dT2n5yI',  # Rainy Day Soul
        '37i9dQZF1DWUzFXarNiofw',  # Rainy Day R&B
        '37i9dQZF1DX9XIFQuFvzM4',  # Rainy Day Folk
        '37i9dQZF1DX5Q27plkaOQ3',  # Rainy Day Acoustic
        '37i9dQZF1DX0SM0LYsmbMT',  # Rainy Day Piano
        '37i9dQZF1DWXe9gFZP0gtP',  # Rainy Day Sleep
        # Add more playlist IDs to reach 50
    ],
    'Chill': [
        '37i9dQZF1DX4WYpdgoIcn6',  # Chill Hits
        '37i9dQZF1DX889U0CL85jj',  # Chill Vibes
        '37i9dQZF1DX6VdMW310YC7',  # Lo-Fi Beats
        '37i9dQZF1DX9sIqqvKsjG8',  # Evening Chill
        '37i9dQZF1DX0SM0LYsmbMT',  # Chill Tracks
        '37i9dQZF1DX4E3UdUs7fUx',  # Chillout Lounge
        '37i9dQZF1DWVOV3mP1TySi',  # Chilled R&B
        '37i9dQZF1DX6xZZEgC9Ubl',  # Chill Folk
        '37i9dQZF1DXdPDLmy88MDk',  # Lofi Beats
        '37i9dQZF1DX6uQnoHESB3u',  # Chill House
        '37i9dQZF1DX2yvmlOdMYzV',  # Chill Pop
        '37i9dQZF1DX2TRYkJECvfC',  # Late Night Vibes
        '37i9dQZF1DWU0ScTcjJBdj',  # Bedroom Pop
        '37i9dQZF1DX6ziVCJnEm59',  # Your Favorite Coffeehouse
        '37i9dQZF1DX3Ogo9pFvBkY',  # Deep Focus
        '37i9dQZF1DX4sWSpwq3LiO',  # Peaceful Piano
        '37i9dQZF1DX8Uebhn9wzrS',  # Instrumental Study
        '37i9dQZF1DX0hvSv9Rf41p',  # Chill Instrumental Beats
        '37i9dQZF1DX0MLFaUdXnjA',  # Chill Out Music
        '37i9dQZF1DX4uPi2roRUwU',  # Chill Latino
        # Add more playlist IDs to reach 50
    ],
    'Happy': [
        '37i9dQZF1DX3rxVfibe1L0',  # Mood Booster
        '37i9dQZF1DX1H4LbvY4OJi',  # Happy Hits!
        '37i9dQZF1DX0UrRvztWcAU',  # Have a Great Day!
        '37i9dQZF1DX7KNKjOK0o75',  # Good Vibes
        '37i9dQZF1DX7SEhw42DW5b',  # Feelin' Good
        '37i9dQZF1DWYBO1MoTDhZI',  # Wake Up Happy
        '37i9dQZF1DX2sUQwD7tbmL',  # Songs to Sing in the Shower
        '37i9dQZF1DX2A29LI7xHn1',  # Just Smile
        '37i9dQZF1DX0s5kDXi1oC5',  # It's a Hit!
        '37i9dQZF1DX6ALfRKlHn1t',  # Happy Folk
        '37i9dQZF1DX3S2ONCFIYHU',  # Confidence Boost
        '37i9dQZF1DX5IDTimEWoTd',  # Young & Free
        '37i9dQZF1DWZjqjZMudx9T',  # Happy Pop Hits
        '37i9dQZF1DWVOMXLzSabd5',  # Sunny Day
        '37i9dQZF1DX1IeqVkK7Ebc',  # Pop Rising
        '37i9dQZF1DX2YSAziAIYdR',  # Happy Drive
        '37i9dQZF1DX2F5hV9dV1jG',  # Mood Ring
        '37i9dQZF1DX4fpCWaHOned',  # Good Vibes Only
        '37i9dQZF1DWXcA4cE8AqW6',  # Happy Beats
        '37i9dQZF1DX8tZsk68tuDw',  # Smile :)
        # Add more playlist IDs to reach 50
    ],
    'Winter': [
        '37i9dQZF1DX2MyUCsl25eb',  # Cozy Christmas
        '37i9dQZF1DX0Yxoavh5qJV',  # Winter Chillout
        '37i9dQZF1DWZLcGGC0HJbc',  # Winter Acoustic
        '37i9dQZF1DX2xKqsL1SVWb',  # Winter Vibes
        '37i9dQZF1DXdPec7aLTmlC',  # Winter Sleep
        '37i9dQZF1DWV5vqkTng2MA',  # Winter Songs
        '37i9dQZF1DX7M1twJ8D6TS',  # Winter Folk
        '37i9dQZF1DX2yvmlOdMYzV',  # Chill Pop
        '37i9dQZF1DXc6IFF23C9jj',  # Winter Run
        '37i9dQZF1DX6xZZEgC9Ubl',  # Chill Folk
        '37i9dQZF1DXaDPSVSkBhhM',  # Winter Instrumental
        '37i9dQZF1DX3bSdu6sAEDF',  # Winter Jazz
        '37i9dQZF1DX6VdMW310YC7',  # Lo-Fi Beats
        '37i9dQZF1DX8ymr6UES7vc',  # Relaxing Massage
        '37i9dQZF1DWWEJlAGA9gs0',  # Deep Sleep
        '37i9dQZF1DX6QDedCAYqRI',  # Rain Sounds
        '37i9dQZF1DX8SfyqmSFDwe',  # Soft Winter
        '37i9dQZF1DX4sWSpwq3LiO',  # Peaceful Piano
        '37i9dQZF1DX8CopunbDxgW',  # Winter Classical
        '37i9dQZF1DX0SM0LYsmbMT',  # Peaceful Guitar
        # Add more playlist IDs to reach 50
    ],
    'Pop': [
        '37i9dQZF1DXcBWIGoYBM5M',  # Today's Top Hits
        '37i9dQZF1DX1IeqVkK7Ebc',  # Pop Rising
        '37i9dQZF1DXarRysLJmuju',  # Pop Remix
        '37i9dQZF1DXbTxeAdrVG2l',  # Hot Hits USA
        '37i9dQZF1DX4dyzvuaRJ0n',  # Confidence Boost
        '37i9dQZF1DX2A29LI7xHn1',  # Just Smile
        '37i9dQZF1DX2sUQwD7tbmL',  # Songs to Sing in the Shower
        '37i9dQZF1DX6aTaZa0K6VA',  # Pop Co-Op
        '37i9dQZF1DX5Ejj0EkURtP',  # Pop Chillout
        '37i9dQZF1DWVlYsZJXqdym',  # Pop Up
        '37i9dQZF1DWXti3N4Wp5xy',  # Pop Right Now
        '37i9dQZF1DX4JAvHpjipBk',  # Teen Party
        '37i9dQZF1DX1lVhptIYRda',  # Pop Ballads
        '37i9dQZF1DWWSrwtXj8amH',  # Hits du Moment
        '37i9dQZF1DX5IDTimEWoTd',  # Young & Free
        '37i9dQZF1DWYcDQ1hSjOpY',  # New Music Friday
        '37i9dQZF1DXa6YOhGMjjgx',  # Pop Rock
        '37i9dQZF1DX4eRPd9frC1m',  # Singled Out
        '37i9dQZF1DWVRSukIED0e9',  # Pop All Day
        '37i9dQZF1DX2A62XvEEcJf',  # Pop International
        # Add more playlist IDs to reach 50
    ],
}


def index(request):
    scope = "streaming user-read-email user-read-private playlist-modify-public playlist-modify-private user-modify-playback-state"
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

    access_token = token_info['access_token']
    weather_data = get_weather_data()
    if not weather_data:
        return HttpResponse("Error fetching weather data.")

    genre = get_genre_from_weather(weather_data['description'])
    playlists = genre_playlists.get(genre, genre_playlists['Pop'])
    if not playlists:
        logger.warning("No playlists available for the selected genre.")
        return HttpResponse("No playlists available for the selected genre.")

    sp = Spotify(auth=access_token)
    playlist_id = playlists[0]  # Select the first playlist
    request.session['playlist_id'] = playlist_id  # Store playlist ID in session

    playlist_info = sp.playlist(playlist_id)
    tracks = playlist_info['tracks']['items']

    # Fetch tracks for the first playlist
    playlist_info = sp.playlist(playlists[0])
    tracks = playlist_info['tracks']['items']

    context = {
        'access_token': access_token,
        'playlist_id': playlist_id,
        'tracks': tracks,
        'playlist_name': playlist_info['name'],
        'playlist_image': playlist_info['images'][0]['url'] if playlist_info['images'] else None,
        'weather_data': weather_data,
        'genre': genre,
        'LOCATION': settings.LOCATION,
        'csrf_token': '',  # Include this if you need CSRF token in template
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