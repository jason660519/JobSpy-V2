#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage module for crawler engine.

Provides storage backends for different data storage needs.
"""

from .minio_client import MinIOClient

__all__ = ['MinIOClient']