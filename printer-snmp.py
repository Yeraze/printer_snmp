#!/usr/bin/env python
from pysnmp import hlapi
def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0] 
def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types 
def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return result 
def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value

snmp_PrinterName = '1.3.6.1.2.1.25.3.2.1.3.1'
snmp_PagesPrinted = '1.3.6.1.2.1.43.10.2.1.4.1.1'
snmp_ColorNames = ['1.3.6.1.2.1.43.11.1.1.6.1.1','1.3.6.1.2.1.43.11.1.1.6.1.2','1.3.6.1.2.1.43.11.1.1.6.1.3','1.3.6.1.2.1.43.11.1.1.6.1.4']
snmp_ColorValue = ['1.3.6.1.2.1.43.11.1.1.9.1.1','1.3.6.1.2.1.43.11.1.1.9.1.2','1.3.6.1.2.1.43.11.1.1.9.1.3','1.3.6.1.2.1.43.11.1.1.9.1.4']
snmp_Colors     = ['black', 'cyan', 'magenta', 'yellow']
oids = list()
oids.append(snmp_PrinterName)
oids.append(snmp_PagesPrinted)
oids.extend(snmp_ColorNames)
oids.extend(snmp_ColorValue)

for ip in ['192.168.4.55', '192.168.4.77']:
	results = get(ip, oids, hlapi.CommunityData('VJhT6t3wTGPHY4J2'))
	print("<div style=\"padding: 1em\">")
	print("<b style=\"font-size:110%%\"><a href=\"http://%s/\">%s</a></b><br/>" % (ip, results[snmp_PrinterName]))
	print("<div style=\"padding-left:2em\">Pages Printed: %s</div>" % results[snmp_PagesPrinted])
	for (name, value, color) in zip(snmp_ColorNames, snmp_ColorValue, snmp_Colors):
		print("<div style=\"width:100px;height:1.1em;border:1px black solid; float:left\">")
		print("<div style=\"width:%s%% ; background-color: %s \">%s</div>" % (results[value], color, results[value]))
		print("</div>")
	print("</div>")
