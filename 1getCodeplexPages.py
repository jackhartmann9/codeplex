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
# 1getCodeplexPages.py <datasource_id> <db password>

# purpose:
# grab all the pages for projects stored on Codeplex before it was shut down
################################################################

import sys
import pymysql

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
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
# for each project, grab the following pages:
# --- home page
# --- history page

selectProjectsQuery = 'SELECT proj_name, proj_url FROM cp_projects \
                       WHERE datasource_id = %s \
                       ORDER BY 1'

insertHTMLQuery = 'INSERT INTO cp_projects_indexes (proj_name, \
                                                    datasource_id, \
                                                    home_html, \
                                                    history_html, \
                                                    last_updated) \
                   VALUES (%s, %s, %s, %s, %s)'

cursor.execute(selectProjectsQuery, (datasourceID,))
projectList = cursor.fetchall()

# insert project pages
for project in projectList:
    projectName = project[0]
    projectUrl = project[1]
    print("grabbing", projectName)

    # set up headers
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    try:
        # grab the main page
        req = urllib2.Request(projectUrl, headers=hdr)
        mainhtml = urllib2.urlopen(req).read()

        # grab the history page
        historyUrl = projectUrl + 'wikipage/history'
        req2 = urllib2.Request(historyUrl, headers=hdr)
        historyhtml = urllib2.urlopen(req2).read()

        cursor.execute(insertHTMLQuery, (projectName,
                                         datasourceID,
                                         mainhtml,
                                         historyhtml,
                                         lastUpdated))
        dbconn.commit()
    except pymysql.Error as error:
        print(error)
        dbconn.rollback()
    except:
        print()
dbconn.close()
