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
# 2parseCodeplexPages.py <datasource_id> <db password>

# purpose:
# parse the pages for Codeplex projects we grabbed before it was shut down
# read in list of projects
# for each project, grab the following pages:
# --- home page
# --- history page
# from the database, parse them out, then update the database
################################################################

import sys
import pymysql
import re
import datetime

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
                         charset="utf8mb4",
                         autocommit=True)
cursor = dbconn.cursor()

selectProjects = 'SELECT proj_name \
                  FROM cp_projects_indexes \
                  WHERE datasource_id = %s'

selectIndexes = 'SELECT history_html \
                 FROM cp_projects_indexes \
                 WHERE datasource_id = %s \
                 AND proj_name = %s'

# this is short for now
updateProjects = 'UPDATE cp_projects SET \
                  create_date = %s, \
                  last_updated = %s \
                  WHERE proj_name = %s AND datasource_id = %s'

# grab the project list
cursor.execute(selectProjects, (datasourceID,))
projectList = cursor.fetchall()


for project in projectList:
    projectName = project[0]
    print("parsing:", projectName)

    # grab the indexes
    cursor.execute(selectIndexes, (datasourceID, projectName))
    historyHtml = cursor.fetchone()[0]

    regex = '<h2 class=\"DateHeader\" id=\"DateHeader(.*?)\">(.*?)<\/h2>'
    match = re.findall(regex, historyHtml)

    # parse out the year and month
    if match:
        firstLongDate = match[-1][1]
        myDate = datetime.datetime.strptime(firstLongDate, '%B, %Y')
        fixedDate = str(myDate.strftime("%Y-%m"))
        print(fixedDate)
        cursor.execute(updateProjects, (fixedDate, lastUpdated, projectName, datasourceID))
dbconn.close()
