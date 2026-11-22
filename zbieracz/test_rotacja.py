import rotacja

CHROME = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
SAFARI = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15'


def test_user_agent_z_przecinkiem_wraca_w_calosci(monkeypatch):
    monkeypatch.setattr(rotacja, 'uzyte', {})
    monkeypatch.setenv('ZBIERACZ_USER_AGENTS', CHROME + '|' + SAFARI)
    assert rotacja.kolejny('ZBIERACZ_USER_AGENTS') == CHROME
    assert rotacja.kolejny('ZBIERACZ_USER_AGENTS') == SAFARI
