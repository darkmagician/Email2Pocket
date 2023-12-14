# -*- coding: utf-8 -*-

import json
import logging
import logging.handlers
import os
import sys

settingFile = 'config.json'
rootDir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)


def configLogging():
    logDir = os.path.join(rootDir, 'log')
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    consoleHandler = logging.StreamHandler(sys.stdout)
    fileHandler = logging.handlers.TimedRotatingFileHandler(os.path.join(logDir, 'email2pocket.log'), when='MIDNIGHT', encoding='utf8')
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO, handlers=[consoleHandler])


def getConfig(configName):
    configPath = os.path.join(rootDir, 'conf', configName)
    if os.path.exists(configPath):
        logger.info('Loading config file from {0}'.format(configPath))
        return json.load(open(configPath, 'r', encoding="utf8"))
    else:
        logger.warn('config file {0} is not found'.format(configPath))
        return None


def saveSettings():
    logger.info(f'saving settings')
    with open(settingFile, 'w') as fp:
        json.dump(settings, fp, indent=2)


settings = getConfig(settingFile)
configLogging()
