#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the terms of GPL v3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# Int. Journal of Information Technology & Web Engineering, 1(3), 17–26.
#
# and
#
# FLOSSmole(2004-2017) FLOSSmole: a project to provide academic access to data
# and analyses of open source projects. Available at http://flossmole.org
#
################################################################
# usage:
#
# 0getCodeplexNames.py <datasource_id> <db password>
#
# purpose:
#
# get & insert all Codeplex project names before site was shut down
# https://www.codeplex.com/site/search?size=1000
# inexplicably yielded the entire project list on one page,
# including spam projects
################################################################
import sys
import re
import pymysql

# grab commandline args
datasourceID = str(sys.argv[1])
pw = str(sys.argv[2])
lastUpdated = None

# Open remote database connection
dbconn = pymysql.connect(host="",
                      user="",
                      passwd=pw,
                      db="",
                      use_unicode=True,
                      charset="utf8mb4")
cursor = dbconn.cursor()


# read in list of projects
f = open('projectUrlsOnly.txt')
print('reading file')
projectList = f.readlines()

insertProjectsQuery = 'INSERT INTO cp_projects (proj_name, \
                                                datasource_id, \
                                                proj_url, \
                                                last_updated) \
                       VALUES (%s, %s, %s, %s)'

# insert projects
for projectUrl in projectList:
    projectUrl = projectUrl.rstrip()
    print("grabbing", projectUrl)
    projMatch = re.match('https:\/\/(.*?)\.codeplex\.com', projectUrl)
    projName = projMatch.group(1)
    cursor.execute(insertProjectsQuery, (projName,
                                         datasourceID,
                                         projectUrl,
                                         lastUpdated))
    dbconn.commit()
dbconn.close()
