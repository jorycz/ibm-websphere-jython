import re
import os
import sys

if len(sys.argv) < 2:
  print "\nUSAGE: script.jy <nodename|all> <server|all>\n"
  os._exit(1)

nodeParam = sys.argv[0]
serverParam = sys.argv[1]

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

for nName in wasNodes:

  if (re.search("(^" + nName + "$)", nodeParam) or nodeParam == 'all'):
    nodeID = AdminConfig.getid('/Node:' + nName )
    servers = AdminConfig.list('ServerEntry', nodeID).split()

    for server in servers:
      sName = AdminConfig.showAttribute(server, "serverName")
      if (re.search("(^" + sName + "$)", serverParam) or serverParam == 'all'):
        jvmGenericProperties = AdminTask.showJVMProperties('[-serverName ' + sName + ' -nodeName ' + nName + ' -propertyName genericJvmArguments]')
        print '\nSERVER [ ' + sName + ' ] NODE [ ' + nName + ' ]'
        if len(jvmGenericProperties) > 0:
          print '- JVM Generic arguments: [ ' + jvmGenericProperties + ' ] '
        else:
          print '- No JVM Generic arguments for server [ ' + sName + ' ] '
        
        # jvmCustomProperties = AdminTask.showJVMSystemProperties('[-serverName ' + sName + ' -nodeName ' + nName + ' -propertyName gpe-log4j.configuration]')
        jvmCustomProperties = AdminTask.showJVMSystemProperties('[-serverName ' + sName + ' -nodeName ' + nName + ']')
        if len(jvmCustomProperties) > 0:
          print '- JVM Custom Properties: '
          # Remove the outer square brackets
          jvmCustomProperties = jvmCustomProperties[1:-1]
          # Strip trailing whitespace
          jvmCustomProperties = jvmCustomProperties.rstrip()
          # Split the string into individual property strings
          properties = jvmCustomProperties.split('] [')
          # Clean up the first and last element
          properties[0] = properties[0][1:]
          properties[-1] = properties[-1][:-1]
          # Split each property into a list of its parts
          properties = [prop.split() for prop in properties]
          # Print each property
          for prop in properties:
            print '\t[' + prop[0] + ']\t\t[' + prop[1] + ']'
        else:
          print '- No JVM Custom properties for server [ ' + sName + ' ] '

  print '\n---------------------------------------------------------------------------------------------------------------'

print '\nDone.\n'
