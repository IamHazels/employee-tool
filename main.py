from enum import Enum
from datetime import datetime, timedelta
import sqlite3

def create_tables():
    connection = sqlite3.connect("employees.sqlite")
    cursor = connection.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Employee (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department VARCHAR(192),
    employee_code VARCHAR(12)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS DisciplinaryRecord(
    id INTEGER PRIMARY KEY,
    employee_id VARCHAR(12),
    reason TEXT,
    expiry_date DATE,
    FOREIGN KEY (employee_id) REFERENCES Employee(id)
    )  ''')

    connection.commit()
    connection.close()

class Level(Enum):
    COUNCELLING = 1
    VERBAL = 2
    WRITTEN = 3
    FINAL = 4
    DISMISSAL = 5 


class Employee:
    
    def __init__(self, name, department, employee_code):
        self._name = name
        self._department = department
        self._employee_code = employee_code
        self.disciplinary_records = []
    
    def add_disciplinary_record(self,reason, level, expiry_months):
        record = DisciplinaryRecord(self._name, self._department, self._employee_code, reason, level, expiry_months)
        self.disciplinary_records.append(record)
        
    def count_disciplinaries(self):
        return len(self.disciplinary_records)
    
    def add_disciplinary_from_input(self):
        reason = input("Enter disciplinary reason: ").lower()
        level = input('Enter level of disciplinary: ').lower()
        expiry_months = int(input("Enter number of months the disciplinary is valid for (enter only the amount of months): "))
        self.add_disciplinary_record(reason,level, expiry_months)
    
class DisciplinaryRecord(Employee):
    def __init__(self, name, department, employee_code, reason,level, expiry_months):
        super().__init__(name, department, employee_code)
        self.reason = reason
        self.level = level
        self.expiry_date = datetime.now() + timedelta(days=expiry_months * 30)
        
    def is_expired(self):
        return datetime.now() > self.expiry_date 
   
def insert_or_update_employee_to_db(employee):
    connection = sqlite3.connect("employees.sqlite")
    cursor = connection.cursor()
    
    cursor.execute('''SELECT id FROM Employee WHERE name=? OR employee_code=? ''', (employee._name, employee._employee_code))
    existing_employee = cursor.fetchone()
    
    if existing_employee:
        employee_id = existing_employee[0]
    else:
        cursor.execute('''INSERT INTO Employee (name,department, employee_code)
                       VALUES (?, ?, ?)''', (employee._name, employee._department, employee._employee_code))
        employee_id = cursor.lastrowid
        
    for record in employee.disciplinary_records:
        cursor.execute('''INSERT INTO DisciplinaryRecord (employee_id, reason, expiry_date) 
                       VALUES (?, ?, ?)''', (employee_id, record.reason, record.expiry_date))
        
    connection.commit()
    connection.close()         
    
# write function to see if employee exists
def employee_exists(instance):
    if isinstance(instance, Employee):
        return instance._employee_code
    else:
        return("Employee does not exist on the system, please create the employee")
        

def create_or_update_employee():
    print("1. Create a new employee record and disciplinary")
    print("2. Add disciplinary record to an existing employee")
    option = input("Enter your choice: ")
    
    if option == "1":
        name = input("Enter the name of the employee: ").lower()
        department = input("Enter the department of the employee: ").lower()
        employee_code = input("Enter the employee code: ").lower()
        employee = Employee(name, department, employee_code)
        employee.add_disciplinary_from_input()
        insert_or_update_employee_to_db(employee)
        print("Employee record added successfully.")
    elif option == "2":
        name_or_code = input("Enter the employee name or employee code: ")
        connection = sqlite3.connect("employees.sqlite")
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM Employee WHERE name=? OR employee_code=?''', (name_or_code,name_or_code))
        employee_data = cursor.fetchone()
        connection.close()
        
        if employee_data:
            name, department, employee_code = employee_data[1], employee_data[2], employee_data[3]
            employee = Employee(name, department, employee_code)
            employee.add_disciplinary_from_input()
            insert_or_update_employee_to_db(employee)
            print("Disciplinary record has been added successfully. ")
        else:
            print("Employee not found. ")
            
def display_employee_records():
    name_or_code = input("Enter employee name or employee code: ").lower()
    connection = sqlite3.connect("employees.sqlite")
    cursor = connection.cursor()
    cursor.execute(''' SELECT * FROM Employee WHERE name=? OR employee_code=?''',(name_or_code, name_or_code))
    employee_data = cursor.fetchone()
    connection.close()
    
    if employee_data:
        name,department, employee_code = employee_data[1], employee_data[2], employee_data[3]
        print("\nEmployee Information: ")
        print("Name: ",name)
        print("Department: ", department)
        print("Employee code: ", employee_code)
        
        connection = sqlite3.connect("employees.sqlite")
        cursor = connection.cursor()
        cursor.execute(''' SELECT * FROM DisciplinaryRecord WHERE employee_id=?''', (employee_data[0],))
        disciplinary_records = cursor.fetchall()
        connection.close()
        
        if disciplinary_records:
            print("\nDisciplinary Records:")
            for record in disciplinary_records:
                print("Reason: ", record[2])
                expiry_date = datetime.strptime(record[3], "%Y-%m-%d %H:%M:%S.%f")
                print("Expiration status: ", "Expiredd" if datetime.now()>expiry_date else "Active")
                
        else:
            print("No disciplinary records were found for this employee. ")
    else:
        print("Employee was not found on the system. ")
        
def display_employees_in_department():
    department = input("Enter the department: ").strip().lower()
    print("Entered department: ", department)
    connection = sqlite3.connect("employees.sqlite")
    cursor = connection.cursor()
    cursor.execute(''' SELECT * FROM Employee WHERE LOWER (TRIM(department))=?''', (department,))
    employee = cursor.fetchall()
    
    
    if employee:
        print("\nEmployees in this department: ", department)
        for employee in employees:
            print("\nEmployee Information: ")
            print("Name", employee[1])
            print("Employee code:", employee[3])
            
            cursor.execute(''' SELECT * FROM DisciplinaryRecord WHERE employee_id=?''', (employee[0],))
            disciplinary_records = cursor.fetchall()
            
            if disciplinary_records:
                print("\n DDisciplinary Records: ")
                for record in disciplinary_records:
                    print("Reason: ", record[2])
                    print("Expiration status: ", "Expired" if datetime.now()> datetime.strptime(record[3], "%Y-%m_%d") else "Active")
            else:
                print("No disciplinary records were found for this employe. ")
    else:
        print("No employees were found for this department. ")
        

create_tables()
def main_menu():
    while True:
        print("/nMain Menu: ")
        print("1. Create or update an employee ")
        print("2. Display an employee's record ")
        print("3. Display all employee's in a department ")
        print("4. Exit")
        option = input("Enter your choice: ")
        
        if option == "1":
            create_or_update_employee()
        elif option == "2":
            display_employee_records()
        elif option == "3":
            display_employees_in_department()
        elif option == "4":
            break
        else:
            print("Invalid option. Please try again.") 
            

main_menu()
        
                    

    
    

    
        
    