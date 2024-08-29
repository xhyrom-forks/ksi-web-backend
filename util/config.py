import os
from typing import Optional, List, Dict, TypedDict

from db import session
import model

MAX_UPLOAD_FILE_SIZE = 25 * 1024 ** 2  # set to slightly larger than on FE as to prevent MB vs MiB mismatches
MAX_UPLOAD_FILE_COUNT = 20


class ConfigRecord(TypedDict):
    key: str
    value: str


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a property from the config table in database
    If key does not exist, then default value is returned
    :param key: key to get value for
    :param default: default value in case the key does not exist
    :return: value in database if the key exists, default otherwise
    """
    prop = session.query(model.Config).get(key)
    return prop.value if prop is not None and prop.value is not None else default


def set_config(key: str, value: str):
    """
    Set a property in the config table in database
    :param key: key to set value for
    :param value: value to set
    """
    prop = session.query(model.Config).get(key)
    if prop is None:
        prop = model.Config(key=key, value=value)
        session.add(prop)
    else:
        prop.value = value
    session.commit()


def get_all(include_secret: bool = True) -> Dict[str, ConfigRecord]:
    """
    Get all properties from the config table in database
    :param include_secret: whether to include secret properties
    :return: dictionary of all properties
    """
    return {prop.key: {'key': prop.key, 'value': prop.value} for prop in session.query(model.Config).all() if not prop.secret or include_secret}


def ksi_conf() -> str:
    """
    Get the email address of the conference (== all emails will CC to this address)
    :return: email address of the conference
    """
    val = get("ksi_conf")
    assert val is not None, "ksi_conf is not set in the config table"
    return val


def mail_sign() -> Optional[str]:
    """
    Get the email signature
    :return: email signature
    """
    return get("mail_sign")


def ksi_web() -> str:
    """
    Get the root URL of the frontend website
    :return: root URL of the frontend website
    """
    return get("web_url", "https://ksi.fi.muni.cz/")


def ksi_web_admin() -> str:
    """
    Get the URL of the admin interface
    :return: URL of the admin interface
    """
    return get("web_url_admin", "https://ksi.fi.muni.cz/admin")


def mail_sender() -> Optional[str]:
    """
    Get the default mail sender
    If None, mails will never bee sent, but instead saved locally

    :return: default mail sender
    """
    return get("mail_sender")


def successful_participant_trophy_id() -> Optional[int]:
    """
    Get the ID of the trophy that is awarded to successful participants
    :return:  ID of the trophy that is awarded to successful participants
    """
    text = get('successful_participant_trophy_id')
    return int(text) if text is not None else None


def backend_url() -> str:
    """
    Get the URL of the backend
    :return: URL of the backend
    """
    return get("backend_url", "https://rest.ksi.fi.muni.cz")


def monitoring_dashboard_url() -> Optional[str]:
    """
    Get the URL of the monitoring dashboard
    :return: URL of the monitoring dashboard
    """
    return get("monitoring_dashboard_url")


def github_token() -> Optional[str]:
    """
    Get the OAuth2.0 personal access token for fi-ksi-admin GitHub account

    This token can be used for making requests to the GitHub API
    """
    return get("github_token")


def seminar_repo() -> Optional[str]:
    """
    Get the name of the seminar repository that contains tasks
    """
    return get("seminar_repo")


def github_api_org_url() -> Optional[str]:
    """
    Get the name of the seminar repository that contains tasks
    """
    return get("github_api_org_url")


def feedback() -> List[str]:
    """
    Get the list of email addresses that should receive feedback
    :return: list of email addresses that should receive feedback
    """
    return [r for r, in session.query(model.FeedbackRecipient.email).all()]


def discord_username_change_webhook() -> Optional[str]:
    """
    Get the webhook URL for Discord that should be called whenever a user changes their Discord username

    :return: webhook URL for Discord that should be called whenever a user changes their Discord username
    """
    return get("webhook_discord_username_change")


def discord_invite_link() -> Optional[str]:
    """
    Get the invite link to the Discord server

    :return: the invite link to the Discord server
    """
    return get("discord_invite_link")


def smtp_server() -> str:
    """
    Get the SMTP server address

    :return: the SMTP server address
    """
    return get("smtp_server", "relay.fi.muni.cz")


def unsuccessful_tries_per_day() -> int:
    """
    Get the number of unsuccessful tries per day per each module per user

    :return: the number of unsuccessful tries per day
    """
    return int(get("unsuccessful_tries_per_day", "20"))


def mail_subject_prefix() -> str:
    """
    Get the prefix of the email subjects

    :return: the prefix of the email subjects
    """
    return get("mail_subject_prefix", "[KSI]")


def seminar_name() -> str:
    """
    Get the name of the seminar

    :return: the name of the seminar
    """
    return get("seminar_name", "Korespondenční seminář z informatiky")


def mail_registration_welcome() -> str:
    """
    Get the email template for the registration welcome email

    :return: the email template for the registration welcome email
    """
    return get("mail_registration_welcome",
               "Korespondenčním semináři z informatiky Fakulty informatiky Masarykovy univerzity.")
