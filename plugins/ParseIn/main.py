from __init__ import TextEncoder
from __init__ import TextDecoder
from __init__ import JSONEncoder
from __init__ import CalcInput
from plugin import ReadFile
#from base import BasePlugin
import json

#plugin = BasePlugin
def main():
    in_file = 'C:\\Users\\tart748\Desktop\\apbs.in.txt'
    test = ReadFile(in_file)
    #test.open()
    #test.__init__(in_file)
    test.read_file()
    #print(test.lines(test.read_file()))
    print(test.xform(test.run(test.read_file()), "text"))
    #print(test.xform_data(test.run(test.read_file())))


    #test.testing()
    #test.other()
    #test.run(test.read_file(test.open()))
    #print (test.run)
    #in_file = 'C:\\Users\\tart748\Desktop\\apbs.in.txt'
    #readfile = open(in_file,'r').readlines()
    #inp1 = TextDecoder()
    #print (inp1.decode("This is a string"))
    #print(inp1.tokenize(readfile))
    #inp1.feed(readfile)
    #print (inp1.parse())
    #print (inp1.feed._tokenize)
    #test = TextEncoder()
    #test.encode(inp1.parse())
    #printx = test.encode(inp1.parse())
    #test2 = CalcInput()
    #print (test2.reads)
    #print (printx)

    #print (inp1.parse())

#JSON
    #jsond = JSONEncoder(json.JSONEncoder)
    #print (jsond.default(inp1.parse()))



if __name__ == '__main__':
    main()
