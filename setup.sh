#!/bin/bash

# This script sets up the sqlite database for use
# It assumes that you have sqlite3 installed

if [ ! -f /tmp/hourflask.db ]; then
	sqlite3 /tmp/hourflask.db < setup/schema.sql
fi