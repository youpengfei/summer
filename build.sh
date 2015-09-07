#!/usr/bin/env bash
source ~/.bash_profile
mvn -U clean package -Dmaven.test.skip=true -s gpc/settings.xml -f gpc >> build.log