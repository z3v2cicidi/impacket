# Copyright (c) 2003-2014 CORE Security Technologies
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
#   [MS-DCOM] Interface implementation
#
#   Best way to learn how to use these calls is to grab the protocol standard
#   so you understand what the call does, and then read the test case located
#   at https://code.google.com/p/impacket/source/browse/#svn%2Ftrunk%2Fimpacket%2Ftestcases%2FSMB-RPC
#
#   Some calls have helper functions, which makes it even easier to use.
#   They are located at the end of this file. 
#   Helper functions start with "h"<name of the call>.
#   There are test cases for them too. 
#
from impacket.dcerpc.v5 import ndr
from impacket.dcerpc.v5.ndr import NDRCALL, NDR, NDRSTRUCT, NDRENUM, NDRPOINTER, NDRUniConformantArray, NDRUniFixedArray, NDRTLSTRUCT
from impacket.dcerpc.v5.dtypes import LPWSTR, WCHAR, ULONGLONG, HRESULT, GUID, USHORT, WSTR, DWORD, LPLONG, LONG, PGUID, ULONG, UUID
from impacket import system_errors
from impacket.uuid import uuidtup_to_bin, string_to_bin
from impacket.dcerpc.v5.enum import Enum
from impacket.dcerpc.v5.rpcrt import TypeSerialization1

CLSID_ActivationContextInfo   = string_to_bin('000001a5-0000-0000-c000-000000000046')
CLSID_ActivationPropertiesIn  = string_to_bin('00000338-0000-0000-c000-000000000046')
CLSID_ActivationPropertiesOut = string_to_bin('00000339-0000-0000-c000-000000000046')
CLSID_CONTEXT_EXTENSION       = string_to_bin('00000334-0000-0000-c000-000000000046')
CLSID_ContextMarshaler        = string_to_bin('0000033b-0000-0000-c000-000000000046')
CLSID_ERROR_EXTENSION         = string_to_bin('0000031c-0000-0000-c000-000000000046')
CLSID_ErrorObject             = string_to_bin('0000031b-0000-0000-c000-000000000046')
CLSID_InstanceInfo            = string_to_bin('000001ad-0000-0000-c000-000000000046')
CLSID_InstantiationInfo       = string_to_bin('000001ab-0000-0000-c000-000000000046')
CLSID_PropsOutInfo            = string_to_bin('00000339-0000-0000-c000-000000000046')
CLSID_ScmReplyInfo            = string_to_bin('000001b6-0000-0000-c000-000000000046')
CLSID_ScmRequestInfo          = string_to_bin('000001aa-0000-0000-c000-000000000046')
CLSID_SecurityInfo            = string_to_bin('000001a6-0000-0000-c000-000000000046')
CLSID_ServerLocationInfo      = string_to_bin('000001a4-0000-0000-c000-000000000046')
CLSID_SpecialSystemProperties = string_to_bin('000001b9-0000-0000-c000-000000000046')
IID_IActivation               = uuidtup_to_bin(('4d9f4ab8-7d1c-11cf-861e-0020af6e7c57','0.0'))
IID_IActivationPropertiesIn   = uuidtup_to_bin(('000001A2-0000-0000-C000-000000000046','0.0'))
IID_IActivationPropertiesOut  = uuidtup_to_bin(('000001A3-0000-0000-C000-000000000046','0.0'))
IID_IContext                  = uuidtup_to_bin(('000001c0-0000-0000-C000-000000000046','0.0'))
IID_IObjectExporter           = uuidtup_to_bin(('99fcfec4-5260-101b-bbcb-00aa0021347a','0.0'))
IID_IRemoteSCMActivator       = uuidtup_to_bin(('000001A0-0000-0000-C000-000000000046','0.0'))
IID_IRemUnknown               = uuidtup_to_bin(('00000131-0000-0000-C000-000000000046','0.0'))
IID_IRemUnknown2              = uuidtup_to_bin(('00000143-0000-0000-C000-000000000046','0.0'))
IID_IUnknown                  = uuidtup_to_bin(('00000000-0000-0000-C000-000000000046','0.0'))

class DCERPCSessionError(Exception):
    def __init__( self, packet = None, error_code = None):
        Exception.__init__(self)
        self.packet = packet
        if packet is not None:
            self.error_code = packet['ErrorCode']
        else:
            self.error_code = error_code
       
    def get_error_code( self ):
        return self.error_code
 
    def get_packet( self ):
        return self.packet

    def __str__( self ):
        key = self.error_code & 0xffff
        if (system_errors.ERROR_MESSAGES.has_key(key)):
            error_msg_short = system_errors.ERROR_MESSAGES[key][0]
            error_msg_verbose = system_errors.ERROR_MESSAGES[key][1] 
            return 'DCOM SessionError: code: 0x%x - %s - %s' % (self.error_code, error_msg_short, error_msg_verbose)
        else:
            return 'DCOM SessionError: unknown error code: 0x%x' % (self.error_code)

################################################################################
# CONSTANTS
################################################################################
# 2.2.1 OID
OID = ULONGLONG

class OID_ARRAY(NDRUniConformantArray):
    item = OID

# 2.2.2 SETID
SETID = ULONGLONG

# 2.2.4 error_status_t
error_status_t = ULONG

# 2.2.6 CID
CID = GUID

# 2.2.7 CLSID
CLSID = GUID

# 2.2.8 IID
IID = GUID
PIID = PGUID

# 2.2.9 IPID
IPID = GUID

# 2.2.10 OXID
OXID = ULONGLONG

# 2.2.18 OBJREF
FLAGS_OBJREF_STANDARD = 0x00000001
FLAGS_OBJREF_HANDLER  = 0x00000002
FLAGS_OBJREF_CUSTOM   = 0x00000004
FLAGS_OBJREF_EXTENDED = 0x00000008

# 2.2.18.1 STDOBJREF
SORF_NOPING = 0x00001000

# 2.2.20 Context
CTXMSHLFLAGS_BYVAL = 0x00000002

# 2.2.20.1 PROPMARSHALHEADER
CPFLAG_PROPAGATE = 0x00000001
CPFLAG_EXPOSE    = 0x00000002
CPFLAG_ENVOY     = 0x00000004

# 2.2.22.2.1 InstantiationInfoData
ACTVFLAGS_DISABLE_AAA            = 0x00000002
ACTVFLAGS_ACTIVATE_32_BIT_SERVER = 0x00000004
ACTVFLAGS_ACTIVATE_64_BIT_SERVER = 0x00000008
ACTVFLAGS_NO_FAILURE_LOG         = 0x00000020

# 2.2.22.2.2 SpecialPropertiesData
SPD_FLAG_USE_CONSOLE_SESSION  = 0x00000001

# 2.2.28.1 IDL Range Constants
MAX_REQUESTED_INTERFACES = 0x8000
MAX_REQUESTED_PROTSEQS   = 0x8000
MIN_ACTPROP_LIMIT        = 1
MAX_ACTPROP_LIMIT        = 10

################################################################################
# STRUCTURES
################################################################################
class handle_t(NDRSTRUCT):
    structure =  (
        ('context_handle_attributes',ULONG),
        ('context_handle_uuid',UUID),
    )
    def __init__(self, data = None,isNDR64 = False):
        NDRSTRUCT.__init__(self, data, isNDR64)
        self['context_handle_uuid'] = '\x00'*20

# 2.2.11 COMVERSION
class COMVERSION(NDRSTRUCT):
    structure = (
        ('MajorVersion',USHORT),
        ('MinorVersion',USHORT),
    )
    def __init__(self, data = None,isNDR64 = False):
        NDRSTRUCT.__init__(self, data, isNDR64)
        if data is None:
            self['MajorVersion'] = 5
            self['MinorVersion'] = 7

class PCOMVERSION(NDRPOINTER):
    referent = (
        ('Data', COMVERSION),
    )

# 2.2.13.1 ORPC_EXTENT
# This MUST contain an array of bytes that form the extent data. 
# The array size MUST be a multiple of 8 for alignment reasons.
class BYTE_ARRAY(NDRUniConformantArray):
    item = 'c'

class PBYTE_ARRAY(NDRPOINTER):
    referent = (
        ('Data', BYTE_ARRAY),
    )

class ORPC_EXTENT(NDRSTRUCT):
    structure = (
        ('id',GUID),
        ('size',ULONG),
        ('data',PBYTE_ARRAY),
    )

# 2.2.13.2 ORPC_EXTENT_ARRAY
# ThisMUSTbeanarrayofORPC_EXTENTs.ThearraysizeMUSTbeamultipleof2for alignment reasons.
class ORPC_EXTENT_ARRAY(NDRUniConformantArray):
    item = ORPC_EXTENT

class PORPC_EXTENT_ARRAY(NDRPOINTER):
    referent = (
        ('Data', ORPC_EXTENT_ARRAY),
    )

class PPORPC_EXTENT_ARRAY(NDRPOINTER):
    referent = (
        ('Data', PORPC_EXTENT_ARRAY),
    )

class ORPC_EXTENT_ARRAY(NDRSTRUCT):
    structure = (
        ('size',ULONG),
        ('reserved',ULONG),
        ('extent',PPORPC_EXTENT_ARRAY),
    )

# 2.2.13.3 ORPCTHIS
class ORPCTHIS(NDRSTRUCT):
    structure = (
        ('version',COMVERSION),
        ('flags',ULONG),
        ('reserved1',ULONG),
        ('cid',CID),
        ('extensions',PPORPC_EXTENT_ARRAY),
    )

# 2.2.13.4 ORPCTHAT
class ORPCTHAT(NDRSTRUCT):
    structure = (
        ('flags',ULONG),
        ('extensions',PPORPC_EXTENT_ARRAY),
    )

# 2.2.14 MInterfacePointer
class MInterfacePointer(NDRSTRUCT):
    structure = (
        ('ulCntData',ULONG),
        ('abData',BYTE_ARRAY),
    )

# 2.2.15 PMInterfacePointerInternal
class PMInterfacePointerInternal(NDRPOINTER):
    referent = (
        ('Data', MInterfacePointer),
    )

# 2.2.16 PMInterfacePointer
class PMInterfacePointer(NDRPOINTER):
    referent = (
        ('Data', MInterfacePointer),
    )

# 2.2.18 OBJREF
class OBJREF(NDRSTRUCT):
    commonHdr = (
        ('signature',ULONG),
        ('flags',ULONG),
        ('iid',GUID),
    )
    def __init__(self, data = None,isNDR64 = False):
        NDRSTRUCT.__init__(self, data, isNDR64)
        if data is None:
            self['signature'] = 0x574F454D

# 2.2.18.1 STDOBJREF
class STDOBJREF(NDRSTRUCT):
    structure = (
        ('flags',ULONG),
        ('cPublicRefs',ULONG),
        ('oxid',OXID),
        ('oid',OID),
        ('ipid',IPID),
    )

# 2.2.18.4 OBJREF_STANDARD
class OBJREF_STANDARD(OBJREF):
    structure = (
        ('std',STDOBJREF),
        ('saResAddr',':'),
    )
    def __init__(self, data = None,isNDR64 = False):
        OBJREF.__init__(self, data, isNDR64)
        if data is None:
            self['flags'] = FLAGS_OBJREF_STANDARD5

# 2.2.18.5 OBJREF_HANDLER
class OBJREF_HANDLER(OBJREF):
    structure = (
        ('std',STDOBJREF),
        ('clsid',CLSID),
        ('saResAddr',':'),
    )
    def __init__(self, data = None,isNDR64 = False):
        OBJREF.__init__(self, data, isNDR64)
        if data is None:
            self['flags'] = FLAGS_OBJREF_HANDLER

# 2.2.18.6 OBJREF_CUSTOM
class OBJREF_CUSTOM(OBJREF):
    structure = (
        ('clsid',CLSID),
        ('cbExtension',ULONG),
        ('ObjectReferenceSize',ULONG),
        ('pObjectData',':'),
    )
    def __init__(self, data = None,isNDR64 = False):
        OBJREF.__init__(self, data, isNDR64)
        if data is None:
            self['flags'] = FLAGS_OBJREF_CUSTOM

# 2.2.18.8 DATAELEMENT
class DATAELEMENT(NDRSTRUCT):
    structure = (
        ('dataID',GUID),
        ('cbSize',ULONG),
        ('cbRounded',ULONG),
        ('Data',':'),
    )

# 2.2.18.7 OBJREF_EXTENDED
class OBJREF_EXTENDED(OBJREF):
    structure = (
        ('std',STDOBJREF),
        ('Signature1',ULONG),
        ('saResAddr',ULONG),
        ('nElms',ULONG),
        ('Signature2',ULONG),
        ('ElmArray',DATAELEMENT),
    )
    def __init__(self, data = None, isNDR64 = False):
        OBJREF.__init__(self, data, isNDR64)
        if data is None:
            self['flags'] = FLAGS_OBJREF_EXTENDED
            self['Signature1'] = 0x4E535956
            self['Signature1'] = 0x4E535956
            self['nElms'] = 0x4E535956

# 2.2.19 DUALSTRINGARRAY
class USHORT_ARRAY(NDRUniConformantArray):
    item = '<H'

class PUSHORT_ARRAY(NDRPOINTER):
    referent = (
        ('Data', USHORT_ARRAY),
    )

class DUALSTRINGARRAY(NDRSTRUCT):
    structure = (
        ('wNumEntries',USHORT),
        ('wSecurityOffset',USHORT),
        ('aStringArray',USHORT_ARRAY),
    )

class PDUALSTRINGARRAY(NDRPOINTER):
    referent = (
        ('Data',DUALSTRINGARRAY),
    )

# 2.2.19.3 STRINGBINDING
class STRINGBINDING(NDRSTRUCT):
    structure = (
        ('wTowerId',USHORT),
        ('aNetworkAddr',LPWSTR),
    )

# 2.2.19.4 SECURITYBINDING
class SECURITYBINDING(NDRSTRUCT):
    structure = (
        ('wAuthnSvc',USHORT),
        ('Reserved',USHORT),
        ('aPrincName',LPWSTR),
    )

# 2.2.20.1 PROPMARSHALHEADER
class PROPMARSHALHEADER(NDRSTRUCT):
    structure = (
        ('clsid',CLSID),
        ('policyId',GUID),
        ('flags',ULONG),
        ('cb',ULONG),
        ('ctxProperty',':'),
    )

class PROPMARSHALHEADER_ARRAY(NDRUniConformantArray):
    item = PROPMARSHALHEADER

# 2.2.20 Context
class Context(NDRSTRUCT):
    structure = (
        ('MajorVersion',USHORT),
        ('MinVersion',USHORT),
        ('ContextId',GUID),
        ('Flags',ULONG),
        ('Reserved',ULONG),
        ('dwNumExtents',ULONG),
        ('cbExtents',ULONG),
        ('MshlFlags',ULONG),
        ('Count',ULONG),
        ('Frozen',ULONG),
        ('PropMarshalHeader',PROPMARSHALHEADER_ARRAY),
    )

# 2.2.21.3 ErrorInfoString
class ErrorInfoString(NDRSTRUCT):
    structure = (
        ('dwMax',ULONG),
        ('dwOffSet',ULONG),
        ('dwActual',IID),
        ('Name',WSTR),
    )

# 2.2.21.2 Custom-Marshaled Error Information Format
class ORPC_ERROR_INFORMATION(NDRSTRUCT):
    structure = (
        ('dwVersion',ULONG),
        ('dwHelpContext',ULONG),
        ('iid',IID),
        ('dwSourceSignature',ULONG),
        ('Source',ErrorInfoString),
        ('dwDescriptionSignature',ULONG),
        ('Description',ErrorInfoString),
        ('dwHelpFileSignature',ULONG),
        ('HelpFile',ErrorInfoString),
    )

# 2.2.21.5 EntryHeader
class EntryHeader(NDRSTRUCT):
    structure = (
        ('Signature',ULONG),
        ('cbEHBuffer',ULONG),
        ('cbSize',ULONG),
        ('reserved',ULONG),
        ('policyID',GUID),
    )

class EntryHeader_ARRAY(NDRUniConformantArray):
    item = EntryHeader

# 2.2.21.4 Context ORPC Extension
class ORPC_CONTEXT(NDRSTRUCT):
    structure = (
        ('SignatureVersion',ULONG),
        ('Version',ULONG),
        ('cPolicies',ULONG),
        ('cbBuffer',ULONG),
        ('cbSize',ULONG),
        ('hr',ULONG),
        ('hrServer',ULONG),
        ('reserved',ULONG),
        ('EntryHeader',EntryHeader_ARRAY),
        ('PolicyData',':'),
    )
    def __init__(self, data = None, isNDR64 = False):
        NDRSTRUCT.__init__(self, data, isNDR64)
        if data is None:
            self['SignatureVersion'] = 0x414E554B

# 2.2.22.1 CustomHeader
class CLSID_ARRAY(NDRUniConformantArray):
    item = CLSID

class PCLSID_ARRAY(NDRPOINTER):
    referent = (
        ('Data', CLSID_ARRAY),
    )

class DWORD_ARRAY(NDRUniConformantArray):
    item = DWORD

class PDWORD_ARRAY(NDRPOINTER):
    referent = (
        ('Data', DWORD_ARRAY),
    )

class CustomHeader(TypeSerialization1):
    structure = (
        ('totalSize',DWORD),
        ('headerSize',DWORD),
        ('dwReserved',DWORD),
        ('destCtx',DWORD),
        ('cIfs',DWORD),
        ('classInfoClsid',CLSID),
        ('pclsid',PCLSID_ARRAY),
        ('pSizes',PDWORD_ARRAY),
        ('pdwReserved',LPLONG),
        #('pdwReserved',LONG),
    )
    def getData(self, soFar = 0):
        self['headerSize'] = len(TypeSerialization1.getData(self, soFar))+len(TypeSerialization1.getDataReferents(self, soFar))
        self['cIfs'] = len(self['pclsid'])
        return TypeSerialization1.getData(self, soFar)

# 2.2.22 Activation Properties BLOB
class ACTIVATION_BLOB(NDRTLSTRUCT):
    structure = (
        ('dwSize',ULONG),
        ('dwReserved',ULONG),
        ('CustomHeader',CustomHeader),
        ('Property',':'),
    )
    def getData(self, soFar = 0):
        self['dwSize'] = len(self['CustomHeader'].getData(soFar))+len(self['CustomHeader'].getDataReferents(soFar))+len(self['Property'])
        self['CustomHeader']['totalSize'] = self['dwSize']
        return NDRTLSTRUCT.getData(self, soFar)

# 2.2.22.2.1 InstantiationInfoData
class IID_ARRAY(NDRUniConformantArray):
    item = IID

class PIID_ARRAY(NDRPOINTER):
    referent = (
        ('Data', IID_ARRAY),
    )

class InstantiationInfoData(TypeSerialization1):
    structure = (
        ('classId',CLSID),
        ('classCtx',DWORD),
        ('actvflags',DWORD),
        ('fIsSurrogate',LONG),
        ('cIID',DWORD),
        ('instFlag',DWORD),
        ('pIID',PIID_ARRAY),
        ('thisSize',DWORD),
        ('clientCOMVersion',COMVERSION),
    )

# 2.2.22.2.2 SpecialPropertiesData
class SpecialPropertiesData(TypeSerialization1):
    structure = (
        ('dwSessionId',ULONG),
        ('fRemoteThisSessionId',LONG),
        ('fClientImpersonating',LONG),
        ('fPartitionIDPresent',LONG),
        ('dwDefaultAuthnLvl',DWORD),
        ('guidPartition',GUID),
        ('dwPRTFlags',DWORD),
        ('dwOrigClsctx',DWORD),
        ('dwFlags',DWORD),
        ('Reserved0',DWORD),
        ('Reserved0',DWORD),
        ('Reserved', '32s=""'),
        #('Reserved1',DWORD),
        #('Reserved2',ULONGLONG),
        #('Reserved3_1',DWORD),
        #('Reserved3_2',DWORD),
        #('Reserved3_3',DWORD),
        #('Reserved3_4',DWORD),
        #('Reserved3_5',DWORD),
    )

# 2.2.22.2.3 InstanceInfoData
class InstanceInfoData(TypeSerialization1):
    structure = (
        ('fileName',LPWSTR),
        ('mode',DWORD),
        ('ifdROT',PMInterfacePointer),
        ('ifdStg',PMInterfacePointer),
    )

# 2.2.22.2.4.1 customREMOTE_REQUEST_SCM_INFO
class customREMOTE_REQUEST_SCM_INFO(NDRSTRUCT):
    structure = (
        ('ClientImpLevel',DWORD),
        ('cRequestedProtseqs',USHORT),
        ('pRequestedProtseqs',PUSHORT_ARRAY),
    )

class PcustomREMOTE_REQUEST_SCM_INFO(NDRPOINTER):
    referent = (
        ('Data', customREMOTE_REQUEST_SCM_INFO),
    )

# 2.2.22.2.4 ScmRequestInfoData
class ScmRequestInfoData(TypeSerialization1):
    structure = (
        ('pdwReserved',LPLONG),
        ('remoteRequest',PcustomREMOTE_REQUEST_SCM_INFO),
    )

# 2.2.22.2.5 ActivationContextInfoData
class ActivationContextInfoData(TypeSerialization1):
    structure = (
        ('clientOK',LONG),
        ('bReserved1',LONG),
        ('dwReserved1',DWORD),
        ('dwReserved2',DWORD),
        ('pIFDClientCtx',PMInterfacePointer),
        ('pIFDPrototypeCtx',PMInterfacePointer),
    )

# 2.2.22.2.6 LocationInfoData
class LocationInfoData(TypeSerialization1):
    structure = (
        ('machineName',LPWSTR),
        ('processId',DWORD),
        ('apartmentId',DWORD),
        ('contextId',DWORD),
    )

# 2.2.22.2.7.1 COSERVERINFO
class COSERVERINFO(NDRSTRUCT):
    structure = (
        ('dwReserved1',DWORD),
        ('pwszName',LPWSTR),
        ('pdwReserved',LPLONG),
        ('dwReserved2',DWORD),
    )

class PCOSERVERINFO(NDRPOINTER):
    referent = (
        ('Data', COSERVERINFO),
    )

# 2.2.22.2.7 SecurityInfoData
class SecurityInfoData(TypeSerialization1):
    structure = (
        ('dwAuthnFlags',DWORD),
        ('pServerInfo',PCOSERVERINFO),
        ('pdwReserved',LPLONG),
    )

# 2.2.22.2.8.1 customREMOTE_REPLY_SCM_INFO
class customREMOTE_REPLY_SCM_INFO(NDRSTRUCT):
    structure = (
        ('Oxid',OXID),
        ('pdsaOxidBindings',DUALSTRINGARRAY),
        ('ipidRemUnknown',IPID),
        ('authnHint',DWORD),
        ('serverVersion',COMVERSION),
    )

class PcustomREMOTE_REPLY_SCM_INFO(NDRPOINTER):
    referent = (
        ('Data', customREMOTE_REPLY_SCM_INFO),
    )

# 2.2.22.2.8 ScmReplyInfoData
class ScmReplyInfoData(TypeSerialization1):
    structure = (
        ('pdwReserved',DWORD),
        ('remoteReply',PcustomREMOTE_REPLY_SCM_INFO),
    )

# 2.2.22.2.9 PropsOutInfo
class HRESULT_ARRAY(NDRUniConformantArray):
    item = HRESULT

class PHRESULT_ARRAY(NDRPOINTER):
    referent = (
        ('Data', HRESULT_ARRAY),
    )

class MInterfacePointer_ARRAY(NDRUniConformantArray):
    item = MInterfacePointer

class PMInterfacePointer_ARRAY(NDRPOINTER):
    referent = (
        ('Data', MInterfacePointer_ARRAY),
    )

class PropsOutInfo(TypeSerialization1):
    structure = (
        ('cIfs',DWORD),
        ('piid',PIID_ARRAY),
        ('phresults',PHRESULT_ARRAY),
        ('ppIntfData',PMInterfacePointer_ARRAY),
    )

# 2.2.23 REMINTERFACEREF
class REMINTERFACEREF(NDRSTRUCT):
    structure = (
        ('ipid',IPID),
        ('cPublicRefs',LONG),
        ('cPrivateRefs',LONG),
    )

# 2.2.24 REMQIRESULT
class REMQIRESULT(NDRSTRUCT):
    structure = (
        ('hResult',HRESULT),
        ('std',STDOBJREF),
    )

# 2.2.25 PREMQIRESULT
class PREMQIRESULT(NDRPOINTER):
    referent = (
        ('Data', REMQIRESULT),
    )

# 2.2.26 REFIPID
REFIPID = PGUID

################################################################################
# RPC CALLS
################################################################################
# 3.1.2.5.1.1 IObjectExporter::ResolveOxid (Opnum 0)
class ResolveOxid(NDRCALL):
    opnum = 0
    structure = (
       ('pOxid', OXID),
       ('cRequestedProtseqs', USHORT),
       ('arRequestedProtseqs', USHORT_ARRAY),
    )

class ResolveOxidResponse(NDRCALL):
    structure = (
       ('ppdsaOxidBindings', PDUALSTRINGARRAY),
       ('pipidRemUnknown', IPID),
       ('pAuthnHint', DWORD),
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.1.2 IObjectExporter::SimplePing (Opnum 1)
class SimplePing(NDRCALL):
    opnum = 1
    structure = (
       ('pSetId', SETID),
    )

class SimplePingResponse(NDRCALL):
    structure = (
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.1.3 IObjectExporter::ComplexPing (Opnum 2)
class ComplexPing(NDRCALL):
    opnum = 2
    structure = (
       ('pSetId', SETID),
       ('SequenceNum', USHORT),
       ('cAddToSet', USHORT),
       ('cDelFromSet', USHORT),
       ('AddToSet', OID_ARRAY),
       ('DelFromSet', OID_ARRAY),
    )

class ComplexPingResponse(NDRCALL):
    structure = (
       ('pSetId', SETID),
       ('pPingBackoffFactor', USHORT),
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.1.4 IObjectExporter::ServerAlive (Opnum 3)
class ServerAlive(NDRCALL):
    opnum = 3
    structure = (
    )

class ServerAliveResponse(NDRCALL):
    structure = (
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.1.5 IObjectExporter::ResolveOxid2 (Opnum 4)
class ResolveOxid2(NDRCALL):
    opnum = 4
    structure = (
       ('pOxid', OXID),
       ('cRequestedProtseqs', USHORT),
       ('arRequestedProtseqs', USHORT_ARRAY),
    )

class ResolveOxid2Response(NDRCALL):
    structure = (
       ('ppdsaOxidBindings', PDUALSTRINGARRAY),
       ('pipidRemUnknown', IPID),
       ('pAuthnHint', DWORD),
       ('pComVersion', COMVERSION),
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.1.6 IObjectExporter::ServerAlive2 (Opnum 5)
class ServerAlive2(NDRCALL):
    opnum = 5
    structure = (
    )

class ServerAlive2Response(NDRCALL):
    structure = (
       ('pComVersion', COMVERSION),
       ('ppdsaOrBindings', PDUALSTRINGARRAY),
       ('pReserved', LPLONG),
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.2.3.1 IActivation:: RemoteActivation (Opnum 0)
class RemoteActivation(NDRCALL):
    opnum = 0
    structure = (
       ('ORPCthis', ORPCTHIS),
       ('Clsid', GUID),
       ('pwszObjectName', LPWSTR),
       ('pObjectStorage', PMInterfacePointer),
       ('ClientImpLevel', DWORD),
       ('Mode', DWORD),
       ('Interfaces', DWORD),
       ('pIIDs', PIID),
       ('cRequestedProtseqs', USHORT),
       ('aRequestedProtseqs', USHORT_ARRAY),
    )

class RemoteActivationResponse(NDRCALL):
    structure = (
       ('ORPCthat', ORPCTHAT),
       ('pOxid', OXID),
       ('ppdsaOxidBindings', PDUALSTRINGARRAY),
       ('pipidRemUnknown', DWORD),
       ('pServerVersion', COMVERSION),
       ('phr', HRESULT),
       ('ppInterfaceData', PMInterfacePointer),
       ('pResults', HRESULT_ARRAY),
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.2.3.2 IRemoteSCMActivator:: RemoteGetClassObject (Opnum 3)
class RemoteGetClassObject(NDRCALL):
    opnum = 3
    structure = (
       ('ORPCthis', ORPCTHIS),
       ('pActProperties', PMInterfacePointer),
    )

class RemoteGetClassObjectResponse(NDRCALL):
    structure = (
       ('ORPCthat', ORPCTHAT),
       ('ppActProperties', PMInterfacePointer),
       ('ErrorCode', error_status_t),
    )

# 3.1.2.5.2.3.3 IRemoteSCMActivator::RemoteCreateInstance (Opnum 4)
class RemoteCreateInstance(NDRCALL):
    opnum = 4
    structure = (
       ('ORPCthis', ORPCTHIS),
       ('pUnkOuter', PMInterfacePointer),
       ('pActProperties', PMInterfacePointer),
    )

class RemoteCreateInstanceResponse(NDRCALL):
    structure = (
       ('ORPCthat', ORPCTHAT),
       ('ppActProperties', PMInterfacePointer),
       ('ErrorCode', error_status_t),
    )

# 3.1.1.5.6.1.1 IRemUnknown::RemQueryInterface (Opnum 3)
class RemQueryInterface(NDRCALL):
    opnum = 3
    structure = (
       ('ripid', REFIPID),
       ('cRefs', ULONG),
       ('cIids', USHORT),
       ('iids', IID_ARRAY),
    )

class RemQueryInterfaceResponse(NDRCALL):
    structure = (
       ('ppQIResults', PREMQIRESULT),
       ('ErrorCode', error_status_t),
    )


class test(NDRCALL):
    opnum = 0
    structure = (
        ('item1', ULONG),
        ('item2', CustomHeader),
        ('item3', USHORT),
    )

################################################################################
# OPNUMs and their corresponding structures
################################################################################
OPNUMS = {
}

################################################################################
# HELPER FUNCTIONS
################################################################################
