"""
Reports routes for the KPI system
"""
from datetime import datetime
import json

from flask import Blueprint, render_template, redirect, url_for, send_file, request, jsonify, Response, abort
from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory
from app.models.tool import Tool, ToolCategory
from app.models.evaluation import Evaluation, SkillEvaluation, ToolEvaluation
from app.reports.generators import get_report_generator, get_available_report_types
from app import db
import io

# Create blueprint
bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
def index():
    """
    Reports index page showing available report types
    """
    report_types = get_available_report_types()
    employees = Employee.query.order_by(Employee.last_name).all()
    skill_categories = SkillCategory.query.order_by(SkillCategory.name).all()
    tool_categories = ToolCategory.query.order_by(ToolCategory.name).all()
    
    return render_template(
        'reports/index.html',
        report_types=report_types,
        employees=employees,
        skill_categories=skill_categories,
        tool_categories=tool_categories
    )

@bp.route('/generate_employee_report', methods=['GET', 'POST'])
def generate_employee_report():
    """
    Generate an employee performance report
    """
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        format_type = request.form.get('format', 'pdf')
        
        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400
            
        # Initialize the report generator
        try:
            report_generator = get_report_generator('employee')
            
            # Collect the data for this report
            report_generator.collect_data(
                employee_id=int(employee_id),
                start_date=start_date,
                end_date=end_date
            )
            
            # Generate the report in the requested format
            if format_type == 'pdf':
                pdf_data = report_generator.generate_pdf('employee_performance.html')
                
                # Create a response with the PDF data
                employee = Employee.query.get(employee_id)
                filename = f"employee_performance_{employee.last_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                return Response(
                    pdf_data,
                    mimetype='application/pdf',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/pdf'
                    }
                )
                
            elif format_type == 'excel':
                excel_data = report_generator.generate_excel()
                
                # Create a response with the Excel data
                employee = Employee.query.get(employee_id)
                filename = f"employee_performance_{employee.last_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                
                return Response(
                    excel_data,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                )
                
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            
    # GET request - show form
    employees = Employee.query.order_by(Employee.last_name).all()
    return render_template('reports/employee_report_form.html', employees=employees)

@bp.route('/generate_team_report', methods=['GET', 'POST'])
def generate_team_report():
    """
    Generate a team performance report
    """
    if request.method == 'POST':
        tier = request.form.get('tier')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        format_type = request.form.get('format', 'pdf')
        employee_ids = request.form.getlist('employee_ids')
        
        if employee_ids:
            employee_ids = [int(id) for id in employee_ids]
        
        # Initialize the report generator
        try:
            report_generator = get_report_generator('team')
            
            # Collect the data for this report
            report_generator.collect_data(
                tier=tier if tier else None,
                start_date=start_date,
                end_date=end_date,
                employee_ids=employee_ids if employee_ids else None
            )
            
            # Generate the report in the requested format
            if format_type == 'pdf':
                pdf_data = report_generator.generate_pdf('team_performance.html')
                
                # Create a response with the PDF data
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"team_performance_{tier or 'all_tiers'}_{timestamp}.pdf"
                
                return Response(
                    pdf_data,
                    mimetype='application/pdf',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/pdf'
                    }
                )
                
            elif format_type == 'excel':
                excel_data = report_generator.generate_excel()
                
                # Create a response with the Excel data
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"team_performance_{tier or 'all_tiers'}_{timestamp}.xlsx"
                
                return Response(
                    excel_data,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                )
                
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            
    # GET request - show form
    employees = Employee.query.order_by(Employee.last_name).all()
    tiers = sorted(set(e.tier for e in employees))
    return render_template('reports/team_report_form.html', employees=employees, tiers=tiers)

@bp.route('/generate_skills_report', methods=['GET', 'POST'])
def generate_skills_report():
    """
    Generate a skills analysis report
    """
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        tier = request.form.get('tier')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        format_type = request.form.get('format', 'pdf')
        
        if category_id:
            category_id = int(category_id)
        
        # Initialize the report generator
        try:
            report_generator = get_report_generator('skills')
            
            # Collect the data for this report
            report_generator.collect_data(
                category_id=category_id,
                tier=tier if tier else None,
                start_date=start_date,
                end_date=end_date
            )
            
            # Generate the report in the requested format
            if format_type == 'pdf':
                pdf_data = report_generator.generate_pdf('skills_analysis.html')
                
                # Create a response with the PDF data
                timestamp = datetime.now().strftime('%Y%m%d')
                category_name = 'all_categories'
                if category_id:
                    category = SkillCategory.query.get(category_id)
                    if category:
                        category_name = category.name.lower().replace(' ', '_')
                        
                filename = f"skills_analysis_{category_name}_{timestamp}.pdf"
                
                return Response(
                    pdf_data,
                    mimetype='application/pdf',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/pdf'
                    }
                )
                
            elif format_type == 'excel':
                excel_data = report_generator.generate_excel()
                
                # Create a response with the Excel data
                timestamp = datetime.now().strftime('%Y%m%d')
                category_name = 'all_categories'
                if category_id:
                    category = SkillCategory.query.get(category_id)
                    if category:
                        category_name = category.name.lower().replace(' ', '_')
                        
                filename = f"skills_analysis_{category_name}_{timestamp}.xlsx"
                
                return Response(
                    excel_data,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                )
                
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            
    # GET request - show form
    skill_categories = SkillCategory.query.order_by(SkillCategory.name).all()
    employees = Employee.query.order_by(Employee.last_name).all()
    tiers = sorted(set(e.tier for e in employees))
    return render_template('reports/skills_report_form.html', skill_categories=skill_categories, tiers=tiers)

@bp.route('/generate_tools_report', methods=['GET', 'POST'])
def generate_tools_report():
    """
    Generate a tool inventory report
    """
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        tier = request.form.get('tier')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        format_type = request.form.get('format', 'pdf')
        
        if category_id:
            category_id = int(category_id)
        
        # Initialize the report generator
        try:
            report_generator = get_report_generator('tools')
            
            # Collect the data for this report
            report_generator.collect_data(
                category_id=category_id,
                tier=tier if tier else None,
                start_date=start_date,
                end_date=end_date
            )
            
            # Generate the report in the requested format
            if format_type == 'pdf':
                pdf_data = report_generator.generate_pdf('tool_inventory.html')
                
                # Create a response with the PDF data
                timestamp = datetime.now().strftime('%Y%m%d')
                category_name = 'all_categories'
                if category_id:
                    category = ToolCategory.query.get(category_id)
                    if category:
                        category_name = category.name.lower().replace(' ', '_')
                        
                filename = f"tool_inventory_{category_name}_{timestamp}.pdf"
                
                return Response(
                    pdf_data,
                    mimetype='application/pdf',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/pdf'
                    }
                )
                
            elif format_type == 'excel':
                excel_data = report_generator.generate_excel()
                
                # Create a response with the Excel data
                timestamp = datetime.now().strftime('%Y%m%d')
                category_name = 'all_categories'
                if category_id:
                    category = ToolCategory.query.get(category_id)
                    if category:
                        category_name = category.name.lower().replace(' ', '_')
                        
                filename = f"tool_inventory_{category_name}_{timestamp}.xlsx"
                
                return Response(
                    excel_data,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                )
                
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            
    # GET request - show form
    tool_categories = ToolCategory.query.order_by(ToolCategory.name).all()
    employees = Employee.query.order_by(Employee.last_name).all()
    tiers = sorted(set(e.tier for e in employees))
    return render_template('reports/tools_report_form.html', tool_categories=tool_categories, tiers=tiers)

@bp.route('/report_options/<report_type>')
def report_options(report_type):
    """
    Get form options for a specific report type
    """
    try:
        # Validate the report type
        if report_type not in ['employee', 'team', 'skills', 'tools']:
            return jsonify({'error': 'Invalid report type'}), 400
            
        # Get the necessary form data based on the report type
        if report_type == 'employee':
            employees = Employee.query.order_by(Employee.last_name).all()
            return render_template('reports/partials/employee_options.html', employees=employees)
            
        elif report_type == 'team':
            employees = Employee.query.order_by(Employee.last_name).all()
            tiers = sorted(set(e.tier for e in employees))
            return render_template('reports/partials/team_options.html', employees=employees, tiers=tiers)
            
        elif report_type == 'skills':
            skill_categories = SkillCategory.query.order_by(SkillCategory.name).all()
            employees = Employee.query.order_by(Employee.last_name).all()
            tiers = sorted(set(e.tier for e in employees))
            return render_template('reports/partials/skills_options.html', skill_categories=skill_categories, tiers=tiers)
            
        elif report_type == 'tools':
            tool_categories = ToolCategory.query.order_by(ToolCategory.name).all()
            employees = Employee.query.order_by(Employee.last_name).all()
            tiers = sorted(set(e.tier for e in employees))
            return render_template('reports/partials/tools_options.html', tool_categories=tool_categories, tiers=tiers)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
