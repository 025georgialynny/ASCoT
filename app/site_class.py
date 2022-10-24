from random import sample
import pandas as pd
import os
import json
import sys
import re
import time
import yaml
import datetime
# Custom class that builds items
from app import build_items
from app.build_items import table_items

class site:
    def __init__(self):
        # list of file names (not including extension) that each batch of data has 
        self.data_files = ["approvals", "logs", "plate_overview", "plate_wells", "samples_overview", "primer_list", "plate_primers"]
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.basedir= os.path.join(sys._MEIPASS, "app")
        except Exception:
            self.basedir = os.path.join(os.path.abspath("."), "app")
        
        # set files as empty dataframe for confirmatory purpases and global status during exec() function calls
        self.approvals = pd.DataFrame()
        self.logs = pd.DataFrame()
        self.plate_overview = pd.DataFrame()
        self.plate_wells = pd.DataFrame()
        self.samples_overview = pd.DataFrame()
        self.primer_list = pd.DataFrame()
        self.plate_primers = pd.DataFrame()
        #############
        # Load jsons that define our data types and store our data 
        self.pages = json.load(open(os.path.join(self.basedir, 'pages.json'))) # all of the pages and the tables that go on them
        self.page_tables = json.load(open(os.path.join(self.basedir, 'tables.json'))) # all of the tables and what data is in each column
        self.data_format = json.load(open(os.path.join(self.basedir, 'main_data.json'))) # definition of data types 
        self.database_outline = json.load(open(os.path.join(self.basedir, 'database_outline.json'))) # definition of table data, etc
        
        self.datadict = {}
        self.usernames = []
        self.names = []
        self.current_sample_version = ""
        self.data_loaded = False
    def set_sample_version(self, sample_version):
        self.current_sample_version = sample_version
    def data_to_dict(self):
        if not self.data_loaded:
            print("Error: No data loaded", sys.stderr)
            return
        for file in self.data_files:
            exec("self. " + file + " = self." + file + ".fillna('')")
            exec("self.datadict['" + file + "'] = self." + file +".to_dict('list')")
        return
    def load_users(self, users):
        self.usernames = list(users.keys())
        self.names = list(users.values())
    def load_data(self, sample_version = ""):
        if self.current_sample_version == "": 
            print("Error - no sample version set", file = sys.stderr)
            if sample_version != "":
                self.set_sample_version(sample_version)
            else:
                return
        for file in self.data_files:
            file_path = os.path.join(self.basedir,'data', "samples", self.current_sample_version , file + ".csv")
            if self.data_loaded:
                exec("self." + file + ".to_csv(r\""+ file_path + "\", index = False)")
            exec("self." + file + " = pd.read_csv(r\""+ file_path + "\")")
            
        self.data_loaded = True
        self.data_to_dict()

    def save_value(self, table, column, row, value, main_id = "",  main_col = "", user = "", savefile = ""):
        save_file = savefile if savefile != "" else self.page_tables[table]["columns"][column]["storage_file"]
        if save_file != "logs" and save_file in self.data_files:
            exec("self." + save_file + ".loc[" + str(row) + ", '" +column + "'] = '" + value + "'")
        elif save_file == "logs":
            if main_col == "sample_name":
                self.log_comment("status", sampleid = main_id, user = user, comment = ' '.join(value.splitlines()))
            else: 
                self.log_comment("status", plateid = main_id, user = user, comment = ' '.join(value.splitlines()))
        else: 
            return -1
        self.load_data()
        return 1

    def insertupdate(self, value_dict, table, main_id = [],  main_col = "", samp = [], main_col_val = ""):
        save_file = table
        if save_file == "logs": 
            return -1
        if len(main_id) < 1: 
            return -1
        
        id_list = []

        for key, value in value_dict.items():
            trustr =  "self." + save_file + ".loc["
            for idx, id in enumerate(main_id): 
                if idx != 0: 
                    trustr += " & "
                try:
                    trustr += "(self." + save_file + "['" + id + "']" + " ==  '" + value[id] + "')"
                except:
                    trustr += "(self." + save_file + "['" + id + "']" + " ==  " + str(value[id]) + ")"
            trustr += "]"
            if len(eval(trustr)) < 1: 
                # add row
                exec("self." + save_file + '.loc[len(self.' + save_file + ')] = ' + str(value))
                
            else: 
                # update row
                exec(trustr + " = [pd.Series( " + str(value) + ")]")
            id_list.append('-'.join([str(value[x]) for x in samp]))
        for _, s in eval("self." + table + ".loc[self." + table + "['" + main_col + "'] ==  '" +  main_col_val + "', " + str([x for x in samp]) + "].iterrows()"):
            s = s.values            
            uid = '-'.join([str(x) for x in s])
            if uid not in id_list: 
                evalstr = "self." + table + ".drop(self." + table 
                evalstr += "[(self." + table + "['" + main_col + "'] ==  '" + main_col_val + "')"
                for idx, thing in enumerate(s):
                    if type(thing) == str: 
                        evalstr += " & (self." + table + "['" +  samp[idx] + "'] == '" + str(thing) + "')"
                    else: 
                        evalstr += " & (self." + table + "['" +  samp[idx] + "'] == " + str(thing) + ")"

                evalstr += "].index, inplace = True)"
 
                exec(evalstr)
               
        self.load_data()
        return 1

    def log_comment(self, action, user, sampleid = "", plateid = "", comment = ""):
        self.logs.loc[len(self.logs)] = [user, time.time(), action, comment,sampleid, plateid]
        self.logs.to_csv(os.path.join(self.basedir, 'data', 'samples', self.current_sample_version, "logs.csv") , index = False)
    def get_key_from_value(self,dictionary, key):
        return list(dictionary.keys())[list(dictionary.values()).index(key)]

    def add_sample_to_plate(self,sample_id, plate_id, row = "", col = ""):
        new_row = {"sample_name": sample_id, "plate_id": plate_id, "well_row": row, "well_column": col}
        self.add_row("plate_wells", new_row)

    def add_samples_to_plate(self,sample_list, plate_id, row = "", col = ""):
        current_list = list(self.plate_wells.sample_name[self.plate_wells.plate_id == plate_id])
        for x in current_list: 
            if x not in sample_list: 
                self.remove_sample(x, plate_id)
            else:
                sample_list.remove(x) 
        for sample_id in sample_list: 
            new_row = {"sample_name": sample_id, "plate_id": plate_id, "well_row": row, "well_column": col}
            self.add_row("plate_wells", new_row)
        self.load_data()
    def savePrimer(self, primerform):
        primer_num1 = max(self.primer_list.primer_num.str.replace(r'\D', '').astype(int))+1
        primer_num2 = primer_num1+1 

        gene = primerform.gene.data.upper()
        pairset = max(self.primer_list.pair_set) + 1
        
        exon = primerform.exon.data
        rsid = primerform.rsid.data
        diplotype = primerform.diplotype.data
        
        
        pnum = primerform.pnum.data if primerform.pnum.data != "" else "p" + str(max(self.primer_list.pnum[self.primer_list.gene == gene].str.replace(r'\D', '').astype(int))+1) if len(self.primer_list.pnum[self.primer_list.gene == gene])>0 else "p1"

        m13 = 1 if primerform.m13.data else 0

        primer_details = gene + "-" + pnum

        f = {
            "primer_num": "BP" + str(primer_num1),
            "pair_set": pairset, 
            "primer_details": primer_details + "-F",
            "gene": gene, 
            "exon": exon, 
            "rsid": rsid, 
            "diplotype": diplotype,
            "pnum": pnum, 
            "M13": m13, 
            "direction": "F"
        }
        self.add_row("primer_list", f)
        b = {
            "primer_num": "BP" + str(primer_num2),
            "pair_set": pairset, 
            "primer_details": primer_details + "-R",
            "gene": gene, 
            "exon": exon, 
            "rsid": rsid, 
            "diplotype": diplotype,
            "pnum": pnum, 
            "M13": m13, 
            "direction": "R"
        }
        self.add_row("primer_list", b)
        self.load_data()

        

    def remove_sample(self, sample_name, plate_id): 
        self.plate_wells = self.plate_wells[[not thing for thing in (self.plate_wells.sample_name == sample_name)&(self.plate_wells.plate_id == plate_id)]].reset_index(drop=True)
        self.load_data()
    def add_row(self, file, datadictionary):
        file_dict = self.database_outline['table_mapping'][self.get_key_from_value(self.database_outline['tables'], file)]
        return_dict = { "files_keys": list(file_dict['variables'].keys()),
                        "file_vals": ["" for key in list(file_dict['variables'].keys())] }
        for key, val in datadictionary.items():
            if key in return_dict['files_keys']:
                return_dict["file_vals"][return_dict["files_keys"].index(key)] = val
            else: 
                print("Error: Key '" + key + "' Not in save file '" + file + "'!!", file = sys.stderr)
                return -1
        for key in file_dict['table_args']['pks']:
            if return_dict["file_vals"][return_dict["files_keys"].index(key)] == "":            
                print("Error: Key '" + key + "' must not be null!!!!", file = sys.stderr)
                return -1      
        exec("self."+ file + ".loc[len(self."+ file + ")] = return_dict['file_vals']", locals())
        exec("self." + file + ".to_csv(os.path.join(self.basedir, 'data', 'samples', '" +self.current_sample_version + "', '" + file + ".csv') , index = False)", globals(), locals())
        self.load_data()
        return 1


class site_functions(site):
    def __init__(self):
        super().__init__()
        self.sample_versions = []
        for folders in os.listdir(os.path.join(self.basedir, 'data', 'samples')):
            self.sample_versions.append(folders)
        #setup dropdown to choose data batch
        self.global_items = build_items.table_items("global")
        self.args  = {}
        self.args["item_list"] =self.sample_versions
        self.global_items.make_item(item_type = "select_dropdown", col = "glob", row = "", args = self.args , custom_id = "sampv_dropdown")
        pass
    def iterable(self, val):
        try:
            (x for x in val)
            return True
        except TypeError:
            return False
    def replace_items_argument(self, repl_string, main_file, cell):
        found = re.findall("\{([^\{\}]*)\}", repl_string)
        if len(found) > 0:
                for item in found:
                    repl_string = re.sub("\{"+ re.escape(item) + "\}", 
                        str(eval("self." + main_file + ".loc[" + str(cell) + ", '" + self.replace_items_argument(item, main_file, cell) + "']")),
                        repl_string)
        return(repl_string)

    def replace_items_query(self, repl_string, main_file, cell):
        found = re.findall("\{([^\{\}]*)\}", repl_string)
        if len(found) > 0:
                for item in found:
                        repl_string = re.sub("\{"+ re.escape(item) + "\}", self.replace_items_query(item), repl_string)
        return str(eval("self." + main_file + ".loc[" + cell + ", " + repl_string + "]", locals()))

    def replace_items_args(self, repl_string, my_args):
        found = re.findall("\{([^\{\}]*)\}", repl_string)
        if len(found) > 0:
                for item in found:
                    if "hidden-" + item in my_args:
                        repl_string = re.sub("\{"+ re.escape(item) + "\}", self.replace_items_args("my_args['hidden-" + item+ "']", my_args) , repl_string)
                    else:
                        repl_string = re.sub("\{"+ re.escape(item) + "\}", self.replace_items_args("my_args['" + item+ "']", my_args) , repl_string)

        return eval(repl_string, locals())

    def get_subset(self, repl_string, file, args):
        subset_str = "self." + file + "[" +str(repl_string) + "].index"
        return(self.replace_items_args(subset_str, dict(args)))


class table_functions(site_functions):
    def __init__(self):
        super().__init__()
    def js_get_data(self, table, args): 
        q_str = ""
        for item, value in args.items(): 
            q_str += f'self.{table}.{item} == "{value}"&'
        q_str = q_str[:-1]
        return eval(f'self.{table}[{q_str}].to_json(orient="records")')
    def build_tables(self, cur_page, args):
            # this function takes in a string that represents a page and builds all of the tables as a dictionary object in the following format:
        # table_dictionary = {
        #       "table_name": {
        #           "column_name": [list of column items]
        #           }
        #       }
        
        # setup dictionary as empty object
        table_dict = {}
        file_dict = {}
        dropdown_dict = {}
        title_dict = {}
        # pages[cur_page]['tables'] lists all of the tables that goes on a page
        for table in self.pages[cur_page]['tables']:   
            if True: #table in ["Plate Report", "Variant Overview" , "Plate Overview", "Choose Plate", "Build Plate", "Design Plate", "Organize Plate"]: 
                file_dict[table] = {}
                table_dict[table], file_dict[table]['main_file'], title_dict[table] = self.get_table(cur_page, table, args, self.page_tables[table])
                if len(self.page_tables[table]['dropdown']) > 0:
                    dropdown_dict[table] = {}
                    file_dict[table]['dropdown'] = {}
                    for dropdown_tab in self.page_tables[table]['dropdown']:
                        dropdown_dict[table][dropdown_tab], file_dict[table]['dropdown'][dropdown_tab] = self.get_dropdown(cur_page, table, args, self.page_tables[table]['dropdown'][dropdown_tab], table_dict[table], dropdown_tab)
                continue     
            # setup table_dict[table] as a dict so things can be assigned
            table_dict[table] = {}
            #get the number of rows in the tables as the length of the first column - important for all columns to have same amount of rows, etc
            # this needs to be a primary key of sort
            trows = len(self.datadict[self.page_tables[table]['columns'][0].split(".")[0]][self.page_tables[table]['columns'][0].split(".")[1]])
            #setup table items object that stores our objects
            titems = table_items(table_id = cur_page+"."+table, column_names = self.page_tables[table]['columns'])
            #iterate through columns to build them
            for item in self.page_tables[table]['columns']:
                # data is stores as "file_name.column_name"
                file, col = item.split(".")
                if trows == 0:
                    # if no items in table set to empty array
                    table_dict[table][col] = []
                    break
                if file == "none":
                    # if file == "none" it indicates that it isn't stored anywhere and that it should be written
                    table_dict[table][col]  = []
                    if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                        for cell in range(0, trows):
                            table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = self.data_format[col]["item"]["args"]))
                else:
                    table_dict[table][col] = self.datadict[file][col]
        main_dict = {}
        main_dict["titles"] = title_dict
        main_dict["tables"] = table_dict
        main_dict["files"] = file_dict
        if len(dropdown_dict.keys()) > 0:
            main_dict["dropdown"] = dropdown_dict
        
        return main_dict
    def get_dropdown(self, cur_page, table, args, table_outline, table_dict, dropdown_table):
        dropdown_args = {}
        dropdowns = []
        pkey = 'sample_name' if 'sample_name' in table_dict.keys() else 'hidden-sample_name' if 'hidden-sample_name' in table_dict.keys() else 'hidden-plate_id' if 'hidden-plate_id' in table_dict.keys() else "plate_id"
        main_file = table_outline['args']['main_file']
        for i in range(0,len(table_dict[list(table_dict.keys())[0]])):
            dd_key = table_dict[pkey][i]
            dropdown_args[dd_key] = dict(args)
            for key, val in table_dict.items():
                if key in dropdown_args[dd_key].keys():
                    print("error - key '" + key + "' already in dropdown args")
                elif len(val) == (0):
                    dropdown_args[dd_key][key] = ""
                else:
                    dropdown_args[dd_key][key] = val[i]
            dropdowns.append("")
            dropdowns[i], _ = self.get_table(cur_page, table, dropdown_args[dd_key], table_outline, dropdown_table)
        return dropdowns, main_file
    def get_table(self, cur_page, table, args, table_outline, dropdown_table = ""):
        table_dict = {}
        table_dict[table] = {}
        table_args = table_outline['args']
        trows = self.replace_items_args(table_args["length"], args)
        
        main_file = table_args["main_file"]
        if "title" in table_args.keys():
            title = table_args["title"]
            for queryitem in re.findall("\{([A-z0-9]*)\}", title):
                title = re.sub("\{"+ queryitem + "\}", args[queryitem], string = title)
        else: 
            title = table
    
        cell_list =  list(self.get_subset(table_args['subset_file'], main_file, args)) if "subset_file" in table_args.keys() else list(range(0,trows))
       
        #print("Cell List:")
        #print(cell_list)
        #print(table_outline['columns'].keys())
        #get the number of rows in the tables as the length of the first column - important for all columns to have same amount of rows, etc
        # this needs to be a primary key of sort
        #trows = len(datadict[page_tables[table]['columns'][0].split(".")[0]][page_tables[table]['columns'][0].split(".")[1]])
        #setup table items object that stores our objects
        titems = table_items(table_id = cur_page+"."+table+"."+dropdown_table, column_names = list(table_outline['columns'].keys()))
        
        #iterate through columns to build them
        for col in list(table_outline['columns'].keys()):
                #fetches item
            cur_item = dict(table_outline['columns'][col])
            storage_file = cur_item['storage_file']
            storage_type = cur_item['type']
            pretty_name = cur_item['pretty_name']
            # data is stores as "file_name.column_name"
            if trows == 0:
                # if no items in table set to empty array
                table_dict[table][col] = []
                break
            #print([col, trows])
            if storage_file == "none" and storage_type != "editable":
                print("NONE")
                # if file == "none" it indicates that it isn't stored anywhere and that it should be written
                table_dict[table][col]  = []
                if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                    for cell in cell_list:
                        table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell.values.tolist(), col = col, args = self.data_format[col]["item"]["args"]))
            elif storage_type == 'variable':
                #do this
                arg_dict = dict(self.data_format[col]['item'])
                                # defined in main_data.json
                if arg_dict['type']!= "" and  arg_dict['type']!= "static": 
                    print(col)
                    columns = []
                    table_dict[table][col]  = []
                    for cell in cell_list:
                        if True:
                            if "query" in cur_item['args'].keys():
                                quer = ""
                                if "columns" in cur_item["args"].keys():
                                    for addcol in cur_item["args"]["columns"]:
                                        #query = self.replace_items_query(cur_item['args']["query"], main_file, cell)
                                        query = cur_item['args']['query']
                                        for queryitem in re.findall("\{([A-z0-9]*)\}", query):
                                            query = re.sub("\{"+ queryitem + "\}", eval("self." + main_file + ".loc[" + str(cell) + ", '" + queryitem + "']"), string = query)
                                        query_eval = eval("self." + storage_file + "["  + query + "]."+addcol)
                                        if len(list(query_eval)) == 0:
                                            quer = []
                                            break
                                        if quer == "": 
                                            quer = list(query_eval)
                                        else: 
                                            quer = [quer[x] + ":  " + list(query_eval)[x] for x in range(len(quer))]
                                    columns.append(titems.make_item_html(item_type=arg_dict['type'], row = cell, col = col, args = {}, content = quer))
                            elif "action" not in cur_item['args'].keys(): 
                                #columns.append("")
                                columns.append(titems.make_item_html(item_type = cur_item['args']['item_type'], row = cell, col = col, args = cur_item['args']["args"]))
                                appended = True
                            else:
                                action = cur_item['args']["action"]
                                for actionitem in re.findall("\{([^\{\}]*)\}", action):
                                    if actionitem == col:
                                        action = re.sub("\{"+ actionitem + "\}", str(columns[len(columns)-1]), action)
                                #columns.append('')
                                columns[len(columns)-1] = str(eval(action))
                        else: # Exception as e:
                            print(cur_item['args']["query"] + " didn't find anything")
                            print("Error linke 274: " + str(e))
                            if not appended: 
                                columns.append('')
                elif "item_type" in cur_item["args"].keys():
                    columns = []
                    for cell in cell_list:
                        appended = False
                        try:
                            if "query" in cur_item['args'].keys():
                                query = self.replace_items_query(cur_item['args']["query"], main_file, cell)
                                #for queryitem in re.findall("\{([A-z0-9]*)\}", query):
                                #    query = re.sub("\{"+ queryitem + "\}", eval(main_file + ".loc[" + str(cell) + ", '" + queryitem + "']"), string = query)
                                #columns.append('')
                                query_eval = eval("self." + storage_file + "["  + query + "]."+col)
                                continue
                                if len(query_eval) == 0:
                                    columns.append("")
                                    appended = True
                                elif len(query_eval) > 1:
                                    columns.append(list(query_eval))
                                    appended = True
                                else: 
                                    columns.append(list(query_eval)[0])
                                    appended = True
                            else: 
                                #columns.append("")
                                columns.append(titems.make_item_html(item_type = cur_item['args']['item_type'], row = cell, col = col, args = cur_item['args']["args"]))
                                appended = True
                            if "action" in cur_item['args'].keys():
                                action = cur_item['args']["action"]
                                for actionitem in re.findall("\{([^\{\}]*)\}", action):
                                    if actionitem == col:
                                        action = re.sub("\{"+ actionitem + "\}", str(columns[len(columns)-1]), action)
                                #columns.append('')
                                columns[len(columns)-1] = str(eval(action))
                        except Exception as e:
                            print(cur_item['args']["query"] + " didn't find anything")
                            print("Error linke 274: " + str(e))
                            if not appended: 
                                columns.append('')
                else:
                    # then the data is static just pulled differently from a different table
                    columns = []
                    for cell in cell_list:
                        appended = False
                        empty = False
                        if True:
                            if "query" in cur_item['args'].keys():
                                query = cur_item['args']["query"]
                                for queryitem in re.findall("\{([^\{\}]*)\}", query):
                                    query = re.sub("\{"+ queryitem + "\}", eval("self." + main_file + ".loc[" + str(cell) + ", '" + queryitem + "']"), string = query)
                                query_eval = eval("self." + storage_file + "["  + query + "]."+col)
                                if len(list(query_eval)) == 0:
                                    columns.append("")
                                    appended = True
                                    empty = True
                                elif len(query_eval) > 1:
                                    columns.append(list(query_eval))
                                    appended = True
                                else: 
                                    columns.append(list(query_eval)[0])
                                    appended = True
                            else: 
                                columns.append("")
                                appended = True
                            if "action" in cur_item['args'].keys() and not empty:
                                action = cur_item['args']["action"]
                                for actionitem in re.findall("\{([^\{\}]*)\}", action):
                                    if actionitem == col:
                                        action = re.sub("\{"+ actionitem + "\}", str(columns[len(columns)-1]), action)
                                #columns.append('')
                                columns[len(columns)-1] = str(eval(action))
                        else: # Exception as e:
                            print(cur_item['args']["query"] + " didn't find anything")
                            print("Error line 309: " + str(e))
                            if not appended: 
                                columns.append('')
                    
                if pretty_name == "":
                    table_dict[table][col] = columns
                else: 
                    table_dict[table][pretty_name] = columns  
            
            elif storage_type == 'editable':
                # defined in main_data.json
                selected = ""
                table_dict[table][col]  = []
                for cell in cell_list:
                    arg_dict = dict(self.data_format[col]["item"]["args"])
                    if 'argument' in cur_item['args'].keys():
                        if type(cur_item['args']['argument']) == list:
                            for arg in cur_item['args']['argument']:
                                exec(arg)
                        else:
                            exec(cur_item['args']['argument'])
                    if 'argument' in arg_dict.keys():
                        for argument in arg_dict["argument"]:
                            arg_dict[argument] = self.replace_items_argument(arg_dict[argument], main_file, cell)
                        if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                            if storage_file != "none":
                                if self.datadict[storage_file][col][cell] != "" or cur_item["unique"] == "False":
                                    table_dict[table][col].append(self.datadict[storage_file][col][cell])
                                else:
                                    table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
                            else:
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
                    elif len(cur_item['args']) > 0:
                        otherarg_dict = {}
                        for curarg in cur_item['args']:
                            if curarg == 'other_args':
                                for newarg, newitem in cur_item['args']['other_args'].items():
                                    if bool(re.search("^Eval:", str(newitem))):
                                        otherarg_dict[newarg] = eval(newitem.replace("Eval:", ""), locals())
                                    else: 
                                        otherarg_dict[newarg] = newitem
                            else:
                                curval = cur_item['args'][curarg]
                                if bool(re.search("^Eval:", str(curval))):
                                    arg_dict[curarg] = eval(curval.replace("Eval:", ""), locals())
                                elif curarg == "selected": 
                                    query = curval
                                    for queryitem in re.findall("\{([^\{\}]*)\}", query):
                                        try:
                                            query = re.sub("\{"+ queryitem + "\}", eval("self." + main_file + ".loc[" + str(cell) + ", '" + queryitem + "']"), string = query)
                                        except:
                                            query = re.sub("\{"+ queryitem + "\}", args[queryitem], string = query)
                                    query_eval = eval(query)
                                    selected = query_eval
                                else: 
                                    arg_dict[curarg] = curval
                        if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                            if storage_file != "none":
                                if self.datadict[storage_file][col][cell] != "" or cur_item["unique"] == "False":
                                    table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict,  other_items = otherarg_dict, setval = self.datadict[storage_file][col][cell]))
                                else:
                                    table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict, other_items = otherarg_dict))
                            else:
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict, other_items = otherarg_dict, selected = selected))
                    else:
                        if storage_file != "none":
                            if self.datadict[storage_file][col][cell] != "" or cur_item["unique"] == "False":
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict, setval = self.datadict[storage_file][col][cell]))
                            else:
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
                        else:
                            table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
            else:
                #storage type == static
                # means that the data comes out of the main storage table directly
                try: 
                    columns = [self.datadict[storage_file][col][x] for x in cell_list]
                except Exception as e:
                    columns = [" " for x in cell_list]

                if pretty_name == "":
                    table_dict[table][col] = columns
                else: 
                    table_dict[table][pretty_name] = columns  
            if ('hidden' in cur_item.keys()):
                table_dict[table]['hidden-'+col] = table_dict[table].pop(col)
        #print(table_dict)
        return table_dict[table], main_file, title
    def get_table_old(self, cur_page, table, args):
        table_dict = {}
        table_dict[table] = {}
        table_args = self.page_tables[table]['args']
        trows = self.replace_items_args(table_args["length"], args)
        main_file = table_args["main_file"]

        
        cell_list =  list(self.get_subset(table_args['subset_file'], main_file, args)) if "subset_file" in table_args.keys() else list(range(0,trows))


        #get the number of rows in the tables as the length of the first column - important for all columns to have same amount of rows, etc
        # this needs to be a primary key of sort
        #trows = len(datadict[page_tables[table]['columns'][0].split(".")[0]][page_tables[table]['columns'][0].split(".")[1]])
        #setup table items object that stores our objects
        titems = table_items(table_id = cur_page+"."+table, column_names = list(self.page_tables[table]['columns'].keys()))
        #iterate through columns to build them
        for col in list(self.page_tables[table]['columns'].keys()):
                #fetches item
            cur_item = dict(self.page_tables[table]['columns'][col])
            storage_file = cur_item['storage_file']
            storage_type = cur_item['type']
            pretty_name = cur_item['pretty_name']
            # data is stores as "file_name.column_name"
            if trows == 0:
                # if no items in table set to empty array
                table_dict[table][col] = []
                break
            if storage_file == "none" and storage_type != "editable":
                print("NONE")
                # if file == "none" it indicates that it isn't stored anywhere and that it should be written
                table_dict[table][col]  = []
                if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                    for cell in cell_list:
                        table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = self.data_format[col]["item"]["args"]))
            elif storage_type == 'variable':
                #do this
                if "item_type" in cur_item["args"].keys():
                    columns = []
                    for cell in cell_list:
                        appended = False
                        try:
                            if "query" in cur_item['args'].keys():
                                query = self.replace_items_query(cur_item['args']["query"], main_file, cell)
                                #for queryitem in re.findall("\{([A-z0-9]*)\}", query):
                                #    query = re.sub("\{"+ queryitem + "\}", eval(main_file + ".loc[" + str(cell) + ", '" + queryitem + "']"), string = query)
                                #columns.append('')
                                query_eval = eval(storage_file + "["  + query + "]."+col)
                                continue
                                if len(query_eval) == 0:
                                    columns.append("")
                                    appended = True
                                elif len(query_eval) > 1:
                                    columns.append(list(query_eval))
                                    appended = True
                                else: 
                                    columns.append(list(query_eval)[0])
                                    appended = True
                            else: 
                                #columns.append("")
                                columns.append(titems.make_item_html(item_type = cur_item['args']['item_type'], row = cell, col = col, args = cur_item['args']["args"]))
                                appended = True
                            if "action" in cur_item['args'].keys():
                                action = cur_item['args']["action"]
                                for actionitem in re.findall("\{([^\{\}]*)\}", action):
                                    if actionitem == col:
                                        action = re.sub("\{"+ actionitem + "\}", str(columns[len(columns)-1]), action)
                                #columns.append('')
                                columns[len(columns)-1] = str(eval(action))
                        except Exception as e:
                            print(cur_item['args']["query"] + " didn't find anything")
                            print("Error linke 274: " + str(e))
                            if not appended: 
                                columns.append('')
                else:
                    # then the data is static just pulled differently from a different table
                    columns = []
                    for cell in cell_list:
                        appended = False
                        try:
                            if "query" in cur_item['args'].keys():
                                query = cur_item['args']["query"]
                                for queryitem in re.findall("\{([^\{\}]*)\}", query):
                                    query = re.sub("\{"+ queryitem + "\}", eval("self." + main_file + ".loc[" + str(cell) + ", '" + queryitem + "']"), string = query)
                                query_eval = eval("self." + storage_file + "["  + query + "]."+col)
                                if len(query_eval) == 0:
                                    columns.append("")
                                    appended = True
                                elif len(query_eval) > 1:
                                    columns.append(list(query_eval))
                                    appended = True
                                else: 
                                    columns.append(list(query_eval)[0])
                                    appended = True
                            else: 
                                columns.append("")
                                appended = True
                            if "action" in cur_item['args'].keys():
                                action = cur_item['args']["action"]
                                for actionitem in re.findall("\{([^\{\}]*)\}", action):
                                    if actionitem == col:
                                        action = re.sub("\{"+ actionitem + "\}", str(columns[len(columns)-1]), action)
                                #columns.append('')
                                columns[len(columns)-1] = str(eval(action))
                        except Exception as e:
                            print(cur_item['args']["query"] + " didn't find anything")
                            print("Error line 309: " + str(e))
                            if not appended: 
                                columns.append('')
                    
                if pretty_name == "":
                    table_dict[table][col] = columns
                else: 
                    table_dict[table][pretty_name] = columns  

            elif storage_type == 'editable':
                # defined in main_data.json
                table_dict[table][col]  = []
                for cell in cell_list:
                    arg_dict = dict(self.data_format[col]["item"]["args"])
                    if 'argument' in cur_item['args'].keys():
                        table_dict[table][col].append("THING NEEDED")
                        pass
                    elif 'argument' in arg_dict.keys():
                        for argument in arg_dict["argument"]:
                            arg_dict[argument] = self.replace_items_argument(arg_dict[argument], main_file, cell)
                        if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                            if storage_file != "none":
                                if self.datadict[storage_file][col][cell] != "" or cur_item["unique"] == "False":
                                    table_dict[table][col].append(self.datadict[storage_file][col][cell])
                                else:
                                    table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
                            else:
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
                    elif len(cur_item['args']) > 0:
                        otherarg_dict = {}
                        for curarg in cur_item['args']:
                            if curarg == 'other_args':
                                for newarg, newitem in cur_item['args']['other_args'].items():
                                    if bool(re.search("^Eval:", str(newitem))):
                                        otherarg_dict[newarg] = eval(newitem.replace("Eval:", ""), locals())
                                    else: 
                                        otherarg_dict[newarg] = newitem
                            else:
                                curval = cur_item['args'][curarg]
                                if bool(re.search("^Eval:", str(curval))):
                                    arg_dict[curarg] = eval(curval.replace("Eval:", ""), locals())
                                else: 
                                    arg_dict[curarg] = curval
                        if self.data_format[col]["item"]["type"] != "": # a type must be set for it to be built with table_dict
                            if storage_file != "none":
                                if self.datadict[storage_file][col][cell] != "" or cur_item["unique"] == "False":
                                    table_dict[table][col].append(self.datadict[storage_file][col][cell])
                                else:
                                    table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict, other_items = otherarg_dict))
                            else:
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict, other_items = otherarg_dict))
                    else:
                        if storage_file != "none":
                            if self.datadict[storage_file][col][cell] != "" or cur_item["unique"] == "False":
                                table_dict[table][col].append(self.datadict[storage_file][col][cell])
                            else:
                                table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
                        else:
                            table_dict[table][col].append(titems.make_item_html(item_type = self.data_format[col]["item"]["type"], row = cell, col = col, args = arg_dict))
            else:
                #storage type == static
                # means that the data comes out of the main storage table directly
                table_dict[table][col] = [self.datadict[storage_file][col][x] for x in cell_list]
        return table_dict[table], main_file
    
    def make_plate_table(self, plate_id):
        plate_rows = self.plate_overview.plate_rows[self.plate_overview.plate_id == plate_id]
        plate_columns = self.plate_overview.plate_columns[self.plate_overview.plate_id == plate_id]
        plate_items = table_items(table_id = "make_plate_table", column_names = [str(x) for x in range(plate_columns)])
        plate_samples = self.plate_wells[self.plate_wells.plate_id == plate_id]
        plate_dict = {}
        for col in range(plate_columns):
            plate_dict[str(col)] = []
            for row in range(plate_rows):
                if len(plate_samples[(plate_samples.plate_rows == row) & (plate_samples.plate_columns == col)]) > 0:
                    plate_dict[str(col)].append(str(list(plate_samples.sample_name[(plate_samples.plate_rows == row) & (plate_samples.plate_columns == col)])[0]))
                plate_dict[str(col)].append()


