from flask import Flask
from flask import request, redirect
from config import settings
import config
import logging
import requests

# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

app = Flask(__name__)
logger = logging.getLogger(__name__)
currentRequestToken = None
pocketCfg = settings['pocket']


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(e, exc_info=True)
    return {"errno": 1,
            "errmsg": 'system error'
            }, 500


@app.route('/auth', methods=['GET'])
def auth():
    global currentRequestToken
    if pocketCfg['access_token']:
        return {"errno": 0, "msg": "configured"}

    callbakUrl = pocketCfg['host'] + '/callback'

    requestToken = getRequestToken(pocketCfg['consumer_key'], callbakUrl)
    currentRequestToken = requestToken
    return redirect(f"https://getpocket.com/auth/authorize?request_token={requestToken}&redirect_uri={callbakUrl}", code=302)


@app.route('/callback', methods=['GET'])
def callback():
    global currentRequestToken
    if currentRequestToken:
        accessToken = getAccessToken(pocketCfg['consumer_key'], currentRequestToken)
        currentRequestToken = None
        if accessToken:
            pocketCfg['access_token'] = accessToken
            config.saveSettings()
            return {"errno": 0, "msg": "done"}
        else:
            return {"errno": 2, "msg": "failed to get access token."}
    return {"errno": 2, "msg": "request token was not set."}


def getAccessToken(consumer_key, code):
    data = {
        "consumer_key": consumer_key,
        "code": code
    }
    response = requests.post("https://getpocket.com/v3/oauth/authorize", headers={"X-Accept": "application/json"}, data=data)
    result = response.json()
    logger.info(f'==>getAccessToken: {result}')
    return result['access_token']


def getRequestToken(consumer_key, callbackUrl):
    data = {
        "consumer_key": consumer_key,
        "redirect_uri": callbackUrl
    }
    response = requests.post("https://getpocket.com/v3/oauth/request", headers={"X-Accept": "application/json"}, data=data)
    result = response.json()
    logger.info(f'==>getRequestToken: {result}')
    return result['code']


def addLink(link, title, tags):
    global pocketCfg
    token = pocketCfg['access_token']
    consumer_key = pocketCfg['consumer_key']
    if not token:
        logger.error("access_token is not set. failed to add link.")
        return None

    data = {
        "consumer_key": consumer_key,
        "access_token": token,
        "url": link
    }
    if title:
        data['title'] = title
    if tags:
        data['tags'] = tags

    response = requests.post("https://getpocket.com/v3/add", headers={"X-Accept": "application/json"}, json=data)
    result = response.json()
    logger.info(f'==>addLink: {result}')
    return result['item']


def startServer():
    http_cfg = settings['http']
    if http_cfg['ssl']['enabled']:
        app.run(port=http_cfg['port'], host=http_cfg['host'],
                ssl_context=(
            os.path.join(config.rootDir, http_cfg['cert']),
            os.path.join(config.rootDir, http_cfg['key'])
        ))
    else:
        app.run(port=http_cfg['port'], host=http_cfg['host'])


if __name__ == '__main__':
    startServer()
