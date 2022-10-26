import sys
import os
import json

nl   = '\n'
tab1     = '    '
tab2     = f"{tab1}{tab1}" 
tab3     = f"{tab2}{tab1}" 
tab4     = f"{tab3}{tab1}" 
tab5     = f"{tab4}{tab1}"
tab6     = f"{tab5}{tab1}"
tab7     = f"{tab6}{tab1}"
tab8     = f"{tab7}{tab1}"

from rtl_reg_block_gen import rtl_reg_block
from uvm_reg_model_gen import reg_model

json_reg_file = sys.argv[1];
registers     = [];
reg_block_name    = json_reg_file.replace('.json','')
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
        uvm_reg_string = f"class {self.class_name} extends uvm_reg;{nl}{nl}"
        uvm_reg_string = f"{uvm_reg_string}{tab1}`uvm_object_utils({self.class_name}){nl}"
        field_string   = ''
        for field in self.fields:
            field_string = f"{field_string}{tab1}rand uvm_reg_field {field};{nl}";
        uvm_reg_string   = f"{uvm_reg_string}{field_string}{nl}"
        self.uvm_code        = f"{self.uvm_code}{uvm_reg_string}"


    def create_uvm_new (self):
        self.new_f = f"{tab1}function new(string name = \"{self.name}\");{nl}"
        self.new_f = f"{self.new_f}{tab2}//specify the name of the register, its width in bits and if it has coverage{nl}"
        self.new_f = f"{self.new_f}{tab2}super.new(name, {self.width}, 1);{nl}";
        self.new_f = f"{self.new_f}{tab1}endfunction{nl}{nl}"
        self.uvm_code  = f"{self.uvm_code}{self.new_f}"


    def create_uvm_build(self):
        self.build_f = f"{tab1}virtual function void build();{nl}";
        self.build_f = f"{self.build_f}{tab2} //specify parent, width, lsb position, rights, volatility{nl}"
        self.build_f = f"{self.build_f}{tab2} //reset value, has reset, is_rand, individually_accessible{nl}"
        field_c =''
        for field in self.fields:
            field_to_access = self.fields[field]
            field_c = f"{field_c}{tab2}{field} = uvm_reg_field::type_id::create(\"{field}\");{nl}"
            field_c = f"""{field_c}{tab2}{field}.configure(this, {field_to_access["width"]}, {field_to_access["offset"]}, {field_to_access["access_type"]}, 0, 0, 1, 1, 1);{nl}"""
        self.build_f  = f"{self.build_f}{field_c}"
        self.build_f  = f"{self.build_f}{tab1}endfunction{nl}"
        self.uvm_code = f"{self.uvm_code}{self.build_f}"


    def append_footer(self):
        self.uvm_code = f"{self.uvm_code}{nl}endclass:{self.class_name}{nl}{nl}"


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
        if name == f"{reg_block_name}_base_address" :
            pass
        reg_name = register_raw_data[name]
        reg = register(name ,reg_name["address"] ,reg_name["width"] ,reg_name["is_resettable"],reg_name["reset_value"],reg_name["mask"],reg_name["fields"])
        registers.append(reg)
    
def generate_rtl_reg_block():
    reg_block = rtl_reg_block(reg_width,reg_block_name,registers)
    reg_block.generate_code()
    
def generate_uvm_reg_model():
    reg_block_tb = reg_model(registers,f"{reg_block_name}")

''' MAIN of the reg_block_gen '''   
if __name__ == "__main__":
    generate_code();
