import re
import os
import sys

if len(sys.argv) < 1:
  print "\nUSAGE: script.jy <policyname>\n"
  print "EXAMPLE: script.jy msgdb_cluster\n"
  os._exit(1)

POLICYNAME = sys.argv[0]

cName = AdminControl.getCell()

print

coreGroups = AdminConfig.list('CoreGroup', AdminConfig.getid('/Cell:'+cName))

for cg in coreGroups.splitlines():
  if re.search('DefaultCoreGroup', cg):
    cgName = AdminConfig.showAttribute(cg, 'name')
    print '==> Core Group: ' + cgName
    policies = AdminConfig.list('HAManagerPolicy', cg)
    for p in policies.splitlines():
      if re.search(POLICYNAME, p):
        policyName = AdminConfig.showAttribute (p, 'name')
        print '==> Policy name: ' + policyName
        print
        currentPreferred = AdminConfig.showAttribute(p, 'preferredServers')
        # print 'CURRENT SERVERS ' + currentPreferred
        # print
        preferred = []
        for server in currentPreferred.split(' '):
          srvId = (str(server).replace('[','').replace(']','').strip())
          srvNodeName = AdminConfig.showAttribute(srvId,'nodeName')
          srvServerName = AdminConfig.showAttribute(srvId,'serverName')
          # print 'Current NODE ' + srvNodeName + ', Current SERVER ' + srvServerName
          preferred.append(srvNodeName+'/'+srvServerName)
        # print preferred
        print '- Current order of servers: ' + ";".join(preferred)
        preferred.reverse()
        # print preferred
        finalServerList = ";".join(preferred)
        print '- New order of servers:     ' + ";".join(preferred)
        print
        answer = str(raw_input('Continue with switchover? WARNING !!! This is runtime operation - change will be imminent !!! [y/n] : '))
        if answer:
          if re.search ('^(y|Y)',answer):
            print 'Changing order ...'
            AdminTask.modifyPolicy('[-coreGroupName ' + cgName + ' -policyName ' + policyName + ' -serversList ' + finalServerList + ']')
            print "\n!!! SAVING & SYNCING configuration to nodes ... Swtichover begins now ...\n"
            AdminConfig.save()
            AdminNodeManagement.syncActiveNodes()
          else:
            print "\nCONFIG RESET ... No change to configuration was performed.\n"
            AdminConfig.reset()
          print 'Done ... \n'
      else:
        policyName = AdminConfig.showAttribute (p, 'name')
        print 'No policy name [' + POLICYNAME + '] exists, found [' + policyName + '].\n'

