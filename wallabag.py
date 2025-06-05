import requests
import datetime
import config
import logging
from config import settings

logger = logging.getLogger(__name__)
wallabagCfg = settings['wallabag']

cachedToken = None


def isEnabled():
    return wallabagCfg and wallabagCfg['host']


def doAuth():
    logger.info("trying to do auth")
    host = wallabagCfg['host']
    data = {
        'grant_type': 'password',
        'client_id': wallabagCfg['client_id'],
        'client_secret': wallabagCfg['client_secret'],
        'username': wallabagCfg['username'],
        'password': wallabagCfg['password']
    }

    response = requests.post(f"{host}/oauth/v2/token", data=data)
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}，错误信息：{response.text}")
    tokenJson = response.json()
    logger.info(f"Get auth: {tokenJson}")
    return tokenJson


def getToken():
    global cachedToken
    now = datetime.datetime.now()
    if cachedToken and cachedToken['expires'] < now:
        return cachedToken['access_token']
    token = doAuth()
    if 'expires_in' in token:
        token['expires'] = now + datetime.timedelta(seconds=token['expires_in'])
        cachedToken = token
        return token['access_token']
    raise Exception('no valid token')


def addLink(link, title=None, tags=None):
    host = wallabagCfg['host']
    token = getToken()
    headers = {
        'accept': '*/*',
        'Authorization': f"Bearer {token}"
    }
    params = {
        'url': link
    }
    if title:
        params['title'] = title
    if tags:
        params['tags'] = ','.join(tags)
    response = requests.post(f"{host}/api/entries.json", headers=headers, data=params)
   # response.raise_for_status()
    result = response.json()
    logger.info(f'==>addLink: {result}')


if __name__ == '__main__':
    addLink("https://mp.weixin.qq.com/s?__biz=MjM5ODkzMzMwMQ==&mid=2650449084&idx=2&sn=e2ca46a6d9046e59d40817b97d7d8f65", "bbb", ["weixin"])
