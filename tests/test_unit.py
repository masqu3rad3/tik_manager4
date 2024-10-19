import pytest
from pathlib import Path
import platform
import os
import subprocess
import http.client
import json
from collections.abc import Mapping

# ENTITY LEVEL

def merge_dicts(original, overrides):
    """
    Recursively merge two dictionaries, giving priority to overrides.
    """
    for key, value in overrides.items():
        if isinstance(value, Mapping):
            original[key] = merge_dicts(original.get(key, {}), value)
        elif isinstance(value, list) and isinstance(original.get(key), list):
            # Merge lists by index if necessary
            for idx, item in enumerate(value):
                if isinstance(item, Mapping) and idx < len(original[key]):
                    original[key][idx] = merge_dicts(original[key][idx], item)
                else:
                    original[key][idx] = item
        else:
            original[key] = value
    return original

def generate_mocked_release_info(override=None, merge=None):
    """Generates a mocked release info.

    Args:
        override_keys (dict, optional): Keys to override. Defaults to None.
    """
    mock_release_info = {
        "url": "https://api.github.com/repos/masqu3rad3/tik_manager4/releases/168612599",
        "assets_url": "https://api.github.com/repos/masqu3rad3/tik_manager4/releases/168612599/assets",
        "upload_url": "https://uploads.github.com/repos/masqu3rad3/tik_manager4/releases/168612599/assets{?name,label}",
        "html_url": "https://github.com/masqu3rad3/tik_manager4/releases/tag/v4.2.0",
        "id": 168612599,
        "author": {
            "login": "masqu3rad3",
            "id": 17269286,
            "node_id": "MDQ6VXNlcjE3MjY5Mjg2",
            "avatar_url": "https://avatars.githubusercontent.com/u/17269286?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/masqu3rad3",
            "html_url": "https://github.com/masqu3rad3",
            "followers_url": "https://api.github.com/users/masqu3rad3/followers",
            "following_url": "https://api.github.com/users/masqu3rad3/following{/other_user}",
            "gists_url": "https://api.github.com/users/masqu3rad3/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/masqu3rad3/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/masqu3rad3/subscriptions",
            "organizations_url": "https://api.github.com/users/masqu3rad3/orgs",
            "repos_url": "https://api.github.com/users/masqu3rad3/repos",
            "events_url": "https://api.github.com/users/masqu3rad3/events{/privacy}",
            "received_events_url": "https://api.github.com/users/masqu3rad3/received_events",
            "type": "User",
            "site_admin": False,
        },
        "node_id": "RE_kwDOGaS8oM4KDNL3",
        "tag_name": "v1.0.0",
        "target_commitish": "main",
        "name": "v4.2.0",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-08-04T16:53:20Z",
        "published_at": "2024-08-04T17:01:06Z",
        "assets": [
            {
                "url": "https://api.github.com/repos/masqu3rad3/tik_manager4/releases/assets/183837851",
                "id": 183837851,
                "node_id": "RA_kwDOGaS8oM4K9SSb",
                "name": "TikManager4_v4.2.0.exe",
                "label": None,
                "uploader": {
                    "login": "masqu3rad3",
                    "id": 17269286,
                    "node_id": "MDQ6VXNlcjE3MjY5Mjg2",
                    "avatar_url": "https://avatars.githubusercontent.com/u/17269286?v=4",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/masqu3rad3",
                    "html_url": "https://github.com/masqu3rad3",
                    "followers_url": "https://api.github.com/users/masqu3rad3/followers",
                    "following_url": "https://api.github.com/users/masqu3rad3/following{/other_user}",
                    "gists_url": "https://api.github.com/users/masqu3rad3/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/masqu3rad3/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/masqu3rad3/subscriptions",
                    "organizations_url": "https://api.github.com/users/masqu3rad3/orgs",
                    "repos_url": "https://api.github.com/users/masqu3rad3/repos",
                    "events_url": "https://api.github.com/users/masqu3rad3/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/masqu3rad3/received_events",
                    "type": "User",
                    "site_admin": False,
                },
                "content_type": "application/x-msdownload",
                "state": "uploaded",
                "size": 69252829,
                "download_count": 10,
                "created_at": "2024-08-04T17:00:38Z",
                "updated_at": "2024-08-04T17:01:01Z",
                "browser_download_url": "https://github.com/masqu3rad3/tik_manager4/releases/download/v4.2.0/TikManager4_v4.2.0.exe",
            }
        ],
        "tarball_url": "https://api.github.com/repos/masqu3rad3/tik_manager4/tarball/v4.2.0",
        "zipball_url": "https://api.github.com/repos/masqu3rad3/tik_manager4/zipball/v4.2.0",
        "body": "## What's Changed\r\n\r\n**Major Updates:**\r\n- New Bundle Ingest Dialog introduced which will make it possible to ingest individual elements from bundled publishes.\r\n- Render extractor added to the nuke (this needs to be added to the target categories from the 'category definitions' section from project and/or common settings)\r\n- Preview extractor added to Maya which will allow multi-playblast publishes.\r\n- Image Plane ingestor added to Maya to create image planes from extracted elements or snapshot publishes\r\n- Sequence ingestor added to Nuke to import published (or snapshot published) elements.\r\n\r\n**Other Updates:**\r\n* Tik 129 when creating a new task populated categories sometimes is not correct by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/120\r\n* 119 410 check for updates not working by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/121\r\n* 115 substance painter select channels format and resolution to export by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/122\r\n* security update for urllib3 dependency by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/123\r\n* Documentation updates by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/127\r\n* Bump certifi from 2024.6.2 to 2024.7.4 in /docs by @dependabot in https://github.com/masqu3rad3/tik_manager4/pull/128\r\n* Hotfix by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/129\r\n* Tik 132 improved ingesting methodology supporting bundles better by @masqu3rad3 in https://github.com/masqu3rad3/tik_manager4/pull/131\r\n\r\n## New Contributors\r\n* @dependabot made their first contribution in https://github.com/masqu3rad3/tik_manager4/pull/128\r\n\r\n**Full Changelog**: https://github.com/masqu3rad3/tik_manager4/compare/v4.1.1...v4.2.0\r\n",
        "discussion_url": "https://github.com/masqu3rad3/tik_manager4/discussions/132",
        "mentions_count": 2,
    }
    if override:
        mock_release_info.update(override)

    if merge:
        mock_release_info = merge_dicts(mock_release_info, merge)

    return mock_release_info
def test_override_keys():
    from pprint import pprint

    merge = {"assets": [{"name": "TikManager4_v4.2.0.dmg"}]}
    test = generate_mocked_release_info(merge=merge)
    pprint(test)


@pytest.mark.parametrize(
    "is_file, system, expected_cmd",
    [
        (True, "Windows", None),  # Windows, path is a file
        (False, "Windows", None),  # Windows, path is a directory
        (True, "Linux", ["xdg-open", "sample"]),  # Linux, path is a file
        (False, "Linux", ["xdg-open", "sample"]),  # Linux, path is a directory
        (True, "Darwin", ["open", "sample"]),  # macOS, path is a file
        (False, "Darwin", ["open", "sample"]),  # macOS, path is a directory
    ],
)
def test_opening_a_folder(tik, is_file, system, expected_cmd, monkeypatch):
    """Tests opening a folder."""
    tik.project.__init__()
    tik.user.__init__()

    target = "sample" if not is_file else "sample.txt"

    # Monkeypatching Path.is_file to return is_file
    monkeypatch.setattr(Path, "is_file", lambda x: is_file)

    # Monkeypatching platform.system to return the specific OS
    monkeypatch.setattr(platform, "system", lambda: system)

    # Tracking calls to os.startfile and subprocess.Popen
    startfile_called = []
    popen_called = []

    def mock_startfile(target):
        startfile_called.append(target)

    def mock_popen(cmd):
        popen_called.append(cmd)

    # Only monkeypatch os.startfile if running on Windows
    # Monkeypatch os.startfile (even if it doesn't exist, which is fine)
    monkeypatch.setattr(os, "startfile", mock_startfile, raising=False)
    monkeypatch.setattr(subprocess, "Popen", mock_popen)

    tik.project._open_folder(target)

    if system == "Windows":
        assert startfile_called == ["sample"]
        assert popen_called == []
    else:
        assert startfile_called == []
        assert popen_called == [expected_cmd]

    # since we already mocked the function, test the show project folder
    tik.project.show_project_folder()
    tik.project.show_database_folder()


def test_copying_path_to_clipboard(tik, monkeypatch):
    """Tests copying a path to the clipboard."""
    tik.project.__init__()
    tik.user.__init__()

    # Tracking calls to pyperclip.copy
    copied = []

    def mock_copy(target):
        copied.append(target)

    monkeypatch.setattr("tik_manager4.external.pyperclip.copy", mock_copy)

    tik.project.copy_path_to_clipboard("sample")
    assert copied == ["sample"]


def test_getting_metadata(tik, monkeypatch):
    """Test getting the metadata of the entity."""
    tik.project.__init__()
    tik.user.__init__()
    assert tik.project.get_metadata(parent_task=None, key=None) == None

    tasks = tik.project.scan_tasks()

    assert tik.project.get_metadata(tasks["main"]) == {}

    # # mock the metadata
    monkeypatch.setattr(
        tasks["main"].metadata, "get_value", lambda _key, _: "monkeypatched_version"
    )

    tik.project._metadata.add_item("key", "monkeypatched_version")

    assert tik.project.get_metadata(tasks["main"], "key") == "monkeypatched_version"
    monkeypatch.undo()

    monkeypatch.setattr(tasks["main"], "_parent_sub", None)
    assert tik.project.get_metadata(tasks["main"], "key") == None
    monkeypatch.undo()


def test_resolving_dcc_names_from_extensions(tik):
    """Test resolving the DCC names from extensions."""

    tik.project.__init__()
    tik.user.__init__()
    assert tik._Main__resolve_dcc_name_from_extension(".ma") == "maya"
    assert tik._Main__resolve_dcc_name_from_extension(".hip") == "houdini"
    assert tik._Main__resolve_dcc_name_from_extension(".UNKNOWN") == "standalone"


# Assuming ReleaseObject is defined in the same module or imported appropriately


def test_get_latest_release_success(tik, monkeypatch):
    tik.project.__init__()
    tik.user.__init__()

    # Sample response data to mock
    mock_release_info = generate_mocked_release_info()

    class MockHTTPSConnection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, method, url, headers):
            assert method == "GET"
            assert url == "/repos/masqu3rad3/tik_manager4/releases/latest"
            assert headers == {"User-Agent": "MyApp"}

        def getresponse(self):
            class MockResponse:
                status = 200

                def read(self):
                    return json.dumps(mock_release_info).encode("utf-8")

            return MockResponse()

        def close(self):
            pass

    monkeypatch.setattr(http.client, "HTTPSConnection", MockHTTPSConnection)

    # Call the method
    result = tik.get_latest_release()

    # Assertions
    assert result._dict == mock_release_info


def test_get_latest_release_failure(tik, monkeypatch):
    tik.project.__init__()
    tik.user.__init__()

    class MockHTTPSConnection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, method, url, headers):
            pass

        def getresponse(self):
            class MockResponse:
                status = 500

                def read(self):
                    return ""

            return MockResponse()

        def close(self):
            pass

    monkeypatch.setattr(http.client, "HTTPSConnection", MockHTTPSConnection)

    # Call the method
    result = tik.get_latest_release()

    # Assertions
    assert result is None


def test_get_latest_release_connection_error(tik, monkeypatch):
    tik.project.__init__()
    tik.user.__init__()

    class MockHTTPSConnection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, method, url, headers):
            raise ConnectionError("Simulated connection error")

        def close(self):
            pass

    monkeypatch.setattr(http.client, "HTTPSConnection", MockHTTPSConnection)

    # Call the method
    result = tik.get_latest_release()

    # Assertions
    assert result is None
    assert tik.log.get_last_message() == (
        "Connection error to github. Check your internet connection",
        "error",
    )


@pytest.mark.parametrize(
    "system, merge_override",
    [
        ("windows", {"assets": [{"name": "TikManager4_v4.2.0.exe"}]}),
        ("mac", {"assets": [{"name": "TikManager4_v4.2.0.dmg"}]}),
        ("debian", {"assets": [{"name": "TikManager4_v4.2.0.deb"}]}),
        ("redhat", {"assets": [{"name": "TikManager4_v4.2.0.rpm"}]})
    ]
)
def test_release_object(tik, system, merge_override):
    mock_release_info = generate_mocked_release_info(merge=merge_override)

    import tik_manager4.objects.main

    release_object = tik_manager4.objects.main.ReleaseObject(mock_release_info)

    assert release_object._dict == mock_release_info
    assert release_object.name == mock_release_info.get("name")
    assert release_object.version.base_version == "1.0.0"
    assert release_object.collect_links()
    installers = {
        "windows": release_object.windows_installer,
        "mac": release_object.mac_installer,
        "debian": release_object.debian_installer,
        "redhat": release_object.redhat_installer,
    }
    assert installers[system]
    assert release_object.tarball == mock_release_info.get("tarball_url")
    assert release_object.zipball == mock_release_info.get("zipball_url")
    assert release_object.is_newer == False
    assert release_object.release_notes == mock_release_info.get("body")

def test_metadata_overrides():
    from tik_manager4.objects.metadata import Metadata
    sample_dict = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    metadata = Metadata(sample_dict)
    assert metadata.is_overridden("key1") == False

    # test if the key doesn't exist
    assert metadata.exists("key4") == False
    assert metadata.is_overridden("key4") == False

    # override it
    metadata.override({"key1": "new_value1"})
    assert metadata.is_overridden("key1") == True