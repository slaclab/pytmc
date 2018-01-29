'''
tmc_render.py

This file contains the tools for recursively exploring the TwinCAT program
structure, parsing relevant pragmas and rendering the resulting EPICS db file.
'''
import logging
logger = logging.getLogger(__name__)
from jinja2 import Environment, PackageLoader, select_autoescape
import re
import versioneer
import textwrap

class SingleRecordData:
    '''
    Data structre for packaging all the information required to render an epics
    record.

    Note
    ----
    The parameters for the constructor are for setting the attributes of this
    class. 
    
    Parameters
    ----------
    pv : str

    rec_type : str

    fields : dict

    comment : str
    
    Attributes
    ----------
    pv : str
        The full PV for the record

    rec_type : str
        Code for record type (e.g. 'ai','bo', etc.)

    fields : dict
        Specifications for each field type and their settings.

    comment : str
        An additional string to be printed above the record in the db file.
    '''
    def __init__(self, pv=None, rec_type=None, fields=None, comment=None):
        self.pv = pv 
        self.rec_type = rec_type
        self.fields = fields
        self.comment = comment

    def add(self, pv_extra):
        '''
        Append an extension term onto the current base. This allows a PV to be
        be constructed in multiple stages. This class could start with a PV of
        'GDET:FEE1' and could use .add('241') and again use .add('ENRC') to
        produce a final PV of 'GDET:FEE1:241:ENRC'.

        Parameters
        ----------
        pv_extra : str
            This is the new term to be appended to the tail end of the existing
            PV. Leading/trailing spaces and colons are scrubbed from pv_extra.
            A colon is used to adjoin the existing PV and the new addition.
        '''
        pv_extra = pv_extra.strip(" :")
        self.pv = self.pv + ":" + pv_extra

    @property
    def check_pv(self):
        return True 

    @property
    def check_rec_type(self):
        return True

    @property
    def check_fields(self):
        return True

    @property
    def check(self):
        '''
        Collection of funcitons to evaluate whether the data in this object
        would make a safe record

        Note
        ----
        Implementation not complete.

        Returns
        -------
        bool
            True if the data is deemed safe through existing checks.  
        '''
        return check_pv and check_rec_type and check_fields


class DbRenderAgent:
    '''
    DbRenderAgent provides convenient tools for rendering the final records
    file.

    Parameters
    ----------
    master_list : list
        list of :class:`~pytmc.SingleRecordData` instances specifying all
        records to be made. This parameter can be accessed later. 

    loader : tuple
        Specify package location of jinja templates. Names in the package are
        speperated by tuple entries instead of periods like normal python
        packages. Uses Jinja2's PackageLoader. 
    
    template : str
        name of the template to be used 
    
    Attributes
    ----------
    master_list : list
        list of :class:`~pytmc.SingleRecordData` instances specifying all
        records to be made.


    '''
    def __init__(self, master_list=None, loader=("pytmc","templates"),
                template="EPICS_record_template.db"):
        if master_list == None:
            master_list = []
        self.master_list = master_list
        self.jinja_env = Environment(
            loader = PackageLoader(*loader),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.template = self.jinja_env.get_template(template)

    def render(self):
        '''
        Generate the rendered document

        Returns
        -------
        str
            Epics record document as a string
        '''
        return self.template.render(
            header = self.header,
            master_list = self.master_list
        )

    @property
    def header(self):
        '''
        Generate and return the message to be placed at the top of generated
        files. Includes information such as pytmc verison

        Returns
        -------
        str
            formatted header message
        '''
        message = '''\
        Epics Record file automatically generated using Pytmc

            pytmc version: {version}'''
        message = message.format(
            version=str(versioneer.get_version())
        )
        message = textwrap.dedent(message)
        message = textwrap.indent(message,"# ",lambda line: True)
        return message


class TmcExplorer:
    def __init__(self, tmc):
        self.tmc = tmc
        self.tmc.isolate_all()
        self.all_records = []


    def exp_DataType(self, dtype):
        raise NotImplementedError

    def exp_Symbols(self):
        raise NotImplementedError

    def make_record(self, target):
        raise NotImplementedError
    
    def make_SubItem_record(self, target):
        raise NotImplementedError
    
    def make_Symbol_record(self, target):
        raise NotImplementedError

    def generate_ads_connection(self, target):
        raise NotImplementedError
