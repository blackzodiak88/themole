#!/usr/bin/python3
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#       
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#       
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Developed by: Nasel(http://www.nasel.com.ar)
# 
# Authors:
# Santiago Alessandri
# Matías Fontanini
# Gastón Traberg

import readline

class CompletionManager:
    def __init__(self, manager, mole):
        self.manager = manager
        self.mole    = mole
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
    
    def completer(self, text, state):
        if text == readline.get_line_buffer():
            # means it's the first word on buffer
            return self.generate_commands(text, state)
        else:
            # not the first word on buffer, may be a parameter
            return self.generate_parameters(text, state)
            
    def generate_parameters(self, text, state):
        if state == 0:
            self.available = []
            self.current = 0
            try:
                line = readline.get_line_buffer().split(' ')
                cmd = self.manager.find(line[0])
            except:
                return 0
            current_params = line[1:-1] if len(line) > 2 else []
            if ',' in text:
                text = text.split(',')[-1]
            for i in cmd.parameters(self.mole, current_params):
                if i[:len(text)] == text:
                    self.available.append(i)
            if len(self.available) == 1:
                text = self.available[0]
                self.available = []
                self.current = len(self.available)
                return text + cmd.parameter_separator(current_params)
        return self.get_completion(text, state)
    
    def generate_commands(self, text, state):
        if state == 0:
            self.available = []
            self.current = 0
            for i in self.manager.commands():
                if i[0:len(text)] == text:
                    self.available.append(i)
            if len(self.available) == 1 and self.available[0] == text:
                self.available = []
                self.current = len(self.available)
                return text + ' '
        return self.get_completion(text, state)
    
    def get_completion(self, text, state):
        if self.current == len(self.available):
            return 0
        else:
            tmp = self.available[self.current]
            self.current += 1
            return tmp + ' '
