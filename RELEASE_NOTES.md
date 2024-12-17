# Release Notes

## v4.3.0
- [TIK-143] Localization and cache management feature added.
- [TIK-144] Improved filtering methodology for views.
- [TIK-142] Persistent UI size and position for the main window.
- [TIK-140] Shotgrid integration.
- [151] Added the ability to edit notes on works. Can be accessed with right-click context menu.
- Metadata improvements. Tasks can directly inherit and override metadata from upstream.

## v4.2.1
- individual photoshop image extracts merged into one extractor
- adding alembic and usd extractors to the 3ds max
- fixing the Autodesk 3ds Max auto installer
- introduce more unit tests
- usd reference function for houdini
- Houdini integration HDAs (currently non-commercial version only)

## v4.2.0
- New Bundle Ingest Dialog introduced which will make it possible to ingest individual elements from bundled publishes.
- Render extractor added to the nuke (this needs to be added to the target categories from the 'category definitions' section from project and/or common settings)
- Preview extractor added to Maya which will allow multi-playblast publishes.
- Image Plane ingestor added to Maya to create image planes from extracted elements or snapshot publishes
- Sequence ingestor added to Nuke to import published (or snapshot published) elements.
- [TIK-129] when creating a new task populated categories sometimes is not correct
- check for updates not working 
- substance painter select channels format and resolution to export
- security update for urllib3 dependency
- Documentation updates
- Bump certifi from 2024.6.2 to 2024.7.4 in /docs
- [TIK-132] improved ingesting methodology supporting bundles better by @masqu3rad3 in #131

## v4.1.1
- Adding mesh transform validation for Maya
- FBX extractor
- making the columns non-editable for task and category views
- hotfix for importomatic name
- Templating Methodology
- Ability to view publshed elements and defined the executable apps for them per user

## v4.1.0
- [TIK-116] bring back the custom thumbnail functionality
- [TIK-117] make the version owner visible in the version layout
- setting the project variables for gaffer when opening a work
- QT bind issue fixed for Katana when Renderman plugin loaded

## v4.0.91
- hotfix - blender thumbnail creation issue which causes errors on new

## v4.0.9
- [TIK-114] gaffer integration
- Deeper level sub-projects delete issue fix
- [TIK-115] substance painter integration

## v4.0.81
- linux compatibility hotfix for katana

## v4.0.8
- Windows installer and documentation update for Mari

## v4.0.7
- Initial Mari Integration

## v4.0.5
- Standard file publish method added
- Initial Trigger (modular rigging tool) implementation
- User Management and Password Change sections added to the settings menu.

## v4.0.3
- Foundry Katana integration.
- various UI updates.
- Blender file extension fixed.
- Blender thumbnails are fixed.
- Preview feature added to Blender and fixed for Houdini.
- various code optimizations and updates.