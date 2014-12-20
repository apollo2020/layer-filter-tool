import os
import sys
import arcpy
import datetime
import subprocess
import pythonaddins
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from tempfile import gettempdir


class CustomTools():
    """Custom tools used in button classes."""

    def __init__(self):
        self.config_attributes = ['MIN', 'MAX', 'NULL_FLAG']
        self.number_types = ['Double', 'Integer', 'Single', 'SmallInteger']
        self.int_types = ['Integer', 'Single', 'SmallInteger']
        self.float_types = ['Double']
        self.ignore_fields = ['Shape', 'SHAPE', 'FID', 'GlobalID', 'GLOBALID', 'FID', 'OBJECTID', 'FREQUENCY']
        self.table_subs = {'Shape_STLength__': 'Shape.STLength',
                           'Shape_STArea__': 'Shape.STArea',
                           'SHAPE_STLength__': 'SHAPE.STLength',
                           'SHAPE_STArea__': 'SHAPE.STArea'}
        self.forward_subs = {'Shape.STLength()': 'Shape.STLength',
                             'Shape.STArea()': 'Shape.STArea',
                             'SHAPE.STLength()': 'SHAPE.STLength',
                             'SHAPE.STArea()': 'SHAPE.STArea'}
        self.reverse_subs = {'Shape.STLength': 'Shape.STLength()',
                             'Shape.STArea': 'Shape.STArea()',
                             'SHAPE.STLength': 'SHAPE.STLength()',
                             'SHAPE.STArea': 'SHAPE.STArea()'}
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        self.temp_dir = gettempdir()
        self.xml_path = os.path.join(self.temp_dir, 'filter_config.xml')
        self.app_files_path = r"\\fileserv\usa\GIS\Code_Catalog\Python\Addins\Projects\LayerFilterTool\AppFiles"
        self.script_path = os.path.join(self.app_files_path, "config_manager.py")
        self.check_config_manager()

    def check_config_manager(self):
        """Create config_manager.py if absent from CustomTools.app_files_path."""

        script = """
import tkFont
from Tkinter import *
from sys import argv
import xml.etree.ElementTree as ET
import datetime
import xml.dom.minidom as minidom


class CustomTools():

    def __init__(self):

        self.int_types = ['Integer', 'Single', 'SmallInteger']
        self.float_types = ['Double']

    def round_up(self, x, n):
        value = x
        if value > 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            if dec_str[n:] != '':
                term_int = int(dec_str[n-1]) + 1
                dec_str = dec_str[:n-1]
                dec_str += str(term_int)
                value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        elif value < 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            dec_str = dec_str[:n]
            value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        else:
            return float(value)

    def round_down(self, x, n):
        value = x
        if value < 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            if dec_str[n:] != '':
                term_int = int(dec_str[n-1]) + 1
                dec_str = dec_str[:n-1]
                dec_str += str(term_int)
                value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        elif value > 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            dec_str = dec_str[:n]
            value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        else:
            return float(value)

    def float_to_string(self, f, n):

        fmt_str = "%." + str(n) + "f"
        str_val = (fmt_str % f).rstrip("0")
        if str_val[-1] == ".":
            str_val += "0"
        return str_val

    def write_config_xml(self, config_dict, file_path):

        result = file_path

        xml = ET.Element('xml')
        xml.set('name', config_dict['name'])
        xml.set('source', config_dict['source'])
        xml.set('datetime', datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))

        for name, config in sorted(config_dict['config'].iteritems()):
            elem = ET.SubElement(xml, name)

            for attr, value in config.iteritems():

                if type(value) is float:
                    value = self.float_to_string(value, 10)
                else:
                    value = str(value)

                elem.set(attr, value)

        raw_xml = ET.tostring(xml)
        parsed_xml = minidom.parseString(raw_xml)
        pretty_xml = parsed_xml.toprettyxml(indent="\\t")
        f = open(file_path, 'w')
        f.write(pretty_xml)
        f.close()

        return result

    def read_config_xml(self, file_path):

        result = {}
        dom = ET.parse(file_path)
        xml = dom.getroot()
        result['name'] = xml.get('name')
        result['source'] = xml.get('source')
        result['config'] = {}

        for elem in xml.getchildren():
            name = elem.tag
            config = elem.attrib
            result['config'][name] = config

        return result


class ConfigManager(Frame, CustomTools):

    def __init__(self, master):

        Frame.__init__(self, master)
        CustomTools.__init__(self)
        self.master = master
        self.xml_path = argv[1]
        self.config_dict = self.read_config_xml(self.xml_path)
        self.widgets = []
        self.resolution = 1
        self.canvas = None
        self.xml_path_label = None
        self.min_width = None
        self.min_height = None
        self.max_width = None
        self.max_height = None
        self.init_ui()

    def init_ui(self):

        path_font = tkFont.Font(size=8, slant="italic")
        attr_font = tkFont.Font(size=8)
        field_font = tkFont.Font(size=12, weight="bold", slant="italic")

        container = LabelFrame(self,
                               height=500,
                               width=400,
                               labelanchor=N,
                               relief=SUNKEN,
                               fg="#666666",
                               borderwidth=1,
                               takefocus=0)

        container.pack(fill=BOTH,
                       expand=YES,
                       padx=5,
                       pady=5)

        container.pack_propagate(0)

        self.canvas = Canvas(container,
                        takefocus=0)

        vbar = Scrollbar(self.canvas,
                         orient=VERTICAL,
                         takefocus=0)

        vbar.pack(side=RIGHT,
                  fill=Y)

        vbar.config(command=self.canvas.yview)

        self.canvas.config(yscrollcommand=vbar.set)

        self.canvas.pack(fill=BOTH,
                    expand=YES)

        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)

        canvas_child = Frame(self.canvas,
                             takefocus=0)

        canvas_child.pack()

        canvas_child_window = self.canvas.create_window(0, 0, anchor=NW, window=canvas_child)

        controls = Frame(self,
                         takefocus=0)

        controls.pack(fill=BOTH)

        self.pack(fill=BOTH, expand=YES)

        for name, config in sorted(self.config_dict['config'].iteritems()):

            data_type = config['TYPE']
            widget_min = float(config['MIN'])
            widget_max = float(config['MAX'])

            if data_type in self.float_types:
                self.resolution = 0.01
                if widget_min != 0.0:
                    widget_min = self.round_down(widget_min, 2)
                if widget_max != 0.0:
                    widget_max = self.round_up(widget_max, 2)

            null_flag = config['USER_NULL_FLAG']

            inner_frame = Frame(canvas_child,
                                takefocus=0)

            inner_frame.pack(side=TOP,
                             anchor=NW,
                             fill=X,
                             padx=5,
                             pady=(5, 10))

            title_frame = Frame(inner_frame,
                                takefocus=0)

            title_frame.pack(side=TOP,
                             anchor=N,
                             fill=X)

            field_name_label = Label(title_frame,
                                     font=field_font,
                                     text="%s" % name,
                                     justify=LEFT,
                                     takefocus=0)

            field_name_label.pack(side=LEFT,
                                  anchor=W)

            null_var = IntVar()
            null_var.field_name = name
            null_var.attr_type = "USER_NULL_FLAG"
            null_var.data_type = data_type
            null_var.set(null_flag)

            null_checkbutton = Checkbutton(title_frame,
                                           text="NULL",
                                           variable=null_var,
                                           takefocus=0)

            null_checkbutton.pack(side=RIGHT,
                                  anchor=E)

            null_checkbutton.bind("<ButtonRelease-1>", self.callback)

            include_label = Label(title_frame,
                                  text="Include: ",
                                  takefocus=0)

            include_label.pack(side=RIGHT,
                               anchor=E)

            min_frame = Frame(inner_frame,
                              takefocus=0)

            min_frame.pack(side=TOP,
                           anchor=NW,
                           fill=X,
                           expand=YES)

            max_frame = Frame(inner_frame,
                              takefocus=0)

            max_frame.pack(side=TOP,
                           anchor=NW,
                           fill=X,
                           expand=YES)

            min_scale_label = Label(min_frame,
                                    fg="#808080",
                                    font=attr_font,
                                    text=">=",
                                    justify=LEFT,
                                    takefocus=0)

            min_scale_label.pack(side=LEFT,
                                 anchor=SW,
                                 pady=(0, 2))

            min_entry_var = StringVar()
            min_entry_var.field_name = name
            min_entry_var.attr_type = "USER_MIN"
            min_entry_var.data_type = data_type

            min_entry = Entry(min_frame,
                              width=8,
                              textvariable=min_entry_var)

            min_entry.pack(side=LEFT,
                           anchor=SW,
                           pady=(0, 2))

            min_entry.field_name = name
            min_entry.attr_type = "USER_MIN"
            min_entry.data_type = data_type
            min_entry.bind('<Return>', self.callback)
            min_entry.bind('<FocusOut>', self.callback)

            min_scale = Scale(min_frame,
                              from_=widget_min,
                              to=widget_max,
                              orient=HORIZONTAL,
                              length=385,
                              takefocus=0,
                              resolution=self.resolution)

            min_scale.pack(side=LEFT,
                           anchor=W,
                           fill=X,
                           expand=YES)

            min_scale.field_name = name
            min_scale.attr_type = "USER_MIN"
            min_scale.data_type = data_type
            min_scale.set(float(config['USER_MIN']))
            min_scale.bind("<ButtonRelease-1>", self.callback)
            min_scale.old_value = min_scale.get()

            min_entry_var.set(min_scale.get())
            min_entry_var.old_value = min_entry_var.get()

            max_scale_label = Label(max_frame,
                                    fg="#808080",
                                    font=attr_font,
                                    text="<=",
                                    justify=LEFT,
                                    takefocus=0)

            max_scale_label.pack(side=LEFT,
                                 anchor=SW,
                                 pady=(0, 2))

            max_entry_var = StringVar()
            max_entry_var.field_name = name
            max_entry_var.attr_type = "USER_MAX"
            max_entry_var.data_type = data_type

            max_entry = Entry(max_frame,
                              width=8,
                              textvariable=max_entry_var)

            max_entry.pack(side=LEFT,
                           anchor=SW,
                           pady=(0, 2))

            max_entry.field_name = name
            max_entry.attr_type = 'USER_MAX'
            max_entry.data_type = data_type
            max_entry.bind('<Return>', self.callback)
            max_entry.bind('<FocusOut>', self.callback)

            max_scale = Scale(max_frame,
                              from_=widget_min,
                              to=widget_max,
                              orient=HORIZONTAL,
                              length=385,
                              takefocus=0,
                              resolution=self.resolution)

            max_scale.pack(side=LEFT,
                           anchor=W,
                           fill=X,
                           expand=YES)

            max_scale.field_name = name
            max_scale.attr_type = "USER_MAX"
            max_scale.data_type = data_type
            max_scale.set(float(config['USER_MAX']))
            max_scale.bind("<ButtonRelease-1>", self.callback)
            max_scale.old_value = max_scale.get()

            max_entry_var.set(max_scale.get())
            max_entry_var.old_value = max_entry_var.get()

            self.widgets += [min_scale,
                             max_scale,
                             null_var,
                             min_entry,
                             max_entry,
                             min_entry_var,
                             max_entry_var]

            if name != sorted(self.config_dict['config'].keys())[-1]:

                hr = Frame(canvas_child,
                           takefocus=0,
                           bd=2,
                           height=2,
                           relief=SUNKEN)

                hr.pack(side=TOP,
                        anchor=NW,
                        fill=X,
                        padx=5)

            self.resolution = 1

        container.update()
        self.canvas.update()
        canvas_child.update()
        container.config(width=canvas_child.winfo_width() + vbar.winfo_width() + 10)
        self.canvas.config(scrollregion=(0, 0, canvas_child.winfo_width(), canvas_child.winfo_height()))

        force_min = Button(controls,
                           text="|<<",
                           width=5,
                           justify=LEFT,
                           command=self.force_min_values,
                           takefocus=0)

        force_min.pack(padx=5,
                       pady=5,
                       side=LEFT)

        force_min.bind("<ButtonRelease-1>", self.callback)

        set_filter = Button(controls,
                            text="Save Settings",
                            command=self.update_config_dict)

        set_filter.pack(padx=5,
                        pady=5,
                        side=LEFT,
                        fill=X,
                        expand=YES)

        force_max = Button(controls,
                           text=">>|",
                           width=5,
                           justify=RIGHT,
                           command=self.force_max_values,
                           takefocus=0)

        force_max.pack(padx=5,
                       pady=5,
                       side=LEFT)

        force_max.bind("<ButtonRelease-1>", self.callback)

        self.xml_path_label = Label(self,
                                    fg="#000000",
                                    bg="#C8C8C8",
                                    font=path_font,
                                    text="%s" % self.xml_path,
                                    justify=CENTER,
                                    takefocus=0)

        self.xml_path_label.pack(fill=X,
                                 side=BOTTOM,
                                 padx=5,
                                 pady=(5, 10))

        self.master.update()
        self.master.title("Filter Configuration Tool  ( %s )" % self.config_dict['name'])
        self.master.geometry("+%d+%d" % (self.master.winfo_screenwidth()/2 - self.master.winfo_width()/2,
                                         self.master.winfo_screenheight()/2 - self.master.winfo_height()/2))
        self.bind("<Configure>", self.on_resize)
        self.min_width = self.master.winfo_width()
        self.max_width = self.min_width
        self.min_height = self.master.winfo_height()
        self.max_height = self.master.winfo_screenheight()
        self.on_resize(self)

    def on_resize(self, event):

        self.master.minsize(self.min_width, self.min_height)
        self.master.maxsize(self.min_width, self.master.winfo_screenheight())

    def on_mousewheel(self, event):

        self.canvas.yview_scroll(-1*(event.delta/120), "units")

    def update_config_dict(self):

        for w in self.widgets:

            if isinstance(w, Scale) or isinstance(w, IntVar):

                name = w.field_name
                attr = w.attr_type
                value = w.get()
                self.config_dict['config'][name][attr] = value

        self.write_config_xml(self.config_dict, self.xml_path)
        self.xml_path_label.configure(bg="#A3FF73")
        self.xml_path_label.update()

    def expand_value(self, value, attr_type):

        if value != 0.0:

            if attr_type == 'MIN':

                value = self.round_down(value, 2)

            if attr_type == 'MAX':

                value = self.round_up(value, 2)

        return value

    def force_min_values(self):

        scales = [w for w in self.widgets
                  if isinstance(w, Scale)
                  and w.attr_type == "USER_MIN"]

        for w in scales:

            w.set(w.cget('from'))
            self.set_entry_value(w)

        self.xml_path_label.configure(bg="#FF7F7F")

    def force_max_values(self):

        scales = [w for w in self.widgets
                  if isinstance(w, Scale)
                  and w.attr_type == 'USER_MAX']

        for w in scales:

            w.set(w.cget('to'))
            self.set_entry_value(w)

        self.xml_path_label.configure(bg="#FF7F7F")

    def validate_scale(self, widget):

        if isinstance(widget, Scale):

            value = widget.get()

            if widget.attr_type == 'USER_MIN':

                max_scale = [w for w in self.widgets
                             if isinstance(w, Scale)
                             and w.field_name == widget.field_name
                             and w.attr_type == 'USER_MAX'][0]

                max_value = max_scale.get()

                if value > max_value:

                    widget.set(max_value)
                    value = widget.get()

            if widget.attr_type == 'USER_MAX':

                min_scale = [w for w in self.widgets
                             if isinstance(w, Scale)
                             and w.field_name == widget.field_name
                             and w.attr_type == 'USER_MIN'][0]

                min_value = min_scale.get()

                if value < min_value:

                    widget.set(min_value)

        else:

            raise Exception("Not a Scale widget.")

    def set_scale_value(self, widget):

        if isinstance(widget, Entry):

            var = [w for w in self.widgets
                   if isinstance(w, StringVar)
                   and w.field_name == widget.field_name
                   and w.attr_type == widget.attr_type][0]

            value = float(var.get())

            scale = [w for w in self.widgets
                     if isinstance(w, Scale)
                     and w.field_name == widget.field_name
                     and w.attr_type == widget.attr_type][0]

            scale.set(value)
            self.validate_scale(scale)
            scale.old_value = scale.get()

            return scale.get()

        else:

            raise Exception("Not a Entry widget.")

    def set_entry_value(self, widget):

        if isinstance(widget, Scale):

            value = widget.get()

            var = [w for w in self.widgets
                   if isinstance(w, StringVar)
                   and w.field_name == widget.field_name
                   and w.attr_type == widget.attr_type][0]

            var.set(str(value))
            var.old_value = var.get()

        else:

            raise Exception("Not a Scale widget.")

    def get_entry_var(self, widget):

        if isinstance(widget, Entry):

            entry_var = [w for w in self.widgets
                         if isinstance(w, StringVar)
                         and w.field_name == widget.field_name
                         and w.attr_type == widget.attr_type][0]

            return entry_var

    def callback(self, event):

        widget = event.widget

        if isinstance(widget, Scale):

            if widget.get() != widget.old_value:

                self.validate_scale(widget)
                self.set_entry_value(widget)
                self.xml_path_label.configure(bg="#FF7F7F")
                widget.old_value = widget.get()

        if isinstance(widget, Entry):

            entry_var = self.get_entry_var(widget)
            new_value = str(self.set_scale_value(widget))
            entry_var.set(new_value)

            if new_value != entry_var.old_value:
                self.xml_path_label.configure(bg="#FF7F7F")
                entry_var.old_value = new_value

        if isinstance(widget, Checkbutton):

            self.xml_path_label.configure(bg="#FF7F7F")


def main():

    root = Tk()
    root.wm_attributes("-topmost", 1)
    app = ConfigManager(root)
    root.mainloop()

if __name__ == '__main__':

    main()"""

        if not (os.path.exists(self.app_files_path) and os.path.isdir(self.app_files_path)):

            os.mkdir(self.app_files_path)

        self.script_path = os.path.join(self.app_files_path, 'config_manager.py')
        f = open(self.script_path, 'w')
        f.write(script)
        f.close()

    def sde_connect(self, database, server="<default server>", username="", password="", version="SDE.DEFAULT"):

        # Check if value entered for option
        try:

            # usage parameters for spatial database connection to upgrade
            server = server.lower()
            version = version.upper()
            database = database.lower()
            service = "sde:sqlserver:" + server
            account_authentication = 'OPERATING_SYSTEM_AUTH'

            # check if direct connection
            if service.find(":") != -1:  # this is direct connect
                sde_conn_file_name = service.replace(":", "_")
                sde_conn_file_name = sde_conn_file_name.replace(";", "")
                sde_conn_file_name = sde_conn_file_name.replace("=", "")
                sde_conn_file_name = sde_conn_file_name.replace("/", "")
                sde_conn_file_name = sde_conn_file_name.replace("\\", "")

            else:
                arcpy.AddMessage("\n+++++++++")
                arcpy.AddMessage("Exiting!!")
                arcpy.AddMessage("+++++++++")
                sys.exit("\nSyntax for a direct connection in the Service parameter is required for geodatabase upgrade.")

            # local variables
            sde_conn_file_name = sde_conn_file_name + "_" + database + "_" + version.split('.')[-1].lower()

            sde_conn_file_path = self.app_files_path + os.sep + sde_conn_file_name + ".sde"

            if os.path.isfile(sde_conn_file_path):
                return sde_conn_file_path

            # Check for the .sde file and delete it if present
            arcpy.env.overwriteOutput=True

            # Variables defined within the script; other variable options commented out at the end of the line
            save_user_info = ""
            save_version_info = ""

            print("Creating ArcSDE Connection File...")
            print(self.app_files_path)
            print(sde_conn_file_name)
            print(server)
            print(service)
            print(database)
            print(account_authentication)
            print(username)
            print(password)
            print(save_user_info)
            print(version)
            print(save_version_info)

            arcpy.CreateArcSDEConnectionFile_management(self.app_files_path,
                                                        sde_conn_file_name,
                                                        server,
                                                        service,
                                                        database,
                                                        account_authentication,
                                                        username,
                                                        password,
                                                        save_user_info,
                                                        version,
                                                        save_version_info)

            for i in range(arcpy.GetMessageCount()):

                if "000565" in arcpy.GetMessage(i):   # check if database connection was successful
                    arcpy.AddReturnMessage(i)
                    arcpy.AddMessage("\n+++++++++")
                    arcpy.AddMessage("Exiting!!")
                    arcpy.AddMessage("+++++++++\n")
                    sys.exit(3)

                else:
                    arcpy.AddReturnMessage(i)
                    arcpy.AddMessage("+++++++++\n")
                    return sde_conn_file_path

        # check if no value entered for option
        except SystemExit as e:

            print e.code
            return

    def get_feature_layers(self, map_obj=None, wildcard=''):
        """Return list of layer objects for specified map document object.

        Only feature layers are returned. All other layer types (group, raster, etc...) are ignored.
        """

        layers = arcpy.mapping.ListLayers(map_obj, wildcard)
        result = [lyr for lyr in layers
                  if lyr.isFeatureLayer]
        return result

    def get_layer_config(self, layer):
        """Build dictionary of configuration values for specified layer's attribute table."""

        desc = arcpy.Describe(layer)

        if layer.supports('SERVICEPROPERTIES'):

            featclass = desc.featureClass.name
            properties = layer.serviceProperties
            workspace = self.sde_connect(server=properties['Server'],
                                         database=properties['Database'],
                                         version=properties['Version'])
            datasource = os.path.join(workspace, featclass)

        else:

            datasource = layer.dataSource

        result = {}
        result['name'] = layer.name
        result['source'] = datasource
        result['config'] = {}

        all_fields = desc.fields

        num_fields = [fld
                      for fld in all_fields
                      if fld.type in self.number_types
                      and fld.name not in self.ignore_fields]

        if len(num_fields) > 0:
            field_array = [[fld.name, attr]
                           for fld in num_fields
                           for attr in ['MIN', 'MAX']]

            arcpy.env.workspace = "in_memory"
            arcpy.env.overwriteOutput = True
            temp_stats = arcpy.Statistics_analysis(datasource, "temp_stats", field_array)
            arcpy.env.overwriteOutput = False
            scur = arcpy.da.SearchCursor(temp_stats, "*")
            raw_vals = zip(scur.fields, scur.next())
            del scur

            for fld in num_fields:

                if fld.name in self.forward_subs:
                    name = self.forward_subs[fld.name]
                else:
                    name = fld.name
                result['config'][name] = {}
                result['config'][name]['TYPE'] = fld.type

                for attr in self.config_attributes:
                    init_value = 0

                    if attr in ['NULL_FLAG']:
                        init_value = 1

                    result['config'][name][attr] = init_value
                    result['config'][name]['USER_' + attr] = init_value

            for pair in raw_vals:
                raw_name = pair[0]
                attr = raw_name.split("_")[0]
                name = raw_name[len(attr) + 1:]

                if name in self.table_subs:
                    name = self.table_subs[name]
                value = pair[-1]

                try:

                    if value is None:
                        value = 0
                    if result['config'][name]['TYPE'] in self.float_types:
                        value = float(value)
                    elif result['config'][name]['TYPE'] in self.int_types:
                        value = int(value)

                    result['config'][name][attr] = value
                    result['config'][name]['USER_' + attr] = value

                except KeyError:
                    print("Key not found for %s, %s" % (name, attr))
                    pass

            for name, attr in sorted(result['config'].iteritems()):

                if result['config'][name]['TYPE'] in self.float_types:
                    if float(result['config'][name]['USER_MIN']) != 0.0:
                        result['config'][name]['USER_MIN'] = self.round_down(result['config'][name]['USER_MIN'], 2)
                    if float(result['config'][name]['USER_MAX']) != 0.0:
                        result['config'][name]['USER_MAX'] = self.round_up(result['config'][name]['USER_MAX'], 2)

        else:
            msg = "No filterable fields found."
            pythonaddins.MessageBox(msg, 'Notification', 0)
            return

        return result

    def float_to_string(self, f, n):
        """Returns string representation of float accurate out to n decimal places"""

        fmt_str = "%." + str(n) + "f"
        str_val = (fmt_str % f).rstrip("0")
        if str_val[-1] == ".":
            str_val += "0"
        return str_val

    def round_up(self, x, n):
        value = x
        if value > 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            if dec_str[n:] != '':
                term_int = int(dec_str[n-1]) + 1
                dec_str = dec_str[:n-1]
                dec_str += str(term_int)
                value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        elif value < 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            dec_str = dec_str[:n]
            value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        else:
            return float(value)

    def round_down(self, x, n):
        value = x
        if value < 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            if dec_str[n:] != '':
                term_int = int(dec_str[n-1]) + 1
                dec_str = dec_str[:n-1]
                dec_str += str(term_int)
                value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        elif value > 0.0:
            int_str = str(x).split('.')[0]
            dec_str = str(x - float(str(x).split('.')[0])).split('.')[-1]
            dec_str = dec_str[:n]
            value = float('.'.join([int_str, dec_str]))
            fmt_str = "%." + str(n) + "f"
            return float(fmt_str % value)
        else:
            return float(value)

    def config_xml_exists(self, layer_name):
        """Check for existing config xml file."""

        if os.path.exists(self.xml_path):

            print("Config xml path exists.")
            config_dict = self.read_config_xml(self.xml_path)
            config_name = config_dict['name']

            if config_name == layer_name:

                print("Config name matches layer name.")
                return True, layer_name

            else:

                print("Config name does not match layer name.")
                return False

        else:

            print("Config xml path does not exist.")
            return False

    def write_config_xml(self, config_dict, file_path):
        """Write a xml file to hold layer configuration values

        XML file used by out-of-process script to build layer filter configuration GUI.
        """

        result = file_path

        xml = ET.Element('xml')
        xml.set('name', config_dict['name'])
        xml.set('source', config_dict['source'])
        xml.set('datetime', datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))

        for name, config in sorted(config_dict['config'].iteritems()):
            elem = ET.SubElement(xml, name)

            for attr, value in config.iteritems():

                if type(value) is float:
                    value = self.float_to_string(value, 10)
                else:
                    value = str(value)

                elem.set(attr, value)

        raw_xml = ET.tostring(xml)
        parsed_xml = minidom.parseString(raw_xml)
        pretty_xml = parsed_xml.toprettyxml(indent="\t")
        f = open(file_path, 'w')
        f.write(pretty_xml)
        f.close()

        return result

    def read_config_xml(self, file_path):
        """Read from xml file to build dictionary of layer configuration values.

        Needed to read from layer filter configuration XML.
        """

        result = {}
        dom = ET.parse(file_path)
        xml = dom.getroot()
        result['name'] = xml.get('name')
        result['source'] = xml.get('source')
        result['config'] = {}
        for elem in xml.getchildren():
            name = elem.tag
            config = elem.attrib
            result['config'][name] = config

        return result


class LayerSelector(object, CustomTools):
    """Implementation for layer_filter_tool_addin.layer_selector (ComboBox)"""

    def __init__(self):
        CustomTools.__init__(self)
        self.items = []
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWWWWWWWWWW'
        self.layer_name = ''
        self.value = '<select a layer>'

    def onSelChange(self, selection):
        self.layer_name = arcpy.mapping.ListLayers(self.mxd, selection)[0].name
        if self.layer_name not in (''):
            configure_filter.enabled = True
            apply_filter.enabled = True
            clear_filter.enabled = True

    def onEditChange(self, text):
        pass

    def onFocus(self, focused):
        # When the combo box has focus, update the combo box with the list of layer names.
        if focused:
            layers = self.get_feature_layers(self.mxd)
            self.items = sorted([lyr.name for lyr in layers])

    def onEnter(self):
        pass

    def refresh(self):
        pass


class ConfigureFilter(object, CustomTools):
    """Implementation for layer_filter_tool_addin.configure_filter (Button)"""

    def __init__(self):
        CustomTools.__init__(self)
        self.enabled = False
        self.checked = False

    def onClick(self):
        """Launch filter config GUI as external python process."""

        layer = self.get_feature_layers(self.mxd, layer_selector.value)[0]

        if not self.config_xml_exists(layer.name):

            config_dict = self.get_layer_config(layer)
            self.write_config_xml(config_dict, self.xml_path)

        print("Launching Filter Configuration Tool...")
        subprocess.Popen(["pythonw", self.script_path, self.xml_path], shell=False)


class ApplyFilter(object, CustomTools):
    """Implementation for layer_filter_tool_addin.apply_filter (Button)"""

    def __init__(self):
        CustomTools.__init__(self)
        self.enabled = False
        self.checked = False

    def onClick(self):
        """Set layer definition query based on current config filter file."""

        query_items = []
        config_dict = self.read_config_xml(configure_filter.xml_path)

        for name, config in sorted(config_dict['config'].iteritems()):

            if name in self.reverse_subs:
                name = self.reverse_subs[name]

            query_string = "%s >= %s AND %s <= %s" % (name, config['USER_MIN'], name, config['USER_MAX'])

            if int(config['USER_NULL_FLAG']) == 1:
                query_string += " OR %s IS NULL" % name

            query_string = "(" + query_string + ")"
            query_items.append(query_string)

        query_string = " AND ".join(query_items)
        layer_name = config_dict['name']
        layer = self.get_feature_layers(self.mxd, layer_name)[0]
        layer.definitionQuery = query_string
        arcpy.RefreshActiveView()


class ClearFilter(object, CustomTools):
    """Implementation for layer_filter_tool_addin.clear_filter (Button)"""

    def __init__(self):
        CustomTools.__init__(self)
        self.enabled = False
        self.checked = False

    def onClick(self):
        query_string = ""
        layer_name = layer_selector.layer_name
        layer = self.get_feature_layers(self.mxd, layer_name)[0]
        layer.definitionQuery = query_string
        arcpy.RefreshActiveView()
