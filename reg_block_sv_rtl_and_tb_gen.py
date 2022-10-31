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
quote    = '"'

from rtl_reg_block_gen import rtl_reg_block
from uvm_reg_model_gen import reg_model

json_reg_file  = sys.argv[1];
registers      = [];
reg_block_name = json_reg_file.replace('.json','')
reg_width      = 32

ADDR_WIDTH_IN_BYTES   = ''
DATA_WIDTH_IN_BYTES   = ''

''' contains basic info about the registers'''

class register:
    
    ''' Class constructor '''
    def __init__(self,name,address,width,reset_value,mask,fields):
        self.name           = name
        self.class_name     = f"{self.name}_t"
        self.address        = address
        self.width          = width
        self.reset_value    = reset_value
        self.mask           = mask
        self.fields         = fields
        self.uvm_code       = ''
        
    def __str__(self):
        print ( f"name= {self.name}  address= {self.address} width= {self.width} resetable= {self.is_resettable}  reset_value= {self.reset_value} mask = {self.mask} fields = {self.fields}" )
    
    ''' Create testbench code '''
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
            field_c = f"""{field_c}{tab2}{field}.configure(.parent(this), .size({field_to_access["width"]}), .lsb_pos({field_to_access["offset"]}), .access({quote}{field_to_access["access_type"]}{quote}), .volatile(0), .reset(0), .has_reset(1), .is_rand(1), .individually_accessible(1));{nl}"""
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
    

def generate_code():
    parse_json_and_fill_reg_data();
    check_parsed_data();
    generate_uvm_reg_model();
    generate_rtl_reg_block();

def check_parsed_data():
    reg_names  = []
    reg_widths = []
    addresses  = []
    for reg in registers:
        """ Check total width of register is the same as """
        for field in reg.fields:
            for field_attribute in reg.fields[field]:
                print (f"{field_attribute} {reg.fields[field][field_attribute]}")
        # exit()
    
"""Throw error on register duplicate name"""
def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
           # raise ValueError("duplicate key: %r" % (k,))
           if k == "Reserved": 
               pass 
           else:
               print (f" REGISTER NAME DUPLICATE:{k} ")
               exit()
        else:
           d[k] = v
    return d




def parse_json_and_fill_reg_data():
    register_raw_data = json.load(open(json_reg_file),object_pairs_hook = dict_raise_on_duplicates)
    for name in register_raw_data:
        global ADDR_WIDTH_IN_BYTES
        global DATA_WIDTH_IN_BYTES
        if name == "ADDR_WIDTH_IN_BYTES" :
            ADDR_WIDTH_IN_BYTES = int(register_raw_data[name])
            continue
        if name == "DATA_WIDTH_IN_BYTES" :
            DATA_WIDTH_IN_BYTES = int(register_raw_data[name])
            continue
        reg_name = register_raw_data[name]
        reg = register(name ,reg_name["address"] ,reg_name["width"] ,reg_name["reset_value"],reg_name["mask"],reg_name["fields"])
        registers.append(reg)
    
def generate_rtl_reg_block():
    reg_block = rtl_reg_block(registers,reg_block_name,ADDR_WIDTH_IN_BYTES,DATA_WIDTH_IN_BYTES)
    reg_block.generate_code()
    
def generate_uvm_reg_model():
    reg_block_tb = reg_model(registers,reg_block_name,ADDR_WIDTH_IN_BYTES)

''' MAIN of the reg_block_gen '''   
if __name__ == "__main__":
    generate_code();
    

    
    
    
