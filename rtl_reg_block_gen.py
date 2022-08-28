n_line   = '\n'
tab      = '    '

class rtl_reg_block:
    
    def __init__(self,reg_width,reg_block_name,registers):
        self.reg_width      = reg_width
        self.reg_block_code = ''
        self.reg_block_name = reg_block_name
        self.registers      = registers
        
    def gen_module_header(self):
        reg_block_header = f"module {self.reg_block_name}#(parameter REG_WIDTH={self.reg_width}) ({n_line}{n_line}"
        reg_block_header =    f"{reg_block_header}{tab}input clk,{n_line}"
        reg_block_header =    f"{reg_block_header}{tab}input resetn,{n_line}"
        self.reg_block_code = f"{self.reg_block_code}{reg_block_header}{n_line}"
        self.gen_reg_interface();
        
    def gen_reg_interface(self):
        reg_if     = f"{n_line}"
        reg_decl   = ''
        last_comma = ','
        for reg in self.registers:
            if reg == self.registers[-1]:
                last_comma = f"{n_line}{tab});";
            reg_if = f"{reg_if}{tab}//{reg.name}{n_line}"
            reg_if = f"{reg_if}{tab}input  {reg.name}_wen_i,{n_line}"
            reg_if = f"{reg_if}{tab}input  [REG_WIDTH-1:0] {reg.name}_wdata_i,{n_line}"
            reg_if = f"{reg_if}{tab}output [REG_WIDTH-1:0] {reg.name}_rdata_o{last_comma}{n_line}{n_line}" 
        self.reg_block_code = f"{self.reg_block_code}{reg_if}"
        
        for reg in self.registers:
            reg_decl = f"{reg_decl}{tab}reg [REG_WIDTH-1:0] {reg.name};{n_line}"
        self.reg_block_code = f"{self.reg_block_code}{reg_decl}"
        
    def gen_registers(self):
        reg_string = ''
        for reg in self.registers:
            reg_string = f"{n_line}{tab}always@(posedge clk or negedge resetn) begin : {reg.name}_inst{n_line}"
            if (reg.is_resettable == "TRUE"):
                reg_string = f"{reg_string}{tab}{tab}if (!resetn) begin{n_line}"
                reg_string = f"{reg_string}{tab}{tab}{tab}{reg.name} <= {reg.reset_value};{n_line}";
                reg_string = f"{reg_string}{tab}{tab}end{n_line}{tab}{tab}else begin{n_line}"
            reg_string = f"{reg_string}{tab}{tab}{tab}if ({reg.name}_wen_i) begin{n_line}"
            reg_string = f"{reg_string}{tab}{tab}{tab}{tab}{reg.name} <= {reg.name}_wdata_i;{n_line}"
            reg_string = f"{reg_string}{tab}{tab}{tab}end{n_line}"
            reg_string = f"{reg_string}{tab}{tab}end{n_line}"
            reg_string = f"{reg_string}{tab}end{n_line}{n_line}"
            reg_string = f"{reg_string}{tab}assign {reg.name}_rdata_o = {reg.name};{n_line}"

                
            self.reg_block_code =f"{self.reg_block_code}{reg_string}"
            
        self.reg_block_code =f"{self.reg_block_code}{n_line}endmodule"
        
    def generate_code(self):
        self.gen_module_header()
        self.gen_registers()
        
        print (self.reg_block_code)