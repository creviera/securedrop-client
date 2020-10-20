# -*- coding: utf-8 -*-

import os
import subprocess

from sqlalchemy import text

from securedrop_client import db

from .utils import add_source


class UpgradeTester:
    """
    This migration verifies that the seen_files, seen_messages, and seen_replies association tables
    now exist, and that the data migration completes successfully.
    """

    JOURNO_NUM = 20
    SOURCE_NUM = 20

    def __init__(self, homedir):
        subprocess.check_call(["sqlite3", os.path.join(homedir, "svs.sqlite"), ".databases"])
        self.session = db.make_session_maker(homedir)()

    def load_data(self):
        for _ in range(self.SOURCE_NUM):
            add_source(self.session)

    def check_upgrade(self):
        sql = "SELECT * FROM seen_files"
        files = self.session.execute(text(sql)).fetchall()
        assert not files


class DowngradeTester:
    """
    This migration verifies that the seen_files, seen_messages, and seen_replies association tables
    are removed.
    """

    JOURNO_NUM = 20
    SOURCE_NUM = 20

    def __init__(self, homedir):
        subprocess.check_call(["sqlite3", os.path.join(homedir, "svs.sqlite"), ".databases"])
        self.session = db.make_session_maker(homedir)()

    def load_data(self):
        sql = "SELECT * FROM seen_files"
        seen_files_exists = self.session.execute(text(sql)).fetchall()
        assert not seen_files_exists

    def check_downgrade(self):
        sql = "SELECT * FROM files"
        seen_files_exists = self.session.execute(text(sql)).fetchall()
        assert not seen_files_exists
