#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from zipfile import ZipFile

zipPath = sys.argv[1]
outPath = sys.argv[2]

titleLookup = {}

with ZipFile(zipPath) as zipTrials:
	for docPath in zipTrials.filelist:
		if not docPath.filename.endswith(".json"):
			continue
		print("Processing: {}".format(docPath.filename))
		ncitdName = docPath.filename.split('/')[-1].split('.')[0]
		
		#Open the file
		with zipTrials.open(docPath.filename) as trialDoc:
			studyinfo = json.loads(trialDoc.read())
		
		#Get the official title of this study
		try:
			officialTitle = studyinfo['FullStudy']['Study']['ProtocolSection']['IdentificationModule']['OfficialTitle']
			titleLookup[ncitdName] = officialTitle
		except KeyError:
			#If this fails, make the title the NCTId
			titleLookup[ncitdName] = ncitdName

with open(outPath, 'w') as jsonOut:
	jsonOut.write(json.dumps(titleLookup))
