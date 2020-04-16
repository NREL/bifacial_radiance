CC = g++
CFLAGS = -D_XOPEN_SOURCE
INCLUDES = -lm
TARGET = gencumulativesky
SOURCES = *.cpp 

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) $(INCLUDES)  -o $(TARGET)

.PHONY : clean

clean:
	rm -f $(TARGET) *.o


