import idautils
import idc
import idaapi
import re


pattern = re.compile(r'(\=\(.+?_)([0-9A-Fa-f]+?)(?=\s-\s0x[0-9A-Fa-f]+?\))')

def decode_data(addr, size):
    # print '[*]begin to find .data segment'
    # data_ea_start = 0
    # local_sections = Segments()
    # for section in local_sections:
    #     seg_name = SegName(section)
    #     if seg_name == '.data':
    #         data_ea_start = section
    #         break
            
    # if data_ea_start == 0:
    #     print '\t[-]can not locate .data segment'
    #     return
    
    # data_ea_end = SegEnd(data_ea_start)
    # print 'data start from 0x%x, end to 0x%x' % (data_ea_start, data_ea_end)
    # size = (data_ea_end - data_ea_start)/4
    # print "size: %d" % size
    # buf = ""
    # for i in range(0, size):
    #     dw = idc.Dword(addr+ i*4)  #(data_ea_start + i*4)
    #     if dw > 0xc3000000 and dw < 0xc3ffffff:
    #         fori = idc.GetFloat(data_ea_start + i*4)
    #         fti = int(fori + fori)
    #         ior = ((fti ^ 0xde) + 0x22) & 0x000000ff
    #         buf += chr(ior)
    
    # print '%s' % buf
    buf = ""
    for i in range(0, size):
        dw = idc.Dword(addr+ i*4)  #(data_ea_start + i*4)
        if dw > 0xc3000000 and dw < 0xc3ffffff:
            fori = idc.GetFloat(addr + i*4)
            fti = int(fori + fori)
            ior = ((fti ^ 0xde) + 0x22) & 0x000000ff
            buf += chr(ior)
    return buf


def main():    
    #decode_data()
    fun_dec_addr = idc.LocByName("sub_A35C")
    data = []
    for addr in idautils.CodeRefsTo(fun_dec_addr, 0):
        data_addr = find_data(addr)
        if data_addr != 0 and data_addr != None :
            size = find_data_size(addr)
            data.append((data_addr, size, addr)) 
            
    for (data_addr, size, call_addr) in data:
        print('0x%x: %s' % (call_addr, decode_data(data_addr, size)))

def find_data(addr):
    _addr = addr
    print("start find sub_A35C caller args[0] from 0x%x" % addr)
    func_head = idc.GetFunctionAttr(addr, idc.FUNCATTR_START)
    if func_head == 0:
        print "ERROR: undefinded func code at 0x%x" % addr
        return 0
    def_addr = find_opnd_def_addr('R0', addr, func_head)
    opndcode = idc.GetMnem(def_addr)
    if opndcode.startswith('ADD'):
        if idc.GetOpType(def_addr, 2) == 0:
            return parse_register_value('R0', def_addr, func_head) + parse_opnd_value(def_addr, func_head, 1)
        else:
            return parse_opnd_value(def_addr, func_head, 1) + parse_opnd_value(def_addr, func_head, 2)
    elif opndcode.startswith('LDR'):
        return 0
    elif opndcode.startswith('LDR'):
        return 0

def find_data_size(addr):
    _addr = addr
    print "start find sub_A35C caller args[1] from 0x%x" % addr
    func_head = idc.GetFunctionAttr(addr, idc.FUNCATTR_START)
    if func_head == 0:
        print "ERROR: undefinded func code at 0x%x" % addr
        return 0
    while _addr > func_head:
        _addr = idc.PrevHead(_addr)
        _opcode = idc.GetMnem(_addr)
        _r0 = idc.GetOpnd(_addr, 0)
        if idc.GetOpType(_addr, 0) == 1 and _r0 == 'R1':
           if  _opcode.startswith('MOV') and idc.GetOpType(_addr, 1) == 5:
               return int(idc.GetOpnd(_addr, 1)[1:], 16)



def find_opnd_def_addr(opnd, from_addr, to_addr):
    _addr = from_addr
    while _addr > to_addr:
        _addr = idc.PrevHead(_addr)
        _opcode = idc.GetMnem(_addr)
        _r0 = idc.GetOpnd(_addr, 0)
        if idc.GetOpType(_addr, 0) == 1 and _r0 == opnd:
            if _opcode.startswith('ADD') or _opcode.startswith('MOV') or _opcode.startswith('LDR'):
                return _addr
    
    print "ERROR: Can not find R0 in this func"
    return 0


def parse_register_value(register, start_addr, end_addr):
    print "start find register: %s from 0x%x to 0x%x" %(register, start_addr, end_addr)
    _addr = start_addr
    while _addr > end_addr:
        _addr = idc.PrevHead(_addr)
        _opnd_first = idc.GetOpnd(_addr, 0)
        if _opnd_first == register:
            _op_code = idc.GetMnem(_addr)
            second_opnd_type = idc.GetOpType(_addr, 1) 
            print 'find register( 0x%x ) -> %s,  type1: %d,  type2: %d' % (_addr, idc.GetDisasm(_addr), second_opnd_type, idc.GetOpType(_addr, 2))
            if _op_code.startswith('LDR'):
                return parse_opnd_value(_addr, end_addr, 1)
            elif _op_code.startswith('ADD'): 
                if(idc.GetOpType(_addr, 2) == 0):
                    if idc.GetOpnd(_addr, 1) == 'PC':
                        #todo: check last _op  =>  LDR             R6, =(_GLOBAL_OFFSET_TABLE_ - 0xAEB6)
                        return 0x00021DB4
                    else: 
                        return parse_register_value(register, _addr, end_addr) + parse_opnd_value(_addr, end_addr, 1)
                else:
                    return parse_opnd_value(_addr, end_addr, 1) + parse_opnd_value(_addr, end_addr, 2)
            elif _op_code.startswith('MOV'):
                 return parse_register_value(idc.GetOpnd(_addr, 1), _addr, end_addr)
            # else:
            #     return 0


def parse_opnd_value(addr, end_addr, position):
    type = idc.GetOpType(addr, position)
    print 'start parse opnd -> %s' % idc.GetOpnd(addr, position)
    if type == 0:
        return 0
    elif type == 1:
        return parse_register_value(idc.GetOpnd(addr, position), addr, end_addr)
    elif type == 2:
        m = pattern.match(idc.GetOpnd(addr, position)) #'=(unk_248E0 - 0x21DB4)'
        if m != None:
            return int(m.group(2), 16) - 0x21DB4
        else:
            print "passe error -> %s at 0x%x" % (idc.GetOpnd(addr, position), addr)
    elif type == 4:
        return find_last_str_operation(idc.GetOpnd(addr, position), addr, end_addr)
    elif type == 5:
        return int(idc.GetOpnd(addr, position)[1:], 16)
    else:
        return 0

def find_last_str_operation(opnd, start_addr, end_addr):
    _addr = start_addr
    while _addr > end_addr:
        _addr = idc.PrevHead(_addr)
        _op = idc.GetMnem(_addr)
        _opnd_first = idc.GetOpnd(_addr, 0)
        if _op.startswith('STR') and idc.GetOpnd(_addr, 1) == opnd:
            print "[find_last_Str] at 0x%x" % (_addr)
            result = parse_register_value(_opnd_first, _addr, end_addr)
            print "[find_last_Str] at 0x%x and result %d" % (_addr, result)
            return result
    
    print "ERROR: can not find STR from 0x%x to 0x%x" % (start_addr, end_addr)

    
main()