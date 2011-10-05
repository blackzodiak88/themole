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

import themole
import completion
import output
import signal
from readline import get_line_buffer
import builtins
import commands


def sigint_handler(x, y):
    manager.mole.abort_query()

class Manager:
    def __init__(self):
        self.mole = themole.TheMole()
        self.cmd_manager = commands.CommandManager()
        self.completer   = completion.CompletionManager(self.cmd_manager, self.mole)
        self.output      = output.PrettyOutputManager()

    def start(self):
        signal.signal(signal.SIGINT, sigint_handler)
        while True:
            try:
                line = [i for i in input('#> ').strip().split(' ') if len(i) > 0]
                if len(line) != 0:
                    cmd = self.cmd_manager.find(line[0])
                    cmd.execute(self.mole, line[1:] if len(line) > 1 else [], self.output)
            except commands.CommandException as ex:
                print(' Error: ' + ex.message)
                print(' Usage: ' + cmd.usage(line[0]))
            except commands.CmdNotFoundException as ex:
                print(' Error: ' + ex.message)
            except commands.QuietCommandException:
                pass
            except EOFError:
                print('')
                exit(0)

if __name__ == '__main__':
    builtins.manager = Manager()
    manager.start()
