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
# 3parseMoreDetails.py <datasource_id> <db password>

# purpose:
# parse the pages for Codeplex projects for: project long name, and description
################################################################

import sys
import pymysql
import re

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

selectProjects = 'SELECT proj_name \
                  FROM cp_projects_indexes \
                  WHERE datasource_id = %s'
# WHERE datasource_id = %s AND proj_name=\'compositewpf\''

selectIndexes = 'SELECT home_html \
                 FROM cp_projects_indexes \
                 WHERE datasource_id = %s \
                 AND proj_name = %s'

# this is short for now
updateProjects = 'UPDATE cp_projects SET \
                  proj_long_name = %s, \
                  description = %s, \
                  last_updated = %s \
                  WHERE proj_name = %s AND datasource_id = %s'

# grab the project list
cursor.execute(selectProjects, (datasourceID,))
projectList = cursor.fetchall()


for project in projectList:
    projectName = project[0]
    projectLongName = ''
    projectDescription = ''
    print("parsing:", projectName)

    # grab the index
    cursor.execute(selectIndexes, (datasourceID, projectName))
    homeHtml = cursor.fetchone()[0]

# <title>Windows USB&#47;DVD Download Tool - Home</title>
# <div class="wikidoc"></div>
    regex = r'<title>(.*?) \- Home<\/title>'
    match = re.search(regex, homeHtml)
    if match:
        projectLongName = match.group(1)

    regex2 = re.compile(r'<div class=\"wikidoc\">(.*?)<\/div>', re.DOTALL)
    match2 = re.search(regex2, homeHtml)
    if match2:
        projectDescription = match2.group(1)

    try:
        cursor.execute(updateProjects, (projectLongName,
                                        projectDescription,
                                        lastUpdated,
                                        projectName,
                                        datasourceID))
        dbconn.commit()
    except:
        print("---error with", projectName)
        dbconn.rollback()
dbconn.close()
