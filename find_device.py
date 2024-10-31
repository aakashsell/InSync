import pyudev
import pyaudio
import subprocess

def find_scarlet_interface():
    p = pyaudio.PyAudio()
    device_list = []

    # Iterate through all available devices
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info.get('name')

        # Check if the device name contains 'Scarlet'
        if 'Scarlet' in device_name:
            device_list.append((device_info, i))

    p.terminate()
    return device_list

def get_device_path():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    observer = pyudev.MonitorObserver(monitor, device_connected)
    observer.start()

    for device in iter(monitor.poll, None):
        if device.action == 'add':
            print("USB Device Connected:")
            print(" Device Path:", device.device_path)
    
    while True:
        try:
            pass
        except KeyboardInterrupt:
            observer.stop()
            break
    return 'silly'

def main():
    device_list = find_scarlet_interface()

    if device_list:
        print("Scarlet Audio Interface found:")
        for device_info, index in device_list:
            print(f"  Device Name: {device_info['name']}, Index: {index}")
            get_device_path()
            #print(f"  Device Path (Identification Info): {path}")
    else:
        print("No Scarlet USB Audio Interface found.")

if __name__ == "__main__":
    main()
