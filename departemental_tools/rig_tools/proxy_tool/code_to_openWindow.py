from maya import OpenMayaUI, cmds
from PySide import QtCore, QtGui
import pymel.core as pymel
import sys
sys.path.append(r"//squeeze/Files/SHARE/Jimmy_Goulet/proxy_tool")
import tool_lib.lib as tool_lib
import ui_core.proxyTool_window as proxyTool_window


reload(tool_lib)
reload(proxyTool_window)


class ProxyTool_Window(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(ProxyTool_Window,self).__init__()
        self.ui = proxyTool_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.proxy_lib=tool_lib.Proxy_making()


        self.ui.action_add_loop.triggered.connect(self.do_add_loop)
        self.ui.action_empty_loop_list.triggered.connect(self.do_empty_memory)
        self.ui.action_soft_reset_loops.triggered.connect(self.do_soft_reset)
        self.ui.action_scinder_mesh.triggered.connect(self.do_scinder_mesh)
        self.ui.action_rename_geo_from_parent.triggered.connect(self.do_only_rename)
        self.ui.action_view_wip.triggered.connect(self.do_show_wip)

        #self.ui.action_tooltips_activation.toolTip() TODO I don't know how to show tooltips


    def do_add_loop(self):
        self.proxy_lib.add_loop(pymel.selected())


    def do_show_wip(self):
        print self.proxy_lib.edges_per_geo_dict
        self.proxy_lib.view_wip()


    def do_empty_memory(self):
        self.proxy_lib.empty_dict()


    def do_soft_reset(self):
        self.proxy_lib.soft_reset_loop_list()


    def do_scinder_mesh(self):
        self.proxy_lib.scinder_mesh()


    def do_only_rename(self):
        self.proxy_lib.rename_from_parent_selection(pymel.selected())


gui=ProxyTool_Window()
gui.show()