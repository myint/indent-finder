#!/bin/bash

package_windows='1'

orig_pwd=$PWD
release_name='indent-finder-1_1'

if [ $package_windows ];
then
    rm -f $release_name.zip
    echo 'Packaging for windows'
    python.exe setup.py bdist_wininst
    cp -f dist/* .
else
    echo 'Packaging for unix'
    rm -f $release_name.tgz
fi
echo '[Press enter]'
read a

dist=/tmp/indent_finder
rm -rf $dist
mkdir $dist

cp -a * $dist

cd $dist
rm -rf CVS
rm -rf build
rm -rf dist
rm -rf tests/CVS
rm -rf *.pyc
rm -rf package*
rm -rf .cvsignore
rm -rf *.zip
rm -rf *.tgz
rm -rf *.tar.gz
if [ ! $package_windows ] ;
then
    rm -rf *.exe
fi

echo 'Package content:'
find $dist
echo '[Press enter]'
read a


echo 'Generating archive'
cd ..
if [ ! $package_windows ] ;
then
    tar zcvf $orig_pwd/$release_name.tgz indent_finder/* 
else
    zip -r $orig_pwd/$release_name.zip indent_finder/*
fi

cd $orig_pwd
echo 'Package content:'
if [ ! $package_windows ] ;
then
    tar tvfz $release_name.tgz
else
    unzip -l $release_name.zip
fi
echo '[Press enter]'
read a
