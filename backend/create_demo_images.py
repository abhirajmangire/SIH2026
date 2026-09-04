import cv2
import numpy as np
import os

os.makedirs('storage/uploads', exist_ok=True)
os.makedirs('storage/tampering', exist_ok=True)

def create_demo_image(name, text, color=(200,200,200), size=(600,400)):
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (size[0]-20, size[1]-20), color, -1)
    cv2.rectangle(img, (30, 30), (size[0]-30, size[1]-30), (150,150,150), 2)
    
    cv2.putText(img, 'GOVERNMENT OF INDIA', (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,100), 2)
    cv2.putText(img, 'PASSPORT', (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,100), 2)
    
    y = 150
    for line in text:
        cv2.putText(img, line, (60, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
        y += 30
    
    cv2.putText(img, 'P<INDSHARMA<<ADITI<<<<<<<<<<<<<<<<<<<<<<<<<<<<', (60, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)
    cv2.putText(img, 'Z12345678IND9003157F3001099<<<<<<<<<<<<<<<0', (60, y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)
    
    cv2.imwrite(f'storage/uploads/{name}', img)

create_demo_image('valid_passport.jpg', [
    'Name: ADITI SHARMA',
    'DOB: 15.03.1990',
    'Passport No: Z1234567',
    'Nationality: IND',
    'Issue: 10.01.2020',
    'Expiry: 09.01.2030'
])

create_demo_image('suspicious_passport.jpg', [
    'Name: RAHUL VERMA',
    'DOB: 22.07.1985',
    'Passport No: A9876543',
    'Nationality: IND',
    'Issue: 05.06.2018',
    'Expiry: 04.06.2028'
], color=(200, 220, 200))

create_demo_image('high_risk_passport.jpg', [
    'Name: PRIYA KUMARI',
    'DOB: 10.11.1992',
    'Passport No: X5555555',
    'Nationality: IND',
    'Issue: 15.03.2019',
    'Expiry: 14.03.2029'
], color=(220, 200, 200))

def create_visa_image(name, text, color=(200,200,200)):
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (580, 380), color, -1)
    cv2.rectangle(img, (30, 30), (570, 370), (150,150,150), 2)
    
    cv2.putText(img, 'VISA', (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100,0,0), 2)
    
    y = 120
    for line in text:
        cv2.putText(img, line, (60, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
        y += 30
    
    cv2.imwrite(f'storage/uploads/{name}', img)

create_visa_image('valid_visa.jpg', [
    'Name: ADITI SHARMA',
    'DOB: 15.03.1990',
    'Passport No: Z1234567',
    'Visa No: V987654321',
    'Type: TOURIST',
    'Issue: 01.02.2024',
    'Expiry: 31.01.2025'
])

create_visa_image('suspicious_visa.jpg', [
    'Name: RAHUL VERMA',
    'DOB: 22.07.1985',
    'Passport No: A9876543',
    'Visa No: V111222333',
    'Type: BUSINESS',
    'Issue: 10.01.2024',
    'Expiry: 09.01.2025'
], color=(200, 220, 200))

create_visa_image('high_risk_visa.jpg', [
    'Name: PRIYA KUMARI',
    'DOB: 11.11.1992',
    'Passport No: X5555555',
    'Visa No: V999888777',
    'Type: STUDENT',
    'Issue: 01.03.2024',
    'Expiry: 28.02.2025'
], color=(220, 200, 200))

def create_face_image(name):
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.rectangle(img, (0,0), (200,200), (180,180,180), -1)
    cv2.circle(img, (100, 80), 40, (100,100,100), -1)
    cv2.ellipse(img, (100, 180), (60, 40), 0, 0, 180, (100,100,100), -1)
    cv2.imwrite(f'storage/uploads/{name}', img)

create_face_image('face_doc.jpg')
create_face_image('face_live.jpg')

print('Demo images created successfully')