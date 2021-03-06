#!/bin/bash
set -e -x

PROJECT="my_project"
# Delete old project if necessary
if [ -d $PROJECT  ]; then
    rm -rf $PROJECT
fi
# Setup a test project
putup $PROJECT
# Run some common tasks
cd $PROJECT
python setup.py test
python setup.py doctest
python setup.py docs
python setup.py version
python setup.py sdist
python setup.py bdist
# Try updating
cd ..
putup --update $PROJECT
cd $PROJECT
git_diff=`git diff`
test ! -n "$git_diff"
# Try changing the description
cd ..
DESCRIPTION="new_description"
putup --update $PROJECT -d $DESCRIPTION
cd $PROJECT
test "`python setup.py --description`" = $DESCRIPTION
cd ..
putup --force --update $PROJECT -d $DESCRIPTION
cd $PROJECT
test "`python setup.py --description`" = $DESCRIPTION
# Try forcing overwrite
putup --force $PROJECT
# Try running Tox
if [[ "$DISTRIB" == "ubuntu" ]]; then
    cd $PROJECT
    tox -e py27
    cd ..
fi
echo "System test successful!"
