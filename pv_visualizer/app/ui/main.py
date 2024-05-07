from trame.app import dev
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, paraview, simput, html,client

from trame_simput import get_simput_manager
from paraview import simple
from datetime import datetime

# from pv_visualizer import html as my_widgets
from pv_visualizer.app.assets import asset_manager
from pv_visualizer.app.ui import (
    pipeline,
    files,
    algorithms,
    settings,
    view_toolbox,
    state_change,
)


def _reload():
    dev.reload(
        pipeline,
        files,
        algorithms,
        settings,
        view_toolbox,
        state_change,
    )


# -----------------------------------------------------------------------------
# Common style properties
# -----------------------------------------------------------------------------

COMPACT = {
    "dense": True,
    "hide_details": True,
}

CONTROLS = [
    pipeline,
    files,
    algorithms,
    settings,
]

# -----------------------------------------------------------------------------
# Dynamic reloading
# -----------------------------------------------------------------------------

LIFE_CYCLES = [
    "on_data_change",
    "on_active_proxy_change",
]

# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------


def initialize(server):
    state, ctrl = server.state, server.controller

    # state
    state.trame__title = "Visualizer"
    state.trame__favicon = asset_manager.icon

    # controller
    ctrl.on_server_reload.add(_reload)
    ctrl.on_data_change.add(ctrl.view_update)
    ctrl.on_data_change.add(ctrl.pipeline_update)

    # Init other components
    state_change.initialize(server)
    for m in CONTROLS:
        m.initialize(server)

    # simput
    simput_manager = get_simput_manager("pxm")
    simput_widget = simput.Simput(
        simput_manager,
        prefix="pxm",
        trame_server=server,
        ref="simput",
        query=("search", ""),
    )
    ctrl.pxm_apply = simput_widget.apply
    ctrl.pxm_reset = simput_widget.reset


    

  


    with SinglePageWithDrawerLayout(server, show_drawer=True, width=300) as layout:
        layout.root = simput_widget

        # -----------------------------------------------------------------------------
        # Toolbar
        # -----------------------------------------------------------------------------
        layout.title.set_text("Visualizer")

        with layout.icon as icon:
            html.Img(src=asset_manager.icon, height=40)
            icon.click = None

        with layout.toolbar as tb:
            tb.dense = True
            tb.clipped_right = True
            vuetify.VSpacer()
            vuetify.VTextField(
                v_show=("!!active_controls",),
                v_model=("search", ""),
                clearable=True,
                outlined=True,
                filled=True,
                rounded=True,
                prepend_inner_icon="mdi-magnify",
                style="max-width: 30vw;",
                **COMPACT,
            )
            vuetify.VSpacer()
            
            #动画
            vuetify.VTextField(
                v_model=("time_value", 0),
                disabled=True,
                hide_details=True,
                dense=True,
                style="max-width: 50px",
                classes="mx-2",
            )
            vuetify.VSlider(
                v_model=("time_value", 0),
                min=0,
                max=("times", 1),
                hide_details=True,
                dense=True,
                style="max-width: 200px",
            )
            vuetify.VCheckbox(
                v_model=("play", False),
                off_icon="mdi-play",
                on_icon="mdi-stop",
                hide_details=True,
                dense=True,
                classes="mx-2",
            )
            vuetify.VProgressLinear(
                indeterminate=True,
                absolute=True,
                bottom=True,
                active=("trame__busy",),
            )

            #----------------上传按钮
            vuetify.VFileInput(
                v_model=("file_exchange", None),
                outlined=True,
                dense=True,
                hide_input=True,
                prepend_icon="mdi-upload",
                style="max-width:40px",
                title="上传文件到根目录"
            )

          
            # -------

            # vuetify.VSwitch(
            # v_model=("$vuetify.lang.locales", {"zhHans":"zhHans"}),
            # hide_details=True,
            # dense=True,
            #     )
          
            with vuetify.VBtnToggle(
                v_model=("active_controls", "files"),
                **COMPACT,
                outlined=True,
                rounded=True,
            ):
                for item in CONTROLS:
                    with vuetify.VBtn(value=item.NAME, **COMPACT):
                        vuetify.VIcon(item.ICON, **item.ICON_STYLE)

        # -----------------------------------------------------------------------------=
        # Drawer
        # -----------------------------------------------------------------------------
        with layout.drawer as dr:
            dr.right = True
            # dr.expand_on_hover = True
            # with vuetify.VBtn(icon=True):
            #     vuetify.VIcon("mdi-upload")            
            for item in CONTROLS:
                item.create_panel(server)

        # -----------------------------------------------------------------------------
        # Main content
        # -----------------------------------------------------------------------------
        with layout.content:
            with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
                view_toolbox.create_view_toolbox(server)
                html_view = paraview.VtkRemoteLocalView(
                    simple.GetRenderView() if simple else None,
                    interactive_ratio=("view_interactive_ratio", 1),
                    interactive_quality=("view_interactive_quality", 70),
                    mode="remote",
                    namespace="view",
                    style="width: 100%; height: 100%;",
                    on_remote_image_capture=f"utils.download('visualizer_remote_capture.png', $event)",
                    on_local_image_capture=f"utils.download('visualizer_local_capture.png', $event)"
                )
                ctrl.view_replace = html_view.replace_view
                ctrl.view_update = html_view.update
                ctrl.view_reset_camera = html_view.reset_camera
                ctrl.view_update_geometry = html_view.update_geometry
                ctrl.view_update_image = html_view.update_image
                ctrl.on_server_ready.add(ctrl.view_update)

        # -----------------------------------------------------------------------------
        # Footer
        # -----------------------------------------------------------------------------
        # layout.footer.hide()

