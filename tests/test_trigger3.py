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


@pytest.fixture(scope="session")
def qapp():
    """A QApplication for the widget tests; offscreen under mayapy."""
    from tik_manager4.ui.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


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


class _Feedback:
    """The one dialog ``save_prompt`` opens, answered by the test."""

    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def browse_save(self, caption="Save", start="", extensions=()):
        self.calls.append((caption, start, tuple(extensions)))
        return self.answer


class _Guides:
    """A stand-in for ``Session.guides``: Maya is never started here."""

    def __init__(self):
        self.imported = []

    def import_(self, path):
        self.imported.append(str(path))


def _rig_work(tik3, tmp_path, name="hero"):
    sub = tik3.project.create_sub_project("assets", mode="asset", parent_path="")
    task = tik3.project.create_task("hero", categories=["Rig"], parent_path=sub.path)
    definitions = tik3.project.category_definitions
    rig = dict(definitions.get_property("Rig"))
    rig["extracts"] = ["source", "guides", "rig"]
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


def test_save_prompt_asks_where_a_never_saved_session_goes(tik3, tmp_path):
    session = Session()
    target = tmp_path / "asked.tr"
    feedback = _Feedback(str(target))
    vcs.host.attach(session=session, feedback=lambda: feedback)
    dcc = tik3.dcc
    assert dcc.get_scene_file() == ""  # the only state save_prompt is called in
    assert dcc.save_prompt() is True
    assert target.exists() and session.file_path == target
    assert feedback.calls[0][2] == (".tr",)
    # once it has a file, it saves in place without asking again.
    assert dcc.save_prompt() is True
    assert len(feedback.calls) == 1


def test_save_prompt_refuses_when_the_user_cancels(tik3, tmp_path):
    session = Session()
    feedback = _Feedback("")
    vcs.host.attach(session=session, feedback=lambda: feedback)
    assert tik3.dcc.save_prompt() is False
    assert session.file_path is None
    assert list(tmp_path.glob("*.tr")) == []


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


def test_dcc_open_resolves_a_bundle_folder(tik3, tmp_path):
    """Publish.load_version hands the DCC handler the SOURCE_ folder itself."""
    bundle = tmp_path / "SOURCE_hero_v001"
    bundle.mkdir()
    Session().save(bundle / "x.tr")
    vcs.host.attach(session=Session())
    tik3.dcc.open(str(bundle))
    assert vcs.host.session_path.endswith("x.tr")


def test_guides_ingest_imports_into_the_active_session(tik3, tmp_path, monkeypatch):
    from tik_manager4.dcc.trigger3.ingest.guides import Guides

    guides = _Guides()
    monkeypatch.setattr(Session, "guides", property(lambda self: guides))
    trg = tmp_path / "library.trg"
    trg.write_text("{}", encoding="utf-8")
    vcs.host.attach(session=Session())
    ingest = Guides()
    ingest.ingest_path = str(trg)
    ingest.bring_in()
    assert ingest.state == "success"
    assert guides.imported == [str(trg)]


def test_guides_ingest_fails_without_a_session(tik3, tmp_path):
    from tik_manager4.dcc.trigger3.ingest.guides import Guides

    trg = tmp_path / "library.trg"
    trg.write_text("{}", encoding="utf-8")
    vcs.host.detach()
    ingest = Guides()
    ingest.ingest_path = str(trg)
    ingest.bring_in()
    assert ingest.state == "failed"


def _plugins_root():
    """The external plugin root shipped with the trigger3 DCC."""
    root = Path(__file__).resolve().parents[1]
    return root / "tik_manager4" / "dcc" / "trigger3" / "plugins"


def test_provider_registers_and_reads_context(tik3, tmp_path):
    import tik.trigger as trigger

    trigger.add_plugin_path(_plugins_root())
    trigger.load_plugins()
    provider = vcs.get_provider("tik_manager")()
    assert provider.available() is True
    assert provider.display_label() == "Tik Manager"
    assert provider.icon_path() is not None
    assert provider.context(str(tmp_path / "loose.tr")) is None
    _task, work, session = _rig_work(tik3, tmp_path)
    context = provider.context(str(session.file_path))
    assert context.label.endswith("hero") and context.version == 1 and context.is_latest


def test_provider_new_version_iterates_the_work(tik3, tmp_path):
    # never import the plugin by its dotted tik_manager4 path: the plugin
    # loader imports it as ``tik_manager.tik_manager`` and a second module
    # object would register the provider twice
    import tik.trigger as trigger

    trigger.add_plugin_path(_plugins_root())
    trigger.load_plugins()
    provider = vcs.get_provider("tik_manager")()
    _task, work, session = _rig_work(tik3, tmp_path)
    path = provider.new_version(vcs.host)
    assert path.endswith("_v002.tr")
    work.reload()
    assert work.version_count == 2


def test_picker_resolves_a_work_version(tik3, tmp_path, qapp):
    from tik_manager4.dcc.trigger3.picker import TikPickerDialog

    _task, work, session = _rig_work(tik3, tmp_path)
    dialog = TikPickerDialog(tik3, "session", [".tr"])
    dialog.select_work(work)
    assert dialog.chosen_path().endswith("hero_v001.tr")
    assert dialog.use_button.isEnabled()


def test_picker_cannot_load_a_version_into_the_session(tik3, tmp_path, qapp):
    """The picker picks; Load/Import/Reference would open or import a scene."""
    from tik_manager4.dcc.trigger3.picker import TikPickerDialog

    _task, work, session = _rig_work(tik3, tmp_path)
    dialog = TikPickerDialog(tik3, "session", [".tr"])
    buttons = dialog.versions.buttons
    # isVisibleTo, not isHidden: a never-shown dialog's children all read as
    # hidden, so only "would you show with the dialog?" is a real assertion.
    for name in TikPickerDialog.ACTION_BUTTONS:
        assert not getattr(buttons, name).isVisibleTo(dialog), name
    assert dialog.use_button.isVisibleTo(dialog)
    # button_states re-shows some of them with every base; they stay hidden.
    dialog.select_work(work)
    for name in TikPickerDialog.ACTION_BUTTONS:
        button = getattr(buttons, name)
        assert not button.isVisibleTo(dialog) and not button.isEnabled(), name


def test_tik_publish_registers_a_publish_version_with_three_elements(tik3, tmp_path):
    import tik.trigger as trigger
    from tik.trigger.core import ActionContext, registry

    trigger.add_plugin_path(_plugins_root())
    trigger.load_plugins()
    cls = registry.get_action("tik_publish")
    assert cls.scope == "publish"

    loose = Session()
    loose.save(tmp_path / "loose.tr")
    ctx = ActionContext(session=loose, base_dir=str(tmp_path))
    assert cls().validate(ctx) == [
        "tik_publish: the session is not saved in a Tik Manager work"
    ]

    _task, work, session = _rig_work(tik3, tmp_path)
    rig = tmp_path / "hero_rig.mb"
    rig.write_bytes(b"rig")
    trg = tmp_path / "hero.trg"
    trg.write_text("{}", encoding="utf-8")
    publish_set = PublishSet.collect(
        session.file_path, session.document, rig=rig, guides=trg
    )
    ctx = ActionContext(session=session, base_dir=session.directory)
    action = cls({"notes": "first"})
    assert action.validate(ctx) == []
    action.deliver(publish_set, ctx)

    work.publish.scan_publish_versions()
    published = work.publish.get_last_version()
    assert published == 1
    version = work.publish.get_version(1)
    assert sorted(version.element_types) == ["guides", "rig", "source"]
    assert version.notes == "first"
    bundle = Path(version.get_resolved_path(version.get_element_path("source")))
    # the bundle carries the session under its own name, which for a work
    # version is "<task>_<category>_<name>_v###.tr".
    assert (bundle / f"{work.name}_v001.tr").exists()


def test_tik_publish_discards_the_reservation_when_an_extract_fails(tik3, tmp_path):
    """A failed extract must leave no .tpub: it would scan as an empty version."""
    import tik.trigger as trigger
    from tik.trigger.core import ActionContext, registry
    from tik.trigger.core.exceptions import ActionExecutionError

    trigger.add_plugin_path(_plugins_root())
    trigger.load_plugins()
    cls = registry.get_action("tik_publish")

    _task, work, session = _rig_work(tik3, tmp_path)
    trg = tmp_path / "hero.trg"
    trg.write_text("{}", encoding="utf-8")
    # no rig artifact, so the rig extractor fails after source has written its
    # bundle -- the folder Publisher.discard cannot unlink on its own.
    publish_set = PublishSet.collect(session.file_path, session.document, guides=trg)
    ctx = ActionContext(session=session, base_dir=session.directory)
    with pytest.raises(ActionExecutionError, match="extract failed"):
        cls().deliver(publish_set, ctx)

    work.publish.scan_publish_versions()
    assert work.publish.get_last_version() == 0
    data_folder = Path(work.publish.get_publish_data_folder())
    assert list(data_folder.glob("*.tpub")) == []
    scene_folder = Path(work.publish.get_publish_project_folder())
    assert list(scene_folder.rglob("SOURCE_*")) == []
