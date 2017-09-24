all: cia.so

cia.so:
	g++ -std=c++11 -shared -I/usr/include/python2.7 -I/$(PWD) -lpython2.7 \
	    -lm -fPIC -O3 -o cia.so cia.cpp

clean:
	rm -f *.so *.o

test: all
	python test_cia.py
