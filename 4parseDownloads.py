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
# 4parseDownloads.py <datasource_id> <db password>

# purpose:
# parse the pages for Codeplex projects for download version, date, and count
################################################################

import sys
import pymysql
from bs4 import BeautifulSoup

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

selectIndexes = 'SELECT home_html \
                 FROM cp_projects_indexes \
                 WHERE datasource_id = %s \
                 AND proj_name = %s'

updateProjects = 'UPDATE cp_projects SET \
                  current_dl_version = %s, \
                  current_dl_date = %s, \
                  download_count = %s, \
                  last_updated = %s \
                  WHERE proj_name = %s AND datasource_id = %s'

# grab the project list
cursor.execute(selectProjects, (datasourceID,))
projectList = cursor.fetchall()


for project in projectList:
    projectName = project[0]
    version = ''
    date = ''
    count = ''
    print("parsing:", projectName)

    # grab the index
    cursor.execute(selectIndexes, (datasourceID, projectName))
    homeHtml = cursor.fetchone()[0]

    # find the 3 download facts we need
    soup = BeautifulSoup(homeHtml, 'lxml')
    currentdiv = soup.find(id="current_rating")
    if currentdiv:
        # find downloads table
        table = currentdiv.find('table')
        rows = table.findChildren(['tr'])

        # (1) get current download version
        vcell = rows[0].find('td')
        vvalue = vcell.string.strip()
        print(vvalue)

        # (2) get download date, sample:
        # <span class="smartDate full" title="4/13/2017 3:00:00 AM"
        tcell = rows[1].find('td')
        tvalue = tcell.string.strip()
        print(tvalue)

        # (3) get download count
        dcell = rows[3].find('td')
        dvalue = dcell.string.strip()
        print(dvalue)

        try:
            cursor.execute(updateProjects, (vvalue,
                                            tvalue,
                                            dvalue,
                                            lastUpdated,
                                            projectName,
                                            datasourceID))
            dbconn.commit()
        except:
            print("---error with", projectName)
            dbconn.rollback()

dbconn.close()
