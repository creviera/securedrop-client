# -*- coding: utf-8 -*-
import os
import random
import string
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session


random.seed("ᕕ( ᐛ )ᕗ")


def random_bool() -> bool:
    return bool(random.getrandbits(1))


def bool_or_none() -> Optional[bool]:
    return random.choice([None, True, False])


def random_bytes(min: int, max: int, nullable: bool) -> Optional[bytearray]:
    if nullable and random_bool():
        return None
    else:
        # return random_chars(random.randint(min, max))
        return bytearray(os.urandom(1000))


def random_name() -> str:
    len = random.randint(1, 100)
    return random_chars(len)


def random_username() -> str:
    len = random.randint(3, 64)
    return random_chars(len)


def random_chars(len: int, chars: str = string.printable) -> str:
    return "".join([random.choice(chars) for _ in range(len)])


def random_ascii_chars(len: int, chars: str = string.ascii_lowercase):
    return "".join([random.choice(chars) for _ in range(len)])


def random_datetime(nullable: bool):
    if nullable and random_bool():
        return None
    else:
        return datetime(
            year=random.randint(1, 9999),
            month=random.randint(1, 12),
            day=random.randint(1, 28),
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=random.randint(0, 1000),
        )


def add_source(session: Session) -> None:
    params = {
        "uuid": str(uuid4()),
        "journalist_designation": random_chars(50),
        "last_updated": random_datetime(nullable=True),
        "interaction_count": random.randint(0, 1000),
    }
    sql = """
    INSERT INTO sources (
        uuid,
        journalist_designation,
        last_updated,
        interaction_count
    )
    VALUES (
        :uuid,
        :journalist_designation,
        :last_updated,
        :interaction_count
    )
    """
    session.execute(text(sql), **params)


def add_journalist(session: Session) -> None:
    if random_bool():
        otp_secret = random_chars(16, string.ascii_uppercase + "234567")
    else:
        otp_secret = None

    is_totp = random_bool()
    if is_totp:
        hotp_counter = 0 if random_bool() else None
    else:
        hotp_counter = random.randint(0, 10000) if random_bool() else None

    last_token = random_chars(6, string.digits) if random_bool() else None

    params = {
        "uuid": str(uuid4()),
        "username": random_username(),
        "session_nonce": 0,
        "pw_salt": random_bytes(1, 64, nullable=True),
        "pw_hash": random_bytes(32, 64, nullable=True),
        "is_admin": bool_or_none(),
        "otp_secret": otp_secret,
        "is_totp": is_totp,
        "hotp_counter": hotp_counter,
        "last_token": last_token,
        "created_on": random_datetime(nullable=True),
        "last_access": random_datetime(nullable=True),
    }
    sql = """
    INSERT INTO journalists (
        uuid,
        username,
        session_nonce,
        pw_salt,
        pw_hash,
        is_admin,
        otp_secret,
        is_totp,
        hotp_counter,
        last_token,
        created_on,
        last_access
    )
    VALUES (
        :uuid,
        :username,
        :session_nonce,
        :pw_salt,
        :pw_hash,
        :is_admin,
        :otp_secret,
        :is_totp,
        :hotp_counter,
        :last_token,
        :created_on,
        :last_access
    );
    """
    session.execute(text(sql), **params)


def add_reply(session: Session, journalist_id: int, source_id: int) -> None:
    params = {
        "uuid": str(uuid4()),
        "journalist_id": journalist_id,
        "source_id": source_id,
        "filename": random_chars(50),
        "size": random.randint(0, 1024 * 1024 * 500),
        "deleted_by_source": 0,
    }
    sql = """
    INSERT INTO replies (uuid, journalist_id, source_id, filename, size, deleted_by_source)
    VALUES (:uuid, :journalist_id, :source_id, :filename, :size, :deleted_by_source)
    """
    session.execute(text(sql), **params)


def add_message(session: Session, source_id: int) -> None:
    params = {
        "uuid": str(uuid4()),
        "source_id": source_id,
        "filename": random_chars(50) + "-msg.gpg",
        "size": random.randint(0, 1024 * 1024 * 500),
        "downloaded": random.choice([True, False]),
    }
    sql = """
    INSERT INTO submissions (uuid, source_id, filename, size, downloaded)
    VALUES (:uuid, :source_id, :filename, :size, :downloaded)
    """
    session.execute(text(sql), **params)


def add_file(session: Session, source_id: int) -> None:
    params = {
        "uuid": str(uuid4()),
        "source_id": source_id,
        "filename": random_chars(50) + "-doc.gz.gpg",
        "size": random.randint(0, 1024 * 1024 * 500),
        "downloaded": random.choice([True, False]),
        "checksum": "sha256:" + random_chars(64),
    }
    sql = """
    INSERT INTO submissions (uuid, source_id, filename, size, downloaded, checksum)
    VALUES (:uuid, :source_id, :filename, :size, :downloaded, :checksum)
    """
    session.execute(text(sql), **params)


def mark_reply_as_seen(session: Session, reply_id: int, journalist_id: int) -> None:
    params = {
        "reply_id": reply_id,
        "journalist_id": journalist_id,
    }
    sql = """
    INSERT INTO seen_replies (reply_id, journalist_id)
    VALUES (:reply_id, :journalist_id)
    """
    try:
        session.execute(text(sql), **params)
    except IntegrityError:
        pass


def mark_file_as_seen(session: Session, file_id: int, journalist_id: int) -> None:
    params = {
        "file_id": file_id,
        "journalist_id": journalist_id,
    }
    sql = """
    INSERT INTO seen_files (file_id, journalist_id)
    VALUES (:file_id, :journalist_id)
    """
    try:
        session.execute(text(sql), **params)
    except IntegrityError:
        pass


def mark_message_as_seen(session: Session, message_id: int, journalist_id: int) -> None:
    params = {
        "message_id": message_id,
        "journalist_id": journalist_id,
    }
    sql = """
    INSERT INTO seen_messages (message_id, journalist_id)
    VALUES (:message_id, :journalist_id)
    """
    try:
        session.execute(text(sql), **params)
    except IntegrityError:
        pass
