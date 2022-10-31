nl       = '\n'
tab1     = '    '
tab2     = f"{tab1}{tab1}" 
tab3     = f"{tab2}{tab1}" 
tab4     = f"{tab3}{tab1}" 
tab5     = f"{tab4}{tab1}"
tab6     = f"{tab5}{tab1}"
tab7     = f"{tab6}{tab1}"
tab8     = f"{tab7}{tab1}"

class rtl_reg_block:
    
    def __init__(self,registers,reg_block_name,ADDR_WIDTH_IN_BYTES,DATA_WIDTH_IN_BYTES):
        self.registers       = registers
        self.reg_block_name  = reg_block_name
        self.base_addr_param = f"{self.reg_block_name}_BASE_ADDR"
        self.reg_addr_width  = 8*ADDR_WIDTH_IN_BYTES
        self.reg_data_width  = 8*DATA_WIDTH_IN_BYTES
        ''' Module names '''
        self.reg_container  = f"{reg_block_name}_reg_container"
        self.reg_decoder    = f"{reg_block_name}_decoder"
        
        ''' Parsed from json'''
        self.reg_container_code  = ''
        self.decoder_code        = ''
        self.reg_block_code      = ''
        
    # Reg container         
    def gen_reg_container_inputs(self):
        reg_block_header = f"module {self.reg_container}#(parameter REG_DATA_WIDTH={self.reg_addr_width}) ({nl}{nl}"
        reg_block_header =    f"{reg_block_header}{tab1}input clk,{nl}"
        reg_block_header =    f"{reg_block_header}{tab1}input resetn,{nl}"
        reg_block_header =    f"{reg_block_header}{tab1}input [REG_DATA_WIDTH-1:0] reg_wdata_i,{nl}"
        self.reg_container_code = f"{self.reg_container_code}{reg_block_header}{nl}"
        self.gen_reg_interface();
        
    # Reg container
    def gen_reg_interface(self):
        reg_if     = f"{nl}"
        reg_decl   = ''
        last_comma = ','
        for reg in self.registers:
            if reg == self.registers[-1]:
                last_comma = f"{nl}{tab1});";
            reg_if = f"{reg_if}{tab1}//{reg.name}{nl}"
            reg_if = f"{reg_if}{tab1}input  {reg.name}_wen_i,{nl}"
            reg_if = f"{reg_if}{tab1}output [REG_DATA_WIDTH-1:0] {reg.name}_rdata_o{last_comma}{nl}{nl}" 
        self.reg_container_code = f"{self.reg_container_code}{reg_if}"
        
        for reg in self.registers:
            reg_decl = f"{reg_decl}{tab1}reg [REG_DATA_WIDTH-1:0] {reg.name};{nl}"
        self.reg_container_code = f"{self.reg_container_code}{reg_decl}"
    
    
    def gen_reg_with_no_reset(self,reg):
        reg_string = f"{nl}{tab1}always_ff @(posedge clk) begin : {reg.name}_inst{nl}"
        reg_string = f"{reg_string}{tab2}if({reg.name}_wen_i) begin{nl}"
        reg_string = f"{reg_string}{tab3}{reg.name} <= reg_wdata_i;{nl}"
        reg_string = f"{reg_string}{tab2}end{nl}"
        reg_string = f"{reg_string}{tab1}end{nl}"
        reg_string = f"{reg_string}{tab1}assign {reg.name}_rdata_o = {reg.name};{nl}"

        return reg_string
    def gen_reg_with_reset(self,reg):
        reg_string = f"{nl}{tab1}always_ff @(posedge clk or negedge resetn) begin : {reg.name}_inst{nl}"
        reg_string = f"{reg_string}{tab2}if (!resetn) begin{nl}"
        reg_string = f"{reg_string}{tab1}{tab1}{tab1}{reg.name} <= {reg.reset_value};{nl}";
        reg_string = f"{reg_string}{tab1}{tab1}end{nl}{tab1}{tab1}else begin{nl}"
        reg_string = f"{reg_string}{tab1}{tab1}{tab1}if ({reg.name}_wen_i) begin{nl}"
        reg_string = f"{reg_string}{tab4}{reg.name} <= reg_wdata_i;{nl}"
        reg_string = f"{reg_string}{tab1}{tab1}{tab1}end{nl}"
        reg_string = f"{reg_string}{tab1}{tab1}end{nl}"
        reg_string = f"{reg_string}{tab1}end{nl}{nl}"
        reg_string = f"{reg_string}{tab1}assign {reg.name}_rdata_o = {reg.name};{nl}"
        # print (reg_string)
        return reg_string
 # Reg container    
    def gen_registers(self):
        reg_string = ''
        for reg in self.registers:
            if (reg.reset_value != "NOT_RESETABLE"):
                reg_string = self.gen_reg_with_reset(reg)
                # reg_string = f"{nl}{tab1}always_ff @(posedge clk or negedge resetn) begin : {reg.name}_inst{nl}"
                # reg_string = f"{reg_string}{tab2}if (!resetn) begin{nl}"
                # reg_string = f"{reg_string}{tab1}{tab1}{tab1}{reg.name} <= {reg.reset_value};{nl}";
                # reg_string = f"{reg_string}{tab1}{tab1}end{nl}{tab1}{tab1}else begin{nl}"
                # reg_string = f"{reg_string}{tab1}{tab1}{tab1}if ({reg.name}_wen_i) begin{nl}"
                # reg_string = f"{reg_string}{tab4}{reg.name} <= reg_wdata_i;{nl}"
                # reg_string = f"{reg_string}{tab1}{tab1}{tab1}end{nl}"
                # reg_string = f"{reg_string}{tab1}{tab1}end{nl}"
                # reg_string = f"{reg_string}{tab1}end{nl}{nl}"
                # reg_string = f"{reg_string}{tab1}assign {reg.name}_rdata_o = {reg.name};{nl}"
            else: 
                reg_string = self.gen_reg_with_no_reset(reg)
                # reg_string = f"{nl}{tab1}always_ff @(posedge clk) begin : {reg.name}_inst{nl}"
                # reg_string = f"{reg_string}{tab2}if({reg.name}_wen_i) begin{nl}"
                # reg_string = f"{reg_string}{tab3}{reg.name} <= reg_wdata_i;{nl}"
                # reg_string = f"{reg_string}{tab2}end{nl}"
                # reg_string = f"{reg_string}{tab1}end{nl}"
                # reg_string = f"{reg_string}{tab1}assign {reg.name}_rdata_o = {reg.name};{nl}"

            self.reg_container_code =f"{self.reg_container_code}{reg_string}"
            
        self.reg_container_code =f"{self.reg_container_code}{nl}endmodule:{self.reg_container}{nl}"
        
    def gen_reg_container(self):
         self.gen_reg_container_inputs()
         self.gen_registers()
   
   
    # Reg decoder
    def gen_decoder_header(self):
        decoder_h= f"module {self.reg_decoder} #(parameter REG_ADDR_WIDTH = {self.reg_addr_width}, parameter REG_DATA_WIDTH = {self.reg_data_width}, parameter BASE_ADDRESS = 0) ({nl}{nl}"
        decoder_h =f"{decoder_h}{tab1}input clk,{nl}"
        decoder_h =f"{decoder_h}{tab1}input resetn,{nl}"
        decoder_h =f"{decoder_h}{nl}{tab1}//input data from the ocp bridge,{nl}"
        decoder_h =f"{decoder_h}{tab1}input [REG_DATA_WIDTH-1:0] reg_wdata_i,{nl}"
        decoder_h =f"{decoder_h}{tab1}input [REG_ADDR_WIDTH-1:0] reg_address_i,{nl}"
        decoder_h =f"{decoder_h}{tab1}input reg_wen_i,{nl}"
        decoder_h =f"{decoder_h}{tab1}input reg_ren_i,{nl}"
        decoder_h =f"{decoder_h}{nl}{tab1}//Write data to reg container{nl}"
        decoder_h =f"{decoder_h}{tab1}output [REG_DATA_WIDTH-1:0] reg_wdata_o,{nl}"
        decoder_h =f"{decoder_h}{nl}{tab1}//Read data from reg container to ocp{nl}"
        decoder_h =f"{decoder_h}{tab1}output [REG_DATA_WIDTH-1:0] reg_rdata_o,{nl}"
        decoder_h =f"{decoder_h}{nl}{tab1}//error to ocp - decode failure or wr and rd in the same time {nl}"
        decoder_h =f"{decoder_h}{tab1}output error_o,"
        decoder_h =f"{decoder_h}{tab1}output ack_o,"
        
        self.decoder_code = f"{self.decoder_code}{decoder_h}{nl}"
        self.gen_decoder_reg_if();
        
           
    def gen_decoder_reg_if(self):
        reg_if     = f"{nl}"
        reg_decl   = ''
        last_comma = ','
        for reg in self.registers:
            reg.wr_o    = f"{reg.name}_wen_o"
            reg.rdata_o = f"{reg.name}_rdata_i"
            if reg == self.registers[-1]:
                last_comma = f"{nl}{tab1});";
            reg_if = f"{reg_if}{tab1}//{reg.name}{nl}"
            # reg_if = f"{reg_if}{tab1}input  {reg.name}_wen_i,{nl}"
            reg_if = f"{reg_if}{tab1}input [REG_DATA_WIDTH-1:0] {reg.rdata_o},{nl}"
            reg_if = f"{reg_if}{tab1}output  {reg.name}_wen_o{last_comma}{nl}{nl}" 
        self.decoder_code = f"{self.decoder_code}{reg_if}"
        
        for reg in self.registers:
            ''' ADD address to specific  reg '''
            reg.addr_var = f"{reg.name}_ADDR"
            ''' ADD wen to specific reg '''
            reg.wen      = f"{reg.name}_wen_o"
            reg.wen_w    = f"{reg.name}_wen_o_w"
            ''' ADD ren to specific reg'''
            reg.ren      = f"{reg.name}_ren_o"
            reg_decl     = f"{reg_decl}{tab1}localparam {reg.addr_var} = BASE_ADDRESS + {reg.address};{nl}"
        self.decoder_code = f"{self.decoder_code}{tab1}//Registers addresses{nl}"
        self.decoder_code = f"{self.decoder_code}{reg_decl}{nl}"
        
        
        state_param = '' 
        # STATE param
        state_param = f"{state_param}{tab1}//ACK/ERR fsm states;{nl}"
        state_param = f"{state_param}{tab1}localparam IDLE = 0;{nl}"
        state_param = f"{state_param}{tab1}localparam RESP = 1;{nl}"
        state_param = f"{state_param}{tab1}localparam ERR  = 2;{nl}"
        state_param = f"{state_param}{nl}{tab1}//internal ack,error{nl}"
        state_param = f"{state_param}{tab1}reg ack;{nl}"
        state_param = f"{state_param}{tab1}reg error;{nl}"
        
        self.decoder_code = f"{self.decoder_code}{state_param}{nl}"
        # Add reg for wr_o en
        reg_wen = ''
        for reg in self.registers:
           reg_wen = f"{reg_wen}{tab1}reg {reg.wen_w};{nl}"
        self.decoder_code = f"{self.decoder_code}{reg_wen}{nl}{nl}"
        
        reg_wen = ''
        for reg in self.registers:
           reg_wen = f"{reg_wen}{tab1}assign {reg.wen} = {reg.wen_w};{nl}"
        self.decoder_code = f"{self.decoder_code}{reg_wen}{nl}"
        
        reg_rdata_int = f"{tab1}//Reg rdata interconnect;{nl}"
        reg_rdata_int = f"{reg_rdata_int}{tab1}reg [REG_DATA_WIDTH-1:0] reg_rdata_int;{nl}"
        
        #Assign wdata_i to wdata_o        
        reg_rdata_int = f"{reg_rdata_int}{tab1}assign reg_wdata_o = reg_wdata_i;{nl}"
        self.decoder_code = f"{self.decoder_code}{reg_rdata_int}"
        
        
    def gen_decoder_error_fsm(self):
        decode_error =f"always @(posedge clk or negedge resetn) begin : DECODER"
        # decode_error =f"always @(posedge clk or negedge resetn) begin : DECODER
        # decode_error =f"always @(posedge clk or negedge resetn) begin : DECODER    
    def gen_decoder_footer(self):
         self.decoder_code = f"{self.decoder_code}endmodule:{self.reg_decoder}{nl}{nl}"
    
    ''' Generate reg block addr decoder'''
        
    def decode_reg_op(self):
        reg_decode        = '' 
        reg_decode_footer = ''
        reg_address       = 'ADDRESS'
        ''' Generate decoding code for each register '''
        for reg in self.registers:
            reg_decode = f"{tab3}{reg.addr_var}: begin{nl}"
            reg_decode = f"{reg_decode}{tab4}case({{reg_wen_i, reg_ren_i}}){nl}"
            reg_decode = f"{reg_decode}{tab5}2'b10: begin{nl}"
            ''' SET WEN for specified reg '''
            for register in self.registers:
                if register.name in reg.addr_var:
                    reg_decode = f"{reg_decode}{tab6}{register.wen_w} = 1'b1;{nl}"
                else: 
                    reg_decode = f"{reg_decode}{tab6}{register.wen_w} = 1'b0;{nl}"
            reg_decode = f"{reg_decode}{tab6}//reg_rdata_int = 0;{nl}"
            reg_decode = f"{reg_decode}{tab5}end{nl}"
            reg_decode = f"{reg_decode}{tab5}2'b01: begin{nl}"
            for register in self.registers:
                reg_decode = f"{reg_decode}{tab6}{register.wen_w} = 1'b0;{nl}"
            reg_decode = f"{reg_decode}{tab6}reg_rdata_int = {reg.rdata_o};{nl}"
            reg_decode = f"{reg_decode}{tab5}end{nl}"
            reg_decode = f"{reg_decode}{tab5}//2'b00: begin{nl}"
            reg_decode = f"{reg_decode}{tab5}//end{nl}"
            reg_decode = f"{reg_decode}{tab5}default: begin{nl}"
            for register in self.registers:
                reg_decode = f"{reg_decode}{tab6}{register.wen_w} = 1'b0;{nl}"
            reg_decode = f"{reg_decode}{tab6}//reg_rdata_int = 'x;{nl}"
            reg_decode = f"{reg_decode}{tab5}end{nl}"
            reg_decode = f"{reg_decode}{tab4}endcase{nl}"
            reg_decode = f"{reg_decode}{tab3}end{nl}"
            self.decoder_code = f"{self.decoder_code}{reg_decode}"
        
        # reg_decode_footer = f"{reg_decode_footer}{tab3}end{nl}"     
        # reg_decode_footer = f"{reg_decode_footer}{tab3}default: begin{nl}"
        for register in self.registers:
            reg_decode = f"{reg_decode_footer}{tab6}{register.wen} = 1'b0;{nl}"
        # reg_decode_footer = f"{reg_decode_footer}{tab4}reg_rdata_int = 1'x;{nl}"
        reg_decode_footer = f"{reg_decode_footer}{tab2}endcase{nl}"
        reg_decode_footer = f"{reg_decode_footer}{tab1}end:ADDR_DECODER{nl}{nl}"        
        
        # assign reg data_o to internal reg data
        self.decoder_code = f"{self.decoder_code}{reg_decode_footer}{nl}"

    def gen_decoder_body(self):
        decoder_body = f"{nl}{tab1}//Decode addresses and set wr_en/rd_en{nl}"
        decoder_body = f"{decoder_body}{tab1}always_comb begin : ADDR_DECODER{nl}"
        decoder_body = f"{decoder_body}{tab2}case(reg_address_i){nl}"
        self.decoder_code = f"{self.decoder_code}{decoder_body}"
        self.decode_reg_op()
        self.gen_rdata_ff()
        self.gen_ack_fsm()
        
        
    def gen_rdata_ff(self):
        block = f"{tab1}reg [REG_DATA_WIDTH-1:0] reg_rdata_ff;{nl}"
        block = f"{block}{tab1}assign reg_rdata_o =  reg_rdata_ff;{nl}{nl}"
        block = f"{block}{tab1}always_ff @(posedge clk or negedge resetn) begin:RDATA_FF{nl}"
        block = f"{block}{tab2}if (!resetn) begin{nl}"
        block = f"{block}{tab3}reg_rdata_ff <= 0;{nl}"
        block = f"{block}{tab2}end{nl}"
        block = f"{block}{tab2}else begin{nl}"
        block = f"{block}{tab3}reg_rdata_ff <= reg_rdata_int;{nl}"
        block = f"{block}{tab2}end{nl}"
        block = f"{block}{tab1}end:RDATA_FF{nl}"
        self.decoder_code = f"{self.decoder_code}{block}{nl}"
    def gen_decoder(self): 
         self.gen_decoder_header()
         self.gen_decoder_body() 
         self.gen_decoder_footer()
         
        
    
    ''' Generate reg block ack / decode error'''
    def gen_next_state(self):
        next_state_fsm = f"{tab1}logic [1:0] state, next_state;{nl}{nl}"
        next_state_fsm = f"{next_state_fsm}{tab1}// NEXT STATE FSM{nl}"
        next_state_fsm = f"{next_state_fsm}{tab1}always @( posedge clk or negedge resetn) begin: ACK_FSM {nl}"
        next_state_fsm = f"{next_state_fsm}{tab2}if(!resetn) begin{nl}"
        next_state_fsm = f"{next_state_fsm}{tab3}state <= IDLE;{nl}"
        next_state_fsm = f"{next_state_fsm}{tab2}end{nl}"
        next_state_fsm = f"{next_state_fsm}{tab2}else begin{nl}"
        next_state_fsm = f"{next_state_fsm}{tab3}state <= next_state;{nl}"
        next_state_fsm = f"{next_state_fsm}{tab2}end{nl}"
        next_state_fsm = f"{next_state_fsm}{tab1}end:ACK_FSM{nl}"
        self.decoder_code = f"{self.decoder_code}{next_state_fsm}{nl}"
        
    def gen_state_calc_always_block(self):
        #IDLE STATE
        block = f"{tab1}// State calculation{nl}"
        block = f"{block}{tab1}always_comb begin : ACK_FSM_STATE_CALC{nl}"
        block = f"{block}{tab2}case(state){nl}"
        block = f"{block}{tab3}IDLE : begin{nl}"
        block = f"{block}{tab4}if (reg_wen_i | reg_ren_i) begin{nl}"
        block = f"{block}{tab5}if(reg_wen_i == reg_ren_i) begin{nl}"
        block = f"{block}{tab6}next_state = ERR;{nl}"
        block = f"{block}{tab5}end{nl}"
        block = f"{block}{tab5}else begin{nl}"
 
        block = f"{block}{tab6}if({nl}"
        for reg in self.registers:
            or_bar = '|'
            if reg == self.registers[-1]:
                or_bar = ') begin'
            block = f"{block}{tab7}reg_address_i == {reg.addr_var} {or_bar} {nl}"
        block = f"{block}{tab8}next_state = RESP;{nl}"
        block = f"{block}{tab7}end{nl}"
        block = f"{block}{tab6}else begin{nl}"
        block = f"{block}{tab7}next_state = ERR;{nl}"
        block = f"{block}{tab6}end{nl}"
        block = f"{block}{tab5}end{nl}"
        block = f"{block}{tab4}end{nl}"
        block = f"{block}{tab4}else begin{nl}"
        block = f"{block}{tab5}next_state = IDLE;{nl}"
        block = f"{block}{tab4}end{nl}"
        block = f"{block}{tab3}end//IDLE{nl}"
        # RESP STATE 
        block = f"{block}{tab3}RESP : begin{nl}"
        block = f"{block}{tab4}if (reg_wen_i | reg_ren_i) begin{nl}"
        block = f"{block}{tab5}if(reg_wen_i == reg_ren_i) begin{nl}"
        block = f"{block}{tab6}next_state = ERR;{nl}"
        block = f"{block}{tab5}end{nl}"
        block = f"{block}{tab5}else begin{nl}"
        block = f"{block}{tab6}if({nl}"
        for reg in self.registers:
            or_bar = '|'
            if reg == self.registers[-1]:
                or_bar = ') begin'
            block = f"{block}{tab7}reg_address_i == {reg.addr_var} {or_bar} {nl}"
        block = f"{block}{tab8}next_state = RESP;{nl}"
        block = f"{block}{tab7}end{nl}"
        block = f"{block}{tab6}else begin{nl}"
        block = f"{block}{tab7}next_state = ERR;{nl}"
        block = f"{block}{tab6}end{nl}"
        block = f"{block}{tab5}end{nl}"
        block = f"{block}{tab4}end{nl}"
        block = f"{block}{tab4}else begin{nl}"
        block = f"{block}{tab5}next_state = IDLE;{nl}"
        block = f"{block}{tab4}end{nl}"
        block = f"{block}{tab3}end//RESP{nl}"
        #ERR_STATE
        block = f"{block}{tab3}ERR : begin{nl}"
        block = f"{block}{tab4}if (reg_wen_i | reg_ren_i) begin{nl}"
        block = f"{block}{tab5}if(reg_wen_i == reg_ren_i) begin{nl}"
        block = f"{block}{tab6}next_state = ERR;{nl}"
        block = f"{block}{tab5}end{nl}"
        block = f"{block}{tab5}else begin{nl}"
        block = f"{block}{tab6}if({nl}"
        for reg in self.registers:
            or_bar = '|'
            if reg == self.registers[-1]:
                or_bar = ') begin'
            block = f"{block}{tab7}reg_address_i == {reg.addr_var} {or_bar} {nl}"
        block = f"{block}{tab8}next_state = RESP;{nl}"
        block = f"{block}{tab7}end{nl}"
        block = f"{block}{tab6}else begin{nl}"
        block = f"{block}{tab7}next_state = ERR;{nl}"
        block = f"{block}{tab6}end{nl}"
        block = f"{block}{tab5}end{nl}"
        block = f"{block}{tab4}end{nl}"
        block = f"{block}{tab4}else begin{nl}"
        block = f"{block}{tab5}next_state = IDLE;{nl}"
        block = f"{block}{tab4}end{nl}"
        block = f"{block}{tab3}end//ERR{nl}"
        block = f"{block}{tab3}default: next_state = IDLE;{nl}"
        block = f"{block}{tab2}endcase{nl}"
        block = f"{block}{tab1}end: ACK_FSM_STATE_CALC{nl}"
        self.decoder_code = f"{self.decoder_code}{block}{nl}"
        
    def gen_ack_and_error_calc(self):
        block = f"{tab1}//Internal regs for calculation of ack/err{nl}"
        block = f"{block}{tab1}reg error_w;{nl}"
        block = f"{block}{tab1}reg ack_w;{nl}{nl}"
        block = f"{block}{tab1}assign error_o  = error_w;{nl}"
        block = f"{block}{tab1}assign ack_o  = ack_w;{nl}{nl}"
        block = f"{block}{tab1}always_comb begin : ACK_ERROR_CALC{nl}"
        block = f"{block}{tab2}case(state){nl}"
        block = f"{block}{tab3}IDLE: begin{nl}"
        block = f"{block}{tab4}ack_w   = 0;{nl}"
        block = f"{block}{tab4}error_w = 0;{nl}"
        block = f"{block}{tab3}end{nl}"
        block = f"{block}{tab3}RESP: begin{nl}"
        block = f"{block}{tab4}ack_w   = 1;{nl}"
        block = f"{block}{tab4}error_w = 0;{nl}"
        block = f"{block}{tab3}end{nl}"
        block = f"{block}{tab3}ERR: begin{nl}"
        block = f"{block}{tab4}ack_w   = 1;{nl}"
        block = f"{block}{tab4}error_w = 1;{nl}"
        block = f"{block}{tab3}end{nl}"
        block = f"{block}{tab2}endcase{nl}"
        block = f"{block}{tab1}end: ACK_ERROR_CALC{nl}"
        self.decoder_code = f"{self.decoder_code}{block}{nl}"
        
    def gen_ack_fsm(self):
        self.gen_next_state();
        self.gen_state_calc_always_block();
        self.gen_ack_and_error_calc();
        
    ''' Here starts code for reg block '''
    def gen_reg_block(self):
        self.gen_reg_block_inputs()
        self.gen_wires()
        self.gen_reg_container_and_decoder_inst()
        
    def gen_reg_block_inputs(self):
        reg_block_header = f"module {self.reg_block_name}#(parameter REG_DATA_WIDTH={self.reg_data_width},parameter REG_ADDR_WIDTH={self.reg_addr_width}) ({nl}{nl}"
        reg_block_header = f"{reg_block_header}{tab1}input clk,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}input resetn,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}input [REG_ADDR_WIDTH-1:0] regb_addr_i,{nl}"
        # reg_block_header = f"{reg_block_header}{tab1}input [REG_ADDR_WIDTH-1:0] regb_str,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}input [REG_DATA_WIDTH-1:0] regb_wbdata_i,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}input regb_ren_i,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}input regb_wen_i,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}output[REG_DATA_WIDTH-1:0] regb_rdata_o,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}output regb_ack_o,{nl}"
        reg_block_header = f"{reg_block_header}{tab1}output error_o{nl}"
        reg_block_header = f"{reg_block_header});{nl}"
        
        self.reg_block_code  =f"{self.reg_block_code}{reg_block_header}{nl}"
        
    def gen_wires(self):
        wires = f"{tab1}wire [REG_DATA_WIDTH-1:0] wdata_w;{nl}"
        for reg in self.registers:
            # reg.wr_o    = f"wire {reg.name}_wen"
            wires = f"{wires}{tab1}wire [REG_DATA_WIDTH-1:0] {reg.name}_rdata_w;{nl}"
     
        wires = f"{wires}{nl}"
        for reg in self.registers:
            # reg.wr_o    = f"wire {reg.name}_wen"
            wires = f"{wires}{tab1}wire {reg.name}_wen_w;{nl}"
        
        self.reg_block_code  =f"{self.reg_block_code}{wires}{nl}"
            
    def gen_reg_container_and_decoder_inst(self):
        ''' decoder and container '''
        
        decoder = f"{nl}{tab1}{self.reg_decoder} #(.REG_DATA_WIDTH(REG_DATA_WIDTH),.REG_ADDR_WIDTH(REG_ADDR_WIDTH)) reg_decoder({nl}"
        decoder = f"{decoder}{tab2}.clk(clk),{nl}"
        decoder = f"{decoder}{tab2}.resetn(resetn),{nl}"
        for reg in self.registers:
            decoder = f"{decoder}{tab2}.{reg.name}_rdata_i({reg.name}_rdata_w),{nl}"
        for reg in self.registers:
            decoder = f"{decoder}{tab2}.{reg.name}_wen_o({reg.name}_wen_w),{nl}"
        decoder = f"{decoder}{tab2}.reg_wdata_i(regb_wbdata_i),{nl}"
        decoder = f"{decoder}{tab2}.reg_address_i(regb_addr_i),{nl}"
        decoder = f"{decoder}{tab2}.reg_wen_i(regb_wen_i),{nl}"
        decoder = f"{decoder}{tab2}.reg_ren_i(regb_ren_i),{nl}"
        decoder = f"{decoder}{tab2}.reg_rdata_o(regb_rdata_o),{nl}"
        decoder = f"{decoder}{tab2}.reg_wdata_o(wdata_w),{nl}"
        decoder = f"{decoder}{tab2}.ack_o(regb_ack_o),{nl}"
        decoder = f"{decoder}{tab2}.error_o(error_o));{nl}"
        
        self.reg_block_code  =f"{self.reg_block_code}{decoder}"
        
        container = f"{nl}{tab1}{self.reg_container} #(.REG_DATA_WIDTH(REG_DATA_WIDTH)) reg_container({nl}"
        container = f"{container}{tab2}.clk(clk),{nl}"
        container = f"{container}{tab2}.resetn(resetn),{nl}"
        for reg in self.registers:
            container = f"{container}{tab2}.{reg.name}_wen_i({reg.name}_wen_w),{nl}"
        for reg in self.registers:
            container = f"{container}{tab2}.{reg.name}_rdata_o({reg.name}_rdata_w),{nl}"
        container = f"{container}{tab2}.reg_wdata_i(wdata_w));{nl}"
        
        container = f"{container}{nl}endmodule:{self.reg_block_name}{nl}"
        self.reg_block_code  =f"{self.reg_block_code}{container}{nl}" 
          
          
        
    ''' Generate reg container, decoder and reg block'''
    def generate_code(self):
         self.gen_reg_container()
         self.gen_decoder()
         self.gen_reg_block();
         
         self.code =f"{self.reg_container_code}{self.decoder_code}{self.reg_block_code}"
         f = open(f"{self.reg_block_name}.sv","w")
         f.write(self.code)
         f.close()
         
         # print (self.code)
         
         print (self.reg_container_code)
         print (self.decoder_code)
         print (self.reg_block_code)
         
