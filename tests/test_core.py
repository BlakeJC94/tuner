from unittest.mock import patch

import spotipy
import pytest

from tuner.core import tuner_match

{
    "display_name": "consistencypls",
    "external_urls": {"spotify": "https://open.spotify.com/user/consistencypls"},
    "followers": {"href": None, "total": 3},
    "href": "https://api.spotify.com/v1/users/consistencypls",
    "id": "consistencypls",
    "images": [],
    "type": "user",
    "uri": "spotify:user:consistencypls",
}


@pytest.fixture
def mock_data():
    return {
        "A": {
            "user": {
                "display_name": "A",
                "external_urls": {"spotify": "https://test.open.spotify.com/user/A"},
                "followers": {"href": None, "total": 3},
                "href": "https://test.api.spotify.com/v1/users/A",
                "id": "A",
                "images": [],
                "type": "user",
                "uri": "test:user:A",
            },
            "user_top_artists": {
                "items": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/4pejUc4iciQfgdX6OKulQn"
                        },
                        "followers": {"href": None, "total": 3620477},
                        "genres": [
                            "alternative metal",
                            "alternative rock",
                            "grunge",
                            "modern rock",
                            "palm desert scene",
                            "rock",
                            "stoner metal",
                            "stoner rock",
                        ],
                        "href": "https://api.spotify.com/v1/artists/4pejUc4iciQfgdX6OKulQn",
                        "id": "4pejUc4iciQfgdX6OKulQn",
                        "images": [
                            {
                                "height": 640,
                                "url": "https://i.scdn.co/image/ab6761610000e5eb909b2c4b7c768ee03445cd10",
                                "width": 640,
                            },
                            {
                                "height": 320,
                                "url": "https://i.scdn.co/image/ab67616100005174909b2c4b7c768ee03445cd10",
                                "width": 320,
                            },
                            {
                                "height": 160,
                                "url": "https://i.scdn.co/image/ab6761610000f178909b2c4b7c768ee03445cd10",
                                "width": 160,
                            },
                        ],
                        "name": "Queens of the Stone Age",
                        "popularity": 71,
                        "type": "artist",
                        "uri": "spotify:artist:4pejUc4iciQfgdX6OKulQn",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6RZUqkomCmb8zCRqc9eznB"
                        },
                        "followers": {"href": None, "total": 1984001},
                        "genres": [
                            "alternative rock",
                            "britpop",
                            "permanent wave",
                            "rock",
                        ],
                        "href": "https://api.spotify.com/v1/artists/6RZUqkomCmb8zCRqc9eznB",
                        "id": "6RZUqkomCmb8zCRqc9eznB",
                        "images": [
                            {
                                "height": 640,
                                "url": "https://i.scdn.co/image/ab6761610000e5ebc8b42133fea50275b77f45e2",
                                "width": 640,
                            },
                            {
                                "height": 320,
                                "url": "https://i.scdn.co/image/ab67616100005174c8b42133fea50275b77f45e2",
                                "width": 320,
                            },
                            {
                                "height": 160,
                                "url": "https://i.scdn.co/image/ab6761610000f178c8b42133fea50275b77f45e2",
                                "width": 160,
                            },
                        ],
                        "name": "Placebo",
                        "popularity": 66,
                        "type": "artist",
                        "uri": "spotify:artist:6RZUqkomCmb8zCRqc9eznB",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/4skJp5OKvcc9eKokiuhi2s"
                        },
                        "followers": {"href": None, "total": 340905},
                        "genres": ["neo-psychedelic"],
                        "href": "https://api.spotify.com/v1/artists/4skJp5OKvcc9eKokiuhi2s",
                        "id": "4skJp5OKvcc9eKokiuhi2s",
                        "images": [
                            {
                                "url": "https://i.scdn.co/image/ab6761610000e5ebfeacc4fe5eb5046f077a998e",
                                "height": 640,
                                "width": 640,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab67616100005174feacc4fe5eb5046f077a998e",
                                "height": 320,
                                "width": 320,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab6761610000f178feacc4fe5eb5046f077a998e",
                                "height": 160,
                                "width": 160,
                            },
                        ],
                        "name": "Pond",
                        "popularity": 49,
                        "type": "artist",
                        "uri": "spotify:artist:4skJp5OKvcc9eKokiuhi2s",
                    },
                ],
                "total": 187,
                "limit": 20,
                "offset": 0,
                "href": "https://api.spotify.com/v1/me/top/artists?offset=0&limit=20&time_range=medium_term",
                "next": "https://api.spotify.com/v1/me/top/artists?offset=20&limit=20&time_range=medium_term",
                "previous": None,
            },
        },
        "B": {
            "user": {
                "display_name": "B",
                "external_urls": {"spotify": "https://test.open.spotify.com/user/B"},
                "followers": {"href": None, "total": 3},
                "href": "https://test.api.spotify.com/v1/users/B",
                "id": "B",
                "images": [],
                "type": "user",
                "uri": "test:user:B",
            },
            "user_top_artists": {
                "items": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/1GhPHrq36VKCY3ucVaZCfo"
                        },
                        "followers": {"href": None, "total": 2123717},
                        "genres": [
                            "alternative dance",
                            "big beat",
                            "breakbeat",
                            "electronica",
                            "rave",
                            "trip hop",
                        ],
                        "href": "https://api.spotify.com/v1/artists/1GhPHrq36VKCY3ucVaZCfo",
                        "id": "1GhPHrq36VKCY3ucVaZCfo",
                        "images": [
                            {
                                "height": 640,
                                "url": "https://i.scdn.co/image/ab6761610000e5ebae05213e52565bfd7e7489b3",
                                "width": 640,
                            },
                            {
                                "height": 320,
                                "url": "https://i.scdn.co/image/ab67616100005174ae05213e52565bfd7e7489b3",
                                "width": 320,
                            },
                            {
                                "height": 160,
                                "url": "https://i.scdn.co/image/ab6761610000f178ae05213e52565bfd7e7489b3",
                                "width": 160,
                            },
                        ],
                        "name": "The Chemical Brothers",
                        "popularity": 62,
                        "type": "artist",
                        "uri": "spotify:artist:1GhPHrq36VKCY3ucVaZCfo",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/0u2qG4roqULELVVO9fMgSG"
                        },
                        "followers": {"href": None, "total": 57524},
                        "genres": ["melodic house", "progressive house"],
                        "href": "https://api.spotify.com/v1/artists/0u2qG4roqULELVVO9fMgSG",
                        "id": "0u2qG4roqULELVVO9fMgSG",
                        "images": [
                            {
                                "height": 640,
                                "url": "https://i.scdn.co/image/ab6761610000e5eb8329e453bbe1c40508ba0021",
                                "width": 640,
                            },
                            {
                                "height": 320,
                                "url": "https://i.scdn.co/image/ab676161000051748329e453bbe1c40508ba0021",
                                "width": 320,
                            },
                            {
                                "height": 160,
                                "url": "https://i.scdn.co/image/ab6761610000f1788329e453bbe1c40508ba0021",
                                "width": 160,
                            },
                        ],
                        "name": "16BL",
                        "popularity": 40,
                        "type": "artist",
                        "uri": "spotify:artist:0u2qG4roqULELVVO9fMgSG",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6nxWCVXbOlEVRexSbLsTer"
                        },
                        "followers": {"href": None, "total": 2467782},
                        "genres": [
                            "australian dance",
                            "australian electropop",
                            "australian indie",
                            "downtempo",
                            "edm",
                            "indietronica",
                        ],
                        "href": "https://api.spotify.com/v1/artists/6nxWCVXbOlEVRexSbLsTer",
                        "id": "6nxWCVXbOlEVRexSbLsTer",
                        "images": [
                            {
                                "height": 640,
                                "url": "https://i.scdn.co/image/ab6761610000e5ebdcbf7ddf047dd267e4de8978",
                                "width": 640,
                            },
                            {
                                "height": 320,
                                "url": "https://i.scdn.co/image/ab67616100005174dcbf7ddf047dd267e4de8978",
                                "width": 320,
                            },
                            {
                                "height": 160,
                                "url": "https://i.scdn.co/image/ab6761610000f178dcbf7ddf047dd267e4de8978",
                                "width": 160,
                            },
                        ],
                        "name": "Flume",
                        "popularity": 72,
                        "type": "artist",
                        "uri": "spotify:artist:6nxWCVXbOlEVRexSbLsTer",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/72tRiBHei5G9M8it4h4sfC"
                        },
                        "followers": {"href": None, "total": 234465},
                        "genres": [
                            "alternative hip hop",
                            "instrumental hip hop",
                            "sudanese pop",
                        ],
                        "href": "https://api.spotify.com/v1/artists/72tRiBHei5G9M8it4h4sfC",
                        "id": "72tRiBHei5G9M8it4h4sfC",
                        "images": [
                            {
                                "url": "https://i.scdn.co/image/ab6761610000e5eb7107fa871c65e7abbff237d6",
                                "height": 640,
                                "width": 640,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab676161000051747107fa871c65e7abbff237d6",
                                "height": 320,
                                "width": 320,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab6761610000f1787107fa871c65e7abbff237d6",
                                "height": 160,
                                "width": 160,
                            },
                        ],
                        "name": "Oddisee",
                        "popularity": 45,
                        "type": "artist",
                        "uri": "spotify:artist:72tRiBHei5G9M8it4h4sfC",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/4V8LLVI7PbaPR0K2TGSxFF"
                        },
                        "followers": {"href": None, "total": 17850183},
                        "genres": ["hip hop", "rap"],
                        "href": "https://api.spotify.com/v1/artists/4V8LLVI7PbaPR0K2TGSxFF",
                        "id": "4V8LLVI7PbaPR0K2TGSxFF",
                        "images": [
                            {
                                "url": "https://i.scdn.co/image/ab6761610000e5ebdfa2b0c7544a772042a12e52",
                                "height": 640,
                                "width": 640,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab67616100005174dfa2b0c7544a772042a12e52",
                                "height": 320,
                                "width": 320,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab6761610000f178dfa2b0c7544a772042a12e52",
                                "height": 160,
                                "width": 160,
                            },
                        ],
                        "name": "Tyler, The Creator",
                        "popularity": 95,
                        "type": "artist",
                        "uri": "spotify:artist:4V8LLVI7PbaPR0K2TGSxFF",
                    },
                ],
                "total": 187,
                "limit": 20,
                "offset": 0,
                "href": "https://api.spotify.com/v1/me/top/artists?offset=0&limit=20&time_range=medium_term",
                "next": "https://api.spotify.com/v1/me/top/artists?offset=20&limit=20&time_range=medium_term",
                "previous": None,
            },
        },
        "C": {
            "user": {
                "display_name": "C",
                "external_urls": {"spotify": "https://test.open.spotify.com/user/C"},
                "followers": {"href": None, "total": 3},
                "href": "https://test.api.spotify.com/v1/users/C",
                "id": "C",
                "images": [],
                "type": "user",
                "uri": "test:user:C",
            },
            "user_top_artists": {
                "items": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/67hb7towEyKvt5Z8Bx306c"
                        },
                        "followers": {"href": None, "total": 1633432},
                        "genres": [
                            "australian dance",
                            "australian electropop",
                            "dance rock",
                            "indietronica",
                            "neo-synthpop",
                        ],
                        "href": "https://api.spotify.com/v1/artists/67hb7towEyKvt5Z8Bx306c",
                        "id": "67hb7towEyKvt5Z8Bx306c",
                        "images": [
                            {
                                "height": 640,
                                "url": "https://i.scdn.co/image/ab6761610000e5eb23ae905f944a230905ffa2a8",
                                "width": 640,
                            },
                            {
                                "height": 320,
                                "url": "https://i.scdn.co/image/ab6761610000517423ae905f944a230905ffa2a8",
                                "width": 320,
                            },
                            {
                                "height": 160,
                                "url": "https://i.scdn.co/image/ab6761610000f17823ae905f944a230905ffa2a8",
                                "width": 160,
                            },
                        ],
                        "name": "Empire Of The Sun",
                        "popularity": 78,
                        "type": "artist",
                        "uri": "spotify:artist:67hb7towEyKvt5Z8Bx306c",
                    },
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/2d0hyoQ5ynDBnkvAbJKORj"
                        },
                        "followers": {"href": None, "total": 6268457},
                        "genres": [
                            "alternative metal",
                            "alternative rock",
                            "conscious hip hop",
                            "funk metal",
                            "hard rock",
                            "nu metal",
                            "political hip hop",
                            "post-grunge",
                            "rap metal",
                            "rap rock",
                            "rock",
                        ],
                        "href": "https://api.spotify.com/v1/artists/2d0hyoQ5ynDBnkvAbJKORj",
                        "id": "2d0hyoQ5ynDBnkvAbJKORj",
                        "images": [
                            {
                                "url": "https://i.scdn.co/image/ab6761610000e5ebda4bd2b213cae330e2a4a901",
                                "height": 640,
                                "width": 640,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab67616100005174da4bd2b213cae330e2a4a901",
                                "height": 320,
                                "width": 320,
                            },
                            {
                                "url": "https://i.scdn.co/image/ab6761610000f178da4bd2b213cae330e2a4a901",
                                "height": 160,
                                "width": 160,
                            },
                        ],
                        "name": "Rage Against The Machine",
                        "popularity": 73,
                        "type": "artist",
                        "uri": "spotify:artist:2d0hyoQ5ynDBnkvAbJKORj",
                    },
                ],
                "total": 187,
                "limit": 20,
                "offset": 0,
                "href": "https://api.spotify.com/v1/me/top/artists?offset=0&limit=20&time_range=medium_term",
                "next": "https://api.spotify.com/v1/me/top/artists?offset=20&limit=20&time_range=medium_term",
                "previous": None,
            },
        },
    }


@pytest.mark.parametrize("user_id", ["A", "B", "C"])
@patch.object(spotipy.Spotify, "current_user_top_artists")
@patch.object(spotipy.Spotify, "current_user")
def test_tuner_match(
    mock_current_user,
    mock_current_user_top_artists,
    user_id,
    mock_data,
):
    mock_current_user.return_value = mock_data[user_id]["user"]
    mock_current_user_top_artists.return_value = mock_data[user_id]["user_top_artists"]
    output = tuner_match()
