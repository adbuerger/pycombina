all:
	g++ -shared -I/usr/include/python2.7 -I/$(PWD) -lpython2.7 -lm -fPIC -O3 -o bnb_jung.so bnb_jung.cpp
