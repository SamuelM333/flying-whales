import configparser
import logging

try:
    from auth_users import AUTH_USERS
except ImportError:
    AUTH_USERS = []

logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.ini'
logger.info("CONFIG: Leyendo archivo de configuracion {}".format(CONFIG_FILE))

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

try:
    # TODO Make this a dict
    HOST_NAME = config["HOST"]["host_name"]
    LOG_DIR = config["DIRS"]['log_dir']
    FLASK_SECRET_KEY = config["FLASK"]["secret_key"]
    LDAP_HOST = config['LDAP']['host']
    LDAP_DN = config['LDAP']['dn']
    LDAP_PASSWORD = config['LDAP']['password']
    BASE_DN = config["LDAP"]["base_dn"]
except KeyError as e:
    logger.critical("CONFIG: Error leyendo archivo de configuración. Error: {}".format(e))
    exit(1)
