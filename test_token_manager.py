from datetime import timedelta
import urllib.parse

from freezegun import freeze_time

from oauth_token_manager import OAuthTokenManager

# -----------------------------------------------------------------------------


def test_token_manager(responses):
    url = 'https://example.com/oauth/token'
    parameters = {
        'grant_type': 'client_credentials',
        'client_id': 'foo',
        'client_secret': 'bar',
    }

    responses.add(responses.POST, url, json={
        'access_token': 'foo',
        'expires_in': 3600,
    })
    responses.add(responses.POST, url, json={
        'access_token': 'bar',
        'expires_in': 3600,
    })

    token_manager = OAuthTokenManager(url, **parameters)

    with freeze_time('2000-01-01') as frozen_datetime:
        assert token_manager.token == 'foo'
        assert token_manager.token == 'foo'

        frozen_datetime.tick(delta=timedelta(seconds=3550))

        assert token_manager.token == 'bar'
        assert token_manager.token == 'bar'

    assert len(responses.calls) == 2

    request_0 = responses.calls[0].request
    assert request_0.headers['Content-Type'] == (
        'application/x-www-form-urlencoded'
    )
    assert dict(urllib.parse.parse_qsl(request_0.body)) == parameters

    request_1 = responses.calls[1].request
    assert request_1.headers['Content-Type'] == (
        'application/x-www-form-urlencoded'
    )
    assert dict(urllib.parse.parse_qsl(request_1.body)) == parameters
