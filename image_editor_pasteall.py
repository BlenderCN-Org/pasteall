# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "PasteAll - Image",
    "author": "Dalai Felinto (dfelinto)",
    "version": (0, 8),
    "blender": (2, 75, 5),
    "location": "Image editor > Properties panel",
    "description": "Send your selection or text to www.pasteall.org",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Image Editor"}


# ########################################################
# PasteAll.org Image Sender Script
#
# Dalai Felinto
# ----------------
# dalaifelinto.com
# @dfelinto
#
# Rio de Janeiro, Brasil
#
# Important Note:
# This script is not official. I did it for fun and for my own usage.
# And please do not abuse of their generosity - use it wisely (a.k.a no flood).
#
# ########################################################


import bpy
import urllib
import urllib.request
import webbrowser


class IMAGE_PT_pasteall(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "PasteAll.org"

    def draw(self, context):
        layout = self.layout
        layout.operator("image.pasteall", icon='URL')
        layout.prop(context.scene, "use_pasteall_webbrowser_image")


class ImageSettings:
    __slots__ = {
            "_data",
            "_image",
            "_scene",
            }

    def __init__(self, scene, image):
        self._scene = scene
        self._image = image
        self._data = {}

        self._store()
        self._change_settings()

    def _store(self):
        """
        store all the scene render settings
        """
        values = {
                "color_depth",
                "color_mode",
                "compression",
                "file_format",
                "quality",
                "views_format",
                }

        image_settings = self._scene.render.image_settings
        for name in values:
            exec("self._data[\"{0}\"] = image_settings.{0}".format(name))


    def _change_settings(self):
        """
        set the saving properties
        """
        image_settings = self._scene.render.image_settings
        use_alpha = self._image.use_alpha

        image_settings.color_depth = '8'
        image_settings.color_mode = 'RGBA' if use_alpha else 'RGB'
        image_settings.compression = 80
        image_settings.file_format = 'PNG' if use_alpha else 'JPG'
        image_settings.quality = 70
        image_settings.views_format = 'STEREO_3D'

    def __del__(self):
        """
        restore all the settings
        """
        image_settings = self._scene.render.image_settings
        for key, value in self._data.items():
            if type(value) == str:
                exec("image_settings.{0} = \"{1}\"".format(key, value))
            else:
                exec("image_settings.{0} = {1}".format(key, value))


class IMAGE_OT_pasteall(bpy.types.Operator):
    """"""
    bl_idname = "image.pasteall"
    bl_label = "PasteAll.org"
    bl_description = "Send the current image to www.pasteall.org"

    @classmethod
    def poll(cls, context):
        if context.area.type != 'IMAGE_EDITOR':
            return False
        else:
            return context.space_data.image != None and \
                    context.space_data.image.has_data

    def invoke(self, context, event):
        image = context.space_data.image

        # save image in a temporary place
        filepath = self._save_image(context, image)

        # upload image and receive the returned page
        html = self._upload_image(filepath)

        # remove image
        self._remove_image(filepath)

        if html is None:
            self.report({'ERROR'}, "Error in sending the image to the server.")
            return {'CANCELLED'}

        # get the link of the posted page
        page = self._get_page(str(html))

        if page is None or page == "":
            self.report({'ERROR'}, "Error in retrieving the page.")
            return {'CANCELLED'}
        else:
            self.report({'INFO'}, page)

        # store the link in the clipboard
        bpy.context.window_manager.clipboard = page

        if context.scene.use_pasteall_webbrowser_image:
            try:
                webbrowser.open_new_tab(page)
            except:
                self.report({'WARNING'}, "Error in opening the page %s." % (page))

        return {'FINISHED'}

    def _save_image(self, context, image):
        """
        save image in a temporary place
        """
        import tempfile
        import os

        image_settings = ImageSettings(context.scene, image)
        use_alpha = image.use_alpha

        dirpath = tempfile.gettempdir()
        filepath = os.path.join(dirpath, "pasteall.{0}".format("png" if use_alpha else "jpg"))

        # save the image
        image.save_render(filepath)

        # restore scene original settings
        del image_settings

        return filepath

    def _upload_image(self, filepath):
        """
        upload image to pasteall server
        and return the returned page
        """
        return None

    def _remove_image(self, filepath):
        """
        delete temporary image
        """
        import os
        os.remove(filepath)

    def _get_page(self, html):
        """"""
        print(html)
        id = html.find('directlink')
        id_begin = id + 12 # hardcoded: directlink">
        id_end = html[id_begin:].find("</a>")

        if id != -1 and id_end != -1:
            return html[id_begin:id_begin + id_end]
        else:
            return None


def register():
    bpy.types.Scene.use_pasteall_webbrowser_image = bpy.props.BoolProperty(
        name='Launch Browser',
        description='Opens the page with the submitted image',
        default=True)

    bpy.utils.register_class(IMAGE_PT_pasteall)
    bpy.utils.register_class(IMAGE_OT_pasteall)


def unregister():
    del bpy.types.Scene.use_pasteall_webbrowser_image
    bpy.utils.unregister_class(IMAGE_PT_pasteall)
    bpy.utils.unregister_class(IMAGE_OT_pasteall)


if __name__ == "__main__":
    register()


