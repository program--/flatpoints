PROJ = flatpoints
INC_DIR = include
SRC = tests/main.cpp

FLAGS = -std=c++11 -Wall -O2

EXE = $(PROJ).out

build:
	g++ $(FLAGS) -I$(INC_DIR) $(SRC) -o $(EXE)

run: build
	./$(EXE)

clean:
	rm $(EXE)
	rm data/test_header.flatpoints

test: run clean