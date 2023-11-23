"""Class to control and revert all panel properties"""

from maya import cmds

class Variable(object):
    def __init__(self, original=None, current=None):
        super(Variable, self).__init__()
        self._originalValue = original
        self._currentValue = current

    @property
    def original(self):
        return self._originalValue

    @original.setter
    def original(self, val):
        self._originalValue = val

    @property
    def current(self):
        return self._currentValue or self._originalValue

    @current.setter
    def current(self, val):
        self._currentValue = val

class PanelManager(object):
    def __init__(self, camera, resolution, inherit=True):
        super(PanelManager, self).__init__()

        if not cmds.objExists(camera):
            raise Exception("%s does not exist" %camera)

        self._camera = camera
        self._activePanel = cmds.getPanel(wf=True)
        self._currentPanels = self.get_camera_panels(self._camera)
        print("currentPANELS", self._currentPanels)
        self._window, self._panel = self.tear_off_panel(camera=camera, resolution=resolution)

        # camera related variables
        self._fieldChart = Variable()
        self._gateMask = Variable()
        self._filmGate = Variable()
        self._filmOrigin = Variable()
        self._filmPivot = Variable()
        self._resolution = Variable()
        self._safeAction = Variable()
        self._safeTitle = Variable()
        self._overscan = Variable()

        # modelEditor variables
        self._allObjects = Variable()
        self._displayAppearance = Variable()
        self._diplayTextures = Variable()
        self._grid = Variable()
        self._useDefaultMaterial = Variable()
        self._polymeshes = Variable()
        self._nurbsCurves = Variable()
        self._nurbsSurfaces = Variable()
        self._imagePlane = Variable()
        self._hud = Variable()

        # inherit the existing panel properties
        if inherit:
            self.inherit_panel_properties()

        self.store_states()


    def store_states(self):
        """Grabs the current state of the properties and store them as original"""

        # set panel variables originals
        self._fieldChart.original = cmds.camera(self._camera, q=True, displayFieldChart=True)
        self._gateMask.original = cmds.camera(self._camera, q=True, displayGateMask=True)
        self._filmGate.original = cmds.camera(self._camera, q=True, displayFilmGate=True)
        self._filmOrigin.original = cmds.camera(self._camera, q=True, displayFilmOrigin=True)
        self._filmPivot.original = cmds.camera(self._camera, q=True, displayFilmPivot=True)
        self._resolution.original = cmds.camera(self._camera, q=True, displayResolution=True)
        self._safeAction.original = cmds.camera(self._camera, q=True, displaySafeAction=True)
        self._safeTitle.original = cmds.camera(self._camera, q=True, displaySafeTitle=True)
        self._overscan.original = cmds.camera(self._camera, q=True, overscan=True)

    def inherit_panel_properties(self, panel=None):
        """
        if there are existing panels for the camera, this method will try to inherit the properties of the Active or LAST unless
        a panel specified
        """

        # override everything if panel defined
        if not panel:
            # In cases there are no existing panels for the camera abort
            if not self._currentPanels:
                return

            # in cases where multiple panels for the same camera
            if len(self._currentPanels) > 1:
                # give priority to the active view (if it belongs to the same camera)
                if self._activePanel in self._currentPanels:
                    panel = self._activePanel
                else:
                    # pick the panel before last one as last resort because last panel is the newly created one
                    panel = self._currentPanels[-2]
        else:
            panel = panel
        # try to get current camera panel
        panel = panel or self._currentPanels[0]


        model_vars = ["activeComponentsXray", "activeCustomGeometry", "activeCustomLighSet",
                      "activeCustomOverrideGeometry", "activeCustomRenderer", "activeOnly",
                      "activeShadingGraph", "activeView", "allObjects", "backfaceCulling",
                      "bufferMode", "bumpResolution", "camera", "cameras", "clipGhosts",
                      "cmEnabled", "colorResolution", "controlVertices", "cullingOverride",
                      "deformers", "dimensions", "displayAppearance", "displayLights", "displayTextures",
                      "dynamicConstraints", "dynamics", "exposure", "filter", "fluids", "fogColor",
                      "fogDensity", "fogEnd", "fogMode", "fogSource", "fogStart", "fogging", "follicles",
                      "gamma", "greasePencils", "grid", "hairSystems", "handles", "headsUpDisplay",
                      "highlightConnection", "hulls", "ignorePanZoom", "ikHandles", "imagePlane",
                      "interactive", "interactiveBackFaceCull", "interactiveDisableShadows", "jointXray",
                      "joints", "lights", "lineWidth", "locators", "lowQualityLighting", "mainListConnection",
                      "manipulators", "maxConstantTransparency", "maximumNumHardwareLights", "motionTrails",
                      "nCloths", "nParticles", "nRigids", "nurbsCurves", "nurbsSurfaces", "objectFilter",
                      "objectFilterShowInHUD", "occlusionCulling", "particleInstancers", "pivots",
                      "planes", "pluginShapes", "polymeshes", "rendererName",
                      "rendererOverrideName", "sceneRenderFilter", "selectionConnection",
                      "selectionHiliteDisplay", "shadingModel", "shadows", "smallObjectCulling",
                      "smoothWireframe", "sortTransparent", "stereoDrawMode",
                      "strokes", "subdivSurfaces", "textureAnisotropic", "textureCompression",
                      "textureDisplay", "textureEnvironmentMap", "textureHilight", "textureMaxSize",
                      "textureSampling", "textures", "transpInShadows", "transparencyAlgorithm",
                      "twoSidedLighting", "useBaseRenderer", "useColorIndex", "useDefaultMaterial",
                      "useInteractiveMode", "useRGBImagePlane", "useReducedRenderer", "viewSelected",
                      "viewTransformName", "wireframeBackingStore", "wireframeOnShaded", "xray"]

        for p in model_vars:
            try:
                cmd = "cmds.modelEditor(panel, q=True, %s=True)" %(p)
                val = eval(cmd)
                if val == None or val == "":
                    val = False
                self.set_editor_variable(p, val)
            except TypeError:
                pass

    #     _____          __  __ ______ _____
    #    / ____|   /\   |  \/  |  ____|  __ \     /\
    #   | |       /  \  | \  / | |__  | |__) |   /  \
    #   | |      / /\ \ | |\/| |  __| |  _  /   / /\ \
    #   | |____ / ____ \| |  | | |____| | \ \  / ____ \
    #    \_____/_/    \_\_|  |_|______|_|  \_\/_/    \_\
    #

    # CAMERA PROPERTIES NEEDS TO BE REVERTED BACK AFTER AS THEY ARE COMMON FOR ALL ACTIVE PANELS

    def set_camera_variable(self, variable, value):
        eval("cmds.camera(self._camera, e=True, {0}={1})".format(variable, value))

    @property
    def display_field_chart(self):
        return self._fieldChart.current

    @display_field_chart.setter
    def display_field_chart(self, val):
        # cmds.camera(self._camera, e=True, displayFieldChart=val)
        # self._fieldChart.current = val
        self._fieldChart.current = self.set_camera_variable("displayFieldChart", val)

    @property
    def display_gate_mask(self):
        return self._gateMask.current

    @display_gate_mask.setter
    def display_gate_mask(self, val):
        cmds.camera(self._camera, e=True, displayGateMask=val)
        self._gateMask.current = val

    @property
    def display_film_gate(self):
        return self._filmGate.current

    @display_film_gate.setter
    def display_film_gate(self, val):
        cmds.camera(self._camera, e=True, displayFilmGate=val)
        self._filmGate.current = val

    @property
    def display_film_origin(self):
        return self._filmOrigin.current

    @display_film_origin.setter
    def display_film_origin(self, val):
        cmds.camera(self._camera, e=True, displayFilmOrigin=val)
        self._filmOrigin.current = val

    @property
    def display_film_pivot(self):
        return self._filmPivot.current

    @display_film_pivot.setter
    def display_film_pivot(self, val):
        cmds.camera(self._camera, e=True, displayFilmPivot=val)
        self._filmPivot.current = val

    @property
    def display_resolution(self):
        return self._resolution.current

    @display_resolution.setter
    def display_resolution(self, val):
        cmds.camera(self._camera, e=True, displayResolution=val)
        self._resolution.current = val

    @property
    def display_safe_action(self):
        return self._safeAction.current

    @display_safe_action.setter
    def display_safe_action(self, val):
        cmds.camera(self._camera, e=True, displaySafeAction=val)
        self._safeAction.current = val

    @property
    def display_safe_title(self):
        return self._safeTitle.current

    @display_safe_title.setter
    def display_safe_title(self, val):
        cmds.camera(self._camera, e=True, displaySafeTitle=val)
        self._safeTitle.current = val

    @property
    def overscan(self):
        return self._overscan.current

    @overscan.setter
    def overscan(self, val):
        cmds.camera(self._camera, e=True, overscan=val)
        self._overscan.current = val

    #    __  __           _      _   ______    _ _ _
    #   |  \/  |         | |    | | |  ____|  | (_) |
    #   | \  / | ___   __| | ___| | | |__   __| |_| |_ ___  _ __
    #   | |\/| |/ _ \ / _` |/ _ \ | |  __| / _` | | __/ _ \| '__|
    #   | |  | | (_) | (_| |  __/ | | |___| (_| | | || (_) | |
    #   |_|  |_|\___/ \__,_|\___|_| |______\__,_|_|\__\___/|_|
    #

    # Model Editors are for panel only properties. They dont need to be stored

    def set_editor_variable(self, variable, value):
        if isinstance(value, str):
            cmd = "cmds.modelEditor(self._panel, e=True, {0}='{1}')".format(variable, value)
        else:
            cmd = "cmds.modelEditor(self._panel, e=True, {0}={1})".format(variable, value)
        try:
            eval(cmd)
        except:
            raise

    @property
    def panel(self):
        return self._panel

    @property
    def all_objects(self):
        return self._allObjects.current

    @all_objects.setter
    def all_objects(self, val):
        self.set_editor_variable("allObjects", val)

    @property
    def display_appearance(self):
        return self._displayAppearance.current

    @display_appearance.setter
    def display_appearance(self, val):
        self.set_editor_variable("displayAppearance", val)

    @property
    def diplay_textures(self):
        return self._diplayTextures.current

    @diplay_textures.setter
    def diplay_textures(self, val):
        self.set_editor_variable("diplayTextures", val)

    @property
    def grid(self):
        return self._grid.current

    @grid.setter
    def grid(self, val):
        self.set_editor_variable("grid", val)

    @property
    def use_default_material(self):
        return self._useDefaultMaterial

    @use_default_material.setter
    def use_default_material(self, val):
        self.set_editor_variable("useDefaultMaterial", val)

    @property
    def polymeshes(self):
        return self._polymeshes

    @polymeshes.setter
    def polymeshes(self, val):
        self.set_editor_variable("polymeshes", val)

    @property
    def nurbs_curves(self):
        return self._nurbsCurves

    @nurbs_curves.setter
    def nurbs_curves(self, val):
        self.set_editor_variable("nurbsCurves", val)

    @property
    def nurbs_surfaces(self):
        return self._nurbsSurfaces

    @nurbs_surfaces.setter
    def nurbs_surfaces(self, val):
        self.set_editor_variable("nurbsSurfaces", val)

    @property
    def image_plane(self):
        return self._imagePlane

    @image_plane.setter
    def image_plane(self, val):
        self.set_editor_variable("imagePlane", val)

    @property
    def hud(self):
        return self._hud

    @hud.setter
    def hud(self, val):
        self.set_editor_variable("hud", val)


    #    __  __ ______ _______ _    _  ____  _____   _____
    #   |  \/  |  ____|__   __| |  | |/ __ \|  __ \ / ____|
    #   | \  / | |__     | |  | |__| | |  | | |  | | (___
    #   | |\/| |  __|    | |  |  __  | |  | | |  | |\___ \
    #   | |  | | |____   | |  | |  | | |__| | |__| |____) |
    #   |_|  |_|______|  |_|  |_|  |_|\____/|_____/|_____/
    #
    #

    @staticmethod
    def get_camera_panels(camera):
        panel_list = []
        for panel_name in cmds.getPanel(type="modelPanel"):
            if cmds.modelPanel(panel_name, query=True, camera=True) == camera:
                panel_list.append(panel_name)
        return panel_list

    @staticmethod
    def tear_off_panel(camera, resolution=(1920, 1080)):
        """Tears of the panel with given resolution"""

        ## Compensate the menu bar for height:
        resolution = [resolution[0], resolution[1]+40]
        tempWindow = cmds.window(title="RBL_Playblast", widthHeight=(resolution[0], resolution[1]), tlc=(0, 0), tb=True, menuBarVisible=False)
        cmds.paneLayout()
        pb_panel = cmds.modelPanel(camera=camera)

        cmds.showWindow(tempWindow)
        return tempWindow, pb_panel

    def set_preset(self, preset):
        """Sets values for pre-defined presets"""

        # TODO: Do more presets
        if preset == "preview":
            # camera properties
            self.display_field_chart = False
            self.display_gate_mask = False
            self.display_film_gate = False
            self.display_film_origin = False
            self.display_film_pivot = False
            self.display_resolution = False
            self.display_safe_action = False
            self.display_safe_title = False

    def revert_all(self):
        """Reverts back all settings into its original state"""

        # get panel variables originals
        self.display_field_chart = self._fieldChart.original
        self.display_gate_mask = self._gateMask.original
        self.display_film_gate = self._filmGate.original
        self.display_film_origin = self._filmOrigin.original
        self.display_film_pivot = self._filmPivot.original
        self.display_resolution = self._resolution.original
        self.display_safe_action = self._safeAction.original
        self.display_safe_title = self._safeTitle.original
        self.overscan = self._overscan.original

    def kill(self):
        # cmds.deleteUI(self._panel)
        self.revert_all()
        cmds.deleteUI(self._window)
        cmds.deleteUI(self._panel, panel=True)
