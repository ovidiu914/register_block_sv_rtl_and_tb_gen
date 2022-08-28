import sys
import os
import json
from rtl_reg_block_gen import rtl_reg_block
from uvm_reg_model_gen import reg_model

json_reg_file = sys.argv[1];
registers     = [];
reg_block_name = json_reg_file.replace('.json','') 
reg_width      = 32

''' class type which contains basic info about the registers'''

class register:
    
    ''' Class constructor '''
    def __init__(self,name,address,width,is_resettable,reset_value,mask,fields):
        self.name           = name
        self.class_name     = f"{self.name}_t"
        self.address        = address
        self.width          = width
        self.is_resettable  = is_resettable
        self.reset_value    = reset_value
        self.mask           = mask
        self.fields         = fields
        self.uvm_code       = ''
        self.rtl_code       = ''
        

    def __str__(self):
        print ( f"name= {self.name}  address= {self.address} width= {self.width} resetable= {self.is_resettable}  reset_value= {self.reset_value} mask = {self.mask} fields = {self.fields}" )

    
    ''' Testbench code'''
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


    def generate_uvm_code(self):
        self.create_uvm_header()
        self.create_uvm_new()
        self.create_uvm_build()
        self.append_footer()
    
    ''' RTL code '''
    
    def generate_rtl_code(self):
        pass
        
    def generate_reg_code(self):
        self.generate_rtl_code()
        self.generate_uvm_code()



def generate_code():
    parse_json_and_fill_reg_data();
    generate_rtl_reg_block();
    generate_uvm_reg_model();
    print ("Generating sv code...DONE")


def parse_json_and_fill_reg_data():
    register_raw_data = json.load(open(json_reg_file))
    for name in register_raw_data:
        reg_name = register_raw_data[name]
        reg = register(name ,reg_name["address"] ,reg_name["width"] ,reg_name["is_resettable"],reg_name["reset_value"],reg_name["mask"],reg_name["fields"])
        registers.append(reg)
        
        
def generate_rtl_reg_block():
    reg_block = rtl_reg_block(reg_width,reg_block_name,registers)
    reg_block.generate_code()
    
def generate_uvm_reg_model():
    pass
        

''' MAIN of the reg_block_gen '''   
if __name__ == "__main__":
    generate_code();
