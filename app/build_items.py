import sys


class select_dropdown:
    def __init__(self, item_id, item_list, selected = "", html_class = "", other_args = {}, setval = "", id_list = ""):
        self.items = item_list
        self.html_class = html_class
        self.item_id = item_id
        self.id_list = id_list
        self.selected = setval
        self.other_args = other_args
        self.html = self.build_html()
    def build_html(self):
        if self.html_class != "": 
            html_output = "<select name = \"" + self.item_id +"\" id = \"" + self.item_id +"\" class = \"form-select "+ self.html_class + "\"> \n "
        else: 
            html_output = "<select name = \"" + self.item_id +"\" id = \"" + self.item_id +"\" class = \"form-select\"> \n "
        for idx, item in enumerate(self.items):
            if self.id_list != "":
                print(self.id_list[idx] == self.selected)
                if self.id_list[idx] == self.selected:
                    html_output += "\t<option value = " + self.id_list[idx] + " selected='selected'>" + item + "</option>\n"
                else:
                    html_output += "\t<option value = " + self.id_list[idx] + ">" + item + "</option>\n"
            else: 
                if item == self.selected:
                    html_output += "\t<option selected>" + item + "</option>\n"
                else:
                    html_output += "\t<option>" + item + "</option>\n"
        html_output += "</select>"
        return html_output


class select_item:
    def __init__(self, item_id, html_class = "", other_args = {}, setval = "", selected = False):
        self.item_id = item_id
        self.html_class = html_class
        self.other_args = other_args
        self.selected = selected
        self.html = self.build_html()
    def build_html(self):
        if self.html_class == "":
            if self.selected:
                html_output = ("<input type = \"checkbox\" class = \"form-check-input position-static\" name = \"" + self.item_id +"\"id = \"" + self.item_id + "\" checked>")
            else:
                html_output = ("<input type = \"checkbox\" class = \"form-check-input position-static\" name = \"" + self.item_id +"\"id = \"" + self.item_id + "\">")
        else:
            if self.selected:
                html_output = ("<input type = \"checkbox\" class = \"form-check-input " + self.html_class + " position-static\" name = \"" + self.item_id +"\" id = \"" + self.item_id + "\" checked>")
            else:
                html_output = ("<input type = \"checkbox\" class = \"form-check-input " + self.html_class + " position-static\" name = \"" + self.item_id +"\" id = \"" + self.item_id + "\">")

        return html_output


class textarea:
    def __init__(self, item_id, html_class = "", rows = "3", other_args = {}, setval = ""):
        self.item_id = item_id
        self.html_class = html_class
        self.rows = rows if type(rows) == str else str(rows)
        self.other_args = other_args
        self.setval = setval
        self.html = self.build_html()
    def build_html(self):
        if self.html_class == "":
            html_output = "<textarea class=\"form-control\" name = \"" + self.item_id +"\"id=\""+ self.item_id + "\" rows=\""+self.rows + "\">"  + self.setval + "</textarea>"
        else:
            html_output = "<textarea class=\"form-control " +  self.html_class + "\" name = \"" + self.item_id +"\"id=\""+ self.item_id + "\" rows=\""+self.rows + "\">"  + self.setval + "</textarea>"
        return html_output

class basic_input:
    def __init__(self, item_id, input_type="text", placeholder = "", html_class = "", query = "", other_args = {}, setval = ""):
        self.item_id = item_id
        self.input_type = input_type
        self.placeholder = placeholder
        self.html_class = html_class
        self.other_args = other_args
        self.setval = setval
        self.html = self.build_html()
    def build_html(self):
        if len(self.other_args) > 0:
            html_output = "<input type=\"" + self.input_type +"\" class=\"form-control " + self.html_class + "\" name = \"" + self.item_id +"\"id=\"" + self.item_id + "\" placeholder=\""+self.placeholder + "\" "
            for arg, item in self.other_args.items():
                html_output += arg + " = '" + str(item) + "' "
            html_output = html_output + " value = " + self.setval + ">"
        else:
            html_output = "<input type=\"" + self.input_type +"\" class=\"form-control " + self.html_class + "\" name = \"" + self.item_id +"\"id=\"" + self.item_id + "\" placeholder=\""+self.placeholder+"\" value = " + self.setval + ">"
        return html_output

class link:
    def __init__(self, href, text = "", html_class = "", item_id = "", other_args = {}, setval = ""):
        self.href = href
        self.text = text if text != "" else href
        self.html_class = html_class
        self.item_id = item_id
        self.other_args = other_args
        self.html = self.build_html()
    def build_html(self):
        if self.html_class == "":
            html_output = "<a href=" + self.href + ">"+self.text+"</a>"
        else:
            html_output = "<a href=" + self.href + " class = \"" + self.html_class + "\">"+self.text+"</a>"
        return html_output

class button_link:
    def __init__(self, href, text = "", html_class = "", item_id = "", other_args = {}, setval = ""):
        self.href = href
        self.text = text if text != "" else href
        self.html_class = html_class
        self.item_id = item_id
        self.other_args = other_args
        self.html = self.build_html()
    def build_html(self):
        if self.html_class == "":
            html_output = "<a class = 'btn btn-primary' href=" + self.href + ">"+self.text+"</a>"
        else:
            html_output = "<a href=" + self.href + " class = \"btn btn-primary " + self.html_class + "\">"+self.text+"</a>"
        return html_output

class textarea_list:
    def __init__(self, item_id, html_class = "", rows = "3", other_args = {}, setval = "", content = ""):
        self.content = eval(content)
        self.item_id = item_id
        self.html_class = html_class
        self.rows = rows if type(rows) == str else str(rows)
        self.other_args = other_args
        self.setval = setval
        self.html = self.build_html()
    def build_html(self):
        html_output = '<div style="height: 100px;overflow-y: scroll;word-wrap: break-word;white-space: normal !important;word-wrap: break-word;"><ul>'
        for item in self.content:
            html_output = html_output + "<li>" + item + "</li>"
        html_output = html_output + "</ul></div>"
        if self.html_class == "":
            html_output =  html_output + "<textarea class=\"form-control\" name = \"" + self.item_id +"\"id=\""+ self.item_id + "\" rows=\""+self.rows + "\">"  + self.setval + "</textarea>"
        else:
            html_output = html_output + "<textarea class=\"form-control " +  self.html_class + "\" name = \"" + self.item_id +"\"id=\""+ self.item_id + "\" rows=\""+self.rows + "\">"  + self.setval + "</textarea>"
        return html_output


class table_items:
    def __init__(self, table_id, column_names=''):
        self.table_id = table_id.replace(" ", "_").lower()
        self.column_names = column_names
        self.item_types = ["select_dropdown", "select_item", "textarea", "basic_input", "link", "button_link", "textarea_list"]
        self.page_items = {}
        for cname in self.column_names:
            self.page_items[cname] = {}
    def make_item(self, item_type, col, row, args, custom_id = "", other_items = {}, setval = "", content = "", selected = ""):
        exec_string = ""
        if item_type in self.item_types:
            if custom_id == "" or custom_id is None:
                id = str(self.table_id) + "." + col + "." +  str(row) 
                id.replace(" ", "_")
            else: 
                id = custom_id
                id.replace(" ", "_")
            exec_string += item_type + "(item_id =\"" + id + "\","
            for key in args: 
                if key != 'argument':
                    if type(args[key]) == list:
                        val = "["
                        for v in args[key]:
                            val += "\"" + v + "\","
                        val = val[:-1] + "]"
                    else: 
                        val = "\""+args[key]+"\""
                    exec_string += key + "=" + val + ","
            exec_string = exec_string[:-1] + ", other_args = " + str(other_items) + ", setval = \"" + str(setval) + "\""
            if content != "": 
                exec_string = exec_string + ", content = \"" + str(content) + "\""
            if selected != "": 
                exec_string = exec_string + ", selected = " + str(selected)
            
            exec_string = "self.page_items['"+col+"'][id]  = " + exec_string + ")"
            if col not in self.page_items.keys():
                self.page_items[col] = {}
            exec(exec_string, globals(), locals())
        else: 
            print(item_type + " not in " + str(self.item_types))
            id = None
        return id
    def get_item_html(self, id):
        try:
            _ , col, _  = id.split(".")
        except:
            for key in self.page_items:
                for item in self.page_items[key]:
                    if id == item:
                        col = key
                        break
        return self.page_items[col][id].html
    def get_item(self, id):
        tid, col, row = id.split(".")
        return self.page_items[col][id]
    def get_ids(self):
        return self.page_items.keys()
    def get_html_all(self, returntype = "dict"):
        for col in self.column_names:
            returnval = {}
            if returntype == "list":
                returnval[col] = []
                for item in self.page_items:
                    returnval[col].append(self.page_items[col][item].html)
            else:
                returnval[col] = {}
                for item in self.page_items:
                    returnval[col][item] = self.page_items[col][item].html
        return returnval
    def make_item_html(self, item_type, col, row, args, custom_id = "", other_items = {}, setval = "", content = "", selected = ""):
        if selected == "":
            id = self.make_item(item_type, col, row, args, custom_id, "{}", setval, content)
        else: 
            id = self.make_item(item_type, col, row, args, custom_id, "{}", setval, content, selected)

        return self.page_items[col][id].html


"""
class file_input: 
    def __init__(self, html_class = "", other_args = {}):
        self.html_class = html_class

    def build_html(self):
        html_output = 
"""