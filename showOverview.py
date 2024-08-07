import re
import os
import sys

heapInitDefault = "50"
heapMaxDefault = "256"

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

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

if len(arg(0)) < 1:
  print 'You can run this script with any argument to bypass this question.\n'
  answer = str(raw_input('Do you want to continue? [y/n] : '))
  if answer:
    if re.search('^(y|Y)',answer):
      print '\n'
    else:
      print 'Exitting ...\n'
      os._exit(0)

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
print ' DMGR    : ' + dmgrNode + ' , ID : ' + dmgrNodeID
for web in webNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+web)
  webNodesID.append(nodeID)
  print ' WEB node: ' + web + ' , ID : ' + nodeID
for was in wasNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+was)
  wasNodesID.append(nodeID)
  print ' WAS node: ' + was + ' , ID : ' + nodeID
print '----------------'

appServers = []
installedApps = []

# SORT BY NODE

for nName in wasNodes:

  maxUsageMemory = 0
  print ' ========================================== '
  print ' ====== NODE SUMMARY [ '+nName+' ] ======'
  print ' ========================================== '

  nodeID = AdminConfig.getid('/Node:' + nName )
  servers = AdminConfig.list('ServerEntry', nodeID).split()

  for server in servers:
    # print 'DEBUG: ' + server

    appServers.append(server)
    # print AdminConfig.showall(server)
    sName = AdminConfig.showAttribute(server, "serverName")
    sType = AdminConfig.showAttribute(server, "serverType")
    serverID = AdminConfig.getid('/Node:' + nName + '/Server:' + sName + '/')
    jvm = AdminConfig.list('JavaVirtualMachine', serverID)
    initialHeapSize = AdminConfig.showAttribute(jvm, 'initialHeapSize')
    maximumHeapSize = AdminConfig.showAttribute(jvm, 'maximumHeapSize')

    # Correct default sizes reported as 0 ...
    if initialHeapSize == "0":
      initialHeapSize = heapInitDefault
    if maximumHeapSize == "0":
      maximumHeapSize = heapMaxDefault
    maxUsageMemory += int(maximumHeapSize)

    print ' SERVER [ ' + sName + ' ] HEAP INIT/MAX [ ' + initialHeapSize + ' / ' + maximumHeapSize + ' MB ]'

    apps = AdminConfig.showAttribute(server, "deployedApplications").split(';')
    for app in apps:
      aName = app.split('/')[0]
      if re.search("^(?!ibmasyncrsp).*", aName):
        print ' \t---> app: ' + aName
        installedApps.append(aName)
  print ' ---> Maximum HEAP available for node ' + nName + ' is configured for ' + str(maxUsageMemory) + ' MB !'

print ''

