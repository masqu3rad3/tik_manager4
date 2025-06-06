# Release Notes

## v4.4.0
- [TIK-176] Active Branching feature added. When the active branching is enabled (default on), users can reach dynamically updated LIVE and PRO branches. LIVE branch gets updated with each new publish. PRO branch can be promoted by admins at any time.
- [TIK-177] Fixed object orientation issue when exporting USD in Blender.
- [TIK-178] User password reset functionality added for admin roles which can be accessed from the settings.
- [TIK-176] Info dialog button added to the version layout. This button will pop-up a dialog with all version information for the selected version.
- [HOTFIX] Nuke sequence importers padding issue fixed.
- [TIK-179] Ability to save selections as work. This function is subject to availability of the DCC. Currently, it is available for Maya, 3dsMax, Nuke and Katana. The function can be accessed from main UI File menu.
- [TIK-174] Houdini LOP and SOP import HDAs updates. Added the 'Allow All Elements' checkbox to make the process of using custom extractors smoother.
- [TIK-181] Speed and memory optimizations. Now publish versions are only gets loaded when its needed.

## v4.3.8
- FBX bug with Maya fixed which was preventing animation baking. Additionally, 'animation only' option exposed to the fbx publishing ui.
- [224] Reference to scene option added to the work items right click menu.
- [TIK-170] Adding recent button to switch between common folders easily.
- [TIK-171] User will be notified when the common folder is changed. The user will be asked to restart the application to apply the changes.
- [TIK-173] Spinner precision issues fixed with UI definitions. Now users can pass the spinner precision values with "decimals" key in the UI definition.
- [TIK-169] Various improvements and fixes with user logins.
- [TIK-159] New workflow for commons-project integration. Now projects will be locked to certain commons. Users won't be able to set a particular project if they are not in the correct commons designated for that project. There is an option to set the project unrestricted (default unchecked) while creating a new project. All previous projects before this update will behave as unrestricted.
- [TIK-163] Methodology to create custom project templates. Users can set the existing project as a new template. The function can be reached from the File menu.
- [TIK-90] After publish, if there are warnings, publish dialog won't be destroyed giving a chance to the user to see the messages. If publish cancelled due to a failed extraction by user, the reserved stalk will be discarded.
- Bug fixed auto-capturing the thumbnail when user cancels selecting a file from the browser.
- [TIK-160] Users now can put their custom extractors, validators, ingestors or ui_extensions under the respective folders in <common folder>/plugins/<DCC>/
- [213] Regional Screen Capture functionality where the user can select a specific region of the screen to capture. This functionality can be reached from the right click menu of the thumbnail section of the main UI.
- [211] Handling kitsu related user login bug where the user gets an error when cancelling login.

## v4.3.7
- [206] Kitsu integration improvements.
- Minor fix for some missing icons.

## v4.3.6
- [TIK-152] Dcc Specific Utils methodology added. Similar to extractors, ingestors and validators, now it is possible to define DCC specific utilities, accessible from the Main UI.
- [TIK-39] Implementation of Purgatory. The deleted items (sub-projects, tasks, works, publishes and versions) are not permanently deleted anymore. They are moved to the purgatory and can be restored if needed with the exception of manual purge of purgatory.
- [TIK-151] Integration of Kitsu.
- Dockable UI for Maya.
- Fix for the resolution related error when replacing preview images.
- Referencing (Link) fix for Blender.
- Improved UI interactions, style changes and performance optimizations.
- Quicktime related error fix when taking playblasts from Maya. 
- Various minor bug fixes and improvements.

## v4.3.1
- [TIK-145] Added native DCC support for snapshots saves. Now the snapshotted works can be directly opened from related DCCs.
- [TIK-146] Making the validations and extracts orderable. The order can be arranged from the settings (per-project or common).
- FBX extractor and Ingestor for Blender. Thanks Hasan Civili for the contribution.
- Commercial Houdini SOP and LOP import HDAs.
- Additional validators for Maya:
    - `Empty Groups` to check if there are leftover empty groups in the scene.
    - `Non-centered Pivots` to validate all transform pivots are centered.
    - `UDIM-Crossing UVs` to check if the UV borders are passing their UDIM spaces.
    - `Overlapping UVs` Optimized algorithm to check the overlapping UVs which is up-to 5x faster than the previous version.
- Customizable Thumbnail Resolution. Now the thumbnail resolution can be defined in the preview_settings with `ThumbnailResolution` key.
- Various Bug Fixes and UI optimizations.

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