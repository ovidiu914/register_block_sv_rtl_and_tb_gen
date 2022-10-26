import sys
import os
import json

# http://cfs-vision.com/2015/07/20/how-to-startup-uvm_reg-systemverilog-library/

nl   = '\n'
tab1     = '    '
tab2     = f"{tab1}{tab1}" 
tab3     = f"{tab2}{tab1}" 
tab4     = f"{tab3}{tab1}" 
tab5     = f"{tab4}{tab1}"
tab6     = f"{tab5}{tab1}"
tab7     = f"{tab6}{tab1}"
tab8     = f"{tab7}{tab1}"

class reg_model:
    def __init__(self,registers,block_name):
        self.reg_model_name = block_name
        self.regs           = registers
        self.reg_model_code = ''
        self.generate_code()

    def generate_code(self):
        self.gen_reg_class()
        self.create_reg_block_code()
        print(self.reg_model_code)
    
    def gen_reg_class(self):
        for reg in self.regs:
            reg.generate_uvm_code()
            self.reg_model_code = f"{self.reg_model_code}{reg.uvm_code}{nl}{nl}"

    ### PARSE REGS TO CREATE REG BLOCK
    def create_reg_block_code(self):
        #Class header and factory macro
        reg_block_s        = f"class {self.reg_model_name} extends uvm_reg_block;{nl}{tab1}`uvm_object_utils({self.reg_model_name}){nl}"
        regs_declaration_s = ''
        #Build function header
        virtual_build_s    = f"{tab1}virtual function void build();{nl}"
        #New function header
        new_function_s     = f"{tab1}function new(string name = \"{self.reg_model_name}\");{nl}"
        new_function_s     = f"{new_function_s}{tab2}super.new(name, UVM_CVR_ALL);{nl}"
        #Process regs
        for reg in self.regs:
            regs_declaration_s = f"{regs_declaration_s}{tab1}rand  {reg.class_name} {reg.name};{nl}"
            new_function_s     = f"{new_function_s}{tab2}{reg.name} = {reg.class_name}::type_id::create(\"{reg.name}\");{nl}"
            virtual_build_s    = f"{virtual_build_s}{tab2}{reg.name}.configure(this,null,\"\");{nl}{tab2}{reg.name}.build();{nl}"
        new_function_s  = f"{new_function_s}{tab1}endfunction{nl}{nl}"

        self.generate_default_map()
        virtual_build_s = f"{virtual_build_s}{self.map_code}"
        virtual_build_s = f"{virtual_build_s}{tab1}endfunction{nl}{nl}"
        reg_block_s = f"{reg_block_s}{regs_declaration_s}{new_function_s}{virtual_build_s}"
        reg_block_s = f"{reg_block_s}endclass:{self.reg_model_name}"
        self.reg_model_code =  f"{self.reg_model_code}{reg_block_s}"

    def generate_reg_model_file(self):
        f = open(f"{self.reg_model_name}.svh","w")
        f.write(self.reg_model_code)
        f.close()

    def generate_default_map(self):
        self.map_code = f"{tab2}default_map = create_map({nl}"
        self.map_code = f"{self.map_code}{tab3}name         = \"{self.reg_model_name}_map\",{nl}"
        self.map_code = f"{self.map_code}{tab3}base_address = 'h0,{nl}"
        self.map_code = f"{self.map_code}{tab3}n_bytes      = 1,{nl}"
        self.map_code = f"{self.map_code}{tab3}endian       = UVM_BIG_ENDIAN);{nl}"
        self.map_code = f"{self.map_code}{tab2}default_map.set_check_on_read(1);{nl}"
        for reg in self.regs:
            reg_acces = ''
            for field in reg.fields:
                reg_acces = reg.fields[field]['access_type']
                break;
            self.map_code = f"{self.map_code}{tab2}map.add_reg({reg.name},{reg.address},{reg_acces};{nl}"

    # def add_registers_to_map(self):

