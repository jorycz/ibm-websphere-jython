import re
import sys
import binascii

ldapNew = 'ldap'

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
  """Will decode am xor'ed password from the format stored in WAS configuration"""
  xor_str = xor_str.replace('{xor}', '')
  value1 = binascii.a2b_base64(xor_str)
  value2 = '_' * len(value1)
  return xorsum(value1, value2)
#########

print '----------------'
if len(sys.argv) < 1:
  print "USAGE: script.jy <serverName1|serverName2|...|all>"
  os._exit(1)
else:
  print "Server: " + serverToListJca

serverToListJca = sys.argv[0]

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

  print ' ========================================== '
  print ' ====== NODE SUMMARY [ '+nName+' ] ======'
  print ' ========================================== '
  
  scopeId = AdminConfig.getid('/Node:' + nName + '/')
  nodeServers = AdminConfig.list('Server', scopeId).split()

  print " > LOOKING ALL JCA & CF on SERVER : [ " + serverToListJca + " ]"
  print ""
  for server in nodeServers:
    # sName = AdminControl.getAttribute(server, 'name')
    # print AdminConfig.getObjectName(server)
    sName = AdminConfig.showAttribute(server, 'name')
    if (sName == serverToListJca or serverToListJca == 'all'):
      jcas = AdminConfig.list('J2CResourceAdapter', AdminConfig.getid('/Cell:' + cName + '/Node:' + nName + '/Server:' + sName + '/')).splitlines()
      for jca in jcas:
        # Search only JCA where name CONTAINS ldap ...
        if re.search('ldap', jca, re.IGNORECASE):
          jcaName = AdminConfig.showAttribute(jca, 'name')
          print "=> JCA found : " + jcaName
          # print ""
          connFactories = AdminConfig.list('J2CConnectionFactory', AdminConfig.getid('/Cell:' + cName + '/Node:' + nName + '/Server:' + sName + '/J2CResourceAdapter:' + jcaName + '/')).splitlines()
          for cf in connFactories:
            cfName = AdminConfig.showAttribute(cf, 'name')
            print "  > CF found : " + cfName
            # print ""
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
                  vd = " (DECODED: " + decode_xor(v) + ")"
              # SHOW ALL PROPERTIES:
              # print  "   > [ " + n + " ] = = = [ " + v + vd + " ]"
              # SHOW ONLY ldapHost property:
              if re.search('ldapHost', n):
                print  "    > [ " + n + " ] = = = [ " + v + vd + " ]"
                AdminConfig.modify(prop, [['value', ldapNew]])
                v = AdminConfig.showAttribute(prop, 'value')
                print  "    > [ " + n + " ] = = = [ " + v + vd + " ] ...... NEW ......"
            print ""

print ''


print 'Reset ...'
AdminConfig.reset()

# print 'Saving ...'
# AdminConfig.save()
# AdminNodeManagement.syncActiveNodes()

print 'Done.'

