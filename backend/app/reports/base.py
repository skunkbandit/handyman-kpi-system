"""
Base report generator class for the KPI system.
"""
import io
import datetime
from abc import ABC, abstractmethod

import pandas as pd
import xlsxwriter
from weasyprint import HTML
from flask import render_template


class ReportGenerator(ABC):
    """Base class for all report generators."""
    
    def __init__(self, title, description, report_type):
        """Initialize the report generator.
        
        Args:
            title (str): Report title
            description (str): Report description
            report_type (str): Type of report (employee, team, skills, tools)
        """
        self.title = title
        self.description = description
        self.report_type = report_type
        self.created_at = datetime.datetime.now()
        self.data = {}
        
    @abstractmethod
    def collect_data(self, **kwargs):
        """Collect data for the report. Must be implemented by subclasses.
        
        Args:
            **kwargs: Arbitrary keyword arguments for filtering data
            
        Returns:
            dict: Dictionary containing the collected data
        """
        pass
    
    @abstractmethod
    def prepare_template_data(self):
        """Prepare data for the report template. Must be implemented by subclasses.
        
        Returns:
            dict: Dictionary containing template variables
        """
        pass
    
    def generate_pdf(self, template_name):
        """Generate a PDF report.
        
        Args:
            template_name (str): Name of the template to use for rendering
            
        Returns:
            bytes: PDF document as bytes
        """
        # Prepare data for the template
        template_data = self.prepare_template_data()
        
        # Render the HTML template
        html_content = render_template(
            f'reports/{template_name}',
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            report_type=self.report_type,
            **template_data
        )
        
        # Generate PDF from HTML
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        return pdf_file.getvalue()
    
    def generate_excel(self):
        """Generate an Excel report.
        
        Returns:
            bytes: Excel document as bytes
        """
        # Create an Excel file in memory
        excel_file = io.BytesIO()
        
        # Get data for the Excel report
        excel_data = self.prepare_excel_data()
        
        # Create the Excel workbook
        workbook = xlsxwriter.Workbook(excel_file)
        
        # Add a title format
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Add a header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F2F2F2',
            'border': 1
        })
        
        # Add a data format
        data_format = workbook.add_format({
            'border': 1
        })
        
        # Process each dataframe in the excel_data
        for sheet_name, df in excel_data.items():
            # Create a worksheet
            worksheet = workbook.add_worksheet(sheet_name)
            
            # Write title
            worksheet.merge_range('A1:H1', self.title, title_format)
            worksheet.merge_range('A2:H2', f'Generated on {self.created_at.strftime("%Y-%m-%d %H:%M")}', workbook.add_format({'align': 'center'}))
            
            # Write the column headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(3, col_num, value, header_format)
            
            # Write the dataframe data
            for row_num, row_data in enumerate(df.values):
                for col_num, value in enumerate(row_data):
                    worksheet.write(row_num + 4, col_num, value, data_format)
                    
            # Auto-size columns
            for i, col in enumerate(df.columns):
                # Get maximum width of data in column
                max_len = max(df[col].astype(str).apply(len).max(), len(str(col)))
                # Add a bit of padding
                worksheet.set_column(i, i, max_len + 2)
        
        # Close the workbook
        workbook.close()
        
        # Return the Excel file as bytes
        excel_file.seek(0)
        return excel_file.getvalue()
    
    @abstractmethod
    def prepare_excel_data(self):
        """Prepare data for the Excel report. Must be implemented by subclasses.
        
        Returns:
            dict: Dictionary containing dataframes for each sheet
        """
        pass
