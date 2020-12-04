from . import forms
from . import models


def selection_valid(selectform):
    """A shortcut function, that returns true, if the SelectionForm is valid and the selection
    given by the user is usable (ergo the timeframe is greater than 0 and a unit was selected) """
    output = False
    if selectform.is_valid() and not selectform.cleaned_data['unit'] == "N" and selectform.cleaned_data['timeframe'] > 0:
        output = True
    return output


def submit_document(docform):
    """A shortcut function, that submits the data from the DocumentForm to the system"""
    doc_name = docform.cleaned_data['document']
    print(str(doc_name))
    doc_save = docform.save()
    id = doc_save.pk
    print(id)


def submit_timeframe(selectform):
    """A shortcut function, that submits the data from the SelectionForm to the system"""
    time_frame = selectform.cleaned_data['timeframe']
    unit = selectform.cleaned_data['unit']
    print(str(time_frame) + str(unit))
    #time_save = selectform.save()
    #id = time_save.pk
    #print(id)