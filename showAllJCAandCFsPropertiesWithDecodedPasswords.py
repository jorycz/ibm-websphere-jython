import re
import os
import sys
import binascii

# https://github.com/digital-shokunin/was_xor_decode/blob/master/xor_decode.py
def xorsum(val1, val2):
  """Create xor sum between two strings"""
  password = ''
  for a, b in zip(val1, val2):
    password = ''.join([password, chr(ord(a) ^ ord(b))])
  return password

def encode_xor(password):
  """Encode a password into the xor format, useful if importing script into larger automated"""
  cipher = '_' * len(password)
  return '{xor}' + binascii.b2a_base64(xorsum(password, cipher))

def decode_xor(xor_str):
  """Will decode am xor'ed password from the format stored in the security.xml"""
  xor_str = xor_str.replace('{xor}', '')
  value1 = binascii.a2b_base64(xor_str)
  value2 = '_' * len(value1)
  return xorsum(value1, value2)
#########################################################################

if len(sys.argv) < 1:
  print "\nUSAGE: script.jy <server|all> (<decodePasswords>)\n"
  os._exit(1)
else:
  serverToListJca = sys.argv[0]

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

print '\n------------------------------------------\nServer to find JCA, ALL CFs & Properties: ' + serverToListJca + '\n'

### TOPOLOGY CONFIG - DMGR, WEB nodes and WAS nodes are defined by part of hostname:
cName = AdminControl.getCell()
cID = AdminConfig.getid('/Cell:'+cName)

# In case of more Cells....
# cells = AdminConfig.list('Cell').split()
# cell = cells[0]
# cName = AdminConfig.showAttribute(cell, 'name')

print '----------------'
print ' Cell Name: ' + cName
print ' Cell ID  : ' + cID

dmgrNode = ''

webNodes = list('')
webNodesID = list('')
webNodeSearch = 'web'

wasNodes = list('')
wasNodesID = list('')
wasNodeSearch = '^.was'

dmgrNodeSearch = 'dmgr|Dmgr'

print '\n****************** Assigning role to nodes by part of hostname ******************'
print '\tDMGR: [' + dmgrNodeSearch + ']\tWEB nodes: [' + webNodeSearch + ']\tWAS nodes: [' + wasNodeSearch + ']'
print '*********************************************************************************\n'

nodes = AdminTask.listNodes()
for nod in nodes.splitlines():
  if re.search (dmgrNodeSearch, nod):
    dmgrNode = nod
  else:
    if re.search (wasNodeSearch, nod):
      wasNodes.append(nod)
    if re.search (webNodeSearch, nod):
      webNodes.append(nod)
####################################################################################

print '--- Topology ---'
dmgrNodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+dmgrNode)
print ' DMGR     : ' + dmgrNode + ' , ID : ' + dmgrNodeID
for web in webNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+web)
  webNodesID.append(nodeID)
  print ' WEB node: ' + web + ' , ID : ' + nodeID
for was in wasNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+was)
  wasNodesID.append(nodeID)
  print ' WAS node: ' + was + ' , ID : ' + nodeID
print '----------------'

# SORT BY NODE

for nName in wasNodes:

  print '\n\n'
  print ' ========================================== '
  print ' ====== NODE SUMMARY [ '+nName+' ] ======'
  print ' ========================================== '
  
  scopeId = AdminConfig.getid('/Node:' + nName + '/')
  nodeServers = AdminConfig.list('Server', scopeId).split()

  for server in nodeServers:
    sName = AdminConfig.showAttribute(server, 'name')
    if (re.search("(^" + serverToListJca + "$)", sName) or serverToListJca == 'all'):
      print '\n ======== LOOKING for ALL JCA & CFs Properties on SERVER : [ ' + sName + ' ]'
      jcas = AdminConfig.list('J2CResourceAdapter', AdminConfig.getid('/Cell:' + cName + '/Node:' + nName + '/Server:' + sName + '/')).splitlines()
      for jca in jcas:
        jcaName = AdminConfig.showAttribute(jca, 'name')
        ### Filter out WebSphere default JCA providers ...
        if re.search("^(?!SIB JMS Resource Adapter|WebSphere MQ Resource Adapter|WebSphere Relational Resource Adapter)", jcaName):
          print "\n   > JCA found : " + jcaName
          print ""
          connFactories = AdminConfig.list('J2CConnectionFactory', AdminConfig.getid('/Cell:' + cName + '/Node:' + nName + '/Server:' + sName + '/J2CResourceAdapter:' + jcaName + '/')).splitlines()
          for cf in connFactories:
            cfName = AdminConfig.showAttribute(cf, 'name')
            cfJndi = AdminConfig.showAttribute(cf, 'jndiName')
            print "     > CF found : " + cfName + ' [ ' + cfJndi + ' ]'
            print ""
            ps = AdminConfig.showAttribute(cf, 'propertySet')
            propList = AdminConfig.list('J2EEResourceProperty', ps).splitlines()
            for prop in propList:
              n = ""
              v = ""
              vd = ""
              if AdminConfig.showAttribute(prop, 'name'):
                n = AdminConfig.showAttribute(prop, 'name')
              if AdminConfig.showAttribute(prop, 'value'):
                v = AdminConfig.showAttribute(prop, 'value')
                if re.search("^{xor}.*", v):
                  vd = " (WARNING !!! DECODED: " + decode_xor(v) + ")"
              if arg(1) == 'decodePasswords':
                print  "       > [ " + n + " ] - - - - - [ " + v + vd + " ]"
              else:
                print  "       > [ " + n + " ] = = = = = [ " + v + " ]"
            print ""
            cpId = AdminConfig.showAttribute(cf, 'connectionPool')
            # print '  - connectionPool ID >> ' + cpId
            # print AdminConfig.showall(cpId)
            ct = AdminConfig.showAttribute(cpId, 'connectionTimeout')
            maxc = AdminConfig.showAttribute(cpId, 'maxConnections')
            minc = AdminConfig.showAttribute(cpId, 'minConnections')
            reap = AdminConfig.showAttribute(cpId, 'reapTime')
            unused = AdminConfig.showAttribute(cpId, 'unusedTimeout')
            aged = AdminConfig.showAttribute(cpId, 'agedTimeout')
            # EntirePool or FailingConnectionOnly
            purgep = AdminConfig.showAttribute(cpId, 'purgePolicy')
            print '       POOL : connectionTimeout [ ' + ct + ' ] maxConnections [ ' + maxc + ' ] minConnections [ ' + minc + ' ] reapTime [ ' + reap + ' ] unusedTimeout [ ' + unused + ' ] agedTimeout [ ' + aged + ' ] purgePolicy [ ' + purgep + ' ]'
            print ''

print '\nDone.\n'

