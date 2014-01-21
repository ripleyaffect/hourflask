#!/bin/bash

# Resets the database
rm /tmp/hourflask.db 
sqlite3 /tmp/hourflask.db < setup/schema.sql
