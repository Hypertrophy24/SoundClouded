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
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from spotipy import SpotifyOAuth, SpotifyClientCredentials

# Setup logging
logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'home.html'  # Assuming 'home.html' is your template

def favicon(request):
    """Handle favicon.ico requests."""
    return HttpResponse(status=204)  # Return an empty response with a 204 No Content status

def get_weather_data():
    """Fetch weather data from Weatherstack API."""
    url = 'http://api.weatherstack.com/current'
    params = {
        'access_key': settings.WEATHERSTACK_API_KEY,
        'query': settings.LOCATION
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
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
            logger.error("Weatherstack API response missing 'current' field.")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
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
        '37i9dQZF1DWVqJMsgEN0F4',
        # Add more playlist IDs to reach 50
    ],
    'Chill': [
        '37i9dQZF1DX4WYpdgoIcn6',  # Chill Hits
        '37i9dQZF1DX889U0CL85jj',
        # Add more playlist IDs to reach 50
    ],
    'Happy': [
        '37i9dQZF1DX3rxVfibe1L0',  # Mood Booster
        '37i9dQZF1DX1H4LbvY4OJi',
        # Add more playlist IDs to reach 50
    ],
    'Winter': [
        '37i9dQZF1DX2MyUCsl25eb',  # Cozy Christmas
        '37i9dQZF1DX2yvmlOdMYzV',
        # Add more playlist IDs to reach 50
    ],
    'Pop': [
        '37i9dQZF1DXcBWIGoYBM5M',  # Today's Top Hits
        '37i9dQZF1DX1IeqVkK7Ebc',
        # Add more playlist IDs to reach 50
    ],
}

def index(request):
    """Index view that initiates Spotify authentication and redirects to 'home'."""
    logger.info("Redirecting to Spotify authorization page.")
    weather_data = get_weather_data()
    if weather_data:
        request.session['weather_data'] = weather_data
        return redirect(reverse('home'))
    else:
        return HttpResponse("Error fetching weather data.")

def callback(request):
    """Handle Spotify authentication callback."""
    logger.info("Handling Spotify callback.")
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="streaming user-read-email user-read-private playlist-modify-public playlist-modify-private user-modify-playback-state",
        show_dialog=True
    )
    code = request.GET.get('code')
    error = request.GET.get('error')
    if error:
        logger.error(f"Spotify callback error: {error}")
        return HttpResponse(f"Error during authentication: {error}")
    if not code:
        logger.error("Missing 'code' parameter in Spotify callback.")
        return HttpResponse("Error: No code parameter found in callback.")
    token_info = sp_oauth.get_access_token(code)
    if not token_info:
        logger.error("Failed to obtain token info from Spotify.")
        return HttpResponse("Error obtaining token info from Spotify.")
    request.session['token_info'] = token_info
    logger.info("Token info stored in session.")
    return redirect(reverse('play'))

def play(request):
    """Main view to display playlists based on weather."""
    logger.info("Loading play view.")
    token_info = request.session.get('token_info')
    if not token_info:
        logger.warning("Missing token info, redirecting to index.")
        return redirect(reverse('index'))

    access_token = token_info['access_token']
    weather_data = request.session.get('weather_data')
    if not weather_data:
        weather_data = get_weather_data()
        if not weather_data:
            logger.error("Failed to fetch weather data.")
            return HttpResponse("Error fetching weather data.")
        request.session['weather_data'] = weather_data

    genre = get_genre_from_weather(weather_data['description'])
    playlists = genre_playlists.get(genre, genre_playlists['Pop'])
    if not playlists:
        logger.warning("No playlists available for the selected genre.")
        return HttpResponse("No playlists available for the selected genre.")

    sp = spotipy.Spotify(auth=access_token)
    request.session['playlist_id'] = playlists[0]  # Store the first playlist ID in session

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

    # Fetch tracks for the first playlist
    playlist_info = sp.playlist(playlists[0])
    tracks = playlist_info['tracks']['items']

    context = {
        'weather_description': weather_data['description'],
        'access_token': access_token,
        'playlist_id': playlists[0],
        'tracks': tracks,
        'playlist_name': playlist_info['name'],
        'playlist_image': playlist_info['images'][0]['url'] if playlist_info['images'] else None,
        'weather_data': weather_data,
        'genre': genre,
        'playlists': playlist_data,
        'LOCATION': settings.LOCATION,
        # Include CSRF token in template if needed
    }
    return render(request, 'home.html', context)

@csrf_exempt
def save_playlist(request):
    """Save the generated playlist to the user's Spotify account."""
    if request.method != 'POST':
        return HttpResponse(status=405)  # Method Not Allowed

    token_info = request.session.get('token_info')
    if not token_info:
        logger.warning("Authentication required to save playlist.")
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    playlist_id = request.session.get('playlist_id')
    if not playlist_id:
        logger.error("No playlist information found in session.")
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

        logger.info("Playlist saved successfully.")
        return JsonResponse({'message': 'Playlist saved to your Spotify account!', 'playlist_url': playlist_url})
    except spotipy.SpotifyException as e:
        logger.error(f"Error saving playlist: {e}")
        return JsonResponse({'error': str(e)}, status=400)
