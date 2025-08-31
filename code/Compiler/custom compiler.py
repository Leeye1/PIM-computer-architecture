# ARM 和 PIM 的操作码表
opcode_table = {
    "ARM": {
        "ADD": "0001",
        "SUB": "0010",
        "MUL": "0011",
        "DIV": "0100",
        "LOAD": "0101",
        "STORE": "0110",
    },
    "PIM": {
        "PMEM_ADD": "0001",
        "PMEM_SUB": "0010",
        "PMEM_MUL": "0011",
        "PMEM_DIV": "0100",
        "PMEM_LOAD": "0101",
        "PMEM_STORE": "0110",
    }
}

# 编译函数：分段生成字段并组合为完整的32位二进制指令
def assemble_instruction(arch, instruction):
    parts = instruction.split()
    op = parts[0]  # 操作指令
    args = parts[1].split(",")  # 参数列表
    
    fields = {}  # 用于存储每个字段的二进制
    
    if arch == "ARM":
        # 指令通用字段
        fields["Opx"] = opcode_table["ARM"].get(op, "0000")  # 操作码
        fields["Op"] = "00010010"  # 示例操作码部分
        fields["Rs1"] = f"{int(args[1][1:]):04b}"  # 源寄存器1
        fields["Rd"] = f"{int(args[0][1:]):04b}"  # 目标寄存器
        
        if op in ["ADD", "SUB", "MUL", "DIV"]:  # Register-Register
            fields["imm5"] = f"{int(args[3]):05b}"  # imm5
            fields["Op2"] = "000"  # 填充
            fields["Rs2"] = f"{int(args[2][1:]):04b}"  # 源寄存器2
        elif op in ["LOAD", "STORE"]:  # Data Transfer
            const_value = f"{int(args[2]):012b}"  # 偏移量
            fields["Const"] = const_value  # Const 保持 12 位完整
            fields["Padding"] = "0000"  # 填充 4 位
            
    elif arch == "PIM":
        # 指令通用字段
        fields["Opx"] = opcode_table["PIM"].get(op, "0000")  # 操作码
        fields["Op"] = "00010010"  # 示例操作码部分
        fields["Rs1"] = f"{int(args[1][1:]):04b}"  # 源寄存器1
        fields["Rd"] = f"{int(args[0][1:]):04b}"  # 目标寄存器
        
        if op in ["PMEM_ADD", "PMEM_SUB", "PMEM_MUL", "PMEM_DIV"]:  # Register-Register
            fields["M"] = "1"  # M 位
            fields["imm4"] = f"{int(args[3]):04b}"  # imm4
            fields["Op2"] = "000"  # 填充
            fields["Rs2"] = f"{int(args[2][1:]):04b}"  # 源寄存器2
        elif op in ["PMEM_LOAD", "PMEM_STORE"]:  # Data Transfer
            const_value = f"{int(args[2]):011b}"  # 偏移量
            fields["M"] = "1"  # M 位 (第 21 位固定为 1)
            fields["Const"] = const_value  # Const 保持 11 位完整
    
    # 打印每个字段
    for field, value in fields.items():
        print(f"{field}: {value} (decimal: {int(value, 2) if value.isdigit() else value})")
    
    # 按正确的顺序组合字段
    if arch == "ARM" and op in ["ADD", "SUB", "MUL", "DIV"]:
        binary = (
            fields["Opx"] +  # 31-28
            fields["Op"] +   # 27-20
            fields["Rs1"] +  # 19-16
            fields["Rd"] +   # 15-12
            fields["imm5"] + # 11-7
            fields["Op2"] +  # 6-4
            fields["Rs2"]    # 3-0
        )
    elif arch == "ARM" and op in ["LOAD", "STORE"]:
        binary = (
            fields["Opx"] +  # 31-28
            fields["Op"] +   # 27-20
            fields["Rs1"] +  # 19-16
            fields["Rd"] +   # 15-12
            fields["Const"]  # 11-0 (完整的 12 位 Const)
        )
    elif arch == "PIM" and op in ["PMEM_ADD", "PMEM_SUB", "PMEM_MUL", "PMEM_DIV"]:
        binary = (
            fields["Opx"] +  # 31-28
            fields["Op"] +   # 27-20
            fields["Rs1"] +  # 19-16
            fields["Rd"] +   # 15-12
            fields["M"] +    # 11
            fields["imm4"] + # 10-7
            fields["Op2"] +  # 6-4
            fields["Rs2"]    # 3-0
        )
    elif arch == "PIM" and op in ["PMEM_LOAD", "PMEM_STORE"]:
        binary = (
            fields["Opx"] +  # 31-28
            fields["Op"] +   # 27-20
            fields["Rs1"] +  # 19-16
            fields["Rd"] +   # 15-12
            fields["M"] +    # 11
            fields["Const"]  # 10-0 (完整的 11 位 Const)
        )
    
    return binary.ljust(32, "0")  # 确保二进制长度为32位

# 解码函数：严格按照字段定义解码指令
def decode_instruction(binary, arch):
    print("\n=== Decoding Instruction ===")
    result = {}
    
    if arch == "ARM":
        if binary[20] == "0":  # ARM Register-Register
            result["Opx"] = binary[0:4]
            result["Op"] = binary[4:12]
            result["Rs1"] = binary[12:16]
            result["Rd"] = binary[16:20]
            result["imm5"] = binary[20:25]
            result["Op2"] = binary[25:28]
            result["Rs2"] = binary[28:32]
            print("Decoded as ARM Register-Register Instruction:")
        else:  # ARM Data Transfer
            result["Opx"] = binary[0:4]
            result["Op"] = binary[4:12]
            result["Rs1"] = binary[12:16]
            result["Rd"] = binary[16:20]
            result["Const"] = binary[20:32]
            print("Decoded as ARM Data Transfer Instruction:")
    
    elif arch == "PIM":
        if binary[20] == "1":  # PIM Register-Register
            result["Opx"] = binary[0:4]
            result["Op"] = binary[4:12]
            result["Rs1"] = binary[12:16]
            result["Rd"] = binary[16:20]
            result["M"] = binary[20:21]
            result["imm4"] = binary[21:25]
            result["Op2"] = binary[25:28]
            result["Rs2"] = binary[28:32]
            print("Decoded as PIM Register-Register Instruction:")
        else:  # PIM Data Transfer
            result["Opx"] = binary[0:4]
            result["Op"] = binary[4:12]
            result["Rs1"] = binary[12:16]
            result["Rd"] = binary[16:20]
            result["M"] = binary[20:21]
            result["Const"] = binary[21:32]
            print("Decoded as PIM Data Transfer Instruction:")
    
    for field, value in result.items():
        print(f"{field}: {value} (decimal: {int(value, 2) if value.isdigit() else value})")
    
    return result

# 判断指令类型（ARM 或 PIM）
def detect_architecture(instruction):
    if instruction.startswith("PMEM_"):
        return "PIM"
    else:
        return "ARM"

# 模拟器：解码并输出指令
def process_instruction(instruction):
    # 检测架构类型
    arch = detect_architecture(instruction)
    print(f"\nInstruction Detected: {instruction}")
    print(f"Architecture Detected: {arch}")

    # 编译汇编指令为二进制
    binary = assemble_instruction(arch, instruction)
    print(f"Binary: {binary}")

    # 解码指令
    decode_instruction(binary, arch)

# 示例运行
def run_example():
    # 示例指令
    instructions = [
        "ADD R1,R2,R3,5",       # ARM ADD
        "PMEM_ADD R1,R2,R3,5",  # PIM ADD
        "LOAD R1,R2,15",        # ARM LOAD
        "PMEM_LOAD R1,R2,15"    # PIM LOAD
    ]

    # 逐条处理指令
    for instruction in instructions:
        process_instruction(instruction)

# 运行示例
run_example()
