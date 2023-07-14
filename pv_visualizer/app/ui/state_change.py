from paraview import simple
from trame.app.file_upload import ClientFile
from trame.app import get_server, asynchronous
import asyncio

animation_scene = simple.GetAnimationScene()
time_keeper = animation_scene.TimeKeeper

def initialize(server):
    state, ctrl = server.state, server.controller

    @state.change("active_controls")
    def update_active_panel(active_controls, **kwargs):
        state.main_drawer = active_controls is not None

    @ctrl.add("on_active_proxy_change")
    def update_active_proxies(**kwargs):
        if simple is None:
            state.active_proxy_source_id = 0
            state.active_proxy_representation_id = 0
            return

        active_view = simple.GetActiveView()
        state.active_proxy_view_id = active_view.GetGlobalIDAsString()

        active_source = simple.GetActiveSource()
        if active_source is None:
            state.active_proxy_source_id = 0
            state.active_proxy_representation_id = 0
        else:
            state.active_proxy_source_id = active_source.GetGlobalIDAsString()
            rep = simple.GetRepresentation(proxy=active_source, view=active_view)
            state.active_proxy_representation_id = rep.GetGlobalIDAsString()

        
    @state.change("file_exchange")
    def file_uploaded(file_exchange, **kwargs):
        if file_exchange is None:
            return

        file = ClientFile(file_exchange)
        file_name = file_exchange.get("name")
        file_size = file_exchange.get("size")
        file_time = file_exchange.get("lastModified")
        file_mime_type = file_exchange.get("type")
        file_binary_content = file_exchange.get(
            "content"
        )  # can be either list(bytes, ...), or bytes
        with open(f"./vtu/{file_name}", 'wb') as f:
            f.write(file.content)

    # Initialize state values
    update_active_proxies()
