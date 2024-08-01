import re
import os
import sys

if len(sys.argv) < 2:
  print "\nUSAGE: script.jy <is|not> <word>\n"
  print "       <is> - show only module mapping where specified word IS found."
  print "       <not> - show only module mapping where specified word IS NOT found."
  print "       <word> - word that MUST or MUST NOT be in module mapping string for listing.\n"
  os._exit(1)

actionParam = sys.argv[0]
wordParam = sys.argv[1]

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
  print 'NODE: [ ' + nName + ' ]\n'
  apps = AdminApp.list('WebSphere:cell=' + cName + ',node=' + nName)
  for app in apps.splitlines():
    mapping = AdminApp.view(app, '-MapModulesToServers')
    for line in mapping.splitlines():
      if re.search('WebSphere', line):
        if actionParam == 'is':
          if re.search(wordParam, line):
            print 'APPLICATION [ ' + app + ' ] - MAPPING IS ON [ ' + wordParam + ' ] MAPPING: [' + line + ']'
        if actionParam == 'not':
          if not re.search(wordParam, line):
            print 'APPLICATION [ ' + app + ' ] - MAPPING IS NOT ON [ ' + wordParam + ' ] MAPPING: [' + line + ']'
            
  print '\n'

print 'Done.\n'