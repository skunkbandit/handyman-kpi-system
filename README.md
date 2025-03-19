# Handyman KPI System

A comprehensive performance tracking and evaluation system for handyman businesses with tiered employee structures.

## Overview

This application helps handyman businesses track employee performance across different skill categories and tool proficiencies. It supports the company's five-tier system:
- Apprentice
- Handyman
- Craftsman 
- Master Craftsman
- Lead Craftsman

The system allows for regular evaluations, progress tracking, skill gap analysis, and comprehensive reporting.

## Features

- **Employee Management**: Track employee information, skill levels, and career progression
- **Skill Evaluation**: Rate employee proficiency in various skill categories
- **Tool Proficiency**: Track tools employees can operate and own
- **Performance Dashboard**: Visual analytics of employee and team performance 
- **Comprehensive Reports**: Generate PDF and Excel reports for performance reviews and analysis
- **Authentication System**: Secure login with role-based permissions and user management

## Technical Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Data Visualization**: Chart.js
- **Database**: SQLite (development), MySQL/PostgreSQL (production)
- **Reporting**: WeasyPrint (PDF generation), XlsxWriter (Excel export)
- **Authentication**: Flask-Login, Flask-WTF for CSRF protection
- **Testing**: pytest, coverage, Selenium