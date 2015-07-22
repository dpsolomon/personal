#!/usr/bin/env python
from copy import deepcopy
import xml.etree.ElementTree as ET
import sys


def dexacro(line):
    '''
    Remove/reformat xacro commands (e.g. $(arg), $(find)) from a line
    '''
    if not line:
        return line
    while line.count('$'):
        #Get keyword associated with script
        idx1 = line.find('$(')
        line = line.replace('$(', ' ', 1)
        idx2 = line.find(')', idx1)
        key, subject = line[idx1:idx2].split() #subject does not include trailing ')'
        if key == 'find':
            line = line[:idx1] + subject + line[idx2+1:]
        else:
            line = line[:idx1] + '{' + subject + '}' + line[idx2+1:]
    return line

def condition_str(conditions):
    return ' & '.join([dexacro(condition) for condition in conditions])


class ArgBlock:
    def __init__(self):
        self.conditions = []
        self.name = str()
        self.value = str()
    def __repr__(self, show_conditions = True):
        conditions = condition_str(self.conditions)
        name = dexacro(self.name)
        value = dexacro(self.value)
        
        rep = str()
        tab = str()
        if show_conditions and conditions:
            rep = 'if ' + conditions + ':\n'
            tab = '  '
        if value:
            if value[0] == '(':
                rep += tab + '%s (= %s)' % (name, value[1:-1])
            else:
                rep += tab + '%s = %s' % (name, value)
        else:
            rep += tab + '%s' % (name)
        return rep
    
class ParamBlock:
    def __init__(self):
        self.conditions = []
        self.ns = str()
        self.name = str()
        self.value = str()
    def __repr__(self, show_conditions = True):
        conditions = condition_str(self.conditions)
        ns = dexacro(self.ns)
        name = dexacro(self.name)
        value = dexacro(self.value)
        
        rep = str()
        tab = str()
        if show_conditions and conditions:
            rep = 'if ' + conditions + ':\n'
            tab = '  '
        rep += tab + '%s%s = %s' % (ns, name, value)
        return rep

class NodeBlock:
    def __init__(self):
        self.conditions = []
        self.ns = str()
        self.name = str()
        self.pkg = str()
        self.type = str()
    def __repr__(self, show_conditions = True):
        conditions = condition_str(self.conditions)
        ns = dexacro(self.ns)
        name = dexacro(self.name)
        pkg = dexacro(self.pkg)
        node_type = dexacro(self.type)
        
        rep = str()
        tab = str()
        if show_conditions and conditions:
            rep = 'if ' + conditions + ':\n'
            tab = '  '
        rep += tab + '%s%s: %s/%s' % (ns, name, pkg, node_type)
        return rep
    
class IncludeBlock:
    def __init__(self):
        self.conditions = []
        self.ns = str()
        self.file = str()
        self.args = []
    def __repr__(self, show_conditions = True):
        conditions = condition_str(self.conditions)
        ns = dexacro(self.ns)
        filename = dexacro(self.file)
        args = [dexacro(str(arg)) for arg in self.args]
        
        rep = str()
        tab = str()
        if show_conditions and conditions:
            rep = 'if ' + conditions + ':\n'
            tab = '  '
        rep += tab + '%s' % (filename)
        for arg in args:
            rep += '\n' + tab + '  ' + arg
        return rep
    
    
class LaunchFileRepresentation:
    def __init__(self, filename):
        self.filename = filename
        self.args = []
        self.params = []
        self.nodes = []
        self.includes = []
        
    def __repr__(self):
        print '\n' + '- '*25
        print self.filename
        tab = '  '

        # Collect args
        rep = '\nargs:\n\n'
        args = {}
        for arg in self.args:
            key = condition_str(arg.conditions)
            val = arg.__repr__(False)
            if key in args:
                args[key].append(val)
            else:
                args[key] = [val]
        for condition, vals in args.items():
            if condition:
                #print tab + 'if ' + condition
                rep += 'if ' + condition + '\n'
                for arg in vals:
                    #print tab + tab + arg
                    rep += tab + arg + '\n'
            else:
                for arg in vals:
                    #print tab + arg
                    rep += arg + '\n'
        #    rep += tab + condition + ':\n'
        #   for item in arg:
        #        rep += tab + '  ' + item + '\n'
                
        #for arg in self.args:
        #    rep += tab + str(arg).replace('\n', '\n'+tab) + '\n'
        rep += '\nparams:\n\n'
        for param in self.params:
            #rep += str(param).replace('\n', '\n'+tab) + '\n'
            rep += str(param).replace('\n', '\n') + '\n'
        rep += '\nnodes:\n\n'
        for node in self.nodes:
            #rep += str(node).replace('\n', '\n'+tab) + '\n'
            rep += str(node).replace('\n', '\n') + '\n'
        rep += '\nincludes:\n\n'
        for include in self.includes:
            #rep += str(include).replace('\n', '\n'+tab) + '\n'
            rep += str(include).replace('\n', '\n') + '\n'
        return rep
        
    def parse_tree(self, tree):
        root = tree.getroot()
        if root.tag != 'launch':
            raise Exception('root does not contain \'launch\' tag (%s)' % (root.tag))
        for child in root:
            self.parse_element(child)
            
    def parse_element(self, element, conditions = [], ns = str()):
        # Collect conditional
        conditions2 = deepcopy(conditions)
        if element.get('if'):
            conditions2.append(element.get('if'))
        if element.get('unless'):
            conditions2.append('!' + element.get('unless'))
#        if element.get('ns'):
#            ns += element.get('ns') + '/'
        
        # Collect blocks
        block = None
        if element.tag == 'arg':
            block = self.parse_arg(element, conditions2)
            self.args.append(block)
        elif element.tag == 'param':
            block = self.parse_param(element, conditions2, ns)
            self.params.append(block)
        elif element.tag == 'rosparam':
            block = self.parse_rosparam(element, conditions2, ns)
            self.params.append(block)
        elif element.tag == 'node':
            block = self.parse_node(element, conditions2, ns)
            self.nodes.append(block)
        elif element.tag == 'include':
            block = self.parse_include(element, conditions2, ns)
            self.includes.append(block)
        
        if element.tag == 'group':
            if element.get('ns'):
                ns += element.get('ns') + '/'
            for child in element:
                self.parse_element(child, conditions2, ns)
    
    # Parsers for element types
    def parse_arg(self, element, conditions = []):
        block = ArgBlock()
        block.conditions.extend(conditions)
        block.name = element.get('name')
        if element.get('value'):
            block.value = element.get('value')
        elif element.get('default'):
            block.value = '(' + element.get('default') + ')'
        return block
        
    def parse_include(self, element, conditions = [], ns = str()):
        block = IncludeBlock()
        block.conditions.extend(conditions)
        block.ns = ns
        if element.get('ns'):
            block.ns += element.get('ns') + '/'
        block.file = element.get('file')
        for arg in element:
            block.args.append(self.parse_arg(arg))
        return block
        
    def parse_param(self, element, conditions = [], ns = str()):
        block = ParamBlock()
        block.conditions.extend(conditions)
        block.ns = ns
        block.name = element.get('name')
        if element.get('value'):
            block.value = element.get('value')
        elif element.get('textfile') or element.get('binfile'):
            block.value = element.get('textfile') or element.get('binfile')
        elif element.get('command'):
            block.value = element.get('command')
        return block
        
    def parse_rosparam(self, element, conditions = [], ns = str()):
        block = ParamBlock()
        block.conditions.extend(conditions)
        block.ns = ns
        if element.get('ns'):
            block.ns += element.get('ns') + '/'
        if element.get('file'):
            block.value = element.get('file')
            if element.get('command'):
                block.name = '(' + element.get('command') + ')'
            else:
                block.name = '(load)'
        elif element.get('param'):
            block.name = element.get('param')
            block.value = element.text
        return block
                
    def parse_node(self, element, conditions = [], ns = str()):
        block = NodeBlock()
        block.conditions.extend(conditions)
        block.ns = ns
        if element.get('ns'):
            block.ns += element.get('ns') + '/'
        if element.get('name'):
            block.name = element.get('name')
        block.pkg = element.get('pkg')
        block.type = element.get('type')
        
        if block.name:
            child_ns = block.name + '/' + block.ns
        for child in element:
            self.parse_element(child, conditions, child_ns)
        return block


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: roslaunch_parser.py path/to/launch_file.launch'
        
    filename = sys.argv[1]
    try:
        tree = ET.parse(filename)
    except IOError:
        print 'Could not open file \'%s\'' % filename
        sys.exit(1)
     
    '''
    root = tree.getroot()
    if root.tag != 'launch':
        raise Exception('root does not contain \'launch\' tag (%s)' % (root.tag))
        
    for child in root:
        parse_element(child)
    '''
    launch_file = LaunchFileRepresentation(filename)
    launch_file.parse_tree(tree)
    print launch_file
    
