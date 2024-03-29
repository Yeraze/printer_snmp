#!/usr/bin/env python
from datetime import datetime
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

# List of OID's to query
snmp_PrinterName = '1.3.6.1.2.1.25.3.2.1.3.1'           # Pretty name for the printer
snmp_PagesPrinted = '1.3.6.1.2.1.43.10.2.1.4.1.1'       # Entry for number of pages printed

#   Fields for names of each of the 4 cartridges
snmp_ColorNames = ['1.3.6.1.2.1.43.11.1.1.6.1.1','1.3.6.1.2.1.43.11.1.1.6.1.2','1.3.6.1.2.1.43.11.1.1.6.1.3','1.3.6.1.2.1.43.11.1.1.6.1.4']
#   Fields for Percentage ink remaining of each of the 4 cartridges
snmp_ColorValue = ['1.3.6.1.2.1.43.11.1.1.9.1.1','1.3.6.1.2.1.43.11.1.1.9.1.2','1.3.6.1.2.1.43.11.1.1.9.1.3','1.3.6.1.2.1.43.11.1.1.9.1.4']
#   Ordered list of color names to be used for the progress bars
snmp_Colors     = ['black', 'cyan', 'magenta', 'yellow']
oids = list()
oids.append(snmp_PrinterName)
oids.append(snmp_PagesPrinted)
oids.extend(snmp_ColorNames)
oids.extend(snmp_ColorValue)

cReplaced = dict()
cReplaced['black']   = [4346, '2021-06-15']
cReplaced['cyan']    = [4746, '2021-09-27']
cReplaced['magenta'] = [4746, '2021-09-27']
cReplaced['yellow']  = [   0, '2021-01-30']


# IP's of the printers to query
for ip in ['192.168.4.77']:
    # For SNMP v2c, enter the community here
    results = get(ip, oids, hlapi.CommunityData('VJhT6t3wTGPHY4J2'))

    # Contain each printer result in a Div, class is "printer" for styling
    print("<div class=\"printer\" style=\"padding: 1em\">")
    print("<b style=\"font-size:110%%\"><a href=\"http://%s/\">%s</a></b><br/>" % (ip, results[snmp_PrinterName]))
    print("<div style=\"padding-left:2em\">Pages Printed: %s</div>" % results[snmp_PagesPrinted])
    for (name, value, color) in zip(snmp_ColorNames, snmp_ColorValue, snmp_Colors):
        print("<div style=\"width:100px;height:1.1em;border:1px black solid; float:left\">")
        print("<div style=\"width:%s%% ;height:100%%; background-color: %s; float:left\">" % (results[value], color))
        if (int(results[value]) < 50):
            print("</div> %s%%" % results[value])
        else:
            print(" %s%%</div>" % results[value])
        print("</div>")
    print("</div>")

print("""
        <br>
        <b>Toner Replacements:</b>
        <table border="1" style="font-size: 80%">
        <tr><th style="width:20em">Color</th><th style="width:20em">Page Count</th><th style="width:20em">Date</th></tr>
""")

for color in snmp_Colors:
    print("""<tr><td><span style="background-color: %s; padding-right:3em">&nbsp;</span> %s  </td>""" % (color, color.title()))
    print("""<td>%s (%s)</td>""" % (cReplaced[color][0], results[snmp_PagesPrinted] - cReplaced[color][0]))
    d = datetime.strptime(cReplaced[color][1], "%Y-%m-%d")
    
    print("""<td>%s (%d days)</td></tr>""" % (cReplaced[color][1], (datetime.now() - d).days))

print("</table>")
