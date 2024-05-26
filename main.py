import cv2
import pytesseract
from PIL import Image
import time
import requests
from datetime import datetime

def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite('vehicle.jpg', frame)
        return 'vehicle.jpg'
    else:
        return None

def read_license_plate(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text.strip()

def generate_ticket(license_plate):
    entry_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    ticket = f"License Plate: {license_plate}\nEntry Time: {entry_time}"
    with open('/dev/usb/lp0', 'w') as printer:
        printer.write(ticket)
    return entry_time

def calculate_fee(entry_time, exit_time):
    FMT = '%Y-%m-%d %H:%M:%S'
    tdelta = datetime.strptime(exit_time, FMT) - datetime.strptime(entry_time, FMT)
    hours = tdelta.total_seconds() / 3600
    rate_per_hour = 10  # Asumiendo una tarifa de $10 por hora
    total_fee = hours * rate_per_hour
    return total_fee

def send_webhook(data):
    url = "http://your-webservice-url.com/webhook"
    response = requests.post(url, json=data)
    return response.status_code

def main():
    while True:
        command = input("Enter 'entry' for vehicle entry or 'exit' for vehicle exit: ")
        if command == 'entry':
            image_path = capture_image()
            if image_path:
                license_plate = read_license_plate(image_path)
                entry_time = generate_ticket(license_plate)
                # Store entry_time in a database or a file for later retrieval
                print(f"Vehicle entered at {entry_time}")
            else:
                print("Failed to capture image.")
        elif command == 'exit':
            image_path = capture_image()
            if image_path:
                license_plate = read_license_plate(image_path)
                # Retrieve entry_time from database or file
                entry_time = "2024-05-26 12:00:00"  # Example entry time
                exit_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                total_fee = calculate_fee(entry_time, exit_time)
                print(f"Total fee for {license_plate}: ${total_fee}")
                # Send webhook
                data = {
                    "license_plate": license_plate,
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "total_fee": total_fee
                }
                send_webhook(data)
            else:
                print("Failed to capture image.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
