PROJ = flatpoints
BASE_DIR = cpp
INC_DIR = include
EXT_DIR = extern
SRC = tests/main.cpp
FLAGS = -std=c++11 -Wall -O2
BIN = $(PROJ).out

build:
	g++ $(FLAGS) -I$(INC_DIR) -I$(EXT_DIR) $(SRC) -o $(BIN)

run: build
	./$(BIN)

clean:
	rm $(BIN)
	rm data/test_header.flatpoints

test: run clean