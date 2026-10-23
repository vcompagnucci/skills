####### Variables
BIN_DIR   = bin
OBJ_DIR   = obj
SRC_DIR   = src
LIB_DIR   = lib
CXXOPT    = -O3 -ftree-vectorize -funroll-loops#
CXXFLAGS  =  -std=c++11 -Wall -Wextra # -g # 
INCPATH   = -Isrc
LDFLAGS   = -lpng -ltiff
LIBS      =

ifdef OMP_CLANG
# Apple clang con libomp de Homebrew (2026-10-15): make OMP_CLANG=1 CPATH=/opt/homebrew/include LIBRARY_PATH=/opt/homebrew/lib
CXXFLAGS += -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include
LDFLAGS  += -L/opt/homebrew/opt/libomp/lib -lomp
else ifdef OMP
CXXFLAGS += -fopenmp
LDFLAGS  += -lgomp
else
CXXFLAGS += -Wno-unknown-pragmas
endif

####### Files
# source files without extension:
SRC_FILES    = $(patsubst $(SRC_DIR)/%.cpp,%,$(shell find $(SRC_DIR)/ -name \
			     '*.cpp' -type f))
SRC_FILES   += $(patsubst $(SRC_DIR)/%.c,%,$(shell find $(SRC_DIR)/ -name \
			     '*.c' -type f))
OBJ_FILES    = $(addprefix $(OBJ_DIR)/,$(addsuffix .o, $(SRC_FILES)))

# name of the application:
TARGET       = $(BIN_DIR)/film_grain_rendering_main

####### Build rules
.PHONY: all clean

all: $(TARGET)

$(BIN_DIR)/film_grain_rendering_main: $(OBJ_FILES)
	@echo "===== Link $@ ====="
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(CXXOPT) -o $@ $^ $(LIBS) $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@echo "===== Compile $< ====="
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(CXXOPT) $(INCPATH) -c $< -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "===== Compile $< ====="
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(CXXOPT) $(INCPATH) -c $< -o $@

clean:
	@echo "===== Clean $< ====="
	@rm -rf $(BIN_DIR) $(OBJ_DIR)
