#! /bin/bash
[ -z $1 ] && echo "Give a version string" && exit 

rm -rf /tmp/sjbeasts
cp -a . /tmp/sjbeasts-$1
cd /tmp/sjbeasts-$1
rm -rf .xvpics
rm *.pyc
rm *.xcf
cd data
rm -rf .xvpics
rm *.pyc
rm *.xcf
for i in `ls -lgo |grep ^d |awk '{print $7}'`; do
	rm -rf $i/.xvpics
	rm $i/*.pyc
	rm $i/*.xcf
done;

cd /tmp
tar -cv /tmp/sjbeasts-$1 > /tmp/sjbeasts-$1.tar
gzip /tmp/sjbeasts-$1.tar

