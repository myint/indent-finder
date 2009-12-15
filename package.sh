#!/bin/bash


release_name=indent_finder-`grep -e "VERSION=" indent_finder.py | cut -d"'" -f2 `

rm -rf $release_name
mkdir $release_name

echo '====== Packaging Indent Finder '
rm -f $release_name.zip
rm -f $release_name.tgz
cp -a indent_finder.py setup.py test_*.py test_files $release_name  
cp -a indent_finder.vim LICENSE.txt README.txt $release_name  

cd $release_name
rm -rf CVS
rm -rf .hg
rm -rf hg.diff
rm -rf build
rm -rf dist
rm -rf tests/CVS
rm -rf *.pyc
rm -rf package*
rm -rf .cvsignore
rm -rf .hgignore
rm -rf *.zip
rm -rf *.tgz
rm -rf *.tar.gz
if [ ! $package_windows ] ;
then
    rm -rf *.exe
fi

echo '====== Package content:'
find .
echo '[Press enter]'
read a


echo '====== Generating archive'
cd ..
zip -r $release_name.zip $release_name/*
tar zcvf $release_name.tgz $release_name/* 

echo '====== Archive content:'
unzip -l $release_name.zip
tar tvfz $release_name.tgz
echo '[Press enter]'
read a

echo '====== Cleaning'
rm -rf build dist
rm -rf $release_name
rm -rf *.pyc


