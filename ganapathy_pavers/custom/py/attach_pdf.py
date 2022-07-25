import frappe

from frappe import _
from frappe import publish_progress
from frappe.core.doctype.file.file import create_new_folder
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def attach_pdf(doctype, doc, show_progress=0):
    doc=frappe.get_doc(doctype, doc)
    fallback_language = frappe.db.get_single_value("System Settings", "language") or "en"
    args = {
        "doctype": doc.doctype,
        "name": doc.name,
        "print_format": doc.print or None,
        "title": doc.get_title(),
        "lang": getattr(doc, "language", fallback_language),
        "show_progress": show_progress
    }

    enqueue(args)
    
    

def enqueue(args):
    """Add method `execute` with given args to the queue."""
    frappe.enqueue(method=execute, queue='long',
                   timeout=30, is_async=True, **args)


def execute(doctype, name, title, print_format, lang=None, show_progress=True):
    """
    Queue calls this method, when it's ready.
    1. Create necessary folders
    2. Get raw PDF data
    3. Save PDF file and attach it to the document
    """
    progress = frappe._dict(title=_("Creating PDF ..."), percent=0, doctype=doctype, docname=name)

    if lang:
        frappe.local.lang = lang

    if show_progress:
        publish_progress(**progress)

    doctype_folder = create_folder(_(doctype), "Home")
    title_folder = create_folder(title, doctype_folder)

    if show_progress:
        progress.percent = 33
        publish_progress(**progress)

    pdf_data = get_pdf_data(doctype, name, print_format)

    if show_progress:
        progress.percent = 66
        publish_progress(**progress)

    save_and_attach(pdf_data, doctype, name, title_folder)

    if show_progress:
        progress.percent = 100
        publish_progress(**progress)


def create_folder(folder, parent):
    """Make sure the folder exists and return it's name."""
    new_folder_name = "/".join([parent, folder])
    
    if not frappe.db.exists("File", new_folder_name):
        create_new_folder(folder, parent)
    
    return new_folder_name


def get_pdf_data(doctype, name, print_format):
    """Document -> HTML -> PDF."""
    html = frappe.get_print(doctype, name, print_format=print_format)
    return frappe.utils.pdf.get_pdf(html)


def save_and_attach(content, to_doctype, to_name, folder):
    """
    Save content to disk and create a File document.
    File document is linked to another document.
    """
    file_name = "{}.pdf".format(to_name.replace(" ", "-").replace("/", "-"))
    file=save_file(file_name, content, to_doctype,
              to_name, folder=folder, is_private=0)

    doc=frappe.get_doc(to_doctype, to_name)
    doc.update({
        'print_link': file.file_url,
        'ts_file' : file.file_name
    })
    doc.submit()
    frappe.db.commit()