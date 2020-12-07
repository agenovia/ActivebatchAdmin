import logging
from Objects import api
from datetime import datetime

import win32com.client


class ABConnectionManager:
    """
    This class is available as a context manager

    with ABConnectionManager('activebatch', 9) as con:
        con.Search('/')
    """

    def __init__(self, server: str = 'activebatch', version: int = None):
        self.server = server
        self.version = version
        self.__con = None

        self.start = None  # datetime.now()

    def __repr__(self):
        return f'ABConnectionManager(server={self.server}, version={self.version})'

    def __enter__(self):
        logging.info(f'Creating an ActiveBatch V{self.version} COM object')
        if self.version is None:
            _com = f'ActiveBatch.AbatJobScheduler'
        else:
            _com = f'ActiveBatch.AbatJobScheduler.{self.version}'

        try:
            # the returned connection manager is an instance JobScheduler
            _js = api.JobScheduler
            _com_obj = win32com.client.Dispatch(_com)
            self.__con = _js(obj=_com_obj, server=self.server, version=self.version)
        except Exception as e:
            logging.exception(e)
            raise Exception
        logging.debug(f"COM object successfully initialized")
        logging.info(f"Connecting to server '{self.server}'")
        try:
            logging.debug(f"con.Connect('{self.server}')")
            self.__con.Connect(self.server)
        except Exception as e:
            logging.exception(e)
            raise Exception
        logging.debug('OK')
        self.start = datetime.now()
        logging.debug(f'connection started on {self.start.strftime("%Y-%m-%d %H:%M:%S")}')
        return self.__con

    def __exit__(self, *exc):
        self.__con.Disconnect()
        end = datetime.now()
        logging.debug(f'connection ended on {end.strftime("%Y-%m-%d %H:%M:%S")}')
        logging.debug(f'Time elapsed: {end - self.start}')

    def close(self):
        self.__exit__()

