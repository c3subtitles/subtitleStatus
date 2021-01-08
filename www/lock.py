#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# lock.py
#
# This file provides some global locks for e.g. amara API functions
# It is mainly used in models.py and statistics_helper.py
#
#==============================================================================

from django_pglocks import advisory_lock


# Lock for access to the amara API
amara_api_lock = "amara_api_lock"

# Lock for access to the Kanboard API
kanboard_api_lock = "kanboard_api_lock"