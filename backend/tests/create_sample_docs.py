from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def get_font(size):
    try:
        # Pillow searches system paths, works automatically on Windows/macOS/Linux if font exists
        return ImageFont.truetype("arial.ttf", size)
    except IOError:
        return ImageFont.load_default()

def create_prescription_clean():
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    font_small = get_font(16)
    
    # Outer Border
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    # Header
    draw.text((40, 40), "DR. ARUN SHARMA, MBBS, MD (Internal Medicine)", fill='black', font=font_large)
    draw.text((40, 80), "Reg. No: KA/45678/2015", fill='black', font=font_medium)
    draw.text((40, 110), "City Medical Centre, 12 MG Road, Bengaluru - 560001", fill='black', font=font_medium)
    draw.text((40, 140), "Ph: +91-80-55551234", fill='black', font=font_medium)
    draw.line([15, 180, 785, 180], fill='black', width=3)
    
    # Patient info
    draw.text((40, 200), "Patient Name: Rajesh Kumar", fill='black', font=font_medium)
    draw.text((40, 230), "Age/Gender: 39 years / Male", fill='black', font=font_medium)
    draw.text((500, 200), "Date: 2024-11-01", fill='black', font=font_medium)
    draw.line([15, 270, 785, 270], fill='black', width=2)
    
    # Diagnosis
    draw.text((40, 290), "Diagnosis: Viral Fever", fill='black', font=font_large)
    draw.text((40, 330), "Symptoms: High grade fever since 3 days, severe body ache", fill='black', font=font_medium)
    
    # Rx section
    draw.text((40, 390), "Rx:", fill='black', font=font_large)
    draw.text((60, 440), "1. Tab Paracetamol 650mg  -  1 tab three times a day x 5 days", fill='black', font=font_medium)
    draw.text((60, 480), "2. Tab Vitamin C 500mg  -  1 tab once daily at night x 7 days", fill='black', font=font_medium)
    
    # Investigations
    draw.text((40, 560), "Investigations Ordered:", fill='black', font=font_medium)
    draw.text((60, 600), "- Complete Blood Count (CBC)", fill='black', font=font_medium)
    draw.text((60, 630), "- Dengue NS1 Antigen Test", fill='black', font=font_medium)
    
    # Footer
    draw.text((500, 850), "[Dr. Arun Sharma]", fill='black', font=font_medium)
    draw.text((500, 880), "Signature & Registration Stamp", fill='black', font=font_small)
    
    os.makedirs('sample_docs', exist_ok=True)
    img.save('sample_docs/prescription_clean.jpg')
    img.save('sample_docs/prescription_clean.pdf', 'PDF')
    print("Saved sample_docs/prescription_clean.jpg and prescription_clean.pdf")


def create_hospital_bill_clean():
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    font_small = get_font(16)
    
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    # Header
    draw.text((40, 40), "CITY MEDICAL CENTRE", fill='black', font=font_large)
    draw.text((40, 80), "12 MG Road, Bengaluru - 560001", fill='black', font=font_medium)
    draw.text((40, 110), "GSTIN: 29AAAAA1111A1Z1", fill='black', font=font_medium)
    draw.line([15, 150, 785, 150], fill='black', width=3)
    
    # Bill Details
    draw.text((40, 170), "INVOICE / BILL", fill='black', font=font_large)
    draw.text((40, 210), "Bill No: CMC/2024/08321", fill='black', font=font_medium)
    draw.text((40, 240), "Patient Name: Rajesh Kumar", fill='black', font=font_medium)
    draw.text((40, 270), "Age/Gender: 39 / Male", fill='black', font=font_medium)
    draw.text((500, 210), "Date: 2024-11-01", fill='black', font=font_medium)
    draw.text((500, 240), "Ref Doctor: Dr. Arun Sharma", fill='black', font=font_medium)
    draw.line([15, 310, 785, 310], fill='black', width=2)
    
    # Line Items Header
    draw.text((40, 330), "Description", fill='black', font=font_medium)
    draw.text((450, 330), "Qty", fill='black', font=font_medium)
    draw.text((550, 330), "Rate (Rs)", fill='black', font=font_medium)
    draw.text((670, 330), "Amount (Rs)", fill='black', font=font_medium)
    draw.line([30, 360, 770, 360], fill='black', width=1)
    
    # Line Items
    draw.text((40, 380), "Consultation Fee (OPD)", fill='black', font=font_medium)
    draw.text((460, 380), "1", fill='black', font=font_medium)
    draw.text((550, 380), "1000.00", fill='black', font=font_medium)
    draw.text((670, 380), "1000.00", fill='black', font=font_medium)
    
    draw.text((40, 420), "CBC Test", fill='black', font=font_medium)
    draw.text((460, 420), "1", fill='black', font=font_medium)
    draw.text((550, 420), "300.00", fill='black', font=font_medium)
    draw.text((670, 420), "300.00", fill='black', font=font_medium)
    
    draw.text((40, 460), "Dengue NS1 Antigen Test", fill='black', font=font_medium)
    draw.text((460, 460), "1", fill='black', font=font_medium)
    draw.text((550, 460), "200.00", fill='black', font=font_medium)
    draw.text((670, 460), "200.00", fill='black', font=font_medium)
    
    draw.line([30, 600, 770, 600], fill='black', width=1)
    
    # Totals
    draw.text((500, 620), "Subtotal: Rs 1500.00", fill='black', font=font_medium)
    draw.text((500, 650), "GST (0%): Rs 0.00", fill='black', font=font_medium)
    draw.text((500, 680), "Total Amount: Rs 1500.00", fill='black', font=font_large)
    
    # Signatures
    draw.text((40, 850), "Payment Mode: UPI", fill='black', font=font_medium)
    draw.text((500, 850), "Received by: Cashier", fill='black', font=font_medium)
    draw.text((500, 880), "Authorized Signatory & Stamp", fill='black', font=font_small)
    
    os.makedirs('sample_docs', exist_ok=True)
    img.save('sample_docs/hospital_bill_clean.jpg')
    img.save('sample_docs/hospital_bill_clean.pdf', 'PDF')
    print("Saved sample_docs/hospital_bill_clean.jpg and hospital_bill_clean.pdf")


def create_prescription_diabetes():
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    font_small = get_font(16)
    
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    # Header
    draw.text((40, 40), "DR. SUNIL MEHTA, MBBS, MD (Endocrinology)", fill='black', font=font_large)
    draw.text((40, 80), "Reg. No: GJ/56789/2014", fill='black', font=font_medium)
    draw.text((40, 110), "Mehta Diabetes Centre, Ahmedabad", fill='black', font=font_medium)
    draw.line([15, 180, 785, 180], fill='black', width=3)
    
    # Patient details
    draw.text((40, 200), "Patient Name: Vikram Joshi", fill='black', font=font_medium)
    draw.text((40, 230), "Age/Gender: 45 years / Male", fill='black', font=font_medium)
    draw.text((500, 200), "Date: 2024-10-15", fill='black', font=font_medium)
    draw.line([15, 270, 785, 270], fill='black', width=2)
    
    # Diagnosis
    draw.text((40, 290), "Diagnosis: Type 2 Diabetes Mellitus", fill='black', font=font_large)
    draw.text((40, 330), "Symptoms: Polyuria, polydipsia, high fasting blood sugar", fill='black', font=font_medium)
    
    # Rx
    draw.text((40, 390), "Rx:", fill='black', font=font_large)
    draw.text((60, 440), "1. Tab Metformin 500mg  -  1 tab twice daily with meals x 90 days", fill='black', font=font_medium)
    draw.text((60, 480), "2. Tab Glimepiride 1mg  -  1 tab once daily before breakfast x 90 days", fill='black', font=font_medium)
    
    # Signatures
    draw.text((500, 850), "[Dr. Sunil Mehta]", fill='black', font=font_medium)
    draw.text((500, 880), "Signature & Registration Stamp", fill='black', font=font_small)
    
    os.makedirs('sample_docs', exist_ok=True)
    img.save('sample_docs/prescription_diabetes.jpg')
    img.save('sample_docs/prescription_diabetes.pdf', 'PDF')
    print("Saved sample_docs/prescription_diabetes.jpg and prescription_diabetes.pdf")


def create_hospital_bill_dental():
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    font_small = get_font(16)
    
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    # Header
    draw.text((40, 40), "SMILE DENTAL CLINIC", fill='black', font=font_large)
    draw.text((40, 80), "44 Jayanagar, Bengaluru - 560041", fill='black', font=font_medium)
    draw.text((40, 110), "GSTIN: 29BBBBB2222B2Z2", fill='black', font=font_medium)
    draw.line([15, 150, 785, 150], fill='black', width=3)
    
    # Details
    draw.text((40, 170), "DENTAL BILL / INVOICE", fill='black', font=font_large)
    draw.text((40, 210), "Bill No: SDC/2024/0981", fill='black', font=font_medium)
    draw.text((40, 240), "Patient Name: Priya Singh", fill='black', font=font_medium)
    draw.text((500, 210), "Date: 2024-10-20", fill='black', font=font_medium)
    draw.line([15, 300, 785, 300], fill='black', width=2)
    
    # Line Items Header
    draw.text((40, 320), "Description", fill='black', font=font_medium)
    draw.text((500, 320), "Qty", fill='black', font=font_medium)
    draw.text((650, 320), "Amount (Rs)", fill='black', font=font_medium)
    draw.line([30, 350, 770, 350], fill='black', width=1)
    
    # Line Items
    draw.text((40, 370), "Root Canal Treatment (Tooth 24)", fill='black', font=font_medium)
    draw.text((500, 370), "1", fill='black', font=font_medium)
    draw.text((650, 370), "8000.00", fill='black', font=font_medium)
    
    draw.text((40, 410), "Teeth Whitening (Cosmetic)", fill='black', font=font_medium)
    draw.text((500, 410), "1", fill='black', font=font_medium)
    draw.text((650, 410), "4000.00", fill='black', font=font_medium)
    
    draw.line([30, 500, 770, 500], fill='black', width=1)
    
    # Totals
    draw.text((500, 520), "Subtotal: Rs 12000.00", fill='black', font=font_medium)
    draw.text((500, 550), "Total Amount: Rs 12000.00", fill='black', font=font_large)
    
    # Signatures
    draw.text((500, 850), "Authorized Signatory", fill='black', font=font_medium)
    draw.text((500, 880), "Smile Dental Clinic Stamp", fill='black', font=font_small)
    
    os.makedirs('sample_docs', exist_ok=True)
    img.save('sample_docs/hospital_bill_dental.jpg')
    img.save('sample_docs/hospital_bill_dental.pdf', 'PDF')
    print("Saved sample_docs/hospital_bill_dental.jpg and hospital_bill_dental.pdf")


def create_diagnostic_report_clean():
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    font_small = get_font(16)
    
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    # Header
    draw.text((40, 40), "PRECISION DIAGNOSTICS PVT LTD", fill='black', font=font_large)
    draw.text((40, 80), "NABL Accredited Lab  |  Lab ID: KA-NABL-1234", fill='black', font=font_medium)
    draw.text((40, 110), "45 Jayanagar, Bengaluru  |  Ph: 080-55554321", fill='black', font=font_medium)
    draw.line([15, 150, 785, 150], fill='black', width=3)
    
    # Patient Info
    draw.text((40, 170), "Patient Name: Rajesh Kumar", fill='black', font=font_medium)
    draw.text((40, 200), "Age/Sex: 39 / Male", fill='black', font=font_medium)
    draw.text((40, 230), "Ref Doctor: Dr. Arun Sharma", fill='black', font=font_medium)
    draw.text((450, 170), "Sample Date: 2024-11-01", fill='black', font=font_medium)
    draw.text((450, 200), "Report Date: 2024-11-01", fill='black', font=font_medium)
    draw.text((450, 230), "Sample ID: PD-2024-18723", fill='black', font=font_medium)
    draw.line([15, 270, 785, 270], fill='black', width=2)
    
    # Lab Results Header
    draw.text((40, 290), "TEST NAME", fill='black', font=font_medium)
    draw.text((320, 290), "RESULT", fill='black', font=font_medium)
    draw.text((480, 290), "UNIT", fill='black', font=font_medium)
    draw.text((600, 290), "NORMAL RANGE", fill='black', font=font_medium)
    draw.line([30, 320, 770, 320], fill='black', width=1)
    
    # Results
    draw.text((40, 340), "Hemoglobin", fill='black', font=font_medium)
    draw.text((320, 340), "13.2", fill='black', font=font_medium)
    draw.text((480, 340), "g/dL", fill='black', font=font_medium)
    draw.text((600, 340), "13.0 - 17.0", fill='black', font=font_medium)
    
    draw.text((40, 380), "WBC Count", fill='black', font=font_medium)
    draw.text((320, 380), "9,800", fill='black', font=font_medium)
    draw.text((480, 380), "/μL", fill='black', font=font_medium)
    draw.text((600, 380), "4,500 - 11,000", fill='black', font=font_medium)
    
    draw.text((40, 420), "Platelet Count", fill='black', font=font_medium)
    draw.text((320, 420), "185,000", fill='black', font=font_medium)
    draw.text((480, 420), "/μL", fill='black', font=font_medium)
    draw.text((600, 420), "150,000 - 450,000", fill='black', font=font_medium)
    
    draw.text((40, 460), "Dengue NS1 Antigen", fill='black', font=font_medium)
    draw.text((320, 460), "NEGATIVE", fill='black', font=font_medium)
    draw.text((480, 460), "—", fill='black', font=font_medium)
    draw.text((600, 460), "—", fill='black', font=font_medium)
    draw.line([30, 500, 770, 500], fill='black', width=1)
    
    # Remarks
    draw.text((40, 520), "Remarks: WBC count is towards upper normal limit.", fill='black', font=font_medium)
    draw.text((40, 550), "Clinical correlation advised.", fill='black', font=font_medium)
    
    # Signatures
    draw.text((500, 850), "Dr. Meena Pillai, MD", fill='black', font=font_medium)
    draw.text((500, 880), "Reg. No: KA/89012/2018", fill='black', font=font_medium)
    draw.text((500, 910), "Signature & Lab Stamp", fill='black', font=font_small)
    
    os.makedirs('sample_docs', exist_ok=True)
    img.save('sample_docs/diagnostic_report_clean.jpg')
    img.save('sample_docs/diagnostic_report_clean.pdf', 'PDF')
    print("Saved sample_docs/diagnostic_report_clean.jpg and diagnostic_report_clean.pdf")


def create_pharmacy_bill_clean():
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    font_small = get_font(16)
    
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    # Header
    draw.text((40, 40), "HEALTH FIRST PHARMACY", fill='black', font=font_large)
    draw.text((40, 80), "Drug Lic. No: KA-BLR-XXXX", fill='black', font=font_medium)
    draw.text((40, 110), "22 Brigade Road, Bengaluru - 560001", fill='black', font=font_medium)
    draw.line([15, 150, 785, 150], fill='black', width=3)
    
    # Bill Details
    draw.text((40, 170), "PHARMACY BILL / INVOICE", fill='black', font=font_large)
    draw.text((40, 210), "Bill No: HFP-24-09821", fill='black', font=font_medium)
    draw.text((40, 240), "Patient Name: Rajesh Kumar", fill='black', font=font_medium)
    draw.text((500, 210), "Date: 2024-11-01", fill='black', font=font_medium)
    draw.text((500, 240), "Prescribing Dr: Dr. Arun Sharma", fill='black', font=font_medium)
    draw.line([15, 300, 785, 300], fill='black', width=2)
    
    # Table Header
    draw.text((40, 320), "MEDICINE NAME", fill='black', font=font_medium)
    draw.text((320, 320), "BATCH", fill='black', font=font_medium)
    draw.text((420, 320), "EXP", fill='black', font=font_medium)
    draw.text((520, 320), "QTY", fill='black', font=font_medium)
    draw.text((600, 320), "MRP (Rs)", fill='black', font=font_medium)
    draw.text((700, 320), "AMT (Rs)", fill='black', font=font_medium)
    draw.line([30, 350, 770, 350], fill='black', width=1)
    
    # Line Items
    draw.text((40, 370), "Paracetamol 650mg", fill='black', font=font_medium)
    draw.text((320, 370), "A2341", fill='black', font=font_medium)
    draw.text((420, 370), "03/26", fill='black', font=font_medium)
    draw.text((520, 370), "15", fill='black', font=font_medium)
    draw.text((600, 370), "2.50", fill='black', font=font_medium)
    draw.text((700, 370), "37.50", fill='black', font=font_medium)
    
    draw.text((40, 410), "Vitamin C 500mg", fill='black', font=font_medium)
    draw.text((320, 410), "B7821", fill='black', font=font_medium)
    draw.text((420, 410), "06/26", fill='black', font=font_medium)
    draw.text((520, 410), "10", fill='black', font=font_medium)
    draw.text((600, 410), "4.00", fill='black', font=font_medium)
    draw.text((700, 410), "40.00", fill='black', font=font_medium)
    draw.line([30, 500, 770, 500], fill='black', width=1)
    
    # Totals
    draw.text((500, 520), "Subtotal: Rs 77.50", fill='black', font=font_medium)
    draw.text((500, 550), "Discount (5%): Rs -3.88", fill='black', font=font_medium)
    draw.text((500, 580), "Net Amount: Rs 73.62", fill='black', font=font_large)
    
    # Signatures
    draw.text((40, 850), "Pharmacist: R. Sharma", fill='black', font=font_medium)
    draw.text((500, 850), "Authorized Signature", fill='black', font=font_medium)
    draw.text((500, 880), "Health First Pharmacy Stamp", fill='black', font=font_small)
    
    os.makedirs('sample_docs', exist_ok=True)
    img.save('sample_docs/pharmacy_bill_clean.jpg')
    img.save('sample_docs/pharmacy_bill_clean.pdf', 'PDF')
    print("Saved sample_docs/pharmacy_bill_clean.jpg and pharmacy_bill_clean.pdf")


def create_hospital_bill_blurry():
    # We will generate a normal bill and then apply a heavy Gaussian blur to make it completely unreadable!
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    font_large = get_font(28)
    font_medium = get_font(20)
    
    draw.rectangle([15, 15, 785, 985], outline='black', width=3)
    
    draw.text((40, 40), "CITY MEDICAL CENTRE", fill='black', font=font_large)
    draw.text((40, 80), "Bill No: CMC/2024/08321", fill='black', font=font_medium)
    draw.text((40, 110), "Patient Name: Rajesh Kumar", fill='black', font=font_medium)
    draw.text((40, 140), "Consultation Fee: Rs 1500.00", fill='black', font=font_medium)
    
    # Apply Blur
    blurry_img = img.filter(ImageFilter.GaussianBlur(radius=8))
    
    os.makedirs('sample_docs', exist_ok=True)
    blurry_img.save('sample_docs/hospital_bill_blurry.jpg')
    blurry_img.save('sample_docs/hospital_bill_blurry.pdf', 'PDF')
    print("Saved sample_docs/hospital_bill_blurry.jpg and hospital_bill_blurry.pdf")


if __name__ == "__main__":
    create_prescription_clean()
    create_hospital_bill_clean()
    create_diagnostic_report_clean()
    create_pharmacy_bill_clean()
    create_prescription_diabetes()
    create_hospital_bill_dental()
    create_hospital_bill_blurry()
    print("All mock sample documents generated successfully in the sample_docs/ directory!")
