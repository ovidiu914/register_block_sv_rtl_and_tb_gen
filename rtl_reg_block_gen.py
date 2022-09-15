n_line   = '\n'
tab      = '    '
tab2     = f"{tab}{tab}" 
tab3     = f"{tab}{tab}{tab}" 
tab4     = f"{tab}{tab}{tab}{tab}" 
tab5     = f"{tab}{tab}{tab}{tab}{tab}"
tab6     = f"{tab}{tab}{tab}{tab}{tab}{tab}"


reg_addr_width = 32
reg_data_width = 32

class rtl_reg_block:
    
    def __init__(self,reg_width,reg_block_name,registers):
        self.reg_width      = reg_width
        self.reg_block_code = ''
        self.decoder_code   = ''
        self.reg_block_name = reg_block_name
        self.registers      = registers
        self.reg_addr_width = 32
        self.reg_data_width = 32
        
    def gen_module_header(self):
        reg_block_header = f"module {self.reg_block_name}#(parameter REG_WIDTH={self.reg_width}) ({n_line}{n_line}"
        reg_block_header =    f"{reg_block_header}{tab}input clk,{n_line}"
        reg_block_header =    f"{reg_block_header}{tab}input resetn,{n_line}"
        reg_block_header =    f"{reg_block_header}{tab}input w_data_i,{n_line}"
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
                reg_string = f"{reg_string}{tab2}if (!resetn) begin{n_line}"
                reg_string = f"{reg_string}{tab}{tab}{tab}{reg.name} <= {reg.reset_value};{n_line}";
                reg_string = f"{reg_string}{tab}{tab}end{n_line}{tab}{tab}else begin{n_line}"
            reg_string = f"{reg_string}{tab}{tab}{tab}if ({reg.name}_wen_i) begin{n_line}"
            reg_string = f"{reg_string}{tab4}{reg.name} <= w_data_i;{n_line}"
            reg_string = f"{reg_string}{tab}{tab}{tab}end{n_line}"
            reg_string = f"{reg_string}{tab}{tab}end{n_line}"
            reg_string = f"{reg_string}{tab}end{n_line}{n_line}"
            reg_string = f"{reg_string}{tab}assign {reg.name}_rdata_o = {reg.name};{n_line}"

                
            self.reg_block_code =f"{self.reg_block_code}{reg_string}"
            
        self.reg_block_code =f"{self.reg_block_code}{n_line}endmodule"
        
    def gen_reg_block(self):
         self.gen_module_header()
         self.gen_registers()
   
   
   
   
    ''' Decoder module header'''
    def gen_decoder_header(self):
        decoder_h= f"module decoder #(parameter REG_ADDR_WIDTH = {self.reg_addr_width}, parameter REG_DATA_WIDTH = {self.reg_addr_width}) ({n_line}{n_line}"
        decoder_h =f"{decoder_h}{tab}input clk,{n_line}"
        decoder_h =f"{decoder_h}{tab}input resetn,{n_line}"
        decoder_h =f"{decoder_h}{n_line}{tab}//input data from the ocp bridge,{n_line}"
        decoder_h =f"{decoder_h}{tab}input [REG_DATA_WIDTH-1:0] reg_wdata_i,{n_line}"
        decoder_h =f"{decoder_h}{tab}input [REG_ADDR_WIDTH-1:0] reg_address_i,{n_line}"
        decoder_h =f"{decoder_h}{tab}input reg_wen_i,{n_line}"
        decoder_h =f"{decoder_h}{tab}input reg_ren_i,{n_line}"
        decoder_h =f"{decoder_h}{n_line}{tab}//Write data to reg container{n_line}"
        decoder_h =f"{decoder_h}{tab}output [REG_DATA_WIDTH-1:0] reg_wdata_o,{n_line}"
        
        self.decoder_code = f"{self.decoder_code}{decoder_h}{n_line}"
        self.gen_decoder_reg_if();
        
           
    def gen_decoder_reg_if(self):
        reg_if     = f"{n_line}"
        reg_decl   = ''
        last_comma = ','
        for reg in self.registers:
            reg.wr_o = f"{reg.name}_wen_o"
            if reg == self.registers[-1]:
                last_comma = f"{n_line}{tab});";
            reg_if = f"{reg_if}{tab}//{reg.name}{n_line}"
            # reg_if = f"{reg_if}{tab}input  {reg.name}_wen_i,{n_line}"
            reg_if = f"{reg_if}{tab}input [REG_DATA_WIDTH-1:0] {reg.name}_rdata_o,{n_line}"
            reg_if = f"{reg_if}{tab}output reg {reg.name}_wen_o{last_comma}{n_line}{n_line}" 
        self.decoder_code = f"{self.decoder_code}{reg_if}"
        
        for reg in self.registers:
            reg.addr_var = f"{reg.name}_ADDR"
            reg_decl     = f"{reg_decl}{tab}localparam {reg.addr_var} = {reg.address};{n_line}"
        self.decoder_code = f"{self.decoder_code}{reg_decl}"
    
        
        reg_rdata_int = f"{n_line}{tab}//Reg rdata interconnect;{n_line}"
        reg_rdata_int = f"{reg_rdata_int}{tab}reg [REG_DATA_WIDTH-1:0] reg_rdata_int;{n_line}"
        self.decoder_code = f"{self.decoder_code}{reg_rdata_int}"
        
    def gen_decoder_footer(self):
         self.decoder_code = f"{self.decoder_code}endmodule:decoder"
         
    def decode_reg_op(self):
        reg_decode        = '' 
        reg_decode_footer = ''
        reg_address       = 'ADDRESS'
        for reg in self.registers:
            reg_decode = f"{tab3}{reg.addr_var}: begin{n_line}"
            reg_decode = f"{reg_decode}{tab4}case({{reg_wen_i, reg_ren_i}}){n_line}"
            reg_decode = f"{reg_decode}{tab5}2'b10: begin{n_line}"
            ''' SET WEN for specified reg '''
            for register in self.registers:
                if register.address == reg_address:
                    reg_decode = f"{reg_decode}{tab6}{register.name}_wen_o = 1'b1;{n_line}"
                else: 
                    reg_decode = f"{reg_decode}{tab6}{register.name}_wen_o = 1'b0;{n_line}"
            reg_decode = f"{reg_decode}{tab6}reg_rdata_int = 0;{n_line}"
            reg_decode = f"{reg_decode}{tab5}end{n_line}"
            reg_decode = f"{reg_decode}{tab5}2'b01: begin{n_line}"
            for register in self.registers:
                reg_decode = f"{reg_decode}{tab6}{register.name}_wen_o = 1'b0;{n_line}"
            reg_decode = f"{reg_decode}{tab6}reg_rdata_int = r0_rdata_i;{n_line}"
            reg_decode = f"{reg_decode}{tab5}end{n_line}"
            reg_decode = f"{reg_decode}{tab5}default: begin{n_line}"
            for register in self.registers:
                reg_decode = f"{reg_decode}{tab6}{register.name}_wen_o = 1'b0;{n_line}"
            reg_decode = f"{reg_decode}{tab6}reg_rdata_int = 'x;{n_line}"
            reg_decode = f"{reg_decode}{tab5}end{n_line}"
            reg_decode = f"{reg_decode}{tab4}endcase{n_line}"
            self.decoder_code = f"{self.decoder_code}{reg_decode}"
             
        reg_decode_footer = f"{reg_decode_footer}{tab3}default: begin{n_line}"
        reg_decode_footer = f"{reg_decode_footer}{tab4}r0_wen_int    = 1'b0;{n_line}"
        reg_decode_footer = f"{reg_decode_footer}{tab4}reg_rdata_int = 1'x;{n_line}"
        self.decoder_code = f"{self.decoder_code}{reg_decode_footer}{n_line}"

    def gen_decoder_body(self):
        decoder_body = f"{n_line}"
        decoder_body = f"{decoder_body}{tab}always_comb begin : ADDR_DECODER{n_line}"
        decoder_body = f"{decoder_body}{tab2}case (reg_address_i){n_line}"
        self.decoder_code = f"{self.decoder_code}{decoder_body}"
        self.decode_reg_op()

    def gen_decoder(self): 
         self.gen_decoder_header()
         self.gen_decoder_body() 
         self.gen_decoder_footer()
         
        
    
        
    ''' Generate reg block and decoder'''
    def generate_code(self):
         self.gen_reg_block()
         self.gen_decoder()
         print (self.reg_block_code)
         print (self.decoder_code)
