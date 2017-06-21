all: cia_bnb.so

cia_bnb.so:
	g++ -shared -I/usr/include/python2.7 -I/$(PWD) -lpython2.7 -lm -fPIC -O3 -o cia_bnb.so cia_bnb.cpp

clean:
	rm -f *.so *.o

test: all
	python test_cia_bnb.py
