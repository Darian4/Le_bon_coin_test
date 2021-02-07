#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys


MAP_ERROR_MESSAGE = "map error"
MAP_SUCCESS =   "...xxxxxx...........\n" + \
                "o..xxxxxx.o....o....\n" + \
                "..oxxxxxx....o...oo.\n" + \
                "..oxxxxxx...o.......\n" + \
                "...xxxxxx...........\n" + \
                "o..xxxxxx.......o...\n" + \
                ".....o.o............\n" + \
                "....................\n" + \
                "...o......o....o...o\n" + \
                "o...............o...\n"


class Slot:
    """A slot store all teh useful data of one element of the map"""
    def __init__(self, pos_x, pos_y, char):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.char = char
        self.max_vert = 0
        self.max_square_size = 0


class MapAnalyser:
    def __init__(self, file_path):
        """Check if a file is valid and save its values to analyze it if is"""
        self.map = []
        self.max_square_slot = None

        with open(file_path, "r") as file_data:
            self.line_size = 0
            line = file_data.readline()
            try:
                self.char_ful = line[-2]    # line[-1] is the EOL char
                self.char_obs = line[-3]
                self.char_emp = line[-4]
                nb_line = int(line[:-4])
            except:  # cant get the number of lines
                print(MAP_ERROR_MESSAGE)
                return

            if self.char_emp in [self.char_obs, self.char_ful] or self.char_emp == self.char_ful:  # 2 char are the same
                print(MAP_ERROR_MESSAGE)
                return

            cpt = 0
            while line:
                line = file_data.readline()[:-1]    # the line without the EOL
                cpt += 1
                try:
                    if line:
                        self.add_line(cpt, line)
                except:
                    print(MAP_ERROR_MESSAGE)
                    return

            if cpt != nb_line + 1:  # the number of lines is invalid
                print(MAP_ERROR_MESSAGE)
                return

    def add_line(self, pos_y, line):
        """Add the line to the map with the given Y position"""
        map_line = []
        #  add the line to the map by creating a slot for each char
        for pos_x, char in enumerate(line):
            if char in [self.char_emp, self.char_obs]:
                map_line.append(Slot(pos_x, pos_y, char))
            else:
                raise Exception('unknown char found')

        #  store and check if the size of lines are the same
        if not self.line_size:
            self.line_size = len(line)
        elif self.line_size != len(line):
            raise Exception('different line sizes')
        self.map.append(map_line)

    def search_square(self):
        """search the biggest square for each slot, considering it's the upper left corner"""
        #  count all the empty spaces beneath each slot
        for column in range(self.line_size):
            current = 0
            for line in reversed(self.map):
                slot = line[column]
                if slot.char == self.char_emp:
                    current += 1
                else:
                    current = 0
                slot.max_vert = current

        #  for each slot, evaluate the size of the maximum square assuming the slot is the upper left corner
        #  for that we look for how far each space can expand horizontally without being longer than the maximum
        #  vertical size
        for line in self.map:
            for index, slot in enumerate(line):
                max_vertical = slot.max_vert
                max_horizontal = 1
                for next_index in range(index + 1, self.line_size):
                    next_slot = line[next_index]
                    if next_slot.char == self.char_obs:  # if the next space is an obstacle we stop
                        break

                    #  if the horizontal size is still smaller than the maximum vertical size even
                    #  if we increase the horizontal size by one, we do it and we continue
                    if (max_horizontal + 1 <= max_vertical) and (max_horizontal + 1 <= next_slot.max_vert):
                        max_horizontal += 1
                        max_vertical = min(max_vertical, next_slot.max_vert)
                    else:
                        break
                slot.max_square_size = min(max_vertical, max_horizontal)

                # store the best slot for later
                if not self.max_square_slot or slot.max_square_size > self.max_square_slot.max_square_size:
                    self.max_square_slot = slot

    def print_map(self, attribute="char"):
        """print the content of the whole map for the wanted attribute"""
        for line in self.map:
            line_text = ""
            for slot in line:
                line_text += str(getattr(slot, attribute))
            print(line_text)

    def fill_max_square(self):
        """Fill the map for the biggest square"""
        if not self.max_square_slot:
            return

        for line in self.map:
            for slot in line:
                if self.max_square_slot.pos_x <= slot.pos_x < \
                        self.max_square_slot.pos_x + self.max_square_slot.max_square_size and \
                        self.max_square_slot.pos_y <= slot.pos_y < \
                        self.max_square_slot.pos_y + self.max_square_slot.max_square_size:
                    slot.char = self.char_ful


class TestMapAnalyser:
    def test_parser_1(self, capsys):
        """test getting a bad number of lines"""
        MapAnalyser("test_parser_1")
        out, err = capsys.readouterr()
        assert(out == MAP_ERROR_MESSAGE + "\n")

    def test_parser_2(self, capsys):
        """test getting the same char twice"""
        MapAnalyser("test_parser_2")
        out, err = capsys.readouterr()
        assert(out == MAP_ERROR_MESSAGE + "\n")

    def test_parser_3(self, capsys):
        """test getting an unknown char"""
        MapAnalyser("test_parser_3")
        out, err = capsys.readouterr()
        assert(out == MAP_ERROR_MESSAGE + "\n")

    def test_parser_4(self, capsys):
        """test getting various line sizes"""
        MapAnalyser("test_parser_4")
        out, err = capsys.readouterr()
        assert(out == MAP_ERROR_MESSAGE + "\n")

    def test_parser_5(self, capsys):
        """test getting bad number of lines"""
        MapAnalyser("test_parser_5")
        out, err = capsys.readouterr()
        assert(out == MAP_ERROR_MESSAGE + "\n")

    def test_succes(self, capsys):
        """test getting bad number of lines"""
        map_analyser = MapAnalyser("test_success")
        map_analyser.search_square()
        map_analyser.fill_max_square()
        map_analyser.print_map()
        out, err = capsys.readouterr()
        assert(MAP_SUCCESS == out)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        map_analyser = MapAnalyser(arg)
        map_analyser.search_square()
        map_analyser.fill_max_square()
        map_analyser.print_map()
