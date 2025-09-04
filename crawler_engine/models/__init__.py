#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JobSpy 數據模型模組
定義系統中使用的各種數據結構和模型
"""

from .search_request import SearchRequest
from .job_data import JobData
from .search_result import SearchResult

__all__ = [
    'SearchRequest',
    'JobData', 
    'SearchResult'
]