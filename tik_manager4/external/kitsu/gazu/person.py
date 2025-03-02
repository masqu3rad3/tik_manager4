from . import client as raw

from .sorting import sort_by_name
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)
from .cache import cache

default = raw.default_client


@cache
def all_organisations(client=default):
    """
    Returns:
        list: Organisations listed in database.
    """
    return sort_by_name(raw.fetch_all("organisations", client=client))


@cache
def all_departments(client=default):
    """
    Returns:
        list: Departments listed in database.
    """
    return sort_by_name(raw.fetch_all("departments", client=client))


@cache
def all_persons(client=default):
    """
    Returns:
        list: Persons listed in database.
    """
    return sort_by_name(raw.fetch_all("persons", client=client))


@cache
def get_time_spents_range(person_id, start_date, end_date, client=default):
    """
    Gets the time spents of the current user for the given date range.

    Args:
        person_id (str): An uuid identifying a person.
        start_date (str): The first day of the date range as a date string with
                          the following format: YYYY-MM-DD
        end_date (str): The last day of the date range as a date string with
                        the following format: YYYY-MM-DD
    Returns:
        list: All of the person's time spents
    """
    date_range = {
        "start_date": start_date,
        "end_date": end_date,
    }
    return raw.get(
        "/data/persons/{}/time-spents".format(person_id),
        params=date_range,
        client=client,
    )


def get_all_month_time_spents(id, date, client=default):
    """
    Args:
        id (str): An uuid identifying a person.
        date (datetime.date): The date of the month to query.

    Returns:
        list: All of the person's time spents for the given month.
    """
    date = date.strftime("%Y/%m")
    return raw.get(
        "data/persons/{}/time-spents/month/all/{}".format(id, date),
        client=client,
    )


@cache
def get_department_by_name(name, client=default):
    """
    Args:
        name (str): Department name.

    Returns:
        dict: Department corresponding to given name.
    """
    return raw.fetch_first(
        "departments",
        {"name": name},
        client=client,
    )


@cache
def get_department(department_id, client=default):
    """
    Args:
        department_id (str): An uuid identifying a department.

    Returns:
        dict: Department corresponding to given department_id.
    """
    return raw.fetch_one("departments", department_id, client=client)


@cache
def get_person(id, relations=False, client=default):
    """
    Args:
        id (str): An uuid identifying a person.
        relations (bool): Whether to get the relations for the given person.

    Returns:
        dict: Person corresponding to given id.
    """
    params = {"id": id}
    if not relations:
        params["relations"] = False

    return raw.fetch_first("persons", params=params, client=client)


@cache
def get_person_by_desktop_login(desktop_login, client=default):
    """
    Args:
        desktop_login (str): Login used to sign in on the desktop computer.

    Returns:
        dict: Person corresponding to given desktop computer login.
    """
    return raw.fetch_first(
        "persons",
        {"desktop_login": desktop_login, "is_bot": False},
        client=client,
    )


@cache
def get_person_by_email(email, client=default):
    """
    Args:
        email (str): User's email.

    Returns:
        dict:  Person corresponding to given email.
    """
    return raw.fetch_first(
        "persons", {"email": email, "is_bot": False}, client=client
    )


@cache
def get_person_by_full_name(
    full_name, first_name=None, last_name=None, client=default
):
    """
    Args:
        full_name (str): User's full name
        first_name (str): User's first name
        last_name (str): User's last name

    Returns:
        dict: Person corresponding to given name.
    """
    if first_name is not None and last_name is not None:
        return raw.fetch_first(
            "persons",
            {
                "first_name": first_name,
                "last_name": last_name,
                "is_bot": False,
            },
            client=client,
        )
    else:
        return raw.fetch_first(
            "persons",
            {"full_name": full_name, "is_bot": False},
            client=client,
        )


@cache
def get_person_url(person, client=default):
    """
    Args:
        person (str / dict): The person dict or the person ID.

    Returns:
        url (str): Web url associated to the given person
    """
    person = normalize_model_parameter(person)
    path = "{host}/people/{person_id}/"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        person_id=person["id"],
    )


@cache
def get_organisation(client=default):
    """
    Returns:
        dict: Database information for organisation linked to auth tokens.
    """
    return raw.get("auth/authenticated", client=client)["organisation"]


def new_department(name, color="", archived=False, client=default):
    """
    Create a new departement based on given parameters.

    Args:
        name (str): the name of the departement.
        color (str): the color of the departement.
        archived (bool): Whether the departement is archived or not.
    Returns:
        dict: Created departement.
    """
    department = get_department_by_name(name, client=client)
    if department is None:
        department = raw.post(
            "data/departments",
            {"name": name, "color": color, "archived": archived},
            client=client,
        )
    return department


def new_person(
    first_name,
    last_name,
    email,
    phone="",
    role="user",
    desktop_login="",
    departments=[],
    password=None,
    active=True,
    contract_type="open-ended",
    client=default,
):
    """
    Create a new person based on given parameters. His/her password will is
    set automatically to default.

    Args:
        first_name (str): the first name of the person.
        last_name (str): the last name of the person.
        email (str): the email of the person.
        phone (str): the phone number of the person.
        role (str): user, manager, admin (wich match CG artist, Supervisor
                    and studio manager)
        desktop_login (str): The login the users uses to log on its computer.
        departments (list): The departments for the person.
        password (str): The password for the person.
        active (bool): Whether the person is active or not.
    Returns:
        dict: Created person.
    """
    person = get_person_by_email(email, client=client)
    if person is None:
        person = raw.post(
            "data/persons",
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "role": role,
                "desktop_login": desktop_login,
                "departments": normalize_list_of_models_for_links(departments),
                "password": password,
                "active": active,
                "contract_type": contract_type,
            },
            client=client,
        )
    return person


def update_person(person, client=default):
    """
    Update a person.

    Args:
        person (dict): The person dict that needs to be upgraded.

    Returns:
        dict: The updated person.
    """

    if "departments" in person:
        person["departments"] = normalize_list_of_models_for_links(
            person["departments"]
        )

    person = normalize_model_parameter(person)
    return raw.put(
        "data/persons/%s" % (person["id"]),
        person,
        client=client,
    )


def remove_person(person, force=False, client=default):
    """
    Remove given person from database.

    Args:
        person (dict): Person to remove.
    """
    person = normalize_model_parameter(person)
    path = "data/persons/%s" % person["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def new_bot(
    name,
    email,
    role="user",
    departments=[],
    active=True,
    expiration_date=None,
    client=default,
):
    """
    Create a new bot based on given parameters. His access token will be in the
    return dict.

    Args:
        name (str): the name of the bot.
        email (str): the email of the bot.
        role (str): user, manager, admin (wich match CG artist, Supervisor
                    and studio manager)
        departments (list): The departments for the person.
        active (bool): Whether the person is active or not.
        expiration_date (str): The expiration date for the bot.
    Returns:
        dict: Created bot.
    """
    bot = raw.post(
        "data/persons",
        {
            "first_name": name,
            "last_name": "",
            "email": email,
            "role": role,
            "departments": normalize_list_of_models_for_links(departments),
            "active": active,
            "expiration_date": expiration_date,
            "is_bot": True,
        },
        client=client,
    )
    return bot


def update_bot(bot, client=default):
    """
    Update a bot.

    Args:
        bot (dict): The bot dict that needs to be upgraded.

    Returns:
        dict: The updated bot.
    """
    return update_person(bot, client=client)


def remove_bot(bot, force=False, client=default):
    """
    Remove given bot from database.

    Args:
        bot (dict): Bot to remove.
    """
    return remove_person(bot, force=force, client=client)


def set_avatar(person, file_path, client=default):
    """
    Upload picture and set it as avatar for given person.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): Path where the avatar file is located on the hard
                         drive.
    """
    person = normalize_model_parameter(person)
    return raw.upload(
        "/pictures/thumbnails/persons/%s" % person["id"],
        file_path,
        client=client,
    )


def get_presence_log(year, month, client=default):
    """
    Args:
        year (int):
        month (int):

    Returns:
        The presence log table for given month and year.
    """
    path = "data/persons/presence-logs/%s-%s" % (year, str(month).zfill(2))
    return raw.get(path, json_response=False, client=client)


def change_password_for_person(person, password, client=default):
    """
    Change the password for given person.

    Args:
        person (str / dict): The person dict or the person ID.
        password (str): The new password.
    Returns:
        dict: success or not.
    """
    person = normalize_model_parameter(person)
    return raw.post(
        "actions/persons/%s/change-password" % (person["id"]),
        {"password": password, "password_2": password},
        client=client,
    )
