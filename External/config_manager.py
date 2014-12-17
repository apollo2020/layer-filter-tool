import tkFont
from Tkinter import *
from sys import argv
import xml.etree.ElementTree as ET
import datetime
import xml.dom.minidom as minidom


class CustomTools():

    def __init__(self):

        pass

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
                if type(value) == float:
                    elem.set(attr, self.float_to_string(value, 10))
                else:
                    elem.set(attr, str(value))

        raw_xml = ET.tostring(xml)
        parsed_xml = minidom.parseString(raw_xml)
        pretty_xml = parsed_xml.toprettyxml(indent="\t")
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
        self.resolution = 0.01
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

            widget_min = self.expand_value(float(config['USER_MIN']), 'USER_MIN')
            widget_max = self.expand_value(float(config['USER_MAX']), 'USER_MAX')
            null_flag = int(float(config['USER_NULL_FLAG']))

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

            min_entry = Entry(min_frame,
                              width=8,
                              textvariable=min_entry_var)

            min_entry.pack(side=LEFT,
                           anchor=SW,
                           pady=(0, 2))

            min_entry.field_name = name
            min_entry.attr_type = "USER_MIN"
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
            min_scale.set(widget_min)
            min_scale.bind("<ButtonRelease-1>", self.callback)
            min_scale.old_value = min_scale.get()

            min_entry_var.set(round(min_scale.cget('from'), 2))
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

            max_entry = Entry(max_frame,
                              width=8,
                              textvariable=max_entry_var)

            max_entry.pack(side=LEFT,
                           anchor=SW,
                           pady=(0, 2))

            max_entry.field_name = name
            max_entry.attr_type = 'USER_MAX'
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
            max_scale.set(widget_max)
            max_scale.bind("<ButtonRelease-1>", self.callback)
            max_scale.old_value = max_scale.get()

            max_entry_var.set(round(max_scale.cget('to'), 2))
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
                            command=self.update_config_dict,
                            takefocus=0)

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

        value = float(value)

        if value % 1.0 > 0.0:

            if attr_type == 'USER_MIN':

                value -= self.resolution

            if attr_type == 'USER_MAX':

                value += self.resolution

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

            if widget.attr_type == 'USER_MIN':

                min_var = [w for w in self.widgets
                           if isinstance(w, StringVar)
                           and w.field_name == widget.field_name
                           and w.attr_type == 'USER_MIN'][0]

                value = float(min_var.get())

                min_scale = [w for w in self.widgets
                             if isinstance(w, Scale)
                             and w.field_name == widget.field_name
                             and w.attr_type == 'USER_MIN'][0]

                min_scale.set(value)
                self.validate_scale(min_scale)

            if widget.attr_type == 'USER_MAX':

                max_var = [w for w in self.widgets
                           if isinstance(w, StringVar)
                           and w.field_name == widget.field_name
                           and w.attr_type == 'USER_MAX'][0]

                value = float(max_var.get())

                max_scale = [w for w in self.widgets
                             if isinstance(w, Scale)
                             and w.field_name == widget.field_name
                             and w.attr_type == 'USER_MAX'][0]

                max_scale.set(value)
                self.validate_scale(max_scale)

        else:

            raise Exception("Not a Entry widget.")

    def set_entry_value(self, widget):

        if isinstance(widget, Scale):

            value = str(widget.get())

            if widget.attr_type == 'USER_MIN':

                min_var = [w for w in self.widgets
                           if isinstance(w, StringVar)
                           and w.field_name == widget.field_name
                           and w.attr_type == 'USER_MIN'][0]

                min_var.set(value)

            if widget.attr_type == 'USER_MAX':

                max_var = [w for w in self.widgets
                           if isinstance(w, StringVar)
                           and w.field_name == widget.field_name
                           and w.attr_type == 'USER_MAX'][0]

                max_var.set(value)

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

            new_value = widget.get()
            old_value = widget.old_value

            if new_value != old_value:

                widget.old_value = new_value
                self.validate_scale(widget)
                self.set_entry_value(widget)
                self.xml_path_label.configure(bg="#FF7F7F")

        if isinstance(widget, Entry):

            entry_var = self.get_entry_var(widget)

            new_value = entry_var.get()
            old_value = entry_var.old_value

            if new_value != old_value:

                entry_var.old_value = new_value
                self.set_scale_value(widget)
                self.xml_path_label.configure(bg="#FF7F7F")

        if isinstance(widget, Checkbutton):

            self.xml_path_label.configure(bg="#FF7F7F")


def main():

    root = Tk()
    root.wm_attributes("-topmost", 1)
    app = ConfigManager(root)
    root.mainloop()

if __name__ == '__main__':

    main()
