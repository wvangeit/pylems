"""
LEMS XML file format parser.

@author: Gautham Ganapathy
@organization: LEMS (http://neuroml.org/lems/, https://github.com/organizations/LEMS)
@contact: gautham@lisphacker.org
"""

import xml.etree.ElementTree as xe

from lems.base import LEMSBase
from lems.errors import ParseError

from lems.model.fundamental import *
from lems.model.component import *


def get_nons_tag_from_node(node):
    tag = node.tag
    bits = tag.split('}')
    if len(bits) == 1:
        return tag
    else:
        return bits[1]

class LEMSXMLNode:
    def __init__(self, pyxmlnode):
        self.tag = get_nons_tag_from_node(pyxmlnode)
        self.ltag = self.tag.lower()

        self.attrib = dict()
        self.lattrib = dict()

        for k in pyxmlnode.attrib:
            self.attrib[k] = pyxmlnode.attrib[k]
            self.lattrib[k.lower()] = pyxmlnode.attrib[k]

        self.children = list()
        for pyxmlchild in pyxmlnode:
            self.children.append(LEMSXMLNode(pyxmlchild))
        
        
class LEMSFileParser(LEMSBase):
    """
    LEMS XML file format parser class.
    """
    
    def __init__(self, model, include_dirs = []):
        """
        Constructor.

        See instance variable documentation for more details on parameters.
        """

        self.model = model
        """ Model instance to be populated from the parsed file.
        @type: lems.model.model.Model """

        self.include_dirs = include_dirs
        """ List of directories to search for included files.
        @type: list(str) """

        self.tag_parse_table = None
        """ Dictionary of xml tags to parse methods
        @type: dict(string -> function) """

        self.valid_children = None
        """ Dictionary mapping each tag to it's list of valid child tags.
        @type: dict(string -> string) """

        self.id_counter = None
        """ Counter generator for generating unique ids.
        @type: generator(int) """
        
        self.init_parser()

    def init_parser(self):
        """
        Initializes the parser
        """

        #self.token_list = None
        #self.prev_token_lists = None

        self.valid_children = dict()
        self.valid_children['lems'] = ['component', 'componenttype',
                                       'target', 'include',
                                       'dimension', 'unit', 'assertion']
        self.valid_children['componenttype'] = ['dynamics',
                                                'child', 'children',
                                                'componentreference',
                                                'exposure', 'eventport',
                                                'fixed', 'link', 'parameter',
                                                'path', 'requirement',
                                                'simulation', 'structure',
                                                'text', 'attachments',
                                                'constant', 'derivedparameter']
        self.valid_children['dynamics'] = ['derivedvariable',
                                           'oncondition', 'onentry',
                                           'onevent', 'onstart',
                                           'statevariable', 'timederivative',
                                           'kineticscheme', 'regime']
        self.valid_children['regime'] = ['derivedvariable',
                                         'oncondition', 'onentry',
                                         'onevent', 'onstart',
                                         'statevariable', 'timederivative',
                                         'kineticscheme', 'transition']
        self.valid_children['oncondition'] = ['eventout', 'stateassignment']
        self.valid_children['onentry'] = ['eventout', 'stateassignment']
        self.valid_children['onevent'] = ['eventout', 'stateassignment']
        self.valid_children['onstart'] = ['eventout', 'stateassignment']
        self.valid_children['structure'] = ['childinstance',
                                            'eventconnection',
                                            'foreach',
                                            'multiinstantiate']
        self.valid_children['simulation'] = ['record', 'run',
                                             'datadisplay', 'datawriter']

        self.tag_parse_table = dict()
        #self.tag_parse_table['assertion'] = self.parse_assertion
        #self.tag_parse_table['attachments'] = self.parse_attachments
        #self.tag_parse_table['child'] = self.parse_child
        #self.tag_parse_table['childinstance'] = self.parse_child_instance
        #self.tag_parse_table['children'] = self.parse_children
        #self.tag_parse_table['component'] = self.parse_component
        #self.tag_parse_table['componentreference'] = self.parse_component_reference
        self.tag_parse_table['componenttype'] = self.parse_component_type
        #self.tag_parse_table['constant'] = self.parse_constant
        #self.tag_parse_table['datadisplay'] = self.parse_data_display
        #self.tag_parse_table['datawriter'] = self.parse_data_writer
        #self.tag_parse_table['derivedparameter'] = self.parse_derived_parameter
        #self.tag_parse_table['derivedvariable'] = self.parse_derived_variable
        self.tag_parse_table['dimension'] = self.parse_dimension
        self.tag_parse_table['dynamics'] = self.parse_dynamics
        #self.tag_parse_table['eventconnection'] = self.parse_event_connection
        #self.tag_parse_table['eventout'] = self.parse_event_out
        #self.tag_parse_table['eventport'] = self.parse_event_port
        self.tag_parse_table['exposure'] = self.parse_exposure
        #self.tag_parse_table['fixed'] = self.parse_fixed
        #self.tag_parse_table['foreach'] = self.parse_foreach
        self.tag_parse_table['include'] = self.parse_include
        #self.tag_parse_table['kineticscheme'] = self.parse_kinetic_scheme
        #self.tag_parse_table['link'] = self.parse_link
        #self.tag_parse_table['multiinstantiate'] = self.parse_multi_instantiate
        #self.tag_parse_table['oncondition'] = self.parse_on_condition
        #self.tag_parse_table['onentry'] = self.parse_on_entry
        #self.tag_parse_table['onevent'] = self.parse_on_event
        #self.tag_parse_table['onstart'] = self.parse_on_start
        self.tag_parse_table['parameter'] = self.parse_parameter
        #self.tag_parse_table['path'] = self.parse_path
        #self.tag_parse_table['record'] = self.parse_record
        #self.tag_parse_table['regime'] = self.parse_regime
        #self.tag_parse_table['requirement'] = self.parse_requirement
        #self.tag_parse_table['run'] = self.parse_run
        #self.tag_parse_table['show'] = self.parse_show
        #self.tag_parse_table['simulation'] = self.parse_simulation
        #self.tag_parse_table['stateassignment'] = self.parse_state_assignment
        #self.tag_parse_table['statevariable'] = self.parse_state_variable
        #self.tag_parse_table['structure'] = self.parse_structure
        self.tag_parse_table['target'] = self.parse_target
        #self.tag_parse_table['text'] = self.parse_text
        #self.tag_parse_table['timederivative'] = self.parse_time_derivative
        #self.tag_parse_table['transition'] = self.parse_transition
        self.tag_parse_table['unit'] = self.parse_unit
        #self.tag_parse_table['with'] = self.parse_with

        self.xml_node_stack = []

        self.current_component_type = None
        self.current_dynamics = None
        
        def counter():
            count = 1
            while True:
                yield count
                count = count + 1

        self.id_counter = counter()

        
    def process_nested_tags(self, node):
        """
        Process child tags.

        @param node: Current node being parsed.
        @type node: xml.etree.Element

        @raise ParseError: Raised when an unexpected nested tag is found.
        """

        for child in node.children:
            self.xml_node_stack = [child] + self.xml_node_stack

            ctagl = child.ltag

            if ctagl in self.tag_parse_table:
                self.tag_parse_table[ctagl](child)
            else:
                raise ParseError("Unrecognized tag '{0}'", ctagl)
                #self.parse_component_by_typename(child, child.tag)

            self.xml_node_stack = self.xml_node_stack[1:]

    def parse(self, xmltext):
        """
        Parse a string containing LEMS XML text.

        @param xmltext: String containing LEMS XML formatted text.
        @type xmltext: str
        """
        
        xml = LEMSXMLNode(xe.XML(xmltext))

        if xml.ltag != 'lems':
            raise ParseError('<Lems> expected as root element')

        self.process_nested_tags(xml)


    def raise_error(self, message, *params, **key_params):
        """
        Raise a parse error.
        """
        
        s = 'Parser error in '

        self.xml_node_stack.reverse()
        if len(self.xml_node_stack) > 1:
            node = self.xml_node_stack[0]
            s += '<{0}'.format(node.tag)
            if 'name' in node.lattrib:
                s += ' name=\"{0}\"'.format(node.lattrib['name'])
            if 'id' in node.lattrib:
                s += ' id=\"{0}\"'.format(node.lattrib['id'])
            s += '>'

        for node in self.xml_node_stack[1:]:
            s += '.<{0}'.format(node.tag)
            if 'name' in node.lattrib:
                s += ' name=\"{0}\"'.format(node.lattrib['name'])
            if 'id' in node.lattrib:
                s += ' id=\"{0}\"'.format(node.lattrib['id'])
            s += '>'

        s += ':\n  ' + message

        raise ParseError(s, *params, **key_params)

        self.xml_node_stack.reverse()


#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################





    def parse_assertion(self, node):
        """
        Parses <Assertion>

        @param node: Node containing the <Assertion> element
        @type node: xml.etree.Element
        """

        print('TODO - <Assertion>')


    def parse_attachments(self, node):
        """
        Parses <Attachments>

        @param node: Node containing the <Attachments> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Attachments can only be made in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('<Attachments> must specify a name for the ' +
                             'attachment.')

        if 'type' in node.lattrib:
            type_ = node.lattrib['type']
        else:
            self.raise_error('<Attachment> must specify a type for the ' +
                             'attachment.')

        self.current_context.add_attachment(name, type_)

    def parse_child(self, node):
        """
        Parses <Child>

        @param node: Node containing the <Child> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Child definitions can only be made in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('<Child> must specify a name for the ' +
                             'reference.')

        if 'type' in node.lattrib:
            type_ = node.lattrib['type']
        else:
            self.raise_error('<Child> must specify a type for the ' +
                             'reference.')

        self.current_context.add_child_def(name, type_)

    def parse_child_instance(self, node):
        """
        Parses <ChildInstance>

        @param node: Node containing the <ChildInstance> element
        @type node: xml.etree.Element
        """

        if self.current_structure == None:
            self.raise_error('Child instantiations can only be made within ' +
                             'a structure definition')

        if 'component' in node.lattrib:
            component = node.lattrib['component']
        else:
            self.raise_error('<ChildInstance> must specify a component '
                             'reference')

        self.current_structure.add_single_child_def(component)

    def parse_children(self, node):
        """
        Parses <Children>

        @param node: Node containing the <Children> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Children definitions can only be made in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('<Children> must specify a name for the ' +
                             'reference.')

        if 'type' in node.lattrib:
            type = node.lattrib['type']
        else:
            self.raise_error('<Children> must specify a type for the ' +
                             'reference.')

        self.current_context.add_children_def(name, type)

    def parse_component_by_typename(self, node, type):
        """
        Parses components defined directly by component name.

        @param node: Node containing the <Component> element
        @type node: xml.etree.Element

        @param type: Type of this component.
        @type type: string

        @raise ParseError: Raised when the component does not have an id.
        """

        raise Exception(("Component initialized using typename "
                         "'{0}' as the XML tag").format(node.tag))

        if self.current_context.context_type == Context.GLOBAL:
            # Global component instatiation
            if 'id' in node.lattrib:
                id_ = node.lattrib['id']
            else:
                self.raise_error('Component must have an id')

            type = node.tag

            component = Component(id_, self.current_context, type, None)

            self.current_context.add_component(component)

        else:
            # Child instantiation

            if 'id' in node.lattrib:
                id_ = node.lattrib['id']
                type = node.tag
            else:
                id_ = node.tag
                if 'type' in node.lattrib:
                    type = node.lattrib['type']
                else:
                    type = '__type_inherited__'

            component = Component(id_, self.current_context, type)

            self.current_context.add_child(component)

        for key in node.attrib:
            if key.lower() not in ['extends', 'id', 'type']:
                param = Parameter(key, '__dimension_inherited__')
                param.set_value(node.attrib[key])
                component.add_parameter(param)

        self.push_context(component.context)
        self.process_nested_tags(node)
        self.pop_context()

    def parse_component(self, node):
        """
        Parses <Component>

        @param node: Node containing the <Component> element
        @type node: xml.etree.Element
        """

        if 'id' in node.lattrib:
            id_ = node.lattrib['id']
        else:
            #self.raise_error('Component must have an id')
            id_ = self.model.make_id()

        if 'type' in node.lattrib:
            type = node.lattrib['type']
        else:
            type = None

        if type == None:
            if 'extends' in node.lattrib:
                extends = node.lattrib['extends']
            else:
                self.raise_error('Component must have a type or must ' +
                                 'extend another component')
        else:
            extends = None

        if 'child' in node.lattrib:
            child = node.lattrib['child']
            id_ = child
        else:
            child = None

        component = Component(id_, self.current_context, type, extends)

        if child:
            self.current_context.add_child(component)
        else:
            self.current_context.add_component(component)

        for key in node.attrib:
            if key.lower() not in ['extends', 'id', 'type', 'child']:
                param = Parameter(key, '__dimension_inherited__')
                param.set_value(node.attrib[key])
                component.add_parameter(param)

        self.push_context(component.context)
        self.process_nested_tags(node)
        self.pop_context()

    def parse_component_reference(self, node):
        """
        Parses <ComponentReference>

        @param node: Node containing the <ComponentTypeRef> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Component references can only be defined in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('<ComponentReference> must specify a name for the ' +
                             'reference.')

        if 'type' in node.lattrib:
            type = node.lattrib['type']
        else:
            self.raise_error('<ComponentReference> must specify a type for the ' +
                             'reference.')

        self.current_context.add_component_ref(name, type)

    def parse_component_type(self, node):
        """
        Parses <ComponentType>

        @param node: Node containing the <ComponentType> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the component type does not have a
        name.
        """

        try:
            name = node.lattrib['name']
        except:
            self.raise_error('<ComponentType> must specify a name')

        if 'extends' in node.lattrib:
            extends = node.lattrib['extends']
        else:
            extends = None

        component_type = ComponentType(name, extends)
        self.model.add_component_type(component_type)

        self.current_component_type = component_type
        self.process_nested_tags(node)
        self.current_component_type = None

    def parse_constant(self, node):
        """
        Parses <Constant>

        @param node: Node containing the <Constant> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the constant does not have a name.
        @raise ParseError: Raised when the constant does not have a
        dimension.
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Constants can only be defined in ' +
                             'a component type')

        try:
            name = node.lattrib['name']
        except:
            self.raise_error('Constant must have a name')

        try:
            dimension = node.lattrib['dimension']
        except:
            dimension = None

        try:
            value = node.lattrib['value']
        except:
            self.raise_error('Constant must have a value')

        constant = Parameter(name, dimension, True, value)

        self.current_context.add_parameter(constant)

    def parse_data_display(self, node):
        """
        Parses <DataDisplay>

        @param node: Node containing the <DataDisplay> element
        @type node: xml.etree.Element
        """

        if self.current_simulation == None:
            self.raise_error('<DataDisplay> must be defined inside a ' +
                             'simulation specification')

        if 'title' in node.lattrib:
            title = node.lattrib['title']
        else:
            self.raise_error('A data display must have a title')

        if 'dataregion' in node.lattrib:
            data_region = node.lattrib['dataregion']
        else:
            data_region = None

        self.current_simulation.add_data_display(title, data_region)

    def parse_data_writer(self, node):
        """
        Parses <DataWriter>

        @param node: Node containing the <DataWriter> element
        @type node: xml.etree.Element
        """

        if self.current_simulation == None:
            self.raise_error('<DataWriter> must be defined inside a ' +
                             'simulation specification')

        if 'path' in node.lattrib:
            path = node.lattrib['path']
        else:
            self.raise_error('A data writer must have a path')

        if 'filename' in node.lattrib:
            file_path = node.lattrib['filename']
        else:
            self.raise_error('A data writer must have a file name')

        self.current_simulation.add_data_writer(path, file_path)

    def parse_derived_parameter(self, node):
        """
        Parses <DerivedParameter>

        @param node: Node containing the <DerivedParameter> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Dynamics must be defined inside a ' +
                             'component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('A derived parameter must have a name')

        if 'dimension' in node.lattrib:
            dimension = node.lattrib['dimension']
        else:
            dimension = None

        if 'value' in node.lattrib:
            value = node.lattrib['value']
        else:
            value = None

        if 'select' in node.lattrib:
            select = node.lattrib['select']
        else:
            select = None

        self.current_context.add_derived_parameter(DerivedParameter(name, dimension,
                                                                    value, select))

    def parse_derived_variable(self, node):
        """
        Parses <DerivedVariable>

        @param node: Node containing the <DerivedVariable> element
        @type node: xml.etree.Element
        """

        if self.current_regime == None:
            self.raise_error('<DerivedVariable> must be defined inside a ' +
                             'dynamics profile or regime')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        elif 'exposure' in node.lattrib:
            name = node.lattrib['exposure']
        else:
            self.raise_error('A derived variable must have a name')

        if 'exposure' in node.lattrib:
            exposure = node.lattrib['exposure']
        else:
            exposure = None

        if 'dimension' in node.lattrib:
            dimension = node.lattrib['dimension']
        else:
            dimension = None

        if 'value' in node.lattrib:
            value = node.lattrib['value']
        else:
            value = None

        if 'select' in node.lattrib:
            select = node.lattrib['select']
        else:
            select = None

        if 'reduce' in node.lattrib:
            reduce = node.lattrib['reduce']
        else:
            reduce = None

        self.current_regime.add_derived_variable(name, exposure, dimension,
                                                 value, select, reduce)

    def parse_dimension(self, node):
        """
        Parses <Dimension>

        @param node: Node containing the <Dimension> element
        @type node: xml.etree.Element

        @raise ParseError: When the name is not a string or if the
        dimension is not a signed integer.
        """

        try:
            name = node.lattrib['name']
        except:
            self.raise_error('<Dimension> must specify a name')

        description = node.lattrib.get('description', '')

        dim = dict()
        for d in ['l', 'm', 't', 'i', 'k', 'c', 'n']:
            dim[d] = int(node.lattrib.get(d, 0))

        self.model.add_dimension(Dimension(name, description, **dim))

    def parse_dynamics(self, node):
        """
        Parses <Dynamics>

        @param node: Node containing the <Behaviour> element
        @type node: xml.etree.Element
        """

        if self.current_component_type == None:
            self.raise_error('Dynamics must be defined inside a component type')

        self.current_dynamics = self.current_component_type.dynamics
        self.process_nested_tags(node)
        self.current_dynamics = None

    def parse_event_out(self, node):
        """
        Parses <EventOut>

        @param node: Node containing the <EventOut> element
        @type node: xml.etree.Element
        """

        if self.current_event_handler == None:
            self.raise_error('<EventOut> must be defined inside an ' +
                             'event handler in a dynamics profile or regime')

        if 'port' in node.lattrib:
            port = node.lattrib['port']
        else:
            self.raise_error('\'port\' attribute not provided for ' +
                             '<StateAssignment>')

        action = EventOut(port)

        self.current_event_handler.add_action(action)

    def parse_event_connection(self, node):
        """
        Parses <EventConnection>

        @param node: Node containing the <EventConnection> element
        @type node: xml.etree.Element
        """

        if self.current_structure == None:
            self.raise_error('<EventConnection> must be defined inside a ' +
                             'structure definition')

        if 'from' in node.lattrib:
            from_ = node.lattrib['from']
        else:
            self.raise_error('\'from\' attribute not provided for ' +
                             '<EventConnection>')

        if 'to' in node.lattrib:
            to = node.lattrib['to']
        else:
            self.raise_error('\'to\' attribute not provided for ' +
                             '<EventConnection>')

        source_port = node.lattrib.get('sourceport', '')
        target_port = node.lattrib.get('targetport', '')
        receiver = node.lattrib.get('receiver', '')
        receiver_container = node.lattrib.get('receivercontainer', '')

        self.current_structure.add_event_connection(from_, to,
                                                    source_port, target_port,
                                                    receiver, receiver_container)

    def parse_event_port(self, node):
        """
        Parses <EventPort>

        @param node: Node containing the <EventPort> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Event ports can only be defined in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error(('<EventPort> must specify a name for the '
                              'event port'))

        if 'direction' in node.lattrib:
            direction = node.lattrib['direction']
        else:
            self.raise_error(('<EventPort> must specify a direction for the '
                              'event port'))

        direction = direction.lower()
        if direction != 'in' and direction != 'out':
            self.raise_error(('Event port direction must be \'in\' '
                              'or \'out\''))

        self.current_context.add_event_port(name, direction)

    def parse_exposure(self, node):
        """
        Parses <Exposure>

        @param node: Node containing the <Exposure> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the exposure name is not
        being defined in the context of a component type.
        """

        if self.current_component_type == None:
            self.raise_error('Exposures must be defined in a component type')

        try:
            name = node.lattrib['name']
        except:
            self.raise_error('<Exposure> must specify a name')

        try:
            dimension = node.lattrib['dimension']
        except:
            self.raise_error("Exposure '{0}' must specify a dimension",
                             name)

        description = node.lattrib.get('description', '')

        self.current_component_type.add_exposure(Exposure(name, dimension, description))

    def parse_fixed(self, node):
        """
        Parses <Fixed>

        @param node: Node containing the <Fixed> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when
        """

        try:
            parameter = node.lattrib['parameter']
        except:
            self.raise_error('Parameter to be fixed must be specified')

        try:
            value = node.lattrib['value']
        except:
            self.raise_error('Value to be fixed must be specified')

        if self.current_context.lookup_parameter(parameter) == None:
            self.current_context.add_parameter(Parameter(
                parameter, '__dimension_inherited__'))
        self.current_context.lookup_parameter(parameter).fix_value(value)

    def parse_foreach(self, node):
        """
        Parses <ForEach>

        @param node: Node containing the <ForEach> element
        @type node: xml.etree.Element
        """

        if self.current_structure == None:
            self.raise_error('<ForEach> can only be made within ' +
                             'a structure definition')

        if 'instances' in node.lattrib:
            target = node.lattrib['instances']
        else:
            self.raise_error('<ForEach> must specify a reference to target'
                             'instances')

        if 'as' in node.lattrib:
            name = node.lattrib['as']
        else:
            self.raise_error('<ForEach> must specify a name for the '
                             'enumerated target instances')

        old_structure = self.current_structure
        self.current_structure = self.current_structure.add_foreach(\
            name, target)

        self.process_nested_tags(node)

        self.current_structure = old_structure

    def parse_include(self, node):
        """
        Parses <Include>

        @param node: Node containing the <Include> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the file to be included is not specified. 
        """

        if 'file' not in node.lattrib:
            self.raise_error('<Include> must specify the file to be included.')

        self.model.include_file(node.lattrib['file'], self.include_dirs)

    def parse_kinetic_scheme(self, node):
        """
        Parses <KineticScheme>

        @param node: Node containing the <KineticScheme> element
        @type node: xml.etree.Element
        """

        if self.current_regime == None:
            self.raise_error('<KineticScheme> must be defined inside a ' +
                             'dynamics profile or regime')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('A name must be provided for <KineticScheme>')

        if 'nodes' in node.lattrib:
            nodes = node.lattrib['nodes']
        else:
            self.raise_error("The 'nodes' must be provided for <KineticScheme>")

        if 'statevariable' in node.lattrib:
            state_variable = node.lattrib['statevariable']
        else:
            self.raise_error("The 'stateVariable' must be provided for <KineticScheme>")

        if 'edges' in node.lattrib:
            edges = node.lattrib['edges']
        else:
            self.raise_error("The 'edges' must be provided for <KineticScheme>")

        if 'edgesource' in node.lattrib:
            edge_source = node.lattrib['edgesource']
        else:
            self.raise_error("The 'edgeSource' must be provided for <KineticScheme>")

        if 'edgetarget' in node.lattrib:
            edge_target = node.lattrib['edgetarget']
        else:
            self.raise_error("The 'edgeTarget' must be provided for <KineticScheme>")

        if 'forwardrate' in node.lattrib:
            forward_rate = node.lattrib['forwardrate']
        else:
            self.raise_error("The 'forwardRate' must be provided for <KineticScheme>")

        if 'reverserate' in node.lattrib:
            reverse_rate = node.lattrib['reverserate']
        else:
            self.raise_error("The 'reverseRate' must be provided for <KineticScheme>")

        self.current_regime.add_kinetic_scheme(name, nodes, state_variable,
                                               edges, edge_source, edge_target,
                                               forward_rate, reverse_rate)

    def parse_link(self, node):
        """
        Parses <Link>

        @param node: Node containing the <Link> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Link variables can only be defined in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('A name must be provided for <Link>')

        if 'type' in node.lattrib:
            type = node.lattrib['type']
        else:
            type = None

        self.current_context.add_link_var(name, type)

    def parse_multi_instantiate(self, node):
        """
        Parses <MultiInstantiate>

        @param node: Node containing the <MultiInstantiate> element
        @type node: xml.etree.Element
        """

        if self.current_structure == None:
            self.raise_error('Child instantiations can only be made within ' +
                             'a structure definition')

        if 'component' in node.lattrib:
            component = node.lattrib['component']
        else:
            self.raise_error('<MultiInstantiate> must specify a component '
                             'reference')

        if 'number' in node.lattrib:
            number = node.lattrib['number']
        else:
            self.raise_error('<MultiInstantiate> must specify a number')

        self.current_structure.add_multi_child_def(component, number)

    def parse_on_condition(self, node):
        """
        Parses <OnCondition>

        @param node: Node containing the <OnCondition> element
        @type node: xml.etree.Element
        """

        if self.current_regime == None:
            self.raise_error('<OnCondition> must be defined inside a ' +
                             'dynamics profile or regime')

        if 'test' in node.lattrib:
            test = node.lattrib['test']
        else:
            self.raise_error('Test expression required for <OnCondition>')

        event_handler = OnCondition(test)

        self.current_event_handler = event_handler
        self.current_regime.add_event_handler(event_handler)

        self.process_nested_tags(node)

        self.current_event_handler = None

    def parse_on_entry(self, node):
        """
        Parses <OnEntry>

        @param node: Node containing the <OnEntry> element
        @type node: xml.etree.Element
        """

        if self.current_regime == None:
            self.raise_error('<OnEntry> must be defined inside a ' +
                             'dynamics profile or regime')

        event_handler = OnEntry()

        self.current_event_handler = event_handler
        self.current_regime.add_event_handler(event_handler)

        self.process_nested_tags(node)

        self.current_event_handler = None

    def parse_on_event(self, node):
        """
        Parses <OnEvent>

        @param node: Node containing the <OnEvent> element
        @type node: xml.etree.Element
        """

        if self.current_regime == None:
            self.raise_error('<OnEvent> must be defined inside a ' +
                             'dynamics profile or regime')

        if 'port' in node.lattrib:
            port = node.lattrib['port']
        else:
            self.raise_error('Port name required for <OnCondition>')

        event_handler = OnEvent(port)

        self.current_event_handler = event_handler
        self.current_regime.add_event_handler(event_handler)

        self.process_nested_tags(node)

        self.current_event_handler = None

    def parse_on_start(self, node):
        """
        Parses <OnStart>

        @param node: Node containing the <OnStart> element
        @type node: xml.etree.Element
        """

        if self.current_regime == None:
            self.raise_error('<OnEvent> must be defined inside a ' +
                             'dynamics profile or regime')

        event_handler = OnStart()

        self.current_event_handler = event_handler
        self.current_regime.add_event_handler(event_handler)

        self.process_nested_tags(node)

        self.current_event_handler = None

    def parse_parameter(self, node):
        """
        Parses <Parameter>

        @param node: Node containing the <Parameter> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the parameter does not have a name.
        @raise ParseError: Raised when the parameter does not have a
        dimension.
        """

        if self.current_component_type == None:
            self.raise_error('Parameters can only be defined in ' +
                             'a component type')

        try:
            name = node.lattrib['name']
        except:
            self.raise_error('<Parameter> must specify a name')

        try:
            dimension = node.lattrib['dimension']
        except:
            self.raise_error("Parameter '{0}' has no dimension",
                             name)

        parameter = Parameter(name, dimension)

        self.current_component_type.add_parameter(parameter)

    def parse_path(self, node):
        """
        Parses <Path>

        @param node: Node containing the <Path> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Path variables can only be defined in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('A name must be provided for <Path>')

        if 'value' in node.lattrib:
            value = node.lattrib['value']
        else:
            value = None

        self.current_context.add_path_var(name, value)

    def parse_record(self, node):
        """
        Parses <Record>

        @param node: Node containing the <Record> element
        @type node: xml.etree.Element
        """

        if self.current_simulation == None:
            self.raise_error('<Record> must be only be used inside a ' +
                             'simulation specification')

        if 'quantity' in node.lattrib:
            quantity = node.lattrib['quantity']
        else:
            self.raise_error('\'quantity\' attribute required for <Record>')

        if 'scale' in node.lattrib:
            scale = node.lattrib['scale']
        else:
            scale = "1"
            #self.raise_error('\'scale\' attribute required for <Record>')

        if 'color' in node.lattrib:
            color  = node.lattrib['color']
        else:
            color = "#000000"
            #self.raise_error('\'color\' attribute required for <Record>')

        self.current_simulation.add_record(quantity, scale, color)

    def parse_regime(self, node):
        """
        Parses <Regime>

        @param node: Node containing the <Behaviour> element
        @type node: xml.etree.Element
        """

        if self.current_dynamics_profile is None:
            self.raise_error('Regime must be defined inside a dynamics profile')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            name = ''

        if 'initial' in node.lattrib:
            initial = (node.lattrib['initial'].strip().lower() == 'true')
        else:
            initial = False

        old_regime = self.current_regime
        self.current_dynamics_profile.add_regime(name, initial)
        self.current_regime = self.current_dynamics_profile.regimes[name]

        self.process_nested_tags(node)

        self.current_regime = old_regime

    def parse_requirement(self, node):
        """
        Parses <Requirement>

        @param node: Node containing the <Requirement> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Requirements can only be defined in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('Name required for <Requirement>')

        if 'dimension' in node.lattrib:
            dimension = node.lattrib['dimension']
        else:
            self.raise_error('Dimension required for <Requirement>')

        self.current_context.add_requirement(name, dimension)

    def parse_run(self, node):
        """
        Parses <Run>

        @param node: Node containing the <Run> element
        @type node: xml.etree.Element
        """

        if self.current_simulation == None:
            self.raise_error('<Run> must be defined inside a ' +
                             'simulation specification')

        if 'component' in node.lattrib:
            component = node.lattrib['component']
        else:
            self.raise_error('<Run> must specify a target component')

        if 'variable' in node.lattrib:
            variable = node.lattrib['variable']
        else:
            self.raise_error('<Run> must specify a state variable')

        if 'increment' in node.lattrib:
            increment = node.lattrib['increment']
        else:
            self.raise_error('<Run> must specify an increment for the ' +
                             'state variable')

        if 'total' in node.lattrib:
            total = node.lattrib['total']
        else:
            self.raise_error('<Run> must specify a final value for the ' +
                             'state variable')

        self.current_simulation.add_run(component, variable, increment, total)

    def parse_show(self, node):
        """
        Parses <Show>

        @param node: Node containing the <Show> element
        @type node: xml.etree.Element
        """

        pass

    def parse_simulation(self, node):
        """
        Parses <Simulation>

        @param node: Node containing the <Simulation> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Simulation must be defined inside a ' +
                             'component type')

        old_simulation = self.current_simulation
        self.current_simulation = self.current_context.simulation

        self.process_nested_tags(node)

        self.current_simulation = old_simulation

    def parse_state_assignment(self, node):
        """
        Parses <StateAssignment>

        @param node: Node containing the <StateAssignment> element
        @type node: xml.etree.Element
        """

        if self.current_event_handler == None:
            self.raise_error('<StateAssignment> must be defined inside an ' +
                             'event handler in a dynamics profile or regime')

        if 'variable' in node.lattrib:
            variable = node.lattrib['variable']
        else:
            self.raise_error('\'variable\' attribute not provided for ' +
                             '<StateAssignment>')

        if 'value' in node.lattrib:
            value = node.lattrib['value']
        else:
            self.raise_error('\'value\' attribute not provided for ' +
                             '<StateAssignment>')

        action = StateAssignment(variable, value)

        self.current_event_handler.add_action(action)


    def parse_state_variable(self, node):
        """
        Parses <StateVariable>

        @param node: Node containing the <StateVariable> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the state variable is not
        being defined in the context of a component type.
        """

        if self.current_regime == None:
            self.raise_error('<StateVariable> must be defined inside a ' +
                             'dynamics profile or regime')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('A state variable must have a name')

        if 'exposure' in node.lattrib:
            exposure = node.lattrib['exposure']
        else:
            exposure = None

        if 'dimension' in node.lattrib:
            dimension = node.lattrib['dimension']
        else:
            self.raise_error('A state variable must have a dimension')

        self.current_regime.add_state_variable(name, exposure, dimension)

    def parse_structure(self, node):
        """
        Parses <Structure>

        @param node: Node containing the <Structure> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Structure must be defined inside a ' +
                             'component type')

        old_structure = self.current_structure
        self.current_structure = self.current_context.structure

        self.process_nested_tags(node)

        self.current_structure = old_structure

    def parse_target(self, node):
        """
        Parses <Target>

        @param node: Node containing the <Target> element
        @type node: xml.etree.Element
        """

        self.model.add_target(node.lattrib['component'])

    def parse_text(self, node):
        """
        Parses <Text>

        @param node: Node containing the <Text> element
        @type node: xml.etree.Element
        """

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Text variables can only be defined in ' +
                             'a component type')

        if 'name' in node.lattrib:
            name = node.lattrib['name']
        else:
            self.raise_error('A name must be provided for <Text>')

        if 'value' in node.lattrib:
            value = node.lattrib['value']
        else:
            value = None

        self.current_context.add_text_var(name, value)

    def parse_time_derivative(self, node):
        """
        Parses <TimeDerivative>

        @param node: Node containing the <TimeDerivative> element
        @type node: xml.etree.Element

        @raise ParseError: Raised when the time derivative is not
        being defined in the context of a component type.
        """

        if self.current_regime == None:
            self.raise_error('<TimeDerivative> must be defined inside a ' +
                             'dynamics profile or regime')

        if self.current_context.context_type != Context.COMPONENT_TYPE:
            self.raise_error('Time derivatives can only be defined in ' +
                             'a component type')

        if 'variable' in node.lattrib:
            name = node.lattrib['variable']
        else:
            self.raise_error('The state variable being differentiated wrt ' +
                             'time must be specified')

        if 'value' in node.lattrib:
            value = node.lattrib['value']
        else:
            self.raise_error('The time derivative expression must be ' +
                             'provided')

        self.current_regime.add_time_derivative(name, value)

    def parse_transition(self, node):
        """
        Parses <Transition>

        @param node: Node containing the <Transition> element
        @type node: xml.etree.Element
        """

        """
        Parses <Transition>

        @param node: Node containing the <Transition> element
        @type node: xml.etree.Element
        """

        if self.current_event_handler == None:
            self.raise_error('<Transition> must be defined inside an ' +
                             'event handler in a dynamics profile or regime')

        if 'regime' in node.lattrib:
            regime = node.lattrib['regime']
        else:
            self.raise_error('\'regime\' attribute not provided for ' +
                             '<Transition>')

        action = Transition(regime)

        self.current_event_handler.add_action(action)

    def parse_unit(self, node):
        """
        Parses <Unit>

        @param node: Node containing the <Unit> element
        @type node: xml.etree.Element

        @raise ParseError: When the name is not a string or the unit
        specfications are incorrect.

        @raise ModelError: When the unit refers to an undefined dimension.
        """

        try:
            symbol = node.lattrib['symbol']
            dimension = node.lattrib['dimension']
        except:
            self.raise_error('Unit must have a symbol and dimension.')

        if 'power' in node.lattrib:
            power = int(node.lattrib['power'])
        else:
            power = 0

        self.model.add_unit(Unit(symbol, dimension, power))

    def parse_with(self, node):
        """
        Parses <With>

        @param node: Node containing the <With> element
        @type node: xml.etree.Element
        """

        if self.current_structure == None:
            self.raise_error('<With> can only be made within ' +
                             'a structure definition')

        if 'instance' in node.lattrib:
            target = node.lattrib['instance']
        else:
            self.raise_error('<With> must specify a reference to target'
                             'instance')

        if 'as' in node.lattrib:
            name = node.lattrib['as']
        else:
            self.raise_error('<With> must specify a name for the '
                             'target instance')

        self.current_structure.add_with(name, target)
