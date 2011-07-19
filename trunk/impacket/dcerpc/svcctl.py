# Copyright (c) 2003-2011 CORE Security Technologies
#
# This software is provided under under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# $Id$
#
# Author: Alberto Solino
#
# Description:
#   SVCCTL (Services Control) interface implementation.
#

import array
from struct import *

from impacket import ImpactPacket
from structure import Structure
import dcerpc

MSRPC_UUID_SVCCTL = '\x81\xbb\x7a\x36\x44\x98\xf1\x35\xad\x32\x98\xf0\x38\x00\x10\x03\x02\x00\x00\x00'

# Error Codes 
ERROR_PATH_NOT_FOUND            = 3
ERROR_ACCESS_DENIES             = 5
ERROR_INVALID_HANDLE            = 6
ERROR_INVALID_DATA              = 13
ERROR_INVALID_PARAMETER         = 87
ERROR_INVALID_NAME              = 123
ERROR_SERVICE_ALREADY_RUNNING   = 1056
ERROR_INVALID_SERVICE_ACCOUNT   = 1057
ERROR_SERVICE_DISABLED          = 1058
ERROR_DATABASE_DOES_NOT_EXIST   = 1065
ERROR_SERVICE_LOGON_FAILURE     = 1069
ERROR_SERVICE_MARKED_FOR_DELETE = 1072
ERROR_SERVICE_EXISTS            = 1073
ERROR_DUPLICATE_SERVICE_NAME    = 1078
ERROR_SHUTDOWN_IN_PROGRESS      = 1115

# Access codes
SERVICE_ALL_ACCESS            = 0X000F01FF
SERVICE_CHANGE_CONFIG         = 0X00000002
SERVICE_ENUMERATE_DEPENDENTS  = 0X00000008
SERVICE_INTERROGATE           = 0X00000080
SERVICE_PAUSE_CONTINUE        = 0X00000040
SERVICE_QUERY_CONFIG          = 0X00000001
SERVICE_QUERY_STATUS          = 0X00000004
SERVICE_START                 = 0X00000010
SERVICE_STOP                  = 0X00000020
SERVICE_USER_DEFINED_CTRL     = 0X00000100
SERVICE_SET_STATUS            = 0X00008000

# Service Types
SERVICE_KERNEL_DRIVER         = 0x00000001
SERVICE_FILE_SYSTEM_DRIVER    = 0x00000002
SERVICE_WIN32_OWN_PROCESS     = 0x00000010
SERVICE_WIN32_SHARE_PROCESS   = 0x00000020
SERVICE_INTERACTIVE_PROCESS   = 0x00000100

# Start Types
SERVICE_BOOT_START            = 0x00000000
SERVICE_SYSTEM_START          = 0x00000001
SERVICE_AUTO_START            = 0x00000002
SERVICE_DEMAND_START          = 0x00000003
SERVICE_DISABLED              = 0x00000004

# Error Control 
SERVICE_ERROR_IGNORE          = 0x00000000
SERVICE_ERROR_NORMAL          = 0x00000001
SERVICE_ERROR_SEVERE          = 0x00000002
SERVICE_ERROR_CRITICAL        = 0x00000003

# Service Control Codes
SERVICE_CONTROL_CONTINUE      = 0x00000003
SERVICE_CONTROL_INTERROGATE   = 0x00000004
SERVICE_CONTROL_PARAMCHANGE   = 0x00000006
SERVICE_CONTROL_PAUSE         = 0x00000002
SERVICE_CONTROL_STOP          = 0x00000001

class SVCCTLRDeleteService(Structure):
    opnum = 2
    alignment = 4
    structure = (
        ('ContextHandle','20s'),
    )
 
class SVCCTLRControlService(Structure):
    opnum = 1
    alignment = 4
    structure = (
        ('ContextHandle','20s'),
        ('Control','<L'),
    )

class SVCCTLRControlServiceResponse(Structure):
    alignment = 4
    structure = (
        ('ServiceStatus','20s'),
    )

class SVCCTLRStartServiceW(Structure):
    opnum = 31
    alignment = 4
    structure = (
        ('ContextHandle','20s'),
        ('argc','<L=0'),
        ('argv','<L=0'),
    )

class SVCCTLROpenServiceW(Structure):
    opnum = 16
    alignment = 4
    structure = (
        ('SCManager','20s'),
        ('ServiceName','w'),
        ('DesiredAccess','<L'),
    )

class SVCCTLROpenServiceWResponse(Structure):
    alignment = 4
    structure = (
        ('ContextHandle','20s'),
        ('ErrorCode','<L'),
    )

class SVCCTLROpenSCManagerW(Structure):
    opnum = 15
    alignment = 4
    structure = (
        ('pMachineName','<L-MachineName'),
        ('MachineName','w'),
        ('DatabaseName','"\x00'),
        ('DesiredAccess','<L'),
    )

class SVCCTLROpenSCManagerAResponse(Structure):
    alignment = 4
    structure = (
        ('ContextHandle','20s'),
        ('ErrorCode','<L'),
    )

class SVCCTLRCloseServiceHandle(Structure):
    opnum = 0
    alignment = 4
    structure = (
       ('ContextHandle','20s'),
    )
   
class SVCCTLRCloseServiceHandlerResponse(Structure):
    alignment = 4
    structure = (
        ('ContextHandle','20s'),
        ('ErrorCode','<L'),
    )

class SVCCTLRCreateServiceW(Structure):
    opnum = 12
    alignment = 4
    structure = (
        ('SCManager','20s'),
        ('ServiceName','w'),
        ('pRefId1','<L-&DisplayName'), # Unique
        ('DisplayName','w'),
        ('DesiredAccess','<L'),
        ('ServiceType','<L'),
        ('StartType','<L'),
        ('ErrorControl','<L'),
        ('BinaryPathName','w'),
        ('LoadOrderGroup','<L=0'),
        ('TagID','<L=0'),
        ('Dependencies','<L=0'),
        ('DependenciesSize','<L=0'),
        #('pServiceStartName','<L-&ServiceStartName'),
        #('ServiceStartName','w'),
        ('ServiceStartName','<L=0'),
        ('Password','<L=0'),
        ('PwSize','<L=0'),
    )
    
 
# OLD Style structs.. leaving this stuff for compatibility purpose. Don't use these structs/functions anymore

class SVCCTLOpenSCManagerHeader(ImpactPacket.Header):
    OP_NUM = 0x1B

    __SIZE = 32

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLOpenSCManagerHeader.__SIZE)

        self.set_referent_id(0xFFFFFF)
        self.set_access_mask(0xF003F)

        if aBuffer: self.load_header(aBuffer)

    def get_referent_id(self):
        return self.get_long(0, '<')
    def set_referent_id(self, id):
        self.set_long(0, id, '<')

    def get_max_count(self):
        return self.get_long(4, '<')
    def set_max_count(self, num):
        self.set_long(4, num, '<')

    def get_offset(self):
        return self.get_long(8, '<')
    def set_offset(self, num):
        self.set_long(8, num, '<')

    def get_cur_count(self):
        return self.get_long(12, '<')
    def set_cur_count(self, num):
        self.set_long(12, num, '<')

    def get_machine_name(self):
        return self.get_bytes().tostring()[:20]
    def set_machine_name(self, name):
        assert len(name) <= 8
        self.set_max_count(len(name) + 1)
        self.set_cur_count(len(name) + 1)
        self.get_bytes()[16:24] = array.array('B', name + (8 - len(name)) * '\x00')

    def get_access_mask(self):
        return self.get_long(28, '<')
    def set_access_mask(self, mask):
        self.set_long(28, mask, '<')


    def get_header_size(self):
        return SVCCTLOpenSCManagerHeader.__SIZE


class SVCCTLRespOpenSCManagerHeader(ImpactPacket.Header):
    __SIZE = 24

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespOpenSCManagerHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)

    def get_return_code(self):
        return self.get_long(20, '<')
    def set_return_code(self, code):
        self.set_long(20, code, '<')


    def get_header_size(self):
        return SVCCTLRespOpenSCManagerHeader.__SIZE


class SVCCTLOpenServiceHeader(ImpactPacket.Header):
    OP_NUM = 0x1C

    __SIZE = 48


    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLOpenServiceHeader.__SIZE)

        self.set_max_count(9)
        self.set_cur_count(9)
        # Write some unknown fluff.
        self.get_bytes()[40:] = array.array('B', '\x00\x10\x48\x60\xff\x01\x0f\x00')

        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)

    def get_max_count(self):
        return self.get_long(20, '<')
    def set_max_count(self, num):
        self.set_long(20, num, '<')

    def get_offset(self):
        return self.get_long(24, '<')
    def set_offset(self, num):
        self.set_long(24, num, '<')

    def get_cur_count(self):
        return self.get_long(28, '<')
    def set_cur_count(self, num):
        self.set_long(28, num, '<')

    def get_service_name(self):
        return self.get_bytes().tostring()[32:40]
    def set_service_name(self, name):
        assert len(name) <= 8
        self.get_bytes()[32:40] = array.array('B', name + (8 - len(name)) * '\x00')


    def get_header_size(self):
        return SVCCTLOpenServiceHeader.__SIZE


class SVCCTLRespOpenServiceHeader(ImpactPacket.Header):
    __SIZE = 24

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespOpenServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)

    def get_return_code(self):
        return self.get_long(20, '<')
    def set_return_code(self, code):
        self.set_long(20, code, '<')


    def get_header_size(self):
        return SVCCTLRespOpenServiceHeader.__SIZE


class SVCCTLCloseServiceHeader(ImpactPacket.Header):
    OP_NUM = 0x0

    __SIZE = 20

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLCloseServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:] = array.array('B', handle)


    def get_header_size(self):
        return SVCCTLCloseServiceHeader.__SIZE


class SVCCTLRespCloseServiceHeader(ImpactPacket.Header):
    __SIZE = 24

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespCloseServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)

    def get_return_code(self):
        return self.get_long(20, '<')
    def set_return_code(self, code):
        self.set_long(20, code, '<')


    def get_header_size(self):
        return SVCCTLRespCloseServiceHeader.__SIZE


class SVCCTLCreateServiceHeader(ImpactPacket.Header):
    OP_NUM = 0x18

    __SIZE = 132

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLCreateServiceHeader.__SIZE)

        self.set_name_max_count(9)
        self.set_name_cur_count(9)
        self.set_service_flags(0x110)
        self.set_start_mode(2)
        self.get_bytes()[40:48] = array.array('B', '\x00\x10\x48\x60\xe4\xa3\x40\x00')
        self.get_bytes()[68:76] = array.array('B', '\x00\x00\x00\x00\xff\x01\x0f\x00')
        self.get_bytes()[84:88] = array.array('B', '\x01\x00\x00\x00')

        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)

    def get_name_max_count(self):
        return self.get_long(4, '<')
    def set_name_max_count(self, num):
        self.set_long(20, num, '<')
        self.set_long(48, num, '<')

    def get_name_offset(self):
        return self.get_long(8, '<')
    def set_name_offset(self, num):
        self.set_long(24, num, '<')
        self.set_long(52, num, '<')

    def get_name_cur_count(self):
        return self.get_long(12, '<')
    def set_name_cur_count(self, num):
        self.set_long(28, num, '<')
        self.set_long(56, num, '<')

    def get_service_name(self):
        return self.get_bytes().tostring()[32:40]
    def set_service_name(self, name):
        self.get_bytes()[32:40] = array.array('B', name + (8 - len(name)) * '\x00')
        self.get_bytes()[60:68] = array.array('B', name + (8 - len(name)) * '\x00')

    # 0x0000100 = Allow service to interact with desktop (needed by vnc server for example)
    # 0x0000010 = Log as: Local System Account
    def get_service_flags(self):
        return self.get_long(76, '<')
    def set_service_flags(self, flags):
        self.set_long(76, flags, '<')

    # 2 Automatic
    # 3 Manual
    # 4 Disabled
    def get_start_mode(self):
        return self.get_long(80, '<')
    def set_start_mode(self, mode):
        self.set_long(80, mode, '<')

    def get_path_max_count(self):
        return self.get_long(88, '<')
    def set_path_max_count(self, num):
        self.set_long(88, num, '<')

    def get_path_offset(self):
        return self.get_long(92, '<')
    def set_path_offset(self, num):
        self.set_long(92, num, '<')

    def get_path_cur_count(self):
        return self.get_long(96, '<')
    def set_path_cur_count(self, num):
        self.set_long(96, num, '<')

    def get_service_path(self):
        return self.get_bytes().tostring()[100:-32]
    def set_service_path(self, path):
        self.get_bytes()[100:-32] = array.array('B', path)
        self.set_path_max_count(len(path)+1)
        self.set_path_cur_count(len(path)+1)


    def get_header_size(self):
        var_size = len(self.get_bytes()) - SVCCTLCreateServiceHeader.__SIZE
        assert var_size > 0
        return SVCCTLCreateServiceHeader.__SIZE + var_size


class SVCCTLRespCreateServiceHeader(ImpactPacket.Header):
    __SIZE = 28

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespCreateServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[4:24]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[4:24] = array.array('B', handle)

    def get_return_code(self):
        return self.get_long(24, '<')
    def set_return_code(self, code):
        self.set_long(24, code, '<')


    def get_header_size(self):
        return SVCCTLRespCreateServiceHeader.__SIZE


class SVCCTLDeleteServiceHeader(ImpactPacket.Header):
    OP_NUM = 0x2

    __SIZE = 20

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLDeleteServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)


    def get_header_size(self):
        return SVCCTLDeleteServiceHeader.__SIZE


class SVCCTLRespDeleteServiceHeader(dcerpc.MSRPCHeader):
    __SIZE = 4

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespDeleteServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_return_code(self):
        return self.get_long(0, '<')
    def set_return_code(self, code):
        self.set_long(0, code, '<')


    def get_header_size(self):
        return SVCCTLRespDeleteServiceHeader.__SIZE


class SVCCTLStopServiceHeader(ImpactPacket.Header):
    OP_NUM = 0x1

    __SIZE = 24

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLStopServiceHeader.__SIZE)

        # Write some unknown fluff.
        self.get_bytes()[20:] = array.array('B', '\x01\x00\x00\x00')

        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)


    def get_header_size(self):
        return SVCCTLStopServiceHeader.__SIZE


class SVCCTLRespStopServiceHeader(ImpactPacket.Header):
    __SIZE = 32

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespStopServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_return_code(self):
        return self.get_long(28, '<')
    def set_return_code(self, code):
        self.set_long(28, code, '<')


    def get_header_size(self):
        return SVCCTLRespStopServiceHeader.__SIZE


class SVCCTLStartServiceHeader(ImpactPacket.Header):
    OP_NUM = 0x1F

    __SIZE = 32

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLStartServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_context_handle(self):
        return self.get_bytes().tolist()[:20]
    def set_context_handle(self, handle):
        assert 20 == len(handle)
        self.get_bytes()[:20] = array.array('B', handle)

    def get_arguments(self):
        raise Exception, "method not implemented"
    def set_arguments(self, arguments):
        args_data = apply(pack, ['<' + 'L'*len(arguments)] + map(id, arguments) )
        args_data += reduce(lambda a, b: a+b,
                            map(lambda element: pack('<LLL', len(element)+1, 0, len(element)+1) + element + '\x00' + '\x00' * ((4 - (len(element) + 1) % 4) % 4), arguments),
                            '')
        data = pack('<LLL', len(arguments), id(arguments), len(arguments)) + args_data
        self.get_bytes()[20:] = array.array('B', data)


    def get_header_size(self):
        var_size = len(self.get_bytes()) - SVCCTLStartServiceHeader.__SIZE
        assert var_size > 0
        return SVCCTLStartServiceHeader.__SIZE + var_size


class SVCCTLRespStartServiceHeader(ImpactPacket.Header):
    __SIZE = 4

    def __init__(self, aBuffer = None):
        ImpactPacket.Header.__init__(self, SVCCTLRespStartServiceHeader.__SIZE)
        if aBuffer: self.load_header(aBuffer)

    def get_return_code(self):
        return self.get_long(0, '<')
    def set_return_code(self, code):
        self.set_long(0, code, '<')


    def get_header_size(self):
        return SVCCTLRespStartServiceHeader.__SIZE


class DCERPCSvcCtl:
    def __init__(self, dcerpc):
        self._dcerpc = dcerpc

    def open_manager(self):
        hostname = 'IMPACT'
        opensc = SVCCTLOpenSCManagerHeader()
        opensc.set_machine_name(hostname)
        self._dcerpc.send(opensc)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespOpenSCManagerHeader(data)
        return retVal

    def create_service(self, context_handle, service_name, service_path):
        creates = SVCCTLCreateServiceHeader()
        creates.set_context_handle(context_handle)
        creates.set_service_name(service_name)
        creates.set_service_path(service_path)
        self._dcerpc.send(creates)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespCreateServiceHeader(data)
        return retVal

    def close_handle(self, context_handle):
        closeh = SVCCTLCloseServiceHeader()
        closeh.set_context_handle(context_handle)
        self._dcerpc.send(closeh)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespCloseServiceHeader(data)
        return retVal

    def delete_service(self, context_handle):
        deletes = SVCCTLDeleteServiceHeader()
        deletes.set_context_handle(context_handle)
        self._dcerpc.send(deletes)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespDeleteServiceHeader(data)
        return retVal

    def open_service(self, context_handle, service_name):
        opens = SVCCTLOpenServiceHeader()
        opens.set_context_handle(context_handle)
        opens.set_service_name(service_name)
        self._dcerpc.send(opens)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespOpenServiceHeader(data)
        return retVal

    def stop_service(self, context_handle):
        stops = SVCCTLStopServiceHeader()
        stops.set_context_handle(context_handle)
        self._dcerpc.send(stops)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespStopServiceHeader(data)
        return retVal

    def start_service(self, context_handle, arguments):
        starts = SVCCTLStartServiceHeader()
        starts.set_arguments( arguments )
        starts.set_context_handle(context_handle)
        self._dcerpc.send(starts)
        data = self._dcerpc.recv()
        retVal = SVCCTLRespStartServiceHeader(data)
        return retVal

# Use these functions to manipulate services. The previous ones are left for backward compatibility reasons.

    def doRequest(self, request, noAnswer = 0, checkReturn = 1):
        self._dcerpc.call(request.opnum, request)
        if noAnswer:
            return
        else:
            answer = self._dcerpc.recv()
            if checkReturn and answer[-4:] != '\x00\x00\x00\x00':
                raise Exception, 'DCE-RPC call returned an error.'
            return answer

    def DeleteService(self, handle):
        deleteService = SVCCTLRDeleteService()
        deleteService['ContextHandle'] = handle
        ans = self.doRequest(deleteService, checkReturn = 1)
        return ans

    def StopService(self, handle):
        controlService = SVCCTLRControlService()
        controlService['ContextHandle'] = handle
        controlService['Control']  = SERVICE_CONTROL_STOP
        ans = self.doRequest(controlService, checkReturn = 1)
        return ans
 
    def OpenServiceW(self, handle, name):
        openService = SVCCTLROpenServiceW()
        openService['SCManager'] = handle
        openService['ServiceName'] = (name+'\x00').encode('utf-16le')
        openService['DesiredAccess'] = SERVICE_ALL_ACCESS

        ans = self.doRequest(openService, checkReturn = 1)
        return SVCCTLROpenServiceWResponse(ans)

    def StartServiceW(self, handle):
        # TODO: Handle Arguments
        startService = SVCCTLRStartServiceW()
        startService['ContextHandle']   = handle
        
        ans = self.doRequest(startService, checkReturn = 1)
      
        return ans

    def CreateServiceW(self, handle, serviceName, displayName, binaryPathName):
        createService = SVCCTLRCreateServiceW()
        createService['SCManager']      = handle
        createService['ServiceName']    = (serviceName+'\x00').encode('utf-16le')
        createService['DisplayName']    = (displayName+'\x00').encode('utf-16le')
        createService['DesiredAccess']  = SERVICE_ALL_ACCESS
        createService['ServiceType']    = SERVICE_WIN32_OWN_PROCESS
        createService['StartType']      = SERVICE_AUTO_START
        createService['ErrorControl']   = SERVICE_ERROR_IGNORE
        createService['BinaryPathName'] = (binaryPathName+'\x00').encode('utf-16le')
        createService['TagID'] = 0
        ans = self.doRequest(createService, checkReturn = 1)
        return ans

    def OpenSCManagerW(self): 
        openSCManager = SVCCTLROpenSCManagerW()
        openSCManager['MachineName'] = 'DUMMY\x00'.encode('utf-16le')
        openSCManager['DesiredAccess'] = SERVICE_START | SERVICE_STOP | SERVICE_CHANGE_CONFIG | SERVICE_QUERY_CONFIG | SERVICE_QUERY_STATUS | SERVICE_ENUMERATE_DEPENDENTS

        ans = self.doRequest(openSCManager, checkReturn = 1)
        return SVCCTLROpenSCManagerAResponse(ans)

    def CloseServiceHandle(self, handle):
        closeHandle = SVCCTLRCloseServiceHandle()
        closeHandle['ContextHandle'] = handle
        ans = self.doRequest(closeHandle, checkReturn = 1)
        return SVCCTLRCloseServiceHandlerResponse(ans)
        
