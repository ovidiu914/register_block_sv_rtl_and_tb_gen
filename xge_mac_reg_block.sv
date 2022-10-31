module xge_mac_reg_block_reg_container#(parameter REG_DATA_WIDTH=32) (

    input clk,
    input resetn,
    input [REG_DATA_WIDTH-1:0] reg_wdata_i,


    //Configuration_register
    input  Configuration_register_wen_i,
    output [REG_DATA_WIDTH-1:0] Configuration_register_rdata_o,

    //Receive_packets_count
    input  Receive_packets_count_wen_i,
    output [REG_DATA_WIDTH-1:0] Receive_packets_count_rdata_o,

    //Transmit_packets_count
    input  Transmit_packets_count_wen_i,
    output [REG_DATA_WIDTH-1:0] Transmit_packets_count_rdata_o
    );

    reg [REG_DATA_WIDTH-1:0] Configuration_register;
    reg [REG_DATA_WIDTH-1:0] Receive_packets_count;
    reg [REG_DATA_WIDTH-1:0] Transmit_packets_count;

    always_ff @(posedge clk or negedge resetn) begin : Configuration_register_inst
        if (!resetn) begin
            Configuration_register <= 'h4;
        end
        else begin
            if (Configuration_register_wen_i) begin
                Configuration_register <= reg_wdata_i;
            end
        end
    end

    assign Configuration_register_rdata_o = Configuration_register;

    always_ff @(posedge clk or negedge resetn) begin : Receive_packets_count_inst
        if (!resetn) begin
            Receive_packets_count <= 'h0;
        end
        else begin
            if (Receive_packets_count_wen_i) begin
                Receive_packets_count <= reg_wdata_i;
            end
        end
    end

    assign Receive_packets_count_rdata_o = Receive_packets_count;

    always_ff @(posedge clk) begin : Transmit_packets_count_inst
        if(Transmit_packets_count_wen_i) begin
            Transmit_packets_count <= reg_wdata_i;
        end
    end
    assign Transmit_packets_count_rdata_o = Transmit_packets_count;

endmodule:xge_mac_reg_block_reg_container
module xge_mac_reg_block_decoder #(parameter REG_ADDR_WIDTH = 32, parameter REG_DATA_WIDTH = 32, parameter BASE_ADDRESS = 0) (

    input clk,
    input resetn,

    //input data from the ocp bridge,
    input [REG_DATA_WIDTH-1:0] reg_wdata_i,
    input [REG_ADDR_WIDTH-1:0] reg_address_i,
    input reg_wen_i,
    input reg_ren_i,

    //Write data to reg container
    output [REG_DATA_WIDTH-1:0] reg_wdata_o,

    //Read data from reg container to ocp
    output [REG_DATA_WIDTH-1:0] reg_rdata_o,

    //error to ocp - decode failure or wr and rd in the same time 
    output error_o,    output ack_o,

    //Configuration_register
    input [REG_DATA_WIDTH-1:0] Configuration_register_rdata_i,
    output  Configuration_register_wen_o,

    //Receive_packets_count
    input [REG_DATA_WIDTH-1:0] Receive_packets_count_rdata_i,
    output  Receive_packets_count_wen_o,

    //Transmit_packets_count
    input [REG_DATA_WIDTH-1:0] Transmit_packets_count_rdata_i,
    output  Transmit_packets_count_wen_o
    );

    //Registers addresses
    localparam Configuration_register_ADDR = BASE_ADDRESS + 'h0;
    localparam Receive_packets_count_ADDR = BASE_ADDRESS + 'h4;
    localparam Transmit_packets_count_ADDR = BASE_ADDRESS + 'h8;

    //ACK/ERR fsm states;
    localparam IDLE = 0;
    localparam RESP = 1;
    localparam ERR  = 2;

    //internal ack,error
    reg ack;
    reg error;

    reg Configuration_register_wen_o_w;
    reg Receive_packets_count_wen_o_w;
    reg Transmit_packets_count_wen_o_w;


    assign Configuration_register_wen_o = Configuration_register_wen_o_w;
    assign Receive_packets_count_wen_o = Receive_packets_count_wen_o_w;
    assign Transmit_packets_count_wen_o = Transmit_packets_count_wen_o_w;

    //Reg rdata interconnect;
    reg [REG_DATA_WIDTH-1:0] reg_rdata_int;
    assign reg_wdata_o = reg_wdata_i;

    //Decode addresses and set wr_en/rd_en
    always_comb begin : ADDR_DECODER
        case(reg_address_i)
            Configuration_register_ADDR: begin
                case({reg_wen_i, reg_ren_i})
                    2'b10: begin
                        Configuration_register_wen_o_w = 1'b1;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        //reg_rdata_int = 0;
                    end
                    2'b01: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        reg_rdata_int = Configuration_register_rdata_i;
                    end
                    //2'b00: begin
                    //end
                    default: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        //reg_rdata_int = 'x;
                    end
                endcase
            end
            Receive_packets_count_ADDR: begin
                case({reg_wen_i, reg_ren_i})
                    2'b10: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b1;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        //reg_rdata_int = 0;
                    end
                    2'b01: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        reg_rdata_int = Receive_packets_count_rdata_i;
                    end
                    //2'b00: begin
                    //end
                    default: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        //reg_rdata_int = 'x;
                    end
                endcase
            end
            Transmit_packets_count_ADDR: begin
                case({reg_wen_i, reg_ren_i})
                    2'b10: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b1;
                        //reg_rdata_int = 0;
                    end
                    2'b01: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        reg_rdata_int = Transmit_packets_count_rdata_i;
                    end
                    //2'b00: begin
                    //end
                    default: begin
                        Configuration_register_wen_o_w = 1'b0;
                        Receive_packets_count_wen_o_w = 1'b0;
                        Transmit_packets_count_wen_o_w = 1'b0;
                        //reg_rdata_int = 'x;
                    end
                endcase
            end
        endcase
    end:ADDR_DECODER


    reg [REG_DATA_WIDTH-1:0] reg_rdata_ff;
    assign reg_rdata_o =  reg_rdata_ff;

    always_ff @(posedge clk or negedge resetn) begin:RDATA_FF
        if (!resetn) begin
            reg_rdata_ff <= 0;
        end
        else begin
            reg_rdata_ff <= reg_rdata_int;
        end
    end:RDATA_FF

    logic [1:0] state, next_state;

    // NEXT STATE FSM
    always @( posedge clk or negedge resetn) begin: ACK_FSM 
        if(!resetn) begin
            state <= IDLE;
        end
        else begin
            state <= next_state;
        end
    end:ACK_FSM

    // State calculation
    always_comb begin : ACK_FSM_STATE_CALC
        case(state)
            IDLE : begin
                if (reg_wen_i | reg_ren_i) begin
                    if(reg_wen_i == reg_ren_i) begin
                        next_state = ERR;
                    end
                    else begin
                        if(
                            reg_address_i == Configuration_register_ADDR | 
                            reg_address_i == Receive_packets_count_ADDR | 
                            reg_address_i == Transmit_packets_count_ADDR ) begin 
                                next_state = RESP;
                            end
                        else begin
                            next_state = ERR;
                        end
                    end
                end
                else begin
                    next_state = IDLE;
                end
            end//IDLE
            RESP : begin
                if (reg_wen_i | reg_ren_i) begin
                    if(reg_wen_i == reg_ren_i) begin
                        next_state = ERR;
                    end
                    else begin
                        if(
                            reg_address_i == Configuration_register_ADDR | 
                            reg_address_i == Receive_packets_count_ADDR | 
                            reg_address_i == Transmit_packets_count_ADDR ) begin 
                                next_state = RESP;
                            end
                        else begin
                            next_state = ERR;
                        end
                    end
                end
                else begin
                    next_state = IDLE;
                end
            end//RESP
            ERR : begin
                if (reg_wen_i | reg_ren_i) begin
                    if(reg_wen_i == reg_ren_i) begin
                        next_state = ERR;
                    end
                    else begin
                        if(
                            reg_address_i == Configuration_register_ADDR | 
                            reg_address_i == Receive_packets_count_ADDR | 
                            reg_address_i == Transmit_packets_count_ADDR ) begin 
                                next_state = RESP;
                            end
                        else begin
                            next_state = ERR;
                        end
                    end
                end
                else begin
                    next_state = IDLE;
                end
            end//ERR
            default: next_state = IDLE;
        endcase
    end: ACK_FSM_STATE_CALC

    //Internal regs for calculation of ack/err
    reg error_w;
    reg ack_w;

    assign error_o  = error_w;
    assign ack_o  = ack_w;

    always_comb begin : ACK_ERROR_CALC
        case(state)
            IDLE: begin
                ack_w   = 0;
                error_w = 0;
            end
            RESP: begin
                ack_w   = 1;
                error_w = 0;
            end
            ERR: begin
                ack_w   = 1;
                error_w = 1;
            end
        endcase
    end: ACK_ERROR_CALC

endmodule:xge_mac_reg_block_decoder

module xge_mac_reg_block#(parameter REG_DATA_WIDTH=32,parameter REG_ADDR_WIDTH=32) (

    input clk,
    input resetn,
    input [REG_ADDR_WIDTH-1:0] regb_addr_i,
    input [REG_DATA_WIDTH-1:0] regb_wbdata_i,
    input regb_ren_i,
    input regb_wen_i,
    output[REG_DATA_WIDTH-1:0] regb_rdata_o,
    output regb_ack_o,
    output error_o
);

    wire [REG_DATA_WIDTH-1:0] wdata_w;
    wire [REG_DATA_WIDTH-1:0] Configuration_register_rdata_w;
    wire [REG_DATA_WIDTH-1:0] Receive_packets_count_rdata_w;
    wire [REG_DATA_WIDTH-1:0] Transmit_packets_count_rdata_w;

    wire Configuration_register_wen_w;
    wire Receive_packets_count_wen_w;
    wire Transmit_packets_count_wen_w;


    xge_mac_reg_block_decoder #(.REG_DATA_WIDTH(REG_DATA_WIDTH),.REG_ADDR_WIDTH(REG_ADDR_WIDTH)) reg_decoder(
        .clk(clk),
        .resetn(resetn),
        .Configuration_register_rdata_i(Configuration_register_rdata_w),
        .Receive_packets_count_rdata_i(Receive_packets_count_rdata_w),
        .Transmit_packets_count_rdata_i(Transmit_packets_count_rdata_w),
        .Configuration_register_wen_o(Configuration_register_wen_w),
        .Receive_packets_count_wen_o(Receive_packets_count_wen_w),
        .Transmit_packets_count_wen_o(Transmit_packets_count_wen_w),
        .reg_wdata_i(regb_wbdata_i),
        .reg_address_i(regb_addr_i),
        .reg_wen_i(regb_wen_i),
        .reg_ren_i(regb_ren_i),
        .reg_rdata_o(regb_rdata_o),
        .reg_wdata_o(wdata_w),
        .ack_o(regb_ack_o),
        .error_o(error_o));

    xge_mac_reg_block_reg_container #(.REG_DATA_WIDTH(REG_DATA_WIDTH)) reg_container(
        .clk(clk),
        .resetn(resetn),
        .Configuration_register_wen_i(Configuration_register_wen_w),
        .Receive_packets_count_wen_i(Receive_packets_count_wen_w),
        .Transmit_packets_count_wen_i(Transmit_packets_count_wen_w),
        .Configuration_register_rdata_o(Configuration_register_rdata_w),
        .Receive_packets_count_rdata_o(Receive_packets_count_rdata_w),
        .Transmit_packets_count_rdata_o(Transmit_packets_count_rdata_w),
        .reg_wdata_i(wdata_w));

endmodule:xge_mac_reg_block

