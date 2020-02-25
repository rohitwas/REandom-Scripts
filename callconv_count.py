import idautils
import idaapi
import idc
stdcall_count = 0
cdecl_count = 0
fastcall_count = 0
thiscall_count= 0

for i in idautils.Functions():
    if "__stdcall" in str(idc.GetType(i)):
        stdcall_count+=1
    if "__cdecl" in str(idc.GetType(i)):
        cdecl_count+=1
    if "__fastcall" in str(idc.GetType(i)):
        fastcall_count+=1    
    if "__thiscall" in str(idc.GetType(i)):
        thiscall_count+=1

print "Found stdcall: %s\n cdecl: %s\n fastcall: %s\n thiscall: %s\n "%(stdcall_count,cdecl_count,fastcall_count,thiscall_count)
