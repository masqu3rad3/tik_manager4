"""The trigger3 DCC: Trigger through its version control host.

Run under mayapy with tikworks on PYTHONPATH:
    $env:PYTHONPATH="D:\\dev\\tikworks\\src\\python;D:\\dev\\tik_manager4"
    mayapy -m pytest tests/test_trigger3.py -q
"""

import shutil
from pathlib import Path

import pytest

pytest.importorskip("tik.trigger", reason="tikworks is not on PYTHONPATH")

from tik.trigger import vcs  # noqa: E402
from tik.trigger.core.publish_set import PublishSet  # noqa: E402
from tik.trigger.session import Session  # noqa: E402


@pytest.fixture
def tik3(tmp_path):
    """tik_manager4 initialised for trigger3 with a throwaway project and user."""
    import tik_manager4

    common = tmp_path / "common"
    common.mkdir()
    user_path = Path.home() / "TikManager4"
    backup = tmp_path / "user_backup"
    if user_path.exists():
        shutil.copytree(str(user_path), str(backup))
        shutil.rmtree(str(user_path))
    user_path.mkdir(parents=True, exist_ok=True)
    tik = tik_manager4.initialize("trigger3", common_folder=str(common))
    tik.user.set("Admin", "1234")
    project = tmp_path / "project"
    tik.create_project(str(project), structure_template="empty")
    tik.set_project(str(project))
    yield tik
    vcs.host.detach()
    shutil.rmtree(str(user_path), ignore_errors=True)
    if backup.exists():
        shutil.copytree(str(backup), str(user_path))


def _rig_work(tik3, tmp_path, name="hero"):
    sub = tik3.project.create_sub_project("assets", mode="asset", parent_path="")
    task = tik3.project.create_task("hero", categories=["Rig"], parent_path=sub.path)
    definitions = tik3.project.category_definitions
    rig = dict(definitions.get_property("Rig"))
    rig["extracts"] = ["source", "rig", "guides"]
    definitions.edit_property("Rig", rig)
    definitions.apply_settings(force=True)
    session = Session()
    vcs.host.attach(session=session)
    work = task.categories["Rig"].create_work(name)
    assert work != -1
    return task, work, session


def test_dcc_forwards_to_the_host(tik3, tmp_path):
    session = Session()
    vcs.host.attach(session=session)
    dcc = tik3.dcc
    assert dcc.name == "trigger3" and dcc.formats == [".tr"]
    assert dcc.get_scene_file() == ""
    assert dcc.is_modified() is False
    saved = dcc.save_as(str(tmp_path / "hero.tr"))
    assert Path(saved).name == "hero.tr"
    assert dcc.get_scene_file().endswith("hero.tr")
    other = Session()
    other.save(tmp_path / "other.tr")
    dcc.open(str(tmp_path / "other.tr"))
    assert dcc.get_scene_file().endswith("other.tr")
    assert dcc.get_dcc_version()


def test_create_work_saves_the_session_as_a_tik_version(tik3, tmp_path):
    _task, work, session = _rig_work(tik3, tmp_path)
    assert session.file_path is not None and session.file_path.suffix == ".tr"
    assert work.versions[-1].file_format == ".tr"
    found, version = tik3.project.find_work_by_absolute_path(str(session.file_path))
    # tik_manager4 names a work <task>_<category>_<name>, e.g. "hero_Rig_hero".
    assert found.name == work.name and version == 1


def test_extractors_write_from_a_prebuilt_publish_set(tik3, tmp_path):
    from tik_manager4.dcc.trigger3.extract.guides import Guides
    from tik_manager4.dcc.trigger3.extract.rig import Rig
    from tik_manager4.dcc.trigger3.extract.source import Source

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    session = Session()
    session.save(work_dir / "hero.tr")
    rig = work_dir / "hero_rig.mb"
    rig.write_bytes(b"rig")
    trg = work_dir / "hero.trg"
    trg.write_text("{}", encoding="utf-8")
    publish_set = PublishSet.collect(
        session.file_path, session.document, rig=rig, guides=trg
    )
    out = tmp_path / "out"
    for cls, suffix in ((Source, ""), (Rig, ".mb"), (Guides, ".trg")):
        extractor = cls()
        extractor.set_publish_set(publish_set)
        extractor.extract_folder = str(out)
        extractor.extract_name = "hero"
        extractor.version_string = "v001"
        extractor.extract()
        assert extractor.state == "success", extractor.message
        assert Path(extractor.resolve_output()).exists()
        assert extractor.resolve_output().endswith(suffix)
    bundle = Path(Source().resolve_output_for(out, "hero", "v001"))
    assert (bundle / "hero.tr").exists() and (bundle / "manifest.json").exists()


def test_source_bundle_info_lists_every_file(tik3, tmp_path):
    from tik_manager4.dcc.trigger3.extract.source import Source

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    session = Session()
    session.save(work_dir / "hero.tr")
    trg = work_dir / "hero.trg"
    trg.write_text("{}", encoding="utf-8")
    extractor = Source()
    extractor.set_publish_set(
        PublishSet.collect(session.file_path, session.document, guides=trg)
    )
    extractor.extract_folder = str(tmp_path / "out")
    extractor.extract_name = "hero"
    extractor.version_string = "v001"
    extractor.extract()
    assert extractor.state == "success", extractor.message
    # the session and the guides share a stem; both must be listed.
    assert set(extractor.bundle_info) == {"hero.tr", "hero.trg", "manifest.json"}
    assert extractor.bundle_info["hero.tr"]["extension"] == ".tr"


def test_source_ingest_opens_the_bundled_session(tik3, tmp_path):
    from tik_manager4.dcc.trigger3.ingest.source import Source

    bundle = tmp_path / "SOURCE_hero_v001"
    bundle.mkdir()
    Session().save(bundle / "hero.tr")
    session = Session()
    vcs.host.attach(session=session)
    ingest = Source()
    ingest.ingest_path = str(bundle)
    ingest.bring_in()
    assert ingest.state == "success"
    assert vcs.host.session_path.endswith("hero.tr")
