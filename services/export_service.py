from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExportService:
    @staticmethod
    def _set_cell_background(cell, fill):
        """Set cell background color"""
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), fill)
        cell._element.get_or_add_tcPr().append(shading_elm)

    @staticmethod
    def _add_table_to_document(doc, title, columns, rows):
        """Add a table to the document with proper formatting"""
        doc.add_heading(title, level=2)
        
        table = doc.add_table(rows=1, cols=len(columns))
        table.style = 'Light Grid Accent 1'
        
        # Add header row
        header_cells = table.rows[0].cells
        for i, col in enumerate(columns):
            header_cells[i].text = col
            # Style header
            for paragraph in header_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ExportService._set_cell_background(header_cells[i], '0070C0')
        
        # Add data rows
        for row_data in rows:
            row_cells = table.add_row().cells
            for i, value in enumerate(row_data):
                row_cells[i].text = str(value)
                # Align right for numeric columns
                for paragraph in row_cells[i].paragraphs:
                    if i > 0 and isinstance(value, (int, float)):
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        doc.add_paragraph()  # Add spacing

    @staticmethod
    def export_financial_summary(summary_data, metrics):
        """Export Financial Summary table to Word document"""
        try:
            doc = Document()
            
            # Add title and metadata
            title = doc.add_heading('Financial Summary Report', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_paragraph()
            
            # Add metrics summary
            doc.add_heading('Key Metrics', level=1)
            metrics_table = doc.add_table(rows=1, cols=2)
            metrics_table.style = 'Light Grid Accent 1'
            
            header_cells = metrics_table.rows[0].cells
            header_cells[0].text = 'Metric'
            header_cells[1].text = 'Value'
            
            for key, value in metrics.items():
                row_cells = metrics_table.add_row().cells
                row_cells[0].text = key
                row_cells[1].text = str(value)
            
            doc.add_paragraph()
            
            # Add financial summary table
            columns = ['Loan ID', 'Group Name', 'Loan Amount (₹)', 'Collected (₹)', 'Pending (₹)', 'EMI Day', 'Status']
            rows = []
            
            for item in summary_data:
                rows.append([
                    item.get('loanId', ''),
                    item.get('groupName', ''),
                    f"₹{item.get('loanAmount', 0):,.2f}",
                    f"₹{item.get('collectedAmount', 0):,.2f}",
                    f"₹{item.get('pendingAmount', 0):,.2f}",
                    item.get('emiDay', ''),
                    item.get('status', ''),
                ])
            
            ExportService._add_table_to_document(doc, 'Financial Summary', columns, rows)
            
            return doc
        except Exception as e:
            logger.exception(f"Error exporting financial summary: {str(e)}")
            raise

    @staticmethod
    def export_user_summary(user_summary_data):
        """Export User Summary table to Word document"""
        try:
            doc = Document()
            
            # Add title and metadata
            title = doc.add_heading('User Summary Report', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_paragraph()
            
            # Add user summary table
            columns = ['User Name', 'Loan ID', 'Group Name', 'Total EMI (₹)', 'Paid EMI (₹)', 'Pending EMI (₹)']
            rows = []
            
            for item in user_summary_data:
                rows.append([
                    item.get('userName', ''),
                    item.get('loanId', ''),
                    item.get('groupName', ''),
                    f"₹{item.get('totalEmi', 0):,.2f}",
                    f"₹{item.get('paidEmi', 0):,.2f}",
                    f"₹{item.get('pendingEmi', 0):,.2f}",
                ])
            
            ExportService._add_table_to_document(doc, 'User Summary', columns, rows)
            
            return doc
        except Exception as e:
            logger.exception(f"Error exporting user summary: {str(e)}")
            raise

    @staticmethod
    def export_emi_summary(emi_summary_data):
        """Export EMI Summary table with details to Word document"""
        try:
            doc = Document()
            
            # Add title and metadata
            title = doc.add_heading('EMI Summary Report', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_paragraph()
            
            # Add EMI summary table
            columns = ['Loan ID', 'User Name', 'Total EMIs', 'Paid EMIs', 'Pending EMIs']
            rows = []
            
            for item in emi_summary_data:
                rows.append([
                    item.get('loanId', ''),
                    item.get('userName', ''),
                    item.get('totalEmis', 0),
                    item.get('paidEmis', 0),
                    item.get('pendingEmis', 0),
                ])
            
            ExportService._add_table_to_document(doc, 'EMI Summary', columns, rows)
            
            # Add detailed EMI information
            doc.add_heading('EMI Details', level=1)
            
            for item in emi_summary_data:
                doc.add_heading(f"Loan: {item.get('loanId')} - User: {item.get('userName')}", level=2)
                
                emi_details = item.get('emiDetails', [])
                if emi_details:
                    detail_columns = ['EMI Date', 'EMI Amount (₹)', 'Status']
                    detail_rows = []
                    
                    for emi in emi_details:
                        detail_rows.append([
                            emi.get('emiDate', ''),
                            f"₹{emi.get('emiAmount', 0):,.2f}",
                            emi.get('emiStatus', ''),
                        ])
                    
                    ExportService._add_table_to_document(doc, f"EMI Details for {item.get('loanId')}", detail_columns, detail_rows)
            
            return doc
        except Exception as e:
            logger.exception(f"Error exporting EMI summary: {str(e)}")
            raise

    @staticmethod
    def export_collections_summary(collections_summary_data):
        """Export Collections Summary table with user details to Word document"""
        try:
            doc = Document()
            
            # Add title and metadata
            title = doc.add_heading('Collections Summary Report', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_paragraph()
            
            # Add collections summary table
            columns = ['Loan Number', 'Group Name', 'Loan Amount (₹)', 'Collected Amount (₹)', 'Pending Amount (₹)', 'Next EMI Date', 'Next EMI Amount (₹)']
            rows = []
            
            for item in collections_summary_data:
                rows.append([
                    item.get('loanId', ''),
                    item.get('groupName', ''),
                    f"₹{item.get('loanAmount', 0):,.2f}",
                    f"₹{item.get('collectedAmount', 0):,.2f}",
                    f"₹{item.get('pendingAmount', 0):,.2f}",
                    item.get('nextEmiDate', ''),
                    f"₹{item.get('nextEmiAmount', 0):,.2f}",
                ])
            
            ExportService._add_table_to_document(doc, 'Collections Summary', columns, rows)
            
            # Add detailed user information
            doc.add_heading('User Details', level=1)
            
            for item in collections_summary_data:
                doc.add_heading(f"Loan: {item.get('loanId')} - Group: {item.get('groupName')}", level=2)
                
                user_details = item.get('userDetails', [])
                if user_details:
                    user_columns = ['User Name', 'Total EMI (₹)', 'Paid EMI (₹)', 'Pending EMI (₹)']
                    user_rows = []
                    
                    for user in user_details:
                        user_rows.append([
                            user.get('userName', ''),
                            f"₹{user.get('totalEmi', 0):,.2f}",
                            f"₹{user.get('paidEmi', 0):,.2f}",
                            f"₹{user.get('pendingEmi', 0):,.2f}",
                        ])
                    
                    ExportService._add_table_to_document(doc, f"User Details for {item.get('loanId')}", user_columns, user_rows)
            
            return doc
        except Exception as e:
            logger.exception(f"Error exporting collections summary: {str(e)}")
            raise
