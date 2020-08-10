#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from zipfile import ZipFile

zipPath = sys.argv[1]
outPath = sys.argv[2]

nameResolveTable = {}

with ZipFile(zipPath) as zipTrials:
	for docPath in zipTrials.filelist:
		if not docPath.filename.endswith(".json"):
			continue
		print("Processing: {}".format(docPath.filename))
		ncitdName = docPath.filename.split('/')[-1].split('.')[0]
		
		#Open the file
		with zipTrials.open(docPath.filename) as trialDoc:
			studyinfo = json.loads(trialDoc.read())
		
		#Create a mapping for the original name
		try:
			orgName = studyinfo['FullStudy']['Study']['ProtocolSection']['IdentificationModule']['OrgStudyIdInfo']['OrgStudyId']
			nameResolveTable[orgName] = ncitdName
		except KeyError:
			pass
		
		#Extract the alternate names
		try:
			for altId in studyinfo['FullStudy']['Study']['ProtocolSection']['IdentificationModule']['SecondaryIdInfoList']['SecondaryIdInfo']:
				print("\t{} --> {}".format(altId['SecondaryId'], ncitdName))
				nameResolveTable[altId['SecondaryId']] = ncitdName
		except KeyError:
			pass
		
		#Lastly, self should always map to self
		nameResolveTable[ncitdName] = ncitdName

with open(outPath, 'w') as jsonOut:
	jsonOut.write(json.dumps(nameResolveTable))
