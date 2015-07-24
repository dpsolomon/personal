#!/usr/bin/env python
from copy import deepcopy
import xml.etree.ElementTree as ET
import sys
try:
    import rospkg
except ImportError:
    pass


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

def condense(text):
    max_len = 90
    lines = text.split('\n')
    rep = ''
    for line in lines:
        if len(line) > max_len:
            space_count = map(str.isspace, line).index(False) # Count number of spaces preceeding line
            rep += line[0:max_len] + '\n'
            for ii in range(1,int(round(len(line)/float(max_len)+0.5))+1):
                rep += ' '*space_count + line[ii*max_len:(ii+1)*max_len] + '\n'
        elif False in map(str.isspace, line):
            rep += line + ' '*(max_len-len(line)) + '\n'
    return rep
    
def graphviz_format(text):
    return text.replace('\n', '\\l').replace('{', '\{').replace('}', '\}').replace('"', "'")

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
            tab = '    '
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
            tab = '    '
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
            tab = '    '
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
            tab = '    '
        rep += tab + '%s' % (filename)
        for arg in args:
            rep += '\n' + tab + '  ' + arg
        return rep
    
    
class LaunchFileRepresentation:
    def __init__(self, title):
        self.title = title
        self.args = []
        self.params = []
        self.nodes = []
        self.includes = []
        
    def __repr__(self):
        rep = '\n' + '- '*25 + '\n' + self.title + '\n'
        tab = '  '

        # Collect args
        rep += '\nargs:\n\n'
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
                rep += 'if ' + condition + '\n'
                for arg in vals:
                    rep += tab + arg + '\n'
            else:
                for arg in vals:
                    rep += arg + '\n'

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
        
    def graphviz(self):
        tab = '  '
        
        # Collect args
        rep_args = ''
        args = {} # Mapping of conditions to arguments
        for arg in self.args:
            key = condition_str(arg.conditions)
            val = arg.__repr__(False).replace('\n', '\\n') #TODO need this?
            if key in args:
                args[key].append(val)
            else:
                args[key] = [val]
        for condition, vals in args.items():
            if condition:
                rep_args += graphviz_format(condense('if ' + condition))
                for arg in vals:
                    rep_args += graphviz_format(condense(tab + arg))
            else:
                for arg in vals:
                    rep_args += graphviz_format(condense(arg))

        # Create representations for params, nodes, includes
        rep_params = ''
        for param in self.params:
            rep_params += graphviz_format(condense(str(param)))
        rep_nodes = ''
        for node in self.nodes:
            rep_nodes += graphviz_format(condense(str(node)))
        rep_includes = ''
        for include in self.includes:
            rep_includes += graphviz_format(condense(str(include)))
            
        rep = '"' + graphviz_format(self.title) + '" [shape=record, label="{' + graphviz_format(self.title)
        if len(rep_args) > 0:
            rep += '|{args\l|' + rep_args + '}'
        if len(rep_params) > 0:
            rep += '|{params\l|' + rep_params + '}'
        if len(rep_nodes) > 0:
            rep += '|{nodes\l|' + rep_nodes + '}'
        if len(rep_includes) > 0:
            rep += '|{includes\l|' + rep_includes + '}'
        rep += '}"];\n'
        
        for include in self.includes:
            rep += '"' + graphviz_format(self.title) + '" -> "' + graphviz_format(dexacro(include.file)) + '";\n'
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
        
class NodeLaunchFile:
    def __init__(self, title):
        self.title = title
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)
        
    def add_children(self, children):
        for child in children:
            self.add_child(child)
            
    def __repr__(self, tab=''):
        rep = ''
        rep += tab + self.title + '[shape=box]' + ';\n'
        for child in self.children:
            rep += tab + self.title + ' -> ' + child + ';\n'
        return rep

def show_help():
    print ('Usage: roslaunch_parser.py [options] path/to/launch_file.launch\n' +
           '  options:\n' +
           '    -h, --help          : Show this message and quit.\n' +
           '    -o filename         : Output for result (default: screen). Specify filename here.\n' +
           '    -a, -c              : Crawl all files (default: just process given file).\n'
           '    -g filename         : Create a graphviz file. Specify filename here.\n'
           '    -v variable value   : Replaces roslaunch variable with given value.\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Minimal usage: roslaunch_parser.py path/to/launch_file.launch; roslaunch_parser.py -h for more info.'
        sys.exit(1)

    # Parse all arguements into variables        
    crawl = False
    output_file = ''
    graphviz_file = ''
    unprocessed_files = []
    var_map = {}
    
    for ii in range(1,len(sys.argv)-1):
        arg = sys.argv[ii]
        if arg in ['-h', '--help']:
            show_help()
            sys.exit(0)
        elif arg in ['-o']:
            if sys.argv[ii+1][0].isalpha():
                output_file = sys.argv[ii+1]
            else:
                print '-o followed by non-alpha character. Ignoring option.'
        elif arg in ['-a', '-c'] and 'rospkg' in sys.modules:
            # if rospkg not on this system, cannot crawl by package name
            crawl = True
            rospack = rospkg.RosPack()
        elif arg in ['-g']:
            if sys.argv[ii+1][0].isalpha():
                graphviz_file = sys.argv[ii+1]
            else:
                print '-g followed by non-alpha character. Ignoring option.'
        elif arg in ['-v']:
            if sys.argv[ii+1][0].isalpha() and sys.argv[ii+2][0].isalpha():
                var_map[sys.argv[ii+1]] = sys.argv[ii+2]
            else:
                print '-v followed by non-alpha character. Ignoring option.'
            
            
    unprocessed_files.append(sys.argv[-1])
    
    # If output is set, open a file for writing
    if len(output_file) > 0:
        try:
            output = open(output_file, 'w')
        except IOError:
            print 'Couldn\'t open \'%s\' for writing output. Outputting to screen.' % (output_file)
            output_file = ''
    
    # Start parsing
    processed_files = [] # Filename added to this list when it is processed (to check for repetition).
    launch_nodes = []    # For graphviz file
    while len(unprocessed_files) > 0:
    
        # Don't reprocess files
        while unprocessed_files[0] in processed_files:
            del unprocessed_files[0]

        # Set filename, delete from unprocessed_files list            
        filename = unprocessed_files[0]
        del unprocessed_files[0]
        processed_files.append(filename)
        
        # Check if filename is relative to ros package
        lfr_title = filename # Title of LaunchFileRepresentation (may be different than filename).
        for key in sorted(var_map):
            filename = filename.replace('{'+key+'}', var_map[key])
            
        if 'rospkg' in sys.modules:
            try:
                package, local_file = filename.split('/', 1)
                filename = rospack.get_path(package) + '/' + local_file
            except (rospkg.common.ResourceNotFound, ValueError):
                pass
                
        
        # Create an element-tree from xml
        try:
            tree = ET.parse(filename)
        except (IOError, TypeError):
            print 'Could not open or parse file \'%s\'' % (filename)
            launch_file = LaunchFileRepresentation(lfr_title)
            launch_nodes.append(launch_file)
            continue
        
        # Create a LaunchFileRepresentation of xml tree.
        launch_file = LaunchFileRepresentation(lfr_title)
        launch_file.parse_tree(tree)
                
        # Write text-representation of launch file to screen or output file.
        if len(output_file) > 0:
            try:
                output.write(str(launch_file))
            except IOError:
                print 'Problem writing to \'%s\'.' % (output_file)
        else:
            print launch_file
        
        # If selected to crawl all includes, pass includes into unprocessed_files list.
        if crawl:
            #node = NodeLaunchFile('"' + launch_file.title + '"')
            for include in launch_file.includes:
            #    node.add_child('"' + dexacro(include.file) + '"')
                unprocessed_files.append(dexacro(include.file))
            #launch_nodes.append(node)
            launch_nodes.append(launch_file)
                
    # Write graphviz file
    if len(graphviz_file) > 0:
        with open(graphviz_file, 'w') as graphviz:
            graphviz.write('\ndigraph launch_nodes {\nnodesep="0.1";\nranksep=0.1;\n')
            for node in launch_nodes:
                graphviz.write(node.graphviz())
            graphviz.write('}\n')
    
    # Close output file
    if len(output_file) > 0:
        output.close()
        
        
