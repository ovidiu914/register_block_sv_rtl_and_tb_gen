import sys
import os
import json

# http://cfs-vision.com/2015/07/20/how-to-startup-uvm_reg-systemverilog-library/

tab   = '    '
new_line= "\n"
# Class which collects data related to register and generates code specific to it

class register:
    def __init__(self,name,address,width,is_resettable,reset_value,mask,fields):
        self.name           = name
        self.class_name     = f"{self.name}_t"
        self.address        = address
        self.width          = width
        self.is_resettable  = is_resettable
        self.reset_value    = reset_value
        self.mask           = mask
        self.fields         = fields
        self.uvm_code           = ''

    def __str__(self):
        print ( f"name= {self.name}  address= {self.address} width= {self.width} resetable= {self.is_resettable}  reset_value= {self.reset_value} mask = {self.mask} fields = {self.fields}" )

    def create_uvm_header(self):
        uvm_reg_string = f"class {self.class_name} extends uvm_reg;{new_line}{new_line}"
        uvm_reg_string = f"{uvm_reg_string}{tab}`uvm_object_utils({self.name}){new_line}"
        field_string   = ''
        for field in self.fields:
            field_string = f"{field_string}{tab}rand uvm_reg_field {field};{new_line}";
        uvm_reg_string   = f"{uvm_reg_string}{field_string}{new_line}"
        self.uvm_code        = f"{self.uvm_code}{uvm_reg_string}"


    def create_uvm_new (self):
        self.new_f = f"{tab}function new(string name = \"{self.name}\");{new_line}"
        self.new_f = f"{self.new_f}{tab}{tab}//specify the name of the register, its width in bits and if it has coverage{new_line}"
        self.new_f = f"{self.new_f}{tab}{tab}super.new(name, {self.width}, 1);{new_line}";
        self.new_f = f"{self.new_f}{tab}endfunction{new_line}{new_line}"
        self.uvm_code  = f"{self.uvm_code}{self.new_f}"

    def create_uvm_build(self):
        self.build_f = f"{tab}virtual function void build();{new_line}";
        self.build_f = f"{self.build_f}{tab}{tab} //specify parent, width, lsb position, rights, volatility{new_line}"
        self.build_f = f"{self.build_f}{tab}{tab} //reset value, has reset, is_rand, individually_accessible{new_line}"
        field_c =''
        for field in self.fields:
            field_to_access = self.fields[field]
            field_c = f"{field_c}{tab}{tab}{field} = uvm_reg_field::type_id::create(\"{field}\");{new_line}"
            field_c = f"""{field_c}{tab}{tab}{field}.configure(this, {field_to_access["width"]}, {field_to_access["offset"]}, {field_to_access["access_type"]}, 0, 0, 1, 1, 1);{new_line}"""
        self.build_f  = f"{self.build_f}{field_c}"
        self.build_f  = f"{self.build_f}{tab}endfunction{new_line}"
        self.uvm_code = f"{self.uvm_code}{self.build_f}"

    def append_footer(self):
        self.uvm_code = f"{self.uvm_code}{new_line}endclass:{self.class_name}{new_line}{new_line}"

    def generate_code(self):
        self.create_uvm_header()
        self.create_uvm_new()
        self.create_uvm_build()
        self.append_footer()

# Reg block class
class reg_model:

    def __init__(self,json_reg_file):
        self.reg_model_name = json_reg_file
        self.data           = json.load(open(json_reg_file))
        self.regs           = []
        self.reg_model_code = ''
        self.base_addr = "0x0"
        self.def_map_code   = ''
        #Parse reg data from json file
        self.parse_reg_data_and_create_registers()
        #Append reg code to file
        self.append_reg_code()
        #Create reg block
        self.create_reg_block_code()
        #Generate reg block class
        self.generate_reg_model_file()
        print (self.reg_model_code)

    def parse_reg_data_and_create_registers(self):
        for name in self.data:
            reg_name = self.data[name]
            reg = register(name ,reg_name["address"] ,reg_name["width"] ,reg_name["is_resettable"],reg_name["reset_value"],reg_name["mask"],reg_name["fields"])
            reg.generate_code()
            self.regs.append(reg)

    def append_reg_code(self):
        for reg in self.regs:
            self.reg_model_code =f"{self.reg_model_code}{reg.code}{new_line}"

    ### PARSE REGS TO CREATE REG BLOCK
    def create_reg_block_code(self):
        #Class header and factory macro
        reg_block_s        = f"class {self.reg_model_name} extends uvm_reg_block;{new_line}{tab}`uvm_object_utils({self.reg_model_name}){new_line}"
        regs_declaration_s = ''
        #Build function header
        virtual_build_s    = f"{tab}virtual function void build();{new_line}"
        #New function header
        new_function_s     = f"{tab}function new(string name = \"{self.reg_model_name}\");{new_line}"
        new_function_s     = f"{new_function_s}{tab}{tab}super.new(name, UVM_CVR_ALL);{new_line}"
        #Process regs
        for reg in self.regs:
            regs_declaration_s = f"{regs_declaration_s}{tab}rand  {reg.class_name} {reg.name};{new_line}"
            new_function_s     = f"{new_function_s}{tab}{tab}{reg.name} = {reg.class_name}::type_id::create(\"{reg.name}\");{new_line} "
            virtual_build_s    = f"{virtual_build_s}{tab}{tab}{reg.name}.configure(this,null,\"\");{new_line}{tab}{tab}{reg.name}.build();{new_line}"
        new_function_s  = f"{new_function_s}{tab}endfunction{new_line}{new_line}"

        self.generate_default_map()
        virtual_build_s = f"{virtual_build_s}{self.def_map_code}"
        virtual_build_s = f"{virtual_build_s}{tab}endfunction{new_line}{new_line}"
        reg_block_s = f"{reg_block_s}{regs_declaration_s}{new_function_s}{virtual_build_s}"
        reg_block_s = f"{reg_block_s}endclass:{self.reg_model_name}"
        self.reg_model_code =  f"{self.reg_model_code}{reg_block_s}"

    def generate_reg_model_file(self):
        f = open(f"{self.reg_model_name}.svh","w")
        f.write(self.reg_model_code)
        f.close()

    def generate_default_map(self):
        self.def_map_code = f"{self.def_map_code }{tab}{tab}default_map = create_map({new_line}"
        self.def_map_code = f"{self.def_map_code}{tab}{tab}{tab}name         = \"{self.reg_model_name}_map\",{new_line}"
        self.def_map_code = f"{self.def_map_code}{tab}{tab}{tab}base_address = {self.base_addr},{new_line}"
        self.def_map_code = f"{self.def_map_code}{tab}{tab}{tab}n_bytes      = 1,{new_line}"
        self.def_map_code = f"{self.def_map_code}{tab}{tab}{tab}endian       = UVM_BIG_ENDIAN);{new_line}"
        self.def_map_code = f"{self.def_map_code}{tab}{tab}{tab}default_map.set_check_on_read(1);{new_line}"
        for reg in self.regs:
            pass
            #self.def_map_code = f"""{self.def_map_code}{tab}{tab}{tab}map.add_reg({reg.name},{reg.address}+{self.base_address},{reg.);\n"""

    # def add_registers_to_map(self):

